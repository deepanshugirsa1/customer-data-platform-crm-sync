from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "data" / "generate_sample_crm.py")])
    sys.path.insert(0, str(ROOT))
    from src.enrichment import enrich_accounts
    from src.identity import resolve_identities
    from src.ingest import ingest_raw
    from src.quality import run_quality_checks
    from src.transform import stage_leads

    n1 = ingest_raw("salesforce", "leads")
    n2 = ingest_raw("hubspot", "contacts")
    staged = stage_leads()
    merged = resolve_identities()
    enriched = enrich_accounts()
    dq = run_quality_checks()
    print(f"ingested={n1 + n2} staged={staged} canonical={merged} enriched={enriched}")
    for check in dq:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['check_name']}: {check['details']}")
    print("Demo complete. Start API: uvicorn src.api.query_api:app --port 8080")


if __name__ == "__main__":
    main()
