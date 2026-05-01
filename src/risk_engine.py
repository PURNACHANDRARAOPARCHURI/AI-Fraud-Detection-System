import numpy as np
def normalize_anomaly(score, min_val=0, max_val=1):
    return (score - min_val) / (max_val - min_val + 1e-6)
def compute_risk(prob, anomaly, is_large_tx, emptied_account, amount):
    anomaly_norm = normalize_anomaly(anomaly)
    rule_score = 0
    if amount > 100000:
        rule_score += 0.2
    if is_large_tx:
        rule_score += 0.2
    if emptied_account:
        rule_score += 0.3
    final_score = (0.6 * prob + 0.3 * anomaly_norm + 0.1 * rule_score)
    final_risk = np.clip(final_score, 0, 1)
    return float(final_risk)