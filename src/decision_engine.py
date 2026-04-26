def make_decision(risk_score):
    high=0.8
    medium_risk=0.5
    if risk_score>=high :
        return "BLOCK"
    elif risk_score>=medium_risk:
        return "REVIEW"
    else:
        return "ALLOW"