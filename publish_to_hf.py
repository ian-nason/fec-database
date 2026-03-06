#!/usr/bin/env python3
"""Upload fec.duckdb to Hugging Face for remote access.

Usage:
    uv run python publish_to_hf.py
    uv run python publish_to_hf.py --db fec.duckdb --repo Nason/fec-database
    HF_TOKEN=hf_xxx uv run python publish_to_hf.py
"""

import argparse
import sys
from pathlib import Path

import duckdb
from huggingface_hub import HfApi, create_repo


def generate_dataset_card(db_path: str) -> str:
    """Generate a HF-compatible README with YAML frontmatter."""
    con = duckdb.connect(db_path, read_only=True)
    rows = con.sql(
        "SELECT table_name, description, row_count, column_count, cycles_covered "
        "FROM _metadata ORDER BY row_count DESC"
    ).fetchall()
    con.close()

    table_rows = "\n".join(
        f"| `{r[0]}` | {r[1]} | {r[2]:,} | {r[3]} | {r[4]} |"
        for r in rows
    )
    total_rows = sum(r[2] for r in rows)
    n_tables = len(rows)

    return f"""---
license: mit
task_categories:
  - tabular-classification
  - tabular-regression
tags:
  - campaign-finance
  - fec
  - elections
  - political-donations
  - pac
  - lobbying
  - duckdb
  - government-data
  - politics
  - united-states
pretty_name: FEC Campaign Finance Database
size_categories:
  - 100M<n<1B
---

# FEC Campaign Finance Database

A clean, queryable DuckDB database built from [FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data) covering federal campaign finance filings.

**{total_rows:,} rows** across **{n_tables} tables** covering candidates, committees, individual contributions, PAC spending, and more.

Built with [fec-database](https://github.com/ian-nason/fec-database).

## Quick Start

### DuckDB CLI

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

### Python

```python
import duckdb
con = duckdb.connect()
con.sql("INSTALL httpfs; LOAD httpfs;")
con.sql(\\\"\\\"\\\"
    ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/main/fec.duckdb'
    AS fec (READ_ONLY)
\\\"\\\"\\\")
con.sql("SELECT * FROM fec._metadata").show()
```

DuckDB uses HTTP range requests, so only the pages needed for your query are downloaded.

## Tables

| Table | Description | Rows | Cols | Cycles |
|-------|-------------|------|------|--------|
{table_rows}

## Pre-built Views

| View | Description |
|------|-------------|
| `v_candidate_totals` | Candidate fundraising totals from individual contributions |
| `v_top_donors` | Aggregated donor activity across all cycles |
| `v_pac_to_candidate` | PAC-to-candidate contributions with org names |
| `v_daily_donations` | Daily donation volume and amounts |

## Data Source

[Federal Election Commission](https://www.fec.gov/data/browse-data/?tab=bulk-data). Bulk data files are public domain and updated weekly.

## License

Database build code: MIT. Underlying data: public domain (U.S. government records).

## GitHub

Full source code, build instructions, and example queries: [github.com/ian-nason/fec-database](https://github.com/ian-nason/fec-database)
"""


def main():
    parser = argparse.ArgumentParser(
        description="Upload fec.duckdb to Hugging Face"
    )
    parser.add_argument("--db", type=Path, default=Path("fec.duckdb"))
    parser.add_argument("--repo", default="Nason/fec-database")
    parser.add_argument("--token", help="HF token (or set HF_TOKEN env var)")
    args = parser.parse_args()

    if not args.db.exists():
        print(f"Error: Database not found at {args.db}")
        sys.exit(1)

    api = HfApi(token=args.token)

    print(f"Creating dataset repo: {args.repo}")
    create_repo(args.repo, repo_type="dataset", exist_ok=True, token=args.token)

    print(f"Generating dataset card from {args.db}")
    card = generate_dataset_card(str(args.db))

    print("Uploading dataset card...")
    api.upload_file(
        path_or_fileobj=card.encode(),
        path_in_repo="README.md",
        repo_id=args.repo,
        repo_type="dataset",
    )

    size_gb = args.db.stat().st_size / (1024**3)
    print(f"Uploading {args.db} ({size_gb:.1f} GB)...")
    api.upload_file(
        path_or_fileobj=str(args.db),
        path_in_repo="fec.duckdb",
        repo_id=args.repo,
        repo_type="dataset",
    )

    print(f"\nUploaded to https://huggingface.co/datasets/{args.repo}")
    print(
        f"\nUsers can now query remotely:\n"
        f"  ATTACH 'https://huggingface.co/datasets/{args.repo}/resolve/main/fec.duckdb'"
        f" AS fec (READ_ONLY);"
    )


if __name__ == "__main__":
    main()
