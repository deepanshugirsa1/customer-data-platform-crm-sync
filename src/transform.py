from __future__ import annotations

import json
import re

from src.db import connect, init_schema


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    return digits or None


def _domain_from_email(email: str | None) -> str | None:
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].lower()


def stage_leads() -> int:
    con = connect()
    init_schema(con)
    rows = con.execute(
        """
        SELECT source, record_id, payload, updated_at
        FROM raw_crm_events
        WHERE object_name IN ('leads', 'contacts')
        """
    ).fetchall()
    con.execute("DELETE FROM staging_leads")
    count = 0
    for source, record_id, payload, updated_at in rows:
        data = json.loads(payload) if isinstance(payload, str) else payload
        email = (data.get("Email") or data.get("email") or "").lower() or None
        company = data.get("Company") or data.get("company")
        phone = _normalize_phone(data.get("Phone") or data.get("phone"))
        status = data.get("Status") or data.get("lifecycleStage")
        con.execute(
            """
            INSERT INTO staging_leads
            (source, record_id, email, company, phone, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [source, record_id, email, company, phone, status, updated_at],
        )
        count += 1
    return count


def domain_from_email(email: str | None) -> str | None:
    return _domain_from_email(email)
