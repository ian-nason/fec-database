# FEC Campaign Finance Database

**360,160,461 rows**, ten source tables, four views and 237 dictionary entries. Cycles 2004–2026; 111 available source/cycle outcomes and nine expected pre-2010 standalone absences. Seven official header files are recorded separately.

| Table | Rows |
|---|---:|
| `candidate_committee_links` | 74,806 |
| `candidates` | 77,688 |
| `committee_contributions` | 5,334,103 |
| `committee_to_committee` | 48,292,895 |
| `committees` | 185,838 |
| `communication_costs` | 25,768 |
| `electioneering_communications` | 1,725 |
| `independent_expenditures` | 635,427 |
| `individual_contributions` | 285,673,429 |
| `operating_expenditures` | 19,858,782 |

## Quick start

```sql
INSTALL httpfs; LOAD httpfs;
SET memory_limit='128MiB'; SET threads=1; SET max_temp_directory_size='0B';
ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/main/fec.duckdb' AS fec (READ_ONLY);
SELECT CAND_ID,CAND_NAME FROM fec.candidates WHERE cycle=2026 AND CAND_OFFICE='H' ORDER BY CAND_ID LIMIT 5;
```

### R with DBI and duckdb

Install the dependencies once with `install.packages(c("DBI", "duckdb"))`.

```r
library(DBI)
con <- dbConnect(duckdb::duckdb(config = list(memory_limit = "128MiB", threads = "1", max_temp_directory_size = "0B")))
dbExecute(con, "INSTALL httpfs")
dbExecute(con, "LOAD httpfs")
dbExecute(con, "ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/main/fec.duckdb' AS fec (READ_ONLY)")
dbGetQuery(con, "SELECT CAND_ID, CAND_NAME FROM fec.candidates WHERE cycle = 2026 AND CAND_OFFICE = 'H' ORDER BY CAND_ID LIMIT 5")
dbDisconnect(con, shutdown = TRUE)
```

DuckDB uses HTTP range requests; queries run on your machine and may need substantial memory or download data. A `LIMIT` does not guarantee a small scan.


Install/upgrade Python with `python -m pip install --upgrade datapond` (the examples use 0.1.5), or install released R datapond from [CRAN](https://cran.r-project.org/package=datapond) with `install.packages("datapond")`. R 0.1.1 remains a separate development version. The catalog ID is `fec`.

## Snapshot and verification

This is a source-identified snapshot, not a live feed. The current-main URLs above follow the latest publication. For reproducible work, replace `main` with the immutable dataset revision you downloaded. Source URLs can change without notice; provenance records individual acquisition times, hashes and sizes.

The refresh adds a net **3,832,549 rows** relative to the October 18 snapshot. This is not a count of new donors or new cash. Master-table rows are entity/cycle records; transaction rows retain reported multiplicity.

The current official 2022 individual-contributions ZIP has a truncated root member: 23,747,535 physical records with a partial last record. Its 34 official date shards independently reproduce all 63,885,802 typed baseline rows and all four SHA-256 limb sums. This release restores that complete baseline-equivalent cycle. It does not treat the root load as complete.

Strict current-source CSV checks cover all 27 standalone source/cycle partitions. Before publication, strict checks corrected a net 1,199 rows lost by this rebuild’s permissive CSV ingestion across 16 partitions. Of the 27 current typed multisets, 23 match the prior snapshot and four differ. Independent-expenditure raw source counts are reported separately from amendment-filtered final counts. Three current operating-expense sources require normalization of exactly one empty terminal field.

[Provenance](https://huggingface.co/datasets/Nason/fec-database/resolve/d8a54956e4cd989625e53b88c7b79ef0c199e2f9/sources-2026-11-09.json), [dictionary](https://huggingface.co/datasets/Nason/fec-database/resolve/d8a54956e4cd989625e53b88c7b79ef0c199e2f9/DICTIONARY.md), and the [portable snapshot validation bundle](https://huggingface.co/datasets/Nason/fec-database/resolve/d8a54956e4cd989625e53b88c7b79ef0c199e2f9/fec-snapshot-validation-2026-11-09.zip) record the checks and source identities. The bundle includes a DuckDB 1.5.5 read-only full-fingerprint verifier, source lock, code, tests and MIT license. It does not bundle the database or raw FEC sources and does not provide an offline or one-command source rebuild.

Fingerprint sums are decimal strings to avoid JSON/JavaScript precision loss. Full typed-row multiset fingerprints preserve multiplicity but do not prove hash injectivity. The separate whole-file SHA-256 identifies this database exactly.

## Interpretation and source quality

The [FEC individual-contributions file](https://www.fec.gov/campaign-finance-data/contributions-individuals-file-description/) covers a subset of reported itemized contributions under rules that changed over time. It is not a census of donations or unique people. Entity IDs recur across cycles: include `cycle` in joins and aggregate child transactions before combining them.

`v_candidate_totals` and `v_top_donors` net specified refund types. `v_daily_donations` excludes refunds and reports positive non-refund transactions. `v_pac_to_candidate` selects direct 24K/24Z contributions. These are different measures. For net contributions, account for memo rows, conduit transfers and refunds; avoid join fan-out. Raw name/employer/address strings are not stable donor identities.

Eight malformed nonblank individual-contribution dates from 2016/2018 remain NULL. No guessed date repair was applied. The retained 2022 interpretation removes 14 balanced wrapper quotes and separately preserves 13 malformed literal-quote fields. FEC does not specify quote escaping, so this is a disclosed interpretation choice. Other conversion/framing outcomes are summarized by source partition in the provenance.

Blank fields become NULL; amounts remain DOUBLE, with floating-point rather than exact decimal arithmetic. Source outlier dates, inconsistent amounts and prank filings remain. Inspect anomalous records against filings. Historical comparisons and parsing choices are retained in the [immutable prior provenance](https://huggingface.co/datasets/Nason/fec-database/blob/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/sources-2026-10-18.json).

The dictionary has exact base-table null percentages. Null statistics and examples for `v_candidate_totals`, `v_daily_donations`, and `v_top_donors` are unavailable after the 2022 correction. View SQL is unchanged.

## Resources and use restrictions

Disk size is not a RAM estimate. Remote queries can transfer much of the file. Contribution views aggregate large tables, and a final `LIMIT` does not guarantee a small scan. Keep the pre-attachment resource limits in the examples, leave process and disk headroom, and expect larger queries to fail when spill is disabled.

**Contributor names and addresses may not be sold or used commercially or to solicit contributions/donations.** See the [FEC sale-or-use guidance](https://www.fec.gov/updates/sale-or-use-contributor-information/). Public-domain copyright status of government data does not remove this use restriction.

Underlying records: U.S. Federal Election Commission. Build and verification code: MIT. [Source repository](https://github.com/ian-nason/fec-database); [original source revision](https://github.com/ian-nason/fec-database/tree/fea7c1400cd3de1842fd25ea29a115ac3214909d).

Database: 22,717,673,472 bytes (21.16 GiB). SHA-256: `5bde1896d2d243283c87de295642cf2f6bd3ded749ba9beb9e220a89d07f0e54`.


## GitHub release sources

The reviewed November 9 snapshot verifier and source lock are in [releases/2026-11-09](releases/2026-11-09). The hosted source bundle and provenance above preserve the exact published release. The root builder documents the earlier pipeline; use the release-specific instructions for this snapshot.
