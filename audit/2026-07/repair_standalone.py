"""Reload the three standalone FEC tables and recreate views (July 2026 audit).

- independent_expenditures / electioneering_communications /
  communication_costs had 100%-NULL or VARCHAR dates (DD-MON-YY and YYYYMMDD
  source formats were never tried) and undeduplicated amendment versions.
- All four views are rebuilt with correct money-summing semantics (24T
  conduit exclusion, refund netting, memo exclusion, no PCC fan-out,
  direct contributions only in v_pac_to_candidate).

The seven bulk tables are untouched.
"""
import re
from pathlib import Path

import duckdb

from build_database import (
    BASE_URL,
    STANDALONE_TABLES,
    build_columns_table,
    build_metadata,
    cast_columns,
    create_views,
    dedupe_ie_amendments,
    download_file,
    export_dictionary,
    load_standalone_csv,
    run_validation,
)

DATA_DIR = Path("data/raw")
DB_PATH = Path("fec.duckdb")
CYCLES = list(range(2004, 2027, 2))

con = duckdb.connect(str(DB_PATH))
con.execute("SET preserve_insertion_order = false")
con.execute(f"SET temp_directory = '{DB_PATH.resolve()}.tmp'")
con.execute("SET memory_limit = '8GB'")

for table_name, url_template in STANDALONE_TABLES:
    print(f"\nReloading {table_name}")
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    for cycle in CYCLES:
        cycle_dir = DATA_DIR / str(cycle)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        filename = url_template.format(cycle=cycle)
        csv_path = cycle_dir / filename
        if not download_file(f"{BASE_URL}/{cycle}/{filename}", csv_path, filename):
            continue
        try:
            n = load_standalone_csv(con, table_name, csv_path, cycle)
            print(f"  {cycle}: {n:,} rows", flush=True)
        except Exception as e:
            print(f"  WARNING: {table_name} {cycle}: {e}")
        finally:
            if csv_path.exists():
                csv_path.unlink()

    cols = [
        r[0] for r in con.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = ?", [table_name],
        ).fetchall()
    ]
    junk = [c for c in cols if re.fullmatch(r"column\d+", c)]
    for c in junk:
        con.execute(f'ALTER TABLE {table_name} DROP COLUMN "{c}"')
    if junk:
        print(f"  dropped {len(junk)} junk column(s)")
    if table_name == "independent_expenditures":
        n_amend = dedupe_ie_amendments(con)
        print(f"  removed {n_amend:,} superseded amendment rows")
    cast_columns(con, table_name)
    print(f"  cast {table_name}")

print("\nVerifying audit defects are gone:")
for tbl, datecol in [
    ("independent_expenditures", "exp_date"),
    ("communication_costs", "TRANSACTION_DT"),
    ("electioneering_communications", "COMMUNICATION_DATE"),
]:
    total, nn = con.execute(
        f'SELECT COUNT(*), COUNT("{datecol}") FROM {tbl}'
    ).fetchone()
    print(f"  {tbl}.{datecol}: {nn:,}/{total:,} non-null ({nn / total:.1%})")
    assert nn / total > 0.85, f"{tbl}.{datecol} still mostly NULL"
ie_2022 = con.execute(
    "SELECT SUM(exp_amo) FROM independent_expenditures WHERE cycle = 2022"
).fetchone()[0]
print(f"  2022 IE total after amendment dedupe: ${ie_2022:,.0f} (was $46.9B)")
ec_type = con.execute(
    "SELECT data_type FROM information_schema.columns WHERE table_name = "
    "'electioneering_communications' AND column_name = 'CALCULATED_CANDIDATE_SHARE'"
).fetchone()[0]
print(f"  EC CALCULATED_CANDIDATE_SHARE type: {ec_type}")
assert ec_type == "DOUBLE"

print("\nRecreating views")
built = {
    r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_type = 'BASE TABLE' AND table_name NOT LIKE '\\_%' ESCAPE '\\'"
    ).fetchall()
}
create_views(con, built)

print("\nVerifying view semantics:")
dup_pcc = con.execute("""
    SELECT COUNT(*) FROM (
        SELECT cycle, CMTE_ID FROM v_candidate_totals
        GROUP BY 1, 2 HAVING COUNT(*) > 1
    )
""").fetchone()[0]
print(f"  v_candidate_totals duplicate (cycle, committee) rows: {dup_pcc} (must be 0)")
assert dup_pcc == 0
biden_harris = con.execute("""
    SELECT candidate_names, net_individual FROM v_candidate_totals
    WHERE cycle = 2024 AND CMTE_ID = 'C00703975'
""").fetchall()
print(f"  shared Biden/Harris PCC now one row: {biden_harris}")
assert len(biden_harris) == 1
pac_types = con.execute(
    "SELECT DISTINCT transaction_type FROM v_pac_to_candidate"
).fetchall()
print(f"  v_pac_to_candidate types: {pac_types} (must be 24K/24Z only)")
assert {t[0] for t in pac_types} <= {"24K", "24Z"}

print("\nRegenerating metadata")
build_metadata(con, built)
run_validation(con, DB_PATH)
build_columns_table(con)
export_dictionary(con, Path("DICTIONARY.md"))
con.execute("CHECKPOINT")
con.close()
print("FEC STANDALONE REPAIR DONE")
