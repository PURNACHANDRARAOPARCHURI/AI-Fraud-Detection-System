import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
from datetime import datetime
from collections import defaultdict

xgb = joblib.load("models/xgb_model.pkl")
iso = joblib.load("models/iso_model.pkl")

from src.risk_enginee import compute_risk
from src.decision_engine import make_decision
from src.reasons import generate_reasons

app = FastAPI(title="Fraud Detection API")

class Transaction(BaseModel):
    account_id: str
    amount: float
    type: int

user_history = defaultdict(list)

def generate_features(data):
    hour = datetime.now().hour
    history = user_history[data.account_id]
    tx_count = len(history)
    if len(history) >= 2:
        diffs = np.diff(history)
        balance_diff = float(np.mean(diffs))
    else:
        balance_diff = 0.0
    is_large_tx = 1 if len(history) > 0 and data.amount > (sum(history)/len(history)) else 0
    outgoing_types = [1, 2, 3, 4]

    emptied_account = 1 if (
        data.type in outgoing_types and
        len(history) > 0 and
        data.amount >= max(history)
    ) else 0
    return [
        data.amount,
        hour,
        is_large_tx,
        tx_count,
        balance_diff,
        emptied_account,
        data.type
    ]

@app.get("/")
def home():
    return {"message": "API running locally 🚀"}

@app.post("/score")
def score(data: Transaction):
    features = generate_features(data)
    X = np.array([features])
    prob = float(xgb.predict_proba(X)[0][1])
    anomaly = float(-iso.decision_function(X)[0])
    risk = compute_risk(
        prob,
        anomaly,
        features[2],
        features[5],
        data.amount
    )
    decision = make_decision(risk)
    feature_dict = {
        "amount": data.amount,
        "type": data.type,
        "hour": features[1],
        "is_large_tx": features[2],
        "tx_count": features[3],
        "balance_diff": features[4],
        "emptied_account": features[5]
    }
    reasons = generate_reasons(feature_dict, prob, anomaly)
    user_history[data.account_id].append(data.amount)
    return {
        "fraud_probability": prob,
        "anomaly_score": anomaly,
        "risk_score": risk,
        "decision": decision,
        "reasons": reasons
    }