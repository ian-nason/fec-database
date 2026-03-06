# FEC Campaign Finance Database

A clean, queryable DuckDB database built from [FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data) covering federal campaign finance filings across multiple election cycles.

## Tables

| Table | Description |
|-------|-------------|
| `candidates` | Candidate master: name, party, office, state, district, status |
| `committees` | Committee master: name, type, party, treasurer, connected org |
| `candidate_committee_links` | Which committees are authorized by which candidates |
| `individual_contributions` | Every individual donation: name, employer, occupation, amount, date |
| `committee_contributions` | PAC/party contributions to candidates |
| `committee_to_committee` | Transfers between committees |
| `operating_expenditures` | Committee operating expenditures: payee, purpose, amount |
| `independent_expenditures` | Independent expenditures for/against candidates |
| `electioneering_communications` | Broadcast ads mentioning candidates near elections |
| `communication_costs` | Internal communications supporting/opposing candidates |

Every row has a `cycle` column (election year: 2004, 2006, ..., 2026).

## Quick Start (Remote Query)

No download needed. DuckDB uses HTTP range requests to fetch only the pages your query touches.

```sql
INSTALL httpfs;
LOAD httpfs;
ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/main/fec.duckdb' AS fec (READ_ONLY);

-- Top presidential candidates by individual donations (2024 cycle)
SELECT c.CAND_NAME, c.CAND_PTY_AFFILIATION AS party,
    SUM(i.TRANSACTION_AMT) AS total, COUNT(*) AS donations
FROM fec.individual_contributions i
JOIN fec.candidates c ON i.CMTE_ID = c.CAND_PCC AND i.cycle = c.cycle
WHERE i.cycle = 2024 AND c.CAND_OFFICE = 'P' AND i.TRANSACTION_AMT > 0
GROUP BY 1, 2 ORDER BY total DESC LIMIT 10;
```

See [`examples/query_examples.sql`](examples/query_examples.sql) for more.

## Build from Source

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Build full database (cycles 2004-2026, ~40 GB download)
uv run python build_database.py

# Build specific cycles
uv run python build_database.py --start-cycle 2020 --end-cycle 2026

# Build specific tables only
uv run python build_database.py --tables candidates committees individual_contributions

# Upload to Hugging Face
uv run python publish_to_hf.py --token hf_YOUR_TOKEN
```

The build downloads FEC bulk zip files and header definitions, loads pipe-delimited data into DuckDB, casts dates (MMDDYYYY -> DATE) and amounts (VARCHAR -> DOUBLE), then creates pre-built analysis views.

## Pre-built Views

| View | Description |
|------|-------------|
| `v_candidate_totals` | Candidate fundraising totals from individual contributions |
| `v_top_donors` | Aggregated donor activity across all cycles |
| `v_pac_to_candidate` | PAC-to-candidate contributions with org names |
| `v_daily_donations` | Daily donation volume and amounts |

## Key Columns

| Column | Tables | Description |
|--------|--------|-------------|
| `CAND_ID` | candidates, committee_contributions | FEC candidate ID (e.g., P80001571) |
| `CMTE_ID` | committees, individual_contributions, etc. | FEC committee ID (e.g., C00703975) |
| `CAND_PCC` | candidates | Principal campaign committee ID (joins to CMTE_ID) |
| `TRANSACTION_AMT` | individual/committee contributions | Dollar amount (DOUBLE) |
| `TRANSACTION_DT` | individual/committee contributions | Transaction date (DATE) |
| `cycle` | all tables | Election cycle year (INTEGER) |

## Data Source

[Federal Election Commission](https://www.fec.gov/data/browse-data/?tab=bulk-data). Bulk data files are public domain and updated weekly (Sunday nights).

## License

Build code: MIT. Underlying data: public domain (U.S. government records).
