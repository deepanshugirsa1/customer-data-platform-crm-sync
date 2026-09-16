from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
RAW.mkdir(parents=True, exist_ok=True)
now = datetime.now(timezone.utc).isoformat()

sf = [
    {
        "id": "sf-leads-001",
        "object": "leads",
        "source": "salesforce",
        "payload": {
            "Email": "alex@acme.io",
            "Company": "Acme",
            "Phone": "+1-415-555-0100",
            "Status": "Open",
        },
        "updatedAt": now,
    },
    {
        "id": "sf-leads-002",
        "object": "leads",
        "source": "salesforce",
        "payload": {
            "Email": "jordan@globex.com",
            "Company": "Globex",
            "Phone": "+1-628-555-0199",
            "Status": "Working",
        },
        "updatedAt": now,
    },
]
hs = [
    {
        "id": "hs-contacts-001",
        "object": "contacts",
        "source": "hubspot",
        "payload": {
            "email": "alex@acme.io",
            "company": "Acme Inc",
            "phone": "4155550100",
            "lifecycleStage": "lead",
        },
        "updatedAt": now,
    },
    {
        "id": "hs-contacts-002",
        "object": "contacts",
        "source": "hubspot",
        "payload": {
            "email": "sam@initech.com",
            "company": "Initech",
            "phone": "5105550144",
            "lifecycleStage": "opportunity",
        },
        "updatedAt": now,
    },
]

def dump(name: str, rows: list[dict]) -> None:
    path = RAW / f"{name}.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    state = {
        "source": rows[0]["source"],
        "object": rows[0]["object"],
        "cursor": now,
    }
    (RAW / f"{name}.state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"wrote {path}")

dump("salesforce_leads", sf)
dump("hubspot_contacts", hs)
