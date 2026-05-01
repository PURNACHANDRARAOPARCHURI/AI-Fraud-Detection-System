def generate_reasons(data, prob, anomaly):
    reasons = []
    if data.get("is_large_tx", 0) == 1:
        reasons.append("Transaction amount is unusually high")
    if data.get("emptied_account", 0) == 1:
        reasons.append("Account was emptied after transaction")
    if data.get("tx_count", 0) >= 10:
        reasons.append("High frequency transactions")
    if data.get("balance_diff", 0) > 20000:
        reasons.append("Unusual balance difference observed")
    if data.get("amount", 0) > 100000:
        reasons.append("Huge transaction amount")
    if data.get("amount", 0) > 100000 and data.get("type") in [1, 4]:
        reasons.append("High-risk large transaction type")
    if prob >= 0.9:
        reasons.append("Model detected high fraud probability")
    elif prob >= 0.7:
        reasons.append("Moderate fraud probability detected")
    if anomaly >= 0.7:
        reasons.append("Transaction deviates from normal behavior")
    if not reasons:
        reasons.append("No strong fraud indicators detected")
    return reasons