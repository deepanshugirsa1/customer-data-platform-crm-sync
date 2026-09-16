-- dbt-style curated model (run via DuckDB in demo)
SELECT
  account_id,
  email,
  company,
  domain,
  phone,
  sources,
  confidence,
  enriched,
  updated_at
FROM canonical_accounts
WHERE confidence >= 0.7
