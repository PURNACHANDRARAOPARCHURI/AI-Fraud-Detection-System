import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
def get_user_transactions(account_id):
    query = "SELECT * FROM transactions WHERE account_id = %s ORDER BY step ASC"
    return pd.read_sql(query, engine, params=(account_id,))
def insert_transaction(tx):
    try:
        print("INSERTING:", tx)

        with engine.begin() as conn:
            query = text("""
                INSERT INTO transactions 
                (account_id, step, type, amount, oldbalanceorg, newbalanceorig)
                VALUES 
                (:account_id, :step, :type, :amount, :oldbalanceOrg, :newbalanceOrig)
            """)
            conn.execute(query, tx)
        print("INSERT SUCCESS")
    except Exception as e:
        print("INSERT ERROR:", e)
        raise e