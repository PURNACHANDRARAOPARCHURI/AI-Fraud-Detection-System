from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
import json

from src.risk_enginee import compute_risk
from src.decision_engine import make_decision
from src.reasons import generate_reasons
from src.loggers import log_transaction

# Load models
xgb = joblib.load("models/xgb_model.pkl")
iso = joblib.load("models/iso_model.pkl")

# Load threshold
try:
    with open("models/config.json") as f:
        config = json.load(f)
    THRESHOLD = config.get("threshold", None)
except:
    THRESHOLD = None

app = FastAPI(title="Fraud Risk Scoring API")


# =========================
# Input Schema
# =========================
class Transaction(BaseModel):
    amount: float
    hour: int
    tx_count: int
    balance_diff: float
    is_large_tx: int
    emptied_account: int
    type: int


# =========================
# Routes
# =========================
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}


@app.post("/score")
def score(data: Transaction):

    # ✅ FIXED feature order (same as training)
    X = np.array([[ 
        data.amount,
        data.hour,
        data.is_large_tx,
        data.tx_count,
        data.balance_diff,
        data.emptied_account,
        data.type
    ]])

    # Predictions
    prob = xgb.predict_proba(X)[0][1]
    anomaly = -iso.decision_function(X)[0]

    # ✅ FIXED (added comma + amount)
    risk = compute_risk(
        prob,
        anomaly,
        data.is_large_tx,
        data.emptied_account,
        data.amount
    )

    # Decision
    if THRESHOLD is not None:
        decision = "BLOCK" if risk > THRESHOLD else "ALLOW"
    else:
        decision = make_decision(risk)

    # Explainability
    reasons = generate_reasons(data.dict(), prob, anomaly)

    # Response
    result = {
        "fraud_probability": float(prob),
        "anomaly_score": float(anomaly),
        "risk_score": float(risk),
        "decision": decision,
        "reasons": reasons
    }

    # Logging
    log_transaction(data.dict(), result)

    return result