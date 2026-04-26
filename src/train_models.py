import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest

from src.feature_engineering import create_features

# =========================
# LOAD DATA (FULL DATASET)
# =========================
df = pd.read_csv("data/paysim.csv")

print("Dataset shape:", df.shape)
print("Fraud distribution:\n", df["isFraud"].value_counts())

# =========================
# FEATURE ENGINEERING
# =========================
df = create_features(df)

# ✅ IMPORTANT: correct order
features = [
    "amount",
    "hour",
    "is_large_tx",
    "tx_count",
    "balance_diff",
    "emptied_account",
    "type"
]

X = df[features]
y = df["isFraud"]

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# =========================
# HANDLE IMBALANCE (CORRECT WAY)
# =========================
scale = (y_train == 0).sum() / (y_train == 1).sum()
print("Scale_pos_weight:", scale)

# =========================
# MODEL TRAINING
# =========================
xgb = XGBClassifier(
    eval_metric="logloss",
    scale_pos_weight=scale,   # 🔥 KEY FIX
    max_depth=6,
    n_estimators=500,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

xgb.fit(X_train, y_train)

# =========================
# ANOMALY MODEL
# =========================
iso = IsolationForest(
    contamination=0.002,
    random_state=42
)
iso.fit(X_train)

probs = xgb.predict_proba(X_test)[:, 1]
preds = (probs > 0.5).astype(int)
print("\n=== Classification Report ===")
print(classification_report(y_test, preds))
print("Prediction distribution:", np.unique(preds, return_counts=True))
os.makedirs("models", exist_ok=True)

joblib.dump(xgb, "models/xgb_model.pkl")
joblib.dump(iso, "models/iso_model.pkl")

print("\n✅ Models saved successfully!")