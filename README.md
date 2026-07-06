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

-- Top presidential campaign committees by net individual donations (2024)
SELECT candidate_names, party, net_individual, num_contributions
FROM fec.v_candidate_totals v
JOIN fec.candidates c ON v.CMTE_ID = c.CAND_PCC AND v.cycle = c.cycle
WHERE v.cycle = 2024 AND c.CAND_OFFICE = 'P'
GROUP BY ALL ORDER BY net_individual DESC LIMIT 10;
```

See [`examples/query_examples.sql`](examples/query_examples.sql) for more.

## How to sum money correctly

Naive `SUM(TRANSACTION_AMT)` over `individual_contributions` overstates
totals substantially. Four rules, all encoded in the pre-built views:

1. **Exclude conduit rows: `TRANSACTION_TP <> '24T'`.** ActBlue and WinRed
   report each earmarked donation as a 24T row, and the recipient committee
   reports the same dollars again (typically 15E). Summing both double
   counts **14-22% of every cycle since 2018** ($4.0B of the $17.9B 2020
   total). `MEMO_CD` does *not* flag these — the 24T rows have NULL memo.
2. **Net out refunds.** 20Y/21Y/22Y rows are refunds *stored as positive
   amounts* (+$1.1B of 22Y alone); `TRANSACTION_AMT > 0` does not exclude
   them. Subtract them instead.
3. **Exclude memo-only rows: `MEMO_CD = 'X'`.**
4. **Treat amounts above ~$5M as suspect.** A few dozen column-shifted rows
   (junk MEMO_CD values, NULL dates) own the top of any naive top-N query,
   and prank filings exist upstream (a $10B "COMMITTEE 300" independent
   expenditure). Candidate self-funding (15C) also sits inside
   individual_contributions.

Other traps: `candidates` master files churn across FEC snapshots, so
1-5% of recent-cycle `committee_contributions.CAND_ID` values have no
same-cycle candidate row (inner joins drop them); a handful of rows carry
wild dates (years 0677-9206) — clamp to the cycle window before
bucketing by date.

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

All views apply the money-summing rules above (24T exclusion, refund
netting, memo exclusion).

| View | Description |
|------|-------------|
| `v_candidate_totals` | Net individual receipts per principal campaign committee; candidates sharing a committee (e.g. Biden/Harris 2024) are aggregated into one row, never fanned out |
| `v_top_donors` | Net donor activity by raw (name, employer, occupation, state) string — beware spelling variants |
| `v_pac_to_candidate` | Direct PAC-to-candidate money only (24K contributions + 24Z in-kind). Independent expenditures are excluded: 24A is spending *against* a candidate |
| `v_daily_donations` | Daily donation volume and amounts |

**Table caveats:** `independent_expenditures` retains only the latest
amendment of each filing (superseded versions are dropped at build time) but
still contains upstream prank filings — sanity-check big numbers against
fec.gov. `electioneering_communications` (1,577 rows) and
`communication_costs` are thin, and all three standalone tables exist from
2010 onward only (FEC does not publish per-cycle CSVs before 2010).

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
