# Customer Data Platform — CRM Sync & Enrichment Ingestion

Bidirectional **customer data platform** that ingests **lead, account, and enrichment**
data from CRMs and third-party APIs into a canonical store (ClickHouse locally via DuckDB),
with identity resolution, deduplication, freshness SLAs, and low-latency query APIs for AI workers.

> **Status: ~65% complete.** Core connectors, sync engine, identity resolution, enrichment,
> quality gates, and demo API run locally. Production Airbyte deployment, live ClickHouse cluster,
> and CRM write-back auth are planned.

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
