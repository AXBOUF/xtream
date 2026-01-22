import pandas as pd
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'washdata_db',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}

BASE_DIR = "/workspaces/xtream/project0/dataschema"
MONTHS = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

def create_table(conn):
    """Create main washdata table with indexes"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS washdata (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        phone VARCHAR(20),
        wash_service VARCHAR(50),
        entry_time TIMESTAMP,
        out_time TIMESTAMP,
        payment_method VARCHAR(20),
        amount_paid DECIMAL(10, 2),
        comments TEXT,
        created_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for fast queries
    CREATE INDEX IF NOT EXISTS idx_created_date ON washdata(created_date);
    CREATE INDEX IF NOT EXISTS idx_user_id ON washdata(user_id);
    CREATE INDEX IF NOT EXISTS idx_entry_time ON washdata(entry_time);
    CREATE INDEX IF NOT EXISTS idx_payment_method ON washdata(payment_method);
    """
    
    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()
    print("✅ Table created with indexes")

def load_month_data(conn, month_name, month_num):
    """Load all Excel files from a month folder into database"""
    month_dir = os.path.join(BASE_DIR, month_name)
    
    if not os.path.exists(month_dir):
        print(f"⚠️  Folder not found: {month_dir}")
        return
    
    xlsx_files = list(Path(month_dir).glob("washdata_*.xlsx"))
    
    if not xlsx_files:
        print(f"⚠️  No files found in {month_name}")
        return
    
    with conn.cursor() as cur:
        for file_path in xlsx_files:
            # Extract date from filename: washdata_DDMMYYYY.xlsx
            filename = file_path.stem  # Remove .xlsx
            date_str = filename.split('_')[1]  # Get DDMMYYYY
            day = date_str[0:2]
            month = date_str[2:4]
            year = date_str[4:8]
            formatted_date = f"{year}-{month}-{day}"
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Insert into database
            for _, row in df.iterrows():
                insert_sql = """
                INSERT INTO washdata 
                (user_id, phone, wash_service, entry_time, out_time, 
                 payment_method, amount_paid, comments, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cur.execute(insert_sql, (
                    int(row['user_id']),
                    row['phone'],
                    row['wash_service'],
                    pd.to_datetime(row['entry_time']),
                    pd.to_datetime(row['out_time']),
                    row['payment_method'],
                    float(row['amount_paid']),
                    row['comments'],
                    formatted_date
                ))
            
            conn.commit()
            print(f"✅ Loaded {file_path.name} ({len(df)} records)")

def load_all_months(conn):
    """Load all monthly data"""
    for idx, month in enumerate(MONTHS, 1):
        print(f"\n📂 Loading {month}...")
        load_month_data(conn, month, idx)

def main():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("🔗 Connected to database")
        
        create_table(conn)
        load_all_months(conn)
        
        # Summary query
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM washdata;")
            total = cur.fetchone()[0]
            print(f"\n📊 Total records loaded: {total}")
        
        conn.close()
        print("✅ Database loading complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()