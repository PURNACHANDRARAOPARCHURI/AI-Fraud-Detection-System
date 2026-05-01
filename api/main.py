from fastapi import FastAPI
import pandas as pd
import joblib
import os
from api.db import get_user_transactions, insert_transaction
from api.schemas import TransactionRequest
from src.feature_engineering import create_features
from src.risk_engine import compute_risk
from src.decision_engine import make_decision
from src.reasons import generate_reasons
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    xgb = joblib.load(os.path.join(BASE_DIR, "models", "xgb_model.pkl"))
    iso = joblib.load(os.path.join(BASE_DIR, "models", "iso_model.pkl"))
except Exception as e:
    print("Model loading error:", e)
    xgb = None
    iso = None
@app.post("/score")
def score(data: TransactionRequest):
    try:
        df = get_user_transactions(data.account_id)
        if df.empty:
            new_balance = max(0, 10000 - data.amount)
            df = pd.DataFrame([{
                "account_id": data.account_id,
                "step": 1,
                "type": data.type,
                "amount": data.amount,
                "oldbalanceOrg": 10000,
                "newbalanceOrig": new_balance
            }])
        else:
            for col in ["oldbalanceOrg", "newbalanceOrig", "step"]:
                if col not in df.columns:
                    df[col] = 10000
            last_balance = df.iloc[-1].get("newbalanceOrig", 10000)
            new_balance = max(0, last_balance - data.amount)
            new_tx = {
                "account_id": data.account_id,
                "step": int(df["step"].max()) + 1,
                "type": data.type,
                "amount": data.amount,
                "oldbalanceOrg": last_balance,
                "newbalanceOrig": new_balance
            }
            df = pd.concat([df, pd.DataFrame([new_tx])], ignore_index=True)
        df["nameOrig"] = df["account_id"]
        df = create_features(df)
        latest = df.iloc[-1].copy()
        features = [
            "amount", "hour", "is_large_tx",
            "tx_count", "balance_diff",
            "emptied_account", "type"
        ]
        for col in features:
            if col not in latest.index:
                latest[col] = 0
        X = latest[features].astype(float).values.reshape(1, -1)
        prob = xgb.predict_proba(X)[0][1] if xgb else 0.5
        anomaly = -iso.decision_function(X)[0] if iso else 0.5
        risk = compute_risk(
            prob,
            anomaly,
            latest.get("is_large_tx", 0),
            latest.get("emptied_account", 0),
            latest.get("amount", 0)
        )
        decision = make_decision(risk)
        reasons = generate_reasons(latest.to_dict(), prob, anomaly)
        final_tx = {
            "account_id": data.account_id,
            "step": int(df["step"].max()),
            "type": data.type,
            "amount": float(latest.get("amount", 0)),
            "oldbalanceOrg": float(latest.get("oldbalanceOrg", 10000)),
            "newbalanceOrig": float(latest.get("newbalanceOrig", 10000))
        }
        insert_transaction(final_tx)
        return {
            "transaction_count": int(latest.get("tx_count", 0)),
            "fraud_probability": float(prob),
            "risk_score": float(risk),
            "decision": decision,
            "reasons": reasons
        }
    except Exception as e:
        return {"error": str(e)}