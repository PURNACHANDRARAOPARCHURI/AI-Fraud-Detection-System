import pandas as pd
def create_features(df):
    df = df.copy()
    df["hour"] = df["step"] % 24
    df["tx_count"] = df.groupby("nameOrig").cumcount() + 1
    df["balance_diff"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
    threshold = df["amount"].quantile(0.95) if len(df) > 5 else df["amount"].max()
    df["is_large_tx"] = (df["amount"] > threshold).astype(int)
    df["emptied_account"] = (df["newbalanceOrig"] == 0).astype(int)
    df["type"] = df["type"].astype(int)
    return df