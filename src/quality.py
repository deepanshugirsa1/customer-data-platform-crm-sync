from __future__ import annotations

from src.db import connect, init_schema


def run_quality_checks(freshness_minutes: int = 5, completeness_pct: float = 98.0) -> list[dict]:
    con = connect()
    init_schema(con)
    results = []

    total = con.execute("SELECT COUNT(*) FROM staging_leads").fetchone()[0]
    with_email = con.execute(
        "SELECT COUNT(*) FROM staging_leads WHERE email IS NOT NULL AND email <> ''"
    ).fetchone()[0]
    completeness = 100.0 if total == 0 else (with_email / total) * 100
    passed_completeness = completeness >= completeness_pct
    results.append(
        {
            "check_name": "email_completeness",
            "passed": passed_completeness,
            "details": f"{completeness:.1f}% emails present (n={total})",
        }
    )

    stale = con.execute(
        f"""
        SELECT COUNT(*) FROM sync_state
        WHERE last_synced_at < current_timestamp - INTERVAL '{freshness_minutes}' MINUTE
        """
    ).fetchone()[0]
    results.append(
        {
            "check_name": "freshness_sla",
            "passed": stale == 0,
            "details": f"{stale} sources past {freshness_minutes}m SLA",
        }
    )

    dupes = con.execute(
        """
        SELECT COUNT(*) FROM (
          SELECT email, COUNT(*) c FROM canonical_accounts
          WHERE email IS NOT NULL GROUP BY email HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]
    results.append(
        {
            "check_name": "no_duplicate_emails",
            "passed": dupes == 0,
            "details": f"{dupes} duplicate emails in canonical",
        }
    )

    con.execute("DELETE FROM dq_results")
    for r in results:
        con.execute(
            "INSERT INTO dq_results (check_name, passed, details) VALUES (?, ?, ?)",
            [r["check_name"], r["passed"], r["details"]],
        )
    return results
