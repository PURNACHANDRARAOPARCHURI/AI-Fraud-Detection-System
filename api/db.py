from sqlalchemy import text

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