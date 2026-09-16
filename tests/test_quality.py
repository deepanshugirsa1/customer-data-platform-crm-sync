from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import connect, init_schema


def test_schema_init():
    con = connect(ROOT / "data" / "processed" / "test_cdp.duckdb")
    init_schema(con)
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    assert "canonical_accounts" in tables
