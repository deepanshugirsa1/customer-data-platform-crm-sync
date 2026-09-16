from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from src.db import connect, init_schema
from src.quality import run_quality_checks

app = FastAPI(title="CDP Query API", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    init_schema(connect())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/accounts")
def list_accounts(limit: int = Query(50, ge=1, le=500)):
    con = connect()
    rows = con.execute(
        """
        SELECT account_id, email, company, domain, phone, sources, confidence, enriched, updated_at
        FROM canonical_accounts
        ORDER BY confidence DESC
        LIMIT ?
        """,
        [limit],
    ).fetchall()
    cols = [
        "account_id",
        "email",
        "company",
        "domain",
        "phone",
        "sources",
        "confidence",
        "enriched",
        "updated_at",
    ]
    return [dict(zip(cols, r)) for r in rows]


@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    con = connect()
    row = con.execute(
        """
        SELECT account_id, email, company, domain, phone, sources, confidence, enriched, updated_at
        FROM canonical_accounts WHERE account_id = ?
        """,
        [account_id],
    ).fetchone()
    if not row:
        raise HTTPException(404, "account not found")
    cols = [
        "account_id",
        "email",
        "company",
        "domain",
        "phone",
        "sources",
        "confidence",
        "enriched",
        "updated_at",
    ]
    return dict(zip(cols, row))


@app.get("/dq")
def dq():
    return run_quality_checks()
