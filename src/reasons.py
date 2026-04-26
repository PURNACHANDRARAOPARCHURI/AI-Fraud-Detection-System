def generate_reasons(data,prob,anamoly):
    reasons=[]
    if data.get("is_large_tx",0)==1:
        reasons.append("Transaction amount is unusally high")
    if data.get("emptied_account",0)==1:
        reasons.append("Account was Emptied afetr Transaction")
    if data.get("tx_count",0)==10:
        reasons.append("High frequency Transactions")
    if data.get("balance_diff",0)>20000:
        reasons.append("unusal balance difference observed")
    if data.get("amount",0)>100000:
        reasons.append("Huge amount change")
    if data.get("type",-1)==2:
        reasons.append("cash-out Transactions are high risk")
    if prob>=0.9:
        reasons.append("Model detected High fraud Probability")
    elif prob>=0.7:
        reasons.append("Chances of Fraud needs to be evaluate")
    if anamoly>=0.7:
        reasons.append("Transactions deviated from original behaviour")
    if not reasons:
        reasons.append("No strong fraud detection indicated")
    return reasons