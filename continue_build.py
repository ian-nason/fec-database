"""Resume an interrupted build into an existing fec.duckdb.

Idempotent: skips any (table, cycle) pair already present in the database,
loads the rest, then runs casts/views/metadata/validation/dictionary.
Safe to re-run after a crash at any point; each (table, cycle) load commits
independently. Pre-seed data/raw/<cycle>/<name>.zip with a manually
repaired download to bypass the downloader for that file.
"""
import re
import time
from pathlib import Path

import duckdb
from tqdm import tqdm

from build_database import (
    BASE_URL,
    BULK_TABLES,
    STANDALONE_TABLES,
    build_columns_table,
    build_metadata,
    cast_columns,
    create_views,
    download_file,
    download_headers,
    export_dictionary,
    extract_zip,
    load_bulk_table,
    load_standalone_csv,
    run_validation,
)

DATA_DIR = Path("data/raw")
DB_PATH = Path("fec.duckdb")
CYCLES = list(range(2004, 2027, 2))

t_start = time.time()
con = duckdb.connect(str(DB_PATH))
con.execute("SET preserve_insertion_order = false")
con.execute(f"SET temp_directory = '{DB_PATH.resolve()}.tmp'")
# Leave headroom for the OS and the CSV reader on a 15GB WSL VM; DuckDB
# spills to the temp directory instead of pressuring the VM.
con.execute("SET memory_limit = '8GB'")


def table_cycles(table_name: str) -> set[int]:
    exists = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
        [table_name],
    ).fetchone()[0]
    if not exists:
        return set()
    return {
        r[0]
        for r in con.execute(f"SELECT DISTINCT cycle FROM {table_name}").fetchall()
    }


print("Resuming FEC build", flush=True)
headers = download_headers(DATA_DIR)

for table_name, zip_name, data_file, header_file in BULK_TABLES:
    if header_file not in headers:
        print(f"  Skipping {table_name} (no header file)")
        continue
    columns = headers[header_file]
    have = table_cycles(table_name)
    todo = [c for c in CYCLES if c not in have]
    if not todo:
        print(f"  {table_name}: complete ({len(have)} cycles)", flush=True)
        continue
    print(f"\n  {table_name}: loading cycles {todo}", flush=True)

    for cycle in tqdm(todo, desc="    cycles", unit="cycle", leave=False):
        cycle_dir = DATA_DIR / str(cycle)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        suffix = str(cycle)[-2:]
        zip_path = cycle_dir / f"{zip_name}{suffix}.zip"
        zip_url = f"{BASE_URL}/{cycle}/{zip_name}{suffix}.zip"
        if not download_file(zip_url, zip_path, f"{zip_name}.zip {cycle}"):
            continue

        txt_path = cycle_dir / data_file
        if not (txt_path.exists() and txt_path.stat().st_size > 0):
            txt_path = extract_zip(zip_path, data_file, cycle_dir)
        if not txt_path or not txt_path.exists() or txt_path.stat().st_size == 0:
            print(f"    WARNING: no data file for {table_name} cycle {cycle}")
            continue

        try:
            n = load_bulk_table(con, table_name, txt_path, columns, cycle)
            print(f"    {table_name} {cycle}: {n:,} rows", flush=True)
        except Exception as e:
            print(f"    WARNING: {table_name} cycle {cycle}: {e}")
        finally:
            if txt_path and txt_path.exists():
                txt_path.unlink()
            if zip_path.exists():
                zip_path.unlink()

for table_name, url_template in STANDALONE_TABLES:
    have = table_cycles(table_name)
    todo = [c for c in CYCLES if c not in have]
    if not todo:
        print(f"  {table_name}: complete ({len(have)} cycles)", flush=True)
        continue
    print(f"\n  {table_name}: loading cycles {todo}", flush=True)

    for cycle in tqdm(todo, desc="    cycles", unit="cycle", leave=False):
        cycle_dir = DATA_DIR / str(cycle)
        cycle_dir.mkdir(parents=True, exist_ok=True)
        filename = url_template.format(cycle=cycle)
        csv_url = f"{BASE_URL}/{cycle}/{filename}"
        csv_path = cycle_dir / filename
        if not download_file(csv_url, csv_path, filename):
            continue
        try:
            n = load_standalone_csv(con, table_name, csv_path, cycle)
            print(f"    {table_name} {cycle}: {n:,} rows", flush=True)
        except Exception as e:
            print(f"    WARNING: {table_name} cycle {cycle}: {e}")
        finally:
            if csv_path.exists():
                csv_path.unlink()

    cols = [
        r[0]
        for r in con.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = ?",
            [table_name],
        ).fetchall()
    ]
    junk = [c for c in cols if re.fullmatch(r"column\d+", c)]
    for c in junk:
        con.execute(f'ALTER TABLE {table_name} DROP COLUMN "{c}"')
    if junk:
        print(f"    -> dropped {len(junk)} junk column(s) from {table_name}")

built = {
    r[0]
    for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_type = 'BASE TABLE' AND table_name NOT LIKE '\\_%' ESCAPE '\\'"
    ).fetchall()
}
print(f"\nTables built: {sorted(built)}", flush=True)

print("\nCasting date and amount columns", flush=True)
for tbl in sorted(built):
    try:
        cast_columns(con, tbl)
        print(f"  Cast: {tbl}", flush=True)
    except Exception as e:
        print(f"  WARNING: casting {tbl}: {e}")

print("\nCreating views", flush=True)
create_views(con, built)
print("Building metadata", flush=True)
build_metadata(con, built)
run_validation(con, DB_PATH)
print("Building _columns data dictionary", flush=True)
build_columns_table(con)
print("Exporting DICTIONARY.md", flush=True)
export_dictionary(con, Path("DICTIONARY.md"))
con.execute("CHECKPOINT")
con.close()
print(f"\nCONTINUE BUILD DONE in {(time.time() - t_start) / 60:.1f} min", flush=True)
