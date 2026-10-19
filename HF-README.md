---
license: other
license_name: public-domain
license_link: https://www.fec.gov/data/browse-data/?tab=bulk-data
pretty_name: FEC Campaign Finance Database
size_categories:
  - 100M<n<1B
tags: [campaign-finance, fec, elections, duckdb]
---

# FEC Campaign Finance Database

**356,327,912 rows**, ten data tables, four views and 237 dictionary entries. Cycles 2004–2026; 111 loaded sources and nine expected pre-2010 absences. Frozen to the source manifest completed **2026-10-18T08:55:34.351341+00:00**; sources have individual modification dates.

| Table | Rows | Columns |
|---|---:|---:|
| `candidate_committee_links` | 74,721 | 8 |
| `candidates` | 77,581 | 16 |
| `committee_contributions` | 5,314,838 | 23 |
| `committee_to_committee` | 48,182,632 | 22 |
| `committees` | 185,708 | 16 |
| `communication_costs` | 25,716 | 26 |
| `electioneering_communications` | 1,711 | 20 |
| `independent_expenditures` | 618,341 | 24 |
| `individual_contributions` | 282,086,037 | 22 |
| `operating_expenditures` | 19,760,627 | 26 |

## Quick start

```sql
INSTALL httpfs; LOAD httpfs;
SET memory_limit='128MiB'; SET threads=1; SET max_temp_directory_size='0B';
ATTACH 'https://huggingface.co/datasets/Nason/fec-database/resolve/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/fec.duckdb' AS fec (READ_ONLY);
SELECT CAND_ID,CAND_NAME FROM fec.candidates WHERE cycle=2026 AND CAND_OFFICE='H' ORDER BY CAND_ID LIMIT 5;
```

Install/upgrade Python with `python -m pip install --upgrade datapond` (the examples use 0.1.5), or install released R datapond from [CRAN](https://cran.r-project.org/package=datapond) with `install.packages("datapond")`. R 0.1.1 remains a separate development version. The catalog ID is `fec`.

The file occupies 19.69 GiB on disk; that is not a RAM estimate. Remote execution can still transfer much of it. Contribution views aggregate large tables, so a final `LIMIT` does not guarantee a small scan. The SQL above sets limits before attachment; leave process and disk headroom, and expect larger queries to fail when spill is disabled.

## Interpretation and source quality

Transaction rows are not unique donors or a complete census of donations. The [FEC individual-contributions file](https://www.fec.gov/campaign-finance-data/contributions-individuals-file-description/) includes a subset of reported itemized contributions under rules that changed over time. Entity IDs recur across cycles: join with `cycle` and aggregate child transactions before combining them.

`v_candidate_totals` and `v_top_donors` net specified refund types. `v_daily_donations` instead excludes refunds and reports positive non-refund transactions; `v_pac_to_candidate` selects direct 24K/24Z contributions. Their outputs are different measures.

All 37 historical changes have documented parsing/upstream explanations. A strict double-quote CSV interpretation removes balanced wrapper quotes from fourteen 2022 fields (twelve RETIRED occupations, one POLICY occupation, one NOT EMPLOYED CURRENTLY employer). Thirteen separate malformed literal-quote recoveries retain literal quotes. FEC's field description does not specify quote escaping; this is a disclosed interpretation choice, not an official rule. Eight malformed nonblank dates in 2016/2018 remain NULL, with raw tokens/identifiers retained in the provenance. No guessed date repair was applied.

A later source added committee **C00962951, CARMELA CONROY VICTORY FUND**, after the validated cutoff. It is outside this frozen snapshot. Source outlier dates, inconsistent amounts and prank filings remain; inspect unusual records against filings. Blank fields become NULL; DOUBLE amounts preserve the existing floating-point representation. For net contributions, account for memo rows, conduit transfers and refunds; avoid join fan-out.

The complete typed-row multiset audits, source hash/CRC checks, exact small-table comparisons and metadata verification are documented in [provenance](https://huggingface.co/datasets/Nason/fec-database/blob/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/sources-2026-10-18.json). Fingerprints preserve multiplicity but are not a claim of hash injectivity. [Dictionary](https://huggingface.co/datasets/Nason/fec-database/blob/aee3ae8b28685104765fb1b1e3ebc2588cb907a3/DICTIONARY.md); [source repository](https://github.com/ian-nason/fec-database). The bounded-loader source patch is merged in [source PR #1](https://github.com/ian-nason/fec-database/pull/1). That source merge does not replace this frozen data artifact.

Underlying records: U.S. Federal Election Commission. Build code: MIT. Published artifact: 21,140,877,312 bytes. SHA-256: `6227fb7c162c3d48a10bb677d2bfd74b21c1acba3aff68eafac2afc49d57a2d4`.

The release dictionary retains its prepublication “candidate” heading and historical audit terminology; it describes the published hash above. Its ID join hints are shorthand: include `cycle` and check child-table multiplicity as described here.
