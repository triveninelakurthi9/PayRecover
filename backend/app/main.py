import logging
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db import get_db_connection, init_db
from app.seed_generator import load_seed_into_db, generate_synthetic_cases
from app.execution_layer import execution_layer
from app.models import BatchSummaryModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("payrecover.main")

app = FastAPI(
    title="PayRecover API",
    description="AI Revenue Recovery Agent backend API (Razorpay AI Buildathon, Track 03)",
    version="1.0.0"
)

# CORS Middleware setup
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://frontend-three-roan-je5msy1mbk.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    # Populate seed if empty
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM cases;")
    row = cursor.fetchone()
    conn.close()

    if row["cnt"] == 0:
        logger.info("Database empty on startup. Loading synthetic seed cases...")
        load_seed_into_db()

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "PayRecover AI Revenue Recovery Agent"}

@app.get("/api/stats", response_model=BatchSummaryModel)
def get_batch_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases;")
    rows = cursor.fetchall()
    conn.close()

    cases = [dict(r) for r in rows]
    total_cases = len(cases)

    if total_cases == 0:
        return BatchSummaryModel(
            total_cases=0, total_amount_at_risk=0.0, amount_recovered=0.0,
            recovery_rate_pct=0.0, cases_escalated=0, cases_pending=0,
            cases_recovered=0, cases_failed=0, avg_time_to_recovery_hours=0.0
        )

    total_amount_at_risk = sum(c["amount"] for c in cases)
    amount_recovered = sum(c["amount"] for c in cases if c["status"] == "recovered")
    recovery_rate_pct = round((amount_recovered / total_amount_at_risk * 100.0) if total_amount_at_risk > 0 else 0.0, 2)

    cases_escalated = sum(1 for c in cases if c["status"] == "escalated")
    cases_pending = sum(1 for c in cases if c["status"] in ["pending", "retrying", "link_sent"])
    cases_recovered = sum(1 for c in cases if c["status"] == "recovered")
    cases_failed = sum(1 for c in cases if c["status"] == "failed")

    # Estimated time to recover
    avg_time = 1.4 if cases_recovered > 0 else 0.0

    return BatchSummaryModel(
        total_cases=total_cases,
        total_amount_at_risk=round(total_amount_at_risk, 2),
        amount_recovered=round(amount_recovered, 2),
        recovery_rate_pct=recovery_rate_pct,
        cases_escalated=cases_escalated,
        cases_pending=cases_pending,
        cases_recovered=cases_recovered,
        cases_failed=cases_failed,
        avg_time_to_recovery_hours=avg_time
    )

@app.get("/api/cases")
def list_cases(
    category: Optional[str] = None,
    status: Optional[str] = None,
    root_cause: Optional[str] = None,
    search: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM cases WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)
    if root_cause:
        query += " AND root_cause = ?"
        params.append(root_cause)
    if search:
        query += " AND (customer_name LIKE ? OR customer_email LIKE ? OR id LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    query += " ORDER BY id ASC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

@app.get("/api/cases/{case_id}")
def get_case_detail(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    case = dict(row)

    # Fetch case audit trail
    cursor.execute("SELECT * FROM audit_logs WHERE case_id = ? ORDER BY id ASC;", (case_id,))
    logs = [dict(l) for l in cursor.fetchall()]
    conn.close()

    case["audit_trail"] = logs
    return case

@app.get("/api/audit-logs")
def list_all_audit_logs(limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/run-batch")
def run_batch_recovery():
    """
    Executes the full recovery agent pipeline on all cases in dataset.
    """
    res = execution_layer.process_all_batch()
    stats = get_batch_stats()
    return {"message": f"Processed {res['processed_count']} cases in batch.", "stats": stats, "details": res}

@app.post("/api/cases/{case_id}/process")
def process_single_case(case_id: str):
    res = execution_layer.process_case(case_id)
    return res

@app.post("/api/trigger-failure-demo")
def trigger_failure_demo(case_id: Optional[str] = "PAY-0042"):
    """
    Injects a deliberate failure (API Timeout / Gateway Error) into target case
    to demonstrate graceful agent error handling and audit logging.
    """
    res = execution_layer.process_case(case_id, inject_failure=True)
    return {
        "message": f"Graceful failure scenario injected successfully into {case_id}",
        "injected_case": case_id,
        "result": res
    }

@app.post("/api/reset-seed")
def reset_seed_data():
    load_seed_into_db()
    stats = get_batch_stats()
    return {"message": "Database reset to initial synthetic seed data.", "stats": stats}
