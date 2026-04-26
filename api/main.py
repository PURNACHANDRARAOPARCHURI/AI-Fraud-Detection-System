from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
import os
import gdown

# =========================
# Download Models from Google Drive
# =========================

os.makedirs("models", exist_ok=True)

FILES = {
    "xgb_model.pkl": "1VJ-5WaXw2H06O6VnaydWWgbWprll2plE",
    "iso_model.pkl": "1W0oPvB9Q8HjThEwxajTCF3gLqYQFqkre"
}

for name, fid in FILES.items():
    path = f"models/{name}"
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        url = f"https://drive.google.com/uc?id={fid}"
        gdown.download(url, path, quiet=False)

# =========================
# Load Models
# =========================

xgb = joblib.load("models/xgb_model.pkl")
iso = joblib.load("models/iso_model.pkl")

# =========================
# Imports (FIXED)
# =========================

from src.risk_enginee import compute_risk
from src.decision_engine import make_decision
from src.reasons import generate_reasons
from src.loggers import log_transaction

# =========================
# FastAPI App
# =========================

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


@app.get("/")
def home():
    return {"message": "Fraud Detection API is running 🚀"}

@app.post("/score")
def score(data: Transaction):

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
    prob = float(xgb.predict_proba(X)[0][1])
    anomaly = float(-iso.decision_function(X)[0])

    # Risk score
    risk = compute_risk(
        prob,
        anomaly,
        data.is_large_tx,
        data.emptied_account,
        data.amount
    )

    # Decision
    decision = make_decision(risk)

    # Explainability
    reasons = generate_reasons(data.dict(), prob, anomaly)

    result = {
        "fraud_probability": prob,
        "anomaly_score": anomaly,
        "risk_score": float(risk),
        "decision": decision,
        "reasons": reasons
    }   
    log_transaction(data.dict(), result)
    return result