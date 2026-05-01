import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

def get_user_transactions(account_id):
    query = "SELECT * FROM transactions WHERE account_id = %s ORDER BY step ASC"
    return pd.read_sql(query, engine, params=[account_id])

def insert_transaction(tx):
    df = pd.DataFrame([tx])
    df.to_sql("transactions", engine, if_exists="append", index=False)