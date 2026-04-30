import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

print(f"🔗 Connecting directly to NeonTech database with psycopg2...")

# Parse connection string
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected to database!")
    
    # Drop old table if exists
    print("🔄 Dropping old transactions table...")
    cursor.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    conn.commit()
    print("✅ Old table dropped")
    
    # Create new table with correct schema
    print("📋 Creating new transactions table...")
    cursor.execute("""
    CREATE TABLE transactions (
        id SERIAL PRIMARY KEY,
        account_id VARCHAR(255) NOT NULL,
        step INTEGER,
        type INTEGER,
        amount FLOAT,
        "oldbalanceOrg" FLOAT,
        "newbalanceOrig" FLOAT,
        nameOrig VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    print("✅ Table created successfully!")
    
    # Create indexes
    print("📊 Creating indexes...")
    cursor.execute("CREATE INDEX idx_account_id ON transactions(account_id);")
    cursor.execute("CREATE INDEX idx_step ON transactions(step);")
    conn.commit()
    print("✅ Indexes created!")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM transactions;")
    count = cursor.fetchone()[0]
    print(f"✅ Table verified - Current record count: {count}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    raise
