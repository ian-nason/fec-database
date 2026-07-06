# Changelog

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
