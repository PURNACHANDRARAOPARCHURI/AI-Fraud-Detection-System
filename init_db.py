import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

print(f"🔗 Connecting to NeonTech database...")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create the transactions table
create_table_sql = """
DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    step INTEGER,
    type INTEGER,
    amount FLOAT,
    oldbalanceOrg FLOAT,
    newbalanceOrig FLOAT,
    nameOrig VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_step ON transactions(step);
"""

try:
    with engine.connect() as conn:
        # Split SQL statements and execute them
        for statement in create_table_sql.split(';'):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()
        
    print("✅ Database initialized successfully!")
    print("   - Created 'transactions' table")
    print("   - Created indexes on account_id and step")
    
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    raise

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM transactions"))
        count = result.scalar()
        print(f"✅ Table verified - Current record count: {count}")
except Exception as e:
    print(f"❌ Error testing connection: {e}")
    raise

engine.dispose()
