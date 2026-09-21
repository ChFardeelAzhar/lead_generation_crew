import sqlite3
from datetime import datetime

DB_NAME = "leads_data.db"

def init_db():
    # Connection banayega ya agar database nahi hai to naya create kar dega
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table create kar rahe hain with UNIQUE constraint
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            owner_name TEXT,
            address TEXT,
            email TEXT,
            contact_number TEXT,
            website_url TEXT,
            category TEXT,
            country TEXT,
            timestamp DATETIME,
            UNIQUE(company_name, contact_number)
        )
    ''')
    conn.commit()
    conn.close()
    print("Database and tables initialized successfully!")

def insert_lead(company_name, owner_name, address, email, contact_number, website_url, category, country):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # INSERT OR IGNORE ka matlab hai ke agar same company+contact dobara aaye, to error nahi dega bas skip kar dega
        cursor.execute('''
            INSERT OR IGNORE INTO leads 
            (company_name, owner_name, address, email, contact_number, website_url, category, country, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_name, owner_name, address, email, contact_number, website_url, category, country, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception as e:
        print(f"Error inserting lead: {e}")
    finally:
        conn.close()

def get_all_leads():
    # Ye function UI table (Dataframe) ko populate karne ke kaam aayega
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT company_name, owner_name, address, email, contact_number, website_url, category, country, timestamp 
        FROM leads 
        ORDER BY timestamp DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    # Is file ko direct run karne par database initialize ho jayega
    init_db()