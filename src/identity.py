from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from src.db import connect, init_schema
from src.reconcile import FieldObservation, load_rule_weights, reconcile_account
from src.transform import domain_from_email


def _account_id(email: str | None, company: str | None) -> str:
    key = (email or company or "unknown").lower()
    return "acc_" + hashlib.sha1(key.encode()).hexdigest()[:12]


def resolve_identities() -> int:
    con = connect()
    init_schema(con)
    rows = con.execute(
        "SELECT source, record_id, email, company, phone, updated_at FROM staging_leads"
    ).fetchall()

    buckets: dict[str, list] = defaultdict(list)
    for row in rows:
        source, record_id, email, company, phone, updated_at = row
        key = (email or "").lower() or (company or "").lower() or record_id
        buckets[key].append(row)

    con.execute("DELETE FROM canonical_accounts")
    weights = load_rule_weights()
    merged = 0
    for key, members in buckets.items():
        # Build per-field observations so reconciliation can pick winners.
        def _obs(idx: int) -> list[FieldObservation]:
            return [
                FieldObservation(source=m[0], value=m[idx], updated_at=str(m[5]))
                for m in members
            ]

        emails = [m[2] for m in members if m[2]]
        sources = sorted({m[0] for m in members})
        # Determine which identity signals fired for this bucket.
        match_signals: list[str] = []
        if emails:
            match_signals.append("exact_email")
        if any(m[3] for m in members):
            match_signals.append("domain_company")
        if any(m[4] for m in members):
            match_signals.append("phone")

        result = reconcile_account(
            {"email": _obs(2), "company": _obs(3), "phone": _obs(4)},
            match_signals=match_signals,
            weights=weights,
        )
        email = result.values["email"]
        company = result.values["company"]
        phone = result.values["phone"]
        confidence = result.confidence
        acc_id = _account_id(email, company)
        con.execute(
            """
            INSERT INTO canonical_accounts
            (account_id, email, company, domain, phone, sources, confidence, enriched, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?::JSON, current_timestamp)
            """,
            [
                acc_id,
                email,
                company,
                domain_from_email(email),
                phone,
                sources,
                confidence,
                json.dumps({}),
            ],
        )
        merged += 1
    return merged
