from __future__ import annotations

from pathlib import Path

import duckdb

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "processed" / "cdp.duckdb"


def connect(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    path = db_path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_crm_events (
            source VARCHAR,
            object_name VARCHAR,
            record_id VARCHAR,
            payload JSON,
            updated_at TIMESTAMP,
            ingested_at TIMESTAMP DEFAULT current_timestamp
        );
        CREATE TABLE IF NOT EXISTS staging_leads (
            source VARCHAR,
            record_id VARCHAR,
            email VARCHAR,
            company VARCHAR,
            phone VARCHAR,
            status VARCHAR,
            updated_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS canonical_accounts (
            account_id VARCHAR PRIMARY KEY,
            email VARCHAR,
            company VARCHAR,
            domain VARCHAR,
            phone VARCHAR,
            sources VARCHAR[],
            confidence DOUBLE,
            enriched JSON,
            updated_at TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sync_state (
            source VARCHAR,
            object_name VARCHAR,
            cursor VARCHAR,
            last_synced_at TIMESTAMP,
            PRIMARY KEY (source, object_name)
        );
        CREATE TABLE IF NOT EXISTS dq_results (
            check_name VARCHAR,
            passed BOOLEAN,
            details VARCHAR,
            checked_at TIMESTAMP DEFAULT current_timestamp
        );
        """
    )
