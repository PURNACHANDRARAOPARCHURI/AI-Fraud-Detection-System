import pandas as pd
def create_features(df):
    df=df.copy()
    df["hour"]=df["step"]%24
    df["tx_count"]=df.groupby("nameOrig").cumcount()
    df["balance_diff"]=df["oldbalanceOrg"]-df["newbalanceOrig"]
    df["is_large_tx"]=(df["amount"]>df["amount"].quantile(0.95)).astype(int)
    df["emptied_account"]=(df["newbalanceOrig"]==0).astype(int)
    df["type"]=df["type"].map({
        "PAYMENT":0,
        "TRANSFER":1,
        "CASH_OUT":2,
        "DEBIT":3,
        "CASH_IN":4}
    ).fillna(-1)
    return df