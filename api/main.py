from fastapi import FastAPI
import pandas as pd
import joblib

from api.db import get_user_transactions, insert_transaction
from api.schemas import TransactionRequest

from src.feature_engineering import create_features
from src.risk_engine import compute_risk
from src.decision_engine import make_decision
from src.reasons import generate_reasons

app = FastAPI()

# Load models
xgb = joblib.load("models/xgb_model.pkl")
iso = joblib.load("models/iso_model.pkl")


@app.post("/score")
def score(data: TransactionRequest):

    df = get_user_transactions(data.account_id)

    # ✅ NEW USER
    if df.empty:
        df = pd.DataFrame([{
            "account_id": data.account_id,
            "step": 1,
            "type": data.type,
            "amount": data.amount,
            "oldbalanceOrg": 10000,
            "newbalanceOrig": 10000 - data.amount
        }])
    else:
        # Ensure required columns
        for col in ["oldbalanceOrg", "newbalanceOrig", "step"]:
            if col not in df.columns:
                df[col] = 10000

        last_balance = df.iloc[-1].get("newbalanceOrig", 10000)

        new_tx = {
            "account_id": data.account_id,
            "step": int(df["step"].max()) + 1,
            "type": data.type,
            "amount": data.amount,
            "oldbalanceOrg": last_balance,
            "newbalanceOrig": last_balance - data.amount
        }

        df = pd.concat([df, pd.DataFrame([new_tx])], ignore_index=True)

    # Required for feature engineering
    df["nameOrig"] = df["account_id"]

    # Feature engineering
    df = create_features(df)
    latest = df.iloc[-1]

    features = [
        "amount", "hour", "is_large_tx",
        "tx_count", "balance_diff",
        "emptied_account", "type"
    ]

    # Ensure features exist
    for col in features:
        if col not in latest:
            latest[col] = 0

    X = latest[features].values.reshape(1, -1)

    # Predictions
    try:
        prob = xgb.predict_proba(X)[0][1]
    except:
        prob = 0.5

    try:
        anomaly = -iso.decision_function(X)[0]
    except:
        anomaly = 0.5

    risk = compute_risk(
        prob,
        anomaly,
        latest.get("is_large_tx", 0),
        latest.get("emptied_account", 0),
        latest.get("amount", 0)
    )

    decision = make_decision(risk)
    reasons = generate_reasons(latest.to_dict(), prob, anomaly)

    # Save transaction
    final_tx = {
        "account_id": data.account_id,
        "step": int(latest.get("tx_count", 0)) + 1,
        "type": data.type,
        "amount": float(latest.get("amount", 0)),
        "oldbalanceOrg": float(latest.get("oldbalanceOrg", 10000)),
        "newbalanceOrig": float(latest.get("newbalanceOrig", 10000))
    }

    insert_transaction(final_tx)

    return {
        "transaction_count": int(latest.get("tx_count", 0)) + 1,
        "fraud_probability": float(prob),
        "risk_score": float(risk),
        "decision": decision,
        "reasons": reasons
    }