from __future__ import annotations

import hashlib
import json
from collections import defaultdict

import yaml
from pathlib import Path

from src.db import connect, init_schema
from src.transform import domain_from_email


def _account_id(email: str | None, company: str | None) -> str:
    key = (email or company or "unknown").lower()
    return "acc_" + hashlib.sha1(key.encode()).hexdigest()[:12]


def resolve_identities() -> int:
    config = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "configs" / "identity.yaml").read_text(
            encoding="utf-8"
        )
    )
    con = connect()
    init_schema(con)
    rows = con.execute(
        "SELECT source, record_id, email, company, phone, updated_at FROM staging_leads"
    ).fetchall()

    buckets: dict[str, list] = defaultdict(list)
    for row in rows:
        source, record_id, email, company, phone, updated_at = row
        key = (email or "").lower() or (company or "").lower() or record_id
        buckets[key].add if False else buckets[key].append(row)

    con.execute("DELETE FROM canonical_accounts")
    merged = 0
    for key, members in buckets.items():
        emails = [m[2] for m in members if m[2]]
        companies = [m[3] for m in members if m[3]]
        phones = [m[4] for m in members if m[4]]
        sources = sorted({m[0] for m in members})
        email = emails[0] if emails else None
        company = companies[0] if companies else None
        phone = phones[0] if phones else None
        confidence = min(1.0, 0.55 + 0.15 * len(sources) + (0.2 if email else 0))
        # weight hint from config (kept simple for demo)
        _ = config.get("rules", [])
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
