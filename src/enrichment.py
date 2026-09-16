from __future__ import annotations

import json

from src.db import connect, init_schema

# Stub enrichment catalog — replace with Clearbit/ZoomInfo HTTP in production.
ENRICHMENT = {
    "acme.io": {"industry": "SaaS", "employees": 120, "funding": "Series B"},
    "globex.com": {"industry": "Manufacturing", "employees": 5000, "funding": "Public"},
    "initech.com": {"industry": "Enterprise Software", "employees": 800, "funding": "Series C"},
}


def enrich_accounts() -> int:
    con = connect()
    init_schema(con)
    rows = con.execute(
        "SELECT account_id, domain FROM canonical_accounts"
    ).fetchall()
    updated = 0
    for account_id, domain in rows:
        payload = ENRICHMENT.get((domain or "").lower(), {"industry": "Unknown"})
        con.execute(
            "UPDATE canonical_accounts SET enriched = ?::JSON WHERE account_id = ?",
            [json.dumps(payload), account_id],
        )
        updated += 1
    return updated
