import pandas as pd
import psycopg2
from psycopg2 import sql
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection with environment variables

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgres'),
    'database': os.getenv('DB_NAME', 'washdata_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', 5432)
}

BASE_DIR = "/app/project0/dataschema"
MONTHS = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

def #load_schema_from_sql(conn):
    """Load the consolidated schema from dailyreport.sql"""
    schema_file = os.path.join(BASE_DIR, "dailyreport.sql")
    
    with open(schema_file, 'r') as f:
        sql_script = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql_script)
        conn.commit()
    print("✅ Schema loaded from dailyreport.sql")

def migrate_excel_data_to_unified_schema(conn, month_name):
    """
    Migrate Excel files from month folders into unified wash_orders table.
    Maps old washdata fields to new consolidated schema.
    """
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
            try:
                # Extract date from filename: washdata_DDMMYYYY.xlsx
                filename = file_path.stem
                date_str = filename.split('_')[1]
                day = date_str[0:2]
                month = date_str[2:4]
                year = date_str[4:8]
                formatted_date = f"{year}-{month}-{day}"
                
                # Read Excel file
                df = pd.read_excel(file_path)
                print(f"  Reading {file_path.name} ({len(df)} rows)...")
                
                # Insert into unified wash_orders table
                for _, row in df.iterrows():
                    insert_sql = """
                    INSERT INTO wash_orders 
                    (phone_number, wash_type, operator_name, entry_time, 
                     checkout_estimated_time, payment_method, price_paid, 
                     comments, created_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """
                    
                    # Map old fields to new schema
                    phone = row.get('phone', '')
                    wash_service = row.get('wash_service', 'xtream')
                    
                    # Normalize wash_service to enum values
                    wash_type_map = {
                        'handpolish': 'handpolish',
                        'xtream': 'xtream',
                        'deluxe': 'deluxe',
                        'hand polish': 'handpolish',
                        'x-tream': 'xtream'
                    }
                    wash_type = wash_type_map.get(wash_service.lower(), 'xtream')
                    
                    entry_time = pd.to_datetime(row.get('entry_time', None), errors='coerce') or pd.Timestamp.now()
                    checkout_time = pd.to_datetime(row.get('out_time', None), errors='coerce')
                    payment_method = row.get('payment_method', 'cash')
                    amount_paid = float(row.get('amount_paid', 0)) if pd.notna(row.get('amount_paid')) else None
                    comments = row.get('comments', '')
                    
                    cur.execute(insert_sql, (
                        phone,
                        wash_type,
                        'migrated_operator',
                        entry_time,
                        checkout_time,
                        payment_method,
                        amount_paid,
                        f"Migrated: {comments}",
                        formatted_date,
                        'completed'  # Historical data marked as completed
                    ))
                
                conn.commit()
                print(f"  ✅ Loaded {file_path.name} ({len(df)} records)")
                
            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
                conn.rollback()

def migrate_all_months(conn):
    """Migrate all monthly Excel data to unified schema"""
    for month in MONTHS:
        print(f"\n📂 Migrating {month}...")
        migrate_excel_data_to_unified_schema(conn, month)

def print_summary(conn):
    """Print database summary statistics"""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM wash_orders;")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM wash_orders WHERE status = 'completed';")
        completed = cur.fetchone()[0]
        
        cur.execute("SELECT SUM(price_paid) FROM wash_orders WHERE status = 'completed';")
        total_revenue = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(DISTINCT phone_number) FROM wash_orders;")
        unique_customers = cur.fetchone()[0]
        
        print("\n" + "="*50)
        print("📊 MIGRATION SUMMARY")
        print("="*50)
        print(f"Total Orders:        {total}")
        print(f"Completed Orders:    {completed}")
        print(f"Total Revenue:       ${total_revenue:.2f}")
        print(f"Unique Customers:    {unique_customers}")
        print("="*50)

def main():
    try:
        print("🚀 Starting Data Migration to Unified Schema...\n")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to database")
        
        # Load unified schema
        #load_schema_from_sql(conn)
        
        # Migrate all historical Excel data
        migrate_all_months(conn)
        
        # Print summary
        print_summary(conn)
        
        conn.close()
        print("\n✅ Data migration complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()