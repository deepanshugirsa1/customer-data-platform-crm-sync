-- Production ClickHouse DDL (local demo uses DuckDB equivalents)
CREATE TABLE IF NOT EXISTS raw_crm_events (
    source String,
    object_name String,
    record_id String,
    payload String,
    updated_at DateTime64(3),
    ingested_at DateTime64(3) DEFAULT now64()
) ENGINE = MergeTree
ORDER BY (source, object_name, updated_at);

CREATE TABLE IF NOT EXISTS canonical_accounts (
    account_id String,
    email String,
    company String,
    domain String,
    phone String,
    sources Array(String),
    confidence Float64,
    enriched String,
    updated_at DateTime64(3)
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY account_id;
