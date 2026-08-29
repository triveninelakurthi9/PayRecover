import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from app.db import get_db_connection, init_db

SEED_FILE = Path(__file__).parent.parent.parent / "seed_data" / "synthetic_cases.json"

FIRST_NAMES = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Neha", "Rahul", "Sneha", "Aditya", "Pooja", 
               "Kabir", "Meera", "Siddharth", "Kavya", "Arjun", "Tanvi", "Karan", "Ishita", "Yash", "Riya"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Gupta", "Rao", "Nair", "Singh", "Mukherjee", "Reddy", "Deshmukh",
              "Joshi", "Kapoor", "Mehta", "Bhat", "Chawla", "Kulkarni", "Saxena", "Chopra", "Dutta", "Iyer"]

RAZORPAY_FAILURE_CODES = [
    ("BAD_REQUEST_ERROR", "EXPIRED_CARD", "Card expiry date has passed. Please update payment details.", "card"),
    ("GATEWAY_ERROR", "INSUFFICIENT_FUNDS", "Account has insufficient balance to complete transaction.", "upi"),
    ("GATEWAY_ERROR", "BANK_TECHNICAL_DECLINE", "Core banking server timed out during authorization.", "netbanking"),
    ("BAD_REQUEST_ERROR", "RISK_CHECK_FAILED", "Transaction flagged by risk engine due to unusual IP location.", "card"),
    ("BAD_REQUEST_ERROR", "INVALID_OTP", "User entered an incorrect 3D-Secure OTP 3 times.", "card"),
    ("GATEWAY_ERROR", "GATEWAY_TIMEOUT", "Payment gateway connection dropped mid-transaction.", "upi"),
    ("BAD_REQUEST_ERROR", "PAYMENT_CANCELLED", "Customer closed the checkout window before authentication.", "netbanking"),
]

ABANDONMENT_REASONS = [
    (None, "Cart left idle at payment selection screen for >30 minutes.", "upi"),
    (None, "Abandoned at OTP verification step after 2 minutes of inactivity.", "card"),
    (None, "Customer exited payment drawer without selecting a payment mode.", "netbanking"),
]

SUBSCRIPTION_FAILURE_REASONS = [
    ("SUBSCRIPTION_ERROR", "AUTOPAY_MANDATE_DECLINED", "UPI Mandate auto-debit rejected by issuing bank.", "upi_autopay"),
    ("BAD_REQUEST_ERROR", "EXPIRED_CARD", "Recurring billing failed: Saved card expired.", "card_recurring"),
    ("GATEWAY_ERROR", "INSUFFICIENT_FUNDS", "Monthly subscription renewal failed due to low account balance.", "upi_autopay"),
]

def generate_synthetic_cases(count: int = 65):
    random.seed(42)  # Deterministic seed for reproducible evaluation
    cases = []
    base_time = datetime.now() - timedelta(hours=36)

    for i in range(1, count + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        customer_name = f"{first} {last}"
        customer_id = f"cust_{first.lower()}_{i:03d}"
        email = f"{first.lower()}.{last.lower()}{i}@example.in"
        phone = f"+9198{random.randint(10000000, 99999999)}"
        
        # Category breakdown: ~45% degradation, ~35% abandonment, ~20% subscription
        cat_roll = random.random()
        if cat_roll < 0.45:
            category = "payment_degradation"
            code, sub_code, desc, method = random.choice(RAZORPAY_FAILURE_CODES)
            failure_code = f"{code}:{sub_code}"
            failure_description = desc
            payment_method = method
            amount = round(random.uniform(499.0, 15999.0), 2)
        elif cat_roll < 0.80:
            category = "checkout_abandonment"
            code, desc, method = random.choice(ABANDONMENT_REASONS)
            failure_code = "CHECKOUT_ABANDONED"
            failure_description = desc
            payment_method = method
            amount = round(random.uniform(299.0, 8999.0), 2)
        else:
            category = "subscription_failure"
            code, sub_code, desc, method = random.choice(SUBSCRIPTION_FAILURE_REASONS)
            failure_code = f"{code}:{sub_code}"
            failure_description = desc
            payment_method = method
            amount = round(random.uniform(999.0, 4999.0), 2)

        # Prior attempts: most 0 or 1, a few 2 or 3
        prior_attempts = random.choice([0, 0, 0, 1, 1, 2, 3])
        channel_pref = random.choice(["email", "whatsapp", "sms"])
        time_offset = timedelta(minutes=random.randint(5, 1800))
        timestamp = (base_time + time_offset).isoformat()

        case_id = f"PAY-{i:04d}"

        case_obj = {
            "id": case_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": email,
            "customer_phone": phone,
            "category": category,
            "amount": amount,
            "currency": "INR",
            "timestamp": timestamp,
            "failure_code": failure_code,
            "failure_description": failure_description,
            "payment_method": payment_method,
            "prior_attempts": prior_attempts,
            "channel_pref": channel_pref,
            "status": "pending",
            "root_cause": None,
            "confidence": 1.0,
            "rule_fired": None,
            "last_action": None,
            "last_action_at": None,
            "razorpay_order_id": f"order_{uuid.uuid4().hex[:12]}",
            "razorpay_payment_link_id": None,
            "razorpay_payment_link_url": None,
            "drafted_message": None
        }
        cases.append(case_obj)

    # Ensure parent dir exists
    SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEED_FILE, "w") as f:
        json.dump(cases, f, indent=2)

    print(f"Generated {len(cases)} synthetic recovery cases in {SEED_FILE}")
    return cases

def load_seed_into_db():
    init_db()
    if not SEED_FILE.exists():
        generate_synthetic_cases()
    
    with open(SEED_FILE, "r") as f:
        cases = json.load(f)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data on seed reload
    cursor.execute("DELETE FROM audit_logs;")
    cursor.execute("DELETE FROM cases;")

    for c in cases:
        cursor.execute("""
            INSERT INTO cases (
                id, customer_id, customer_name, customer_email, customer_phone,
                category, amount, currency, timestamp, failure_code,
                failure_description, payment_method, prior_attempts, channel_pref,
                status, razorpay_order_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            c["id"], c["customer_id"], c["customer_name"], c["customer_email"], c["customer_phone"],
            c["category"], c["amount"], c["currency"], c["timestamp"], c["failure_code"],
            c["failure_description"], c["payment_method"], c["prior_attempts"], c["channel_pref"],
            c["status"], c["razorpay_order_id"]
        ))

    conn.commit()
    conn.close()
    print(f"Loaded {len(cases)} synthetic cases into SQLite DB successfully.")

if __name__ == "__main__":
    load_seed_into_db()
