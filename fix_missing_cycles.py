#!/usr/bin/env python3
"""Fix missing cycles in fec.duckdb: individual_contributions 2016/2018, candidates 2022."""

import duckdb
import urllib.request
import zipfile
import os
import tempfile

DB_PATH = "fec.duckdb"
FEC_BASE = "https://cg-519a459a-0ea3-42c2-b7bc-fa1143481f74.s3-us-gov-west-1.amazonaws.com/bulk-downloads"
HEADER_BASE = "https://www.fec.gov/files/bulk-downloads/data_dictionaries"

def get_headers(header_file):
    """Download and parse FEC header CSV to get column names."""
    url = f"{HEADER_BASE}/{header_file}"
    print(f"  Fetching headers from {url}")
    req = urllib.request.urlopen(url)
    text = req.read().decode("utf-8")
    req.close()
    # First row is column names
    return [c.strip().strip('"') for c in text.strip().split("\n")[0].split(",")]

def load_indiv(con, cycle):
    """Load individual contributions for a given cycle."""
    yr = str(cycle)[2:]  # e.g. "16" from 2016
    zip_url = f"{FEC_BASE}/{cycle}/indiv{yr}.zip"
    print(f"Downloading {zip_url}...")

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f"indiv{yr}.zip")
        urllib.request.urlretrieve(zip_url, zip_path)

        print(f"  Extracting...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmpdir)

        # Find the data file
        data_file = None
        for f in os.listdir(tmpdir):
            if f.endswith(".txt") and f != zip_path:
                data_file = os.path.join(tmpdir, f)
                break
        if not data_file:
            # Try itcont.txt specifically
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.lower() == "itcont.txt":
                        data_file = os.path.join(root, f)
                        break

        if not data_file:
            print(f"  ERROR: Could not find data file in zip")
            return 0

        print(f"  Found data file: {data_file}")

        # Get headers
        headers = get_headers("indiv_header_file.csv")
        print(f"  Headers ({len(headers)}): {headers[:5]}...")

        # Build column spec for read_csv
        col_spec = {h: "VARCHAR" for h in headers}

        # Read raw data
        escaped_path = data_file.replace("'", "''")
        con.sql(f"""
            CREATE OR REPLACE TEMP TABLE _raw_indiv AS
            SELECT * FROM read_csv('{escaped_path}',
                delim='|', header=false, columns={col_spec},
                ignore_errors=true, null_padding=true, quote='')
        """)

        raw_count = con.sql("SELECT COUNT(*) FROM _raw_indiv").fetchone()[0]
        print(f"  Raw rows: {raw_count:,}")

        # Insert with proper casting
        # Build SELECT with casting for DATE and DOUBLE columns
        target_cols = con.sql("DESCRIBE individual_contributions").fetchall()
        select_parts = []
        for col_info in target_cols:
            col_name = col_info[0]
            col_type = col_info[1]
            if col_name == "cycle":
                select_parts.append(f"{cycle} AS cycle")
            elif col_type == "DATE":
                select_parts.append(f"TRY_STRPTIME({col_name}, '%m%d%Y')::DATE AS {col_name}")
            elif col_type == "DOUBLE":
                select_parts.append(f"TRY_CAST({col_name} AS DOUBLE) AS {col_name}")
            else:
                select_parts.append(col_name)

        select_sql = ", ".join(select_parts)
        con.sql(f"INSERT INTO individual_contributions SELECT {select_sql} FROM _raw_indiv")
        con.sql("DROP TABLE _raw_indiv")

        print(f"  Inserted {raw_count:,} rows for cycle {cycle}")
        return raw_count

def load_candidates(con, cycle):
    """Load candidates for a given cycle."""
    yr = str(cycle)[2:]
    zip_url = f"{FEC_BASE}/{cycle}/cn{yr}.zip"
    print(f"Downloading {zip_url}...")

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f"cn{yr}.zip")
        urllib.request.urlretrieve(zip_url, zip_path)

        print(f"  Extracting...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmpdir)

        data_file = None
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                if f.lower().endswith(".txt"):
                    data_file = os.path.join(root, f)
                    break

        if not data_file:
            print(f"  ERROR: Could not find data file")
            return 0

        print(f"  Found data file: {data_file}")

        headers = get_headers("cn_header_file.csv")
        print(f"  Headers ({len(headers)}): {headers[:5]}...")

        col_spec = {h: "VARCHAR" for h in headers}

        escaped_path = data_file.replace("'", "''")
        con.sql(f"""
            CREATE OR REPLACE TEMP TABLE _raw_cn AS
            SELECT * FROM read_csv('{escaped_path}',
                delim='|', header=false, columns={col_spec},
                ignore_errors=true, null_padding=true, quote='')
        """)

        raw_count = con.sql("SELECT COUNT(*) FROM _raw_cn").fetchone()[0]
        print(f"  Raw rows: {raw_count:,}")

        target_cols = con.sql("DESCRIBE candidates").fetchall()
        select_parts = []
        for col_info in target_cols:
            col_name = col_info[0]
            col_type = col_info[1]
            if col_name == "cycle":
                select_parts.append(f"{cycle} AS cycle")
            elif col_type == "DATE":
                select_parts.append(f"TRY_STRPTIME({col_name}, '%m%d%Y')::DATE AS {col_name}")
            elif col_type == "DOUBLE":
                select_parts.append(f"TRY_CAST({col_name} AS DOUBLE) AS {col_name}")
            else:
                select_parts.append(col_name)

        select_sql = ", ".join(select_parts)
        con.sql(f"INSERT INTO candidates SELECT {select_sql} FROM _raw_cn")
        con.sql("DROP TABLE _raw_cn")

        print(f"  Inserted {raw_count:,} rows for cycle {cycle}")
        return raw_count

def main():
    con = duckdb.connect(DB_PATH)

    # Check what's missing
    indiv_cycles = [r[0] for r in con.sql("SELECT DISTINCT cycle FROM individual_contributions ORDER BY cycle").fetchall()]
    cand_cycles = [r[0] for r in con.sql("SELECT DISTINCT cycle FROM candidates ORDER BY cycle").fetchall()]
    print(f"Current individual_contributions cycles: {indiv_cycles}")
    print(f"Current candidates cycles: {cand_cycles}")

    expected = list(range(2004, 2028, 2))
    missing_indiv = [c for c in expected if c not in indiv_cycles]
    missing_cand = [c for c in expected if c not in cand_cycles]
    print(f"Missing individual_contributions: {missing_indiv}")
    print(f"Missing candidates: {missing_cand}")

    if not missing_indiv and not missing_cand:
        print("Nothing to fix!")
        con.close()
        return

    # Load missing individual contributions
    for cycle in missing_indiv:
        load_indiv(con, cycle)

    # Load missing candidates
    for cycle in missing_cand:
        load_candidates(con, cycle)

    # Update _metadata
    print("\nUpdating _metadata...")
    for table in ["individual_contributions", "candidates"]:
        row_count = con.sql(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        cycles = con.sql(f"SELECT MIN(cycle)||'-'||MAX(cycle) FROM {table}").fetchone()[0]
        con.sql(f"UPDATE _metadata SET row_count = {row_count}, cycles_covered = '{cycles}' WHERE table_name = '{table}'")
        print(f"  {table}: {row_count:,} rows, cycles {cycles}")

    # Verify
    print("\nVerification:")
    indiv_cycles = [r[0] for r in con.sql("SELECT DISTINCT cycle FROM individual_contributions ORDER BY cycle").fetchall()]
    cand_cycles = [r[0] for r in con.sql("SELECT DISTINCT cycle FROM candidates ORDER BY cycle").fetchall()]
    print(f"  individual_contributions cycles: {indiv_cycles}")
    print(f"  candidates cycles: {cand_cycles}")

    con.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
