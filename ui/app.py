import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fraud Detection System", layout="centered")

st.title("💳 Smart Fraud Detection")
st.markdown("### Real-time Transaction Risk Analysis")

current_time = datetime.now()
st.info(f"🕒 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

st.subheader("Enter Transaction Details")

account_id = st.text_input("👤 Account ID", value="user_1")

amount = st.number_input("💰 Transaction Amount", min_value=0.0, value=1000.0)

tx_type = st.selectbox(
    "🏦 Transaction Type",
    ["CASH_IN", "CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT"]
)

type_mapping = {
    "CASH_IN": 0,
    "CASH_OUT": 1,
    "DEBIT": 2,
    "PAYMENT": 3,
    "TRANSFER": 4
}

if st.button("🔍 Analyze Transaction"):
    data = {
        "account_id": account_id,
        "amount": amount,
        "type": type_mapping[tx_type]
    }

    with st.spinner("Analyzing transaction... Please wait ⏳"):
        try:
            response = requests.post(
                f"{API_URL}/score",
                json=data,
                timeout=90
            )

            if response.status_code == 200:
                result = response.json()

                st.success("✅ Analysis Completed")

                col1, col2 = st.columns(2)

                col1.metric("Fraud Probability", f"{result['fraud_probability']:.2f}")
                col2.metric("Risk Score", f"{result['risk_score']:.2f}")

                st.subheader("🚦 Decision")

                if result["decision"] == "BLOCK":
                    st.error("🚫 Transaction Blocked (Fraud Suspected)")
                else:
                    st.success("✅ Transaction Allowed")

                st.subheader("📊 Anomaly Score")
                st.write(result["anomaly_score"])

                st.subheader("🧠 Why this decision?")
                for reason in result.get("reasons", []):
                    st.write("•", reason)

            else:
                st.error("❌ API Error")

        except requests.exceptions.ReadTimeout:
            st.warning("⏳ Server is waking up. Try again in a few seconds.")

        except Exception as e:
            st.error(f"❌ Connection Error: {e}")