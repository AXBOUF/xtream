#!/usr/bin/env python3
"""
Simplified Excel to PostgreSQL Migration Script
"""
import os
import pandas as pd
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
import glob
from pathlib import Path

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'washdata_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Connected to database {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def parse_date_from_filename(filename):
    """Parse date from DDMMYYYY format filename"""
    base = Path(filename).stem
    # Extract date from washdata_DDMMYYYY.xlsx format
    if 'washdata_' in base:
        date_str = base.replace('washdata_', '')
        if len(date_str) == 8:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int(date_str[4:8])
            return datetime(year, month, day).date()
    return None

def map_service_type(service_name):
    """Map Excel service names to database enum values"""
    service_mapping = {
        'Hand Polish': 'handpolish',
        'Super Wash': 'deluxe',  # Map Super Wash to deluxe
        'Detail': 'deluxe',
        'Xtreme': 'xtream',
        'Deluxe': 'deluxe'
    }
    return service_mapping.get(service_name, 'deluxe')  # Default to deluxe

def process_excel_file(filepath, conn):
    """Process a single Excel file and insert into database"""
    try:
        # Read Excel file
        df = pd.read_excel(filepath)
        
        # Parse date from filename
        file_date = parse_date_from_filename(filepath)
        if not file_date:
            print(f"⚠️  Could not parse date from {filepath}")
            return False
            
        # Map columns to database schema
        records = []
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('phone', '')):
                continue
                
            record = {
                'phone_number': str(row.get('phone', '')).strip(),
                'customer_name': row.get('customer_name', ''),
                'wash_type': map_service_type(row.get('wash_service', 'deluxe')),
                'operator_name': row.get('operator_name', 'migrated'),
                'vehicle_plate': row.get('vehicle_plate', ''),
                'payment_method': row.get('payment_method', 'cash'),
                'price_paid': row.get('amount_paid', 0),
                'discount_applied': row.get('discount', 0),
                'status': 'completed',
                'created_date': file_date,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'comments': f"Migrated from {Path(filepath).name}"
            }
            records.append(record)
        
        # Insert records into database
        if records:
            cur = conn.cursor()
            
            # Prepare insert statement
            insert_query = """
            INSERT INTO wash_orders (
                phone_number, customer_name, wash_type, operator_name, vehicle_plate,
                payment_method, price_paid, discount_applied, status, created_date,
                created_at, updated_at, comments
            ) VALUES (
                %(phone_number)s, %(customer_name)s, %(wash_type)s, %(operator_name)s,
                %(vehicle_plate)s, %(payment_method)s, %(price_paid)s, %(discount_applied)s,
                %(status)s, %(created_date)s, %(created_at)s, %(updated_at)s, %(comments)s
            )
            """
            
            # Execute batch insert
            cur.executemany(insert_query, records)
            conn.commit()
            cur.close()
            
            print(f"✅ {filepath}: Migrated {len(records)} records")
            return True
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        conn.rollback()
        return False

def main():
    """Main migration function"""
    print("🚀 Starting Excel to PostgreSQL Migration...")
    
    # Connect to database
    conn = connect_db()
    if not conn:
        return
    
    total_files = 0
    successful_files = 0
    total_records = 0
    
    # Find all Excel files in project0/dataschema directory
    excel_pattern = "project0/dataschema/**/*.xlsx"
    excel_files = glob.glob(excel_pattern, recursive=True)
    
    print(f"📁 Found {len(excel_files)} Excel files")
    
    for filepath in excel_files:
        total_files += 1
        if process_excel_file(filepath, conn):
            successful_files += 1
            # Count records in this file for stats
            try:
                df = pd.read_excel(filepath)
                total_records += len(df)
            except:
                pass
    
    conn.close()
    
    print(f"\n📊 Migration Summary:")
    print(f"   Total files: {total_files}")
    print(f"   Successful: {successful_files}")
    print(f"   Total records: {total_records}")
    print(f"   Status: {'✅ Success' if successful_files == total_files else '❌ Partial failure'}")

if __name__ == "__main__":
    main()