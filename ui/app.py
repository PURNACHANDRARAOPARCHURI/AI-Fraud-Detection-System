import streamlit as st
import requests
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8000/score"

st.set_page_config(page_title="Fraud Detection", layout="wide")

# =========================
# HEADER
# =========================
st.title("🏦 Fraud Risk Monitoring System")
st.caption("Real-time transaction monitoring and fraud detection")

st.markdown("---")

# =========================
# SECTION 1: USER TRANSACTION
# =========================
st.subheader("🧾 Transaction Initiated")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("💰 Transaction Amount", min_value=0.0, step=100.0)

with col2:
    tx_type = st.selectbox(
        "💳 Transaction Type",
        ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]
    )

# =========================
# AUTO TIME (REALISTIC)
# =========================
hour = datetime.now().hour
st.write(f"⏰ Transaction Time: {hour}:00 (auto-detected)")

st.markdown("---")

# =========================
# SECTION 2: SYSTEM ANALYSIS
# =========================
st.subheader("⚙️ System Behavioral Analysis")

# Simulate realistic account behavior
old_balance = random.uniform(10000, 200000)
new_balance = max(old_balance - amount, 0)

balance_diff = old_balance - new_balance
tx_count = random.randint(0, 20)
emptied_account = 1 if new_balance == 0 else 0
is_large_tx = 1 if amount > 200000 else 0

col3, col4, col5 = st.columns(3)

col3.metric("🔁 Transaction Frequency", tx_count)
col4.metric("💼 Old Balance", f"{old_balance:.0f}")
col5.metric("📉 New Balance", f"{new_balance:.0f}")

col6, col7 = st.columns(2)
col6.metric("📊 Balance Change", f"{balance_diff:.0f}")
col7.metric("🏦 Account Emptied", "Yes" if emptied_account else "No")

st.info("Behavioral and financial features are automatically derived from transaction context")

st.markdown("---")

# =========================
# SECTION 3: DECISION ENGINE
# =========================
if st.button("🚀 Analyze Transaction"):

    payload = {
        "amount": amount,
        "hour": hour,
        "tx_count": tx_count,
        "balance_diff": balance_diff,
        "is_large_tx": is_large_tx,
        "emptied_account": emptied_account,
        "type": ["PAYMENT","TRANSFER","CASH_OUT","DEBIT","CASH_IN"].index(tx_type)
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            data = response.json()

            st.markdown("## 🚨 Risk Decision Engine Output")

            col8, col9, col10 = st.columns(3)

            col8.metric("Fraud Probability", f"{data['fraud_probability']:.2f}")
            col9.metric("Risk Score", f"{data['risk_score']:.2f}")
            col10.metric("Decision", data["decision"])

            # Decision Alerts
            if data["decision"] == "BLOCK":
                st.error("🚨 Transaction Blocked (High Risk)")
            elif data["decision"] == "REVIEW":
                st.warning("⚠️ Flagged for Manual Review")
            else:
                st.success("✅ Transaction Approved")

            st.markdown("---")

            # Explainability
            st.subheader("Why was this flagged?")
            for r in data["reasons"]:
                st.write("•", r)

        else:
            st.error("API Error")

    except:
        st.error("🚨 Backend API is not running. Start FastAPI server.")