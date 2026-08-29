import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "payrecover.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'INR',
        timestamp TEXT NOT NULL,
        failure_code TEXT,
        failure_description TEXT,
        payment_method TEXT,
        prior_attempts INTEGER DEFAULT 0,
        channel_pref TEXT DEFAULT 'email',
        status TEXT DEFAULT 'pending',
        root_cause TEXT,
        confidence REAL DEFAULT 1.0,
        rule_fired TEXT,
        last_action TEXT,
        last_action_at TEXT,
        razorpay_order_id TEXT,
        razorpay_payment_link_id TEXT,
        razorpay_payment_link_url TEXT,
        drafted_message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create audit_logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        root_cause TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        rule_fired TEXT NOT NULL,
        outcome TEXT NOT NULL,
        amount_at_stake REAL NOT NULL,
        explanation TEXT NOT NULL,
        raw_details TEXT,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    );
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("SQLite Database initialized successfully at:", DB_PATH)
