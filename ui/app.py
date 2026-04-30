import streamlit as st
import requests
from datetime import datetime

# 🔗 Change this when deploying
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fraud Detection System", layout="centered")

st.title("💳 Smart Fraud Detection System")
st.markdown("### Real-time Transaction Risk Analysis")

# ⏱ Current time
current_time = datetime.now()
st.info(f"🕒 Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

st.subheader("Enter Transaction Details")

# 👤 User input
account_id = st.text_input("👤 Account ID", value="user_1")

amount = st.number_input(
    "💰 Transaction Amount",
    min_value=0.0,
    value=1000.0
)

tx_type_label = st.selectbox(
    "🏦 Transaction Type",
    ["CASH_IN", "CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT"]
)

# 🔁 Map UI → Model input
type_mapping = {
    "PAYMENT": 0,
    "TRANSFER": 1,
    "CASH_OUT": 2,
    "DEBIT": 3,
    "CASH_IN": 4
}

# 🚀 Button
if st.button("🔍 Analyze Transaction"):

    data = {
        "account_id": account_id,
        "amount": amount,
        "type": type_mapping[tx_type_label]
    }

    with st.spinner("Analyzing transaction... ⏳"):
        try:
            response = requests.post(
                f"{API_URL}/score",
                json=data,
                timeout=30
            )

            # 🔍 DEBUG INFO (VERY IMPORTANT)
            st.write("Status Code:", response.status_code)
            st.write("Raw Response:", response.text)

            if response.status_code == 200:
                result = response.json()

                st.success("✅ Analysis Completed")

                # 👤 Transaction count
                st.metric("📊 Transaction Count", result.get("transaction_count", 0))

                # 🆕 New user case
                if "message" in result:
                    st.info(result["message"])
                    st.write("Decision:", result.get("decision"))
                
                else:
                    # 📊 Metrics
                    col1, col2 = st.columns(2)

                    col1.metric(
                        "Fraud Probability",
                        f"{result.get('fraud_probability', 0):.2f}"
                    )

                    col2.metric(
                        "Risk Score",
                        f"{result.get('risk_score', 0):.2f}"
                    )

                    # 🚦 Decision
                    st.subheader("🚦 Decision")

                    decision = result.get("decision")

                    if decision == "BLOCK":
                        st.error("🚫 Transaction Blocked")
                    elif decision == "REVIEW":
                        st.warning("⚠️ Needs Review")
                    else:
                        st.success("✅ Transaction Allowed")

                    # 📉 Anomaly score (optional)
                    if "anomaly_score" in result:
                        st.subheader("📊 Anomaly Score")
                        st.write(result["anomaly_score"])

                    # 🧠 Reasons
                    if "reasons" in result:
                        st.subheader("🧠 Why this decision?")
                        for reason in result["reasons"]:
                            st.write("•", reason)

            else:
                st.error("❌ API Error")

        except requests.exceptions.ReadTimeout:
            st.warning("⏳ Server is slow / waking up. Try again.")

        except Exception as e:
            st.error(f"❌ Connection Error: {e}")