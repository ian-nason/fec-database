# FEC Campaign Finance Database

A clean, queryable DuckDB database built from [FEC bulk data](https://www.fec.gov/data/browse-data/?tab=bulk-data) covering federal campaign finance filings across multiple election cycles.

The separately audited [18 October 2026 data release](https://huggingface.co/datasets/Nason/fec-database/tree/aee3ae8b28685104765fb1b1e3ebc2588cb907a3) is published: 356,327,912 rows in ten data tables, four views and 237 dictionary entries. Its [provenance](https://huggingface.co/datasets/Nason/fec-database/blob/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/sources-2026-10-18.json) and [release dictionary](https://huggingface.co/datasets/Nason/fec-database/blob/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/DICTIONARY.md) describe that frozen artifact. Merging loader changes does not rebuild or replace it.

[Quick start](#quick-start) · [Tables](#tables) · [Keys](#key-columns) · [Views](#pre-built-views) · [Interpretation](#interpret-contribution-totals) · [Build](#build-from-source)

## Quick Start

This frozen file is 21,140,877,312 bytes (19.69 GiB). Query it over HTTP without downloading the whole file first. Start with candidate records; contribution-ranking views can scan hundreds of millions of transactions even with a final `LIMIT`.

```sql
SET memory_limit='128MiB'; SET threads=1; SET max_temp_directory_size='0B';
INSTALL httpfs; LOAD httpfs;
ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/fec.duckdb' AS fec (READ_ONLY);
SELECT CAND_ID, CAND_NAME, CAND_OFFICE, CAND_OFFICE_ST
FROM fec.candidates WHERE cycle=2026
ORDER BY CAND_ID LIMIT 5;
```

Install/upgrade Python with `python -m pip install --upgrade datapond` (the examples use 0.1.5), or install released R datapond from [CRAN](https://cran.r-project.org/package=datapond) with `install.packages("datapond")`. R 0.1.1 remains a separate development version.

Remote queries run on your machine. File size is disk storage, not required RAM; selected columns reduce transfer, but filters and a final `LIMIT` do not guarantee a small scan. A 128 MiB setting limits DuckDB's buffer pool, not the whole Python/R process. Larger queries can fail with spill disabled. Download only when you have room for the file, temporary download bytes and any existing copy. The SQL quick start above sets limits before attachment; the package examples below set them immediately after connecting.

```python
import datapond
con = datapond.connect("fec")
con.execute("SET memory_limit='128MiB'; SET threads=1; SET max_temp_directory_size='0B'")
con.sql("SELECT CAND_ID, CAND_NAME FROM candidates WHERE cycle=2026 ORDER BY CAND_ID LIMIT 5").show()
con.close()
```

```r
con <- datapond::dp_connect("fec")
DBI::dbExecute(con, "SET memory_limit='128MiB'; SET threads=1; SET max_temp_directory_size='0B'")
DBI::dbGetQuery(con, "SELECT CAND_ID, CAND_NAME FROM candidates WHERE cycle=2026 ORDER BY CAND_ID LIMIT 5")
datapond::dp_disconnect(con)
```

See [`examples/query_examples.sql`](examples/query_examples.sql) for larger analyses. Review the view definitions and resource needs before running them.

## Tables

| Table | Description |
|-------|-------------|
| `candidates` | Candidate master: name, party, office, state, district, status |
| `committees` | Committee master: name, type, party, treasurer, connected org |
| `candidate_committee_links` | Which committees are authorized by which candidates |
| `individual_contributions` | Reported individual-contribution transactions: name, employer, occupation, amount, date |
| `committee_contributions` | PAC/party contributions to candidates |
| `committee_to_committee` | Transfers between committees |
| `operating_expenditures` | Committee operating expenditures: payee, purpose, amount |
| `independent_expenditures` | Independent expenditures for/against candidates |
| `electioneering_communications` | Broadcast ads mentioning candidates near elections |
| `communication_costs` | Internal communications supporting/opposing candidates |

Every row has a `cycle` column (election year: 2004, 2006, ..., 2026).


The [FEC individual-contributions file](https://www.fec.gov/campaign-finance-data/contributions-individuals-file-description/) is a subset of reported itemized contributions under inclusion rules that changed over time. A transaction row is not a distinct donor or a complete census of donations. Candidate and committee tables instead describe entities within a cycle.

## Key Columns

| Column | Tables | Description |
|--------|--------|-------------|
| `CAND_ID` | candidates, committee_contributions | FEC candidate ID (e.g., P80001571) |
| `CMTE_ID` | committees, individual_contributions, etc. | FEC committee ID (e.g., C00703975) |
| `CAND_PCC` | candidates | Principal campaign committee ID (joins to CMTE_ID) |
| `TRANSACTION_AMT` | individual/committee contributions | Dollar amount (DOUBLE) |
| `TRANSACTION_DT` | individual/committee contributions | Transaction date (DATE) |
| `cycle` | all tables | Election cycle year (INTEGER) |


Column names vary: `electioneering_communications` uses `CANDIDATE_ID` and `COMMITTEE_ID`; `independent_expenditures` uses `cand_id` and `spe_id`. Consult each table's dictionary. Use `cycle` together with candidate/committee IDs when joining across these tables. Child transaction tables contain many rows per entity; check the intended unit and aggregate before combining them. Names are not reliable person identifiers.

## Pre-built Views

The views answer different questions. `v_candidate_totals` and `v_top_donors` net the listed refund types; `v_daily_donations` excludes refunds and reports positive non-refund transactions. `v_pac_to_candidate` selects direct 24K/24Z contributions. None is a substitute for the source filing totals.

| View | Description |
|------|-------------|
| `v_candidate_totals` | Net individual receipts per principal campaign committee; candidates sharing a committee (e.g. Biden/Harris 2024) are aggregated into one row, never fanned out |
| `v_top_donors` | Net donor activity by raw (name, employer, occupation, state) string — beware spelling variants |
| `v_pac_to_candidate` | Direct PAC-to-candidate money only (24K contributions + 24Z in-kind). Independent expenditures are excluded: 24A is spending *against* a candidate |
| `v_daily_donations` | Positive non-refund individual transactions by date and cycle; not net daily cash flow |

**Table caveats:** `independent_expenditures` retains only the latest
amendment of each filing (superseded versions are dropped at build time) but
still contains upstream prank filings — sanity-check big numbers against
fec.gov. `electioneering_communications` (1,711 rows in the October 2026 release) and
`communication_costs` are thin, and all three standalone tables exist from
2010 onward only (FEC does not publish per-cycle CSVs before 2010).

## Interpret contribution totals

A raw `SUM(TRANSACTION_AMT)` can double-count flows or confuse receipts with refunds. The two net-individual views apply the first three rules below. The historical numerical examples are retained from earlier audits; they were not recomputed for the October 18 snapshot:

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

Other issues noted in those earlier audits: `candidates` master files churn across FEC snapshots, so
1-5% of recent-cycle `committee_contributions.CAND_ID` values have no
same-cycle candidate row (inner joins drop them); a handful of rows carry
wild dates (years 0677-9206) — clamp to the cycle window before
bucketing by date.

## Data Source

[Federal Election Commission](https://www.fec.gov/data/browse-data/?tab=bulk-data). Bulk data files are public domain and updated weekly (Sunday nights).


This artifact is frozen to the October 18, 2026 source manifest, not a live feed. Source files can change after that cutoff; consult the linked provenance for their individual identities. No automatic refresh is promised.

## Build from Source

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Build full database (cycles 2004-2026, ~40 GB download)
uv run python build_database.py

# Build specific cycles
uv run python build_database.py --start-cycle 2020 --end-cycle 2026

# Build specific tables only
uv run python build_database.py --tables candidates committees individual_contributions

# After separate audit approval, publish using existing Hugging Face authentication
uv run python publish_to_hf.py
```

The build downloads FEC bulk ZIP files and header definitions. Bulk fields are typed during insertion; standalone CSV fields are cast afterwards. It then creates analysis views and validates the candidate. A successful build alone does not authorize publication.

## Building with bounded resources

Use a fresh output path. The builder refuses to overwrite an existing database, WAL, or build manifest.

```bash
DATAPOND_MEMORY_LIMIT=512MiB DATAPOND_THREADS=1 DATAPOND_MAX_TEMP_SIZE=1GiB \
  uv run python build_database.py --output build-candidate/fec.duckdb --data-dir build-candidate/raw
```

Bulk ZIP members stream into batches of at most 100,000 records or 32 MiB, with a 512 KiB logical-record limit. Dates and amounts are typed during insertion, avoiding a second full-table rewrite. DuckDB's default buffer pool is 512 MiB, one thread, with at most 1 GiB of local spill; total process RAM can exceed the buffer-pool limit, so leave desktop headroom and monitor disk/RAM during a full build. The builder requires DuckDB 1.4.4 or later.

Strict parsing preserves literal quotes that the former automatic CSV dialect could truncate. Recovery of malformed individual-contribution quotes requires every affected physical line to have all 21 fields, a committee ID and the required 19-digit record ID. Ambiguous framing stops the build. Invalid UTF-8 records are excluded only with exact bytes, hashes and physical line numbers saved in an adjacent `.invalid-utf8.jsonl` file; characters are never replaced silently.

The strict parsing, quote recovery and exact-byte quarantine safeguards above apply to bulk ZIP members. Standalone CSV tables still use the existing permissive CSV reader and later type casting.

Each completed bulk source writes a `.load.json` receipt with its SHA256, CRC, row/line accounting, conversion counts and repairs. A failed source leaves its archive, partial candidate and diagnostic batch intact. The overall `.manifest.json` stays `incomplete` on failure. Inspect those files before any manual recovery; do not publish an incomplete candidate or retry a partial cycle in place. Publication additionally requires a separate full data audit and review of historical differences. A successful builder run alone does not authorize publication.

For a new full build, use a fresh `--data-dir` as well as a fresh output path. Existing source receipts, quarantine files, diagnostic batches and partial downloads are refused before source acquisition. Every bulk source gets a streaming parse/CRC preflight before its first INSERT; unresolved multiline framing therefore stops before that cycle has any committed rows. Earlier completed cycles remain in the incomplete candidate for manual investigation; automatic recovery is intentionally unsupported.

The final view validation can require more working memory or spill than loading. Review available RAM/disk and, if needed, set the documented environment limits explicitly before a full production build; the builder never increases them automatically. A resource failure leaves the candidate local and unpublishable. Default limits are conservative, not a guarantee that every complete historical audit fits. The maintenance rebuild uses its own externally guarded audit workflow. Quarantine is capped at 16 MiB per source, with the exact quarantine filename recorded in that source's receipt.

Use a fresh output directory to preserve existing documentation: the existing final export step writes DICTIONARY.md in the output directory. The refusal guarantee above applies to the database, WAL, manifest and source recovery evidence. Quarantine's encoded JSON byte cap is also checked during preflight, before any row is inserted.

## License

Build code: MIT. Underlying data: public domain (U.S. government records).

The reviewed current hosted card is retained in [HF-README.md](HF-README.md). For a future release, update counts and version links, retain the guidance and caveats, and inspect the rendered card before upload.

The release dictionary retains its prepublication “candidate” heading and historical audit terminology; it describes the published hash above. Its ID join hints are shorthand: include `cycle` and check child-table multiplicity as described here.
