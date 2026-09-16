# Customer Data Platform — CRM Sync & Enrichment Ingestion

Bidirectional **customer data platform** that ingests **lead, account, and enrichment**
data from CRMs and third-party APIs into a canonical store (ClickHouse locally via DuckDB),
with identity resolution, deduplication, freshness SLAs, and low-latency query APIs for AI workers.

> **Status: ~65% complete.** Core connectors, sync engine, identity resolution, enrichment,
> quality gates, and demo API run locally. Production Airbyte deployment, live ClickHouse cluster,
> and CRM write-back auth are planned.

## What works today vs. planned

| Area | Status | Notes |
|------|--------|-------|
| TypeScript connectors (Salesforce, HubSpot) | Done | Airbyte-style contracts, incremental cursors, JSONL export handoff |
| Ingestion → raw → staging → canonical | Done | DuckDB (ClickHouse-compatible) medallion layers |
| Identity resolution & dedup | Done | Bucketing on email/domain/phone into canonical accounts |
| Field-level reconciliation & confidence | Done | Most-recent-wins + source priority, config-driven weights |
| Enrichment from third-party catalog | Done | Domain/firmographic enrichment merged into canonical |
| Quality gates (completeness, freshness, dedupe) | Done | Run in `run_demo.py`, results persisted to `dq_results` |
| dbt-style curated models + tests | Done | Unique/not-null/range + source freshness SLA |
| Low-latency query API for AI workers | Done | FastAPI `src/api/query_api.py` |
| Tests + CI | Done | pytest suite + GitHub Actions pipeline/type-check |
| Live Salesforce/HubSpot OAuth | Planned | Currently mock connectors over sample extracts |
| Production Airbyte + ClickHouse cluster | Planned | DuckDB stands in locally |
| Bidirectional CRM write-back | Planned | Conflict resolution + idempotent upserts |
| AuthN/Z + PII tokenization on API | Planned | Query API is open in the demo |

## Stack

- **TypeScript** custom connectors (Salesforce, HubSpot)
- **Python** sync orchestration, identity resolution, enrichment
- **DuckDB** as local ClickHouse-compatible analytics store
- **Airbyte-style** connector contracts + sync catalog
- **dbt-style** SQL models for curated layers

## Quickstart

```bash
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
npm install
python data/generate_sample_crm.py
python run_demo.py
uvicorn src.api.query_api:app --reload --port 8080
```

## Architecture

```
Salesforce / HubSpot / Enrichment APIs
          │
   TypeScript connectors
          │
     Sync orchestrator (Python)
          │
   Raw → Staging → Canonical (DuckDB / ClickHouse)
          │
   Identity resolution + enrichment
          │
   Query API  ──►  AI workers
```
