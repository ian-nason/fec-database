# Changelog

## 2026-09-14 — Data refresh (FEC bulk files as of 2026-09-14)

- Rebuilt from the FEC bulk downloads for all 12 cycles (2004-2026). Total
  rows 347,171,337 → 354,943,430: `individual_contributions` 280,827,680,
  `committee_to_committee` 48,118,471, `operating_expenditures` 19,725,971,
  `committee_contributions` 5,304,857, `independent_expenditures` 602,587
  (74,486 superseded amendment versions removed at build time).
- The July audit's repairs are now regression checks in the build: standalone
  table dates > 85% non-null, `CALCULATED_CANDIDATE_SHARE` typed DOUBLE, one
  `v_candidate_totals` row per (cycle, committee), `v_pac_to_candidate`
  limited to 24K/24Z, conduit (24T) rows excluded from totals, and all 12
  cycles present (a silently skipped download would otherwise drop a cycle).
  A failing check aborts the build with a non-zero exit.
- DuckDB memory capped (default 6 GB, run at 4 GB / 2 threads for this build)
  with `DATAPOND_MEMORY_LIMIT` / `DATAPOND_THREADS` overrides; `continue_build.py`
  uses the same settings. File size 37.7 → 35.2 GB (insertion order no longer
  preserved, which compresses better). `publish_to_hf.py --card-only`.
- Caveats unchanged: prank filings remain (treat single contributions > $5M
  as suspect); upstream dates range from year 0677 to 9206; `CAND_ID`
  resolves for ~95-99% of rows.

## 2026-07-06 — Full refresh + data-quality audit

Rebuilt from current FEC bulk downloads (cycles 2004-2026) and repaired
after an independent SQL-verified audit.

**Data changes**
- 347,171,337 rows across 10 tables (previous published build: 339.5M).
- Cycle 2020 individual contributions complete at 69,352,160 rows.
- `independent_expenditures`: 74,030 superseded amendment versions removed —
  only the latest version of each filing is kept (2022 IE total dropped from
  $46.9B to $33.6B; remaining inflation is upstream prank filings, see
  caveats).

**Fixes**
- Standalone-table dates now parse (previously 100% NULL):
  `independent_expenditures` (DD-MON-YY), `communication_costs` (YYYYMMDD),
  `electioneering_communications` (DD-MON-YY, amounts now numeric).
- All four views rebuilt with correct money semantics: conduit rows
  (`TRANSACTION_TP = '24T'`, the ActBlue/WinRed double count worth 14-22% of
  every cycle since 2018) excluded; refunds (20Y/21Y/22Y, stored as positive
  amounts) netted out; memo rows excluded.
- `v_candidate_totals` aggregates per principal campaign committee, so
  candidates sharing a committee (Biden/Harris 2024) no longer fan out into
  double-counted rows.
- `v_pac_to_candidate` is direct contributions only (24K/24Z) — it
  previously counted independent expenditures *against* a candidate as
  support.

**Known caveats** (see the README's "How to sum money correctly")
- Upstream prank filings remain in `independent_expenditures` (e.g. a $10B
  "COMMITTEE 300" row) — treat amounts above ~$5M as suspect anywhere.
- A few thousand rows carry wild dates (years 0677-9206); clamp to the
  cycle window before bucketing.
- Recent-cycle `committee_contributions.CAND_ID` values fail to resolve to
  same-cycle candidates at 1-5% (FEC master-file churn).
