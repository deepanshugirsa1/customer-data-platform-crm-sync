from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.db import connect, init_schema

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def ingest_raw(source: str, object_name: str) -> int:
    con = connect()
    init_schema(con)
    path = RAW_DIR / f"{source}_{object_name}.jsonl"
    records = load_jsonl(path)
    for rec in records:
        con.execute(
            """
            INSERT INTO raw_crm_events (source, object_name, record_id, payload, updated_at)
            VALUES (?, ?, ?, ?::JSON, ?)
            """,
            [
                rec.get("source", source),
                rec.get("object", object_name),
                rec["id"],
                json.dumps(rec.get("payload", {})),
                rec.get("updatedAt", datetime.now(timezone.utc).isoformat()),
            ],
        )
    state_path = RAW_DIR / f"{source}_{object_name}.state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        con.execute(
            """
            INSERT OR REPLACE INTO sync_state (source, object_name, cursor, last_synced_at)
            VALUES (?, ?, ?, current_timestamp)
            """,
            [state["source"], state["object"], state.get("cursor")],
        )
    return len(records)
