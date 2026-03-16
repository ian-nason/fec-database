#!/usr/bin/env python3
"""
FEC Campaign Finance Database Builder

Downloads FEC bulk data files, harmonizes schemas across election cycles,
and produces a queryable DuckDB database with pre-built views.

Data source: https://www.fec.gov/data/browse-data/?tab=bulk-data
Updated weekly (Sunday nights). All public domain.

Usage:
    uv run python build_database.py
    uv run python build_database.py --start-cycle 2020 --end-cycle 2026
    uv run python build_database.py --start-cycle 1980
    uv run python build_database.py --tables candidates committees individual_contributions
"""

import argparse
import io
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import duckdb
import requests
from tqdm import tqdm

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_OUTPUT = "fec.duckdb"
DEFAULT_START = 2004
DEFAULT_END = 2026

BASE_URL = "https://www.fec.gov/files/bulk-downloads"
HEADER_URL = f"{BASE_URL}/data_dictionaries"

# ---------------------------------------------------------------------------
# Table definitions
# ---------------------------------------------------------------------------

# Bulk zip tables: (table_name, zip_file, data_file_inside_zip, header_file)
BULK_TABLES = [
    ("candidates",               "cn",     "cn.txt",       "cn_header_file.csv"),
    ("committees",               "cm",     "cm.txt",       "cm_header_file.csv"),
    ("candidate_committee_links","ccl",    "ccl.txt",      "ccl_header_file.csv"),
    ("individual_contributions", "indiv",  "itcont.txt",   "indiv_header_file.csv"),
    ("committee_contributions",  "pas2",   "itpas2.txt",   "pas2_header_file.csv"),
    ("committee_to_committee",   "oth",    "itoth.txt",    "oth_header_file.csv"),
    ("operating_expenditures",   "oppexp", "oppexp.txt",   "oppexp_header_file.csv"),
]

# Standalone CSV tables (comma-delimited, WITH headers, per-cycle)
STANDALONE_TABLES = [
    ("independent_expenditures",    "independent_expenditure_{cycle}.csv"),
    ("electioneering_communications", "ElectioneeringComm_{cycle}.csv"),
    ("communication_costs",         "CommunicationCosts_{cycle}.csv"),
]

TABLE_DESCRIPTIONS = {
    "candidates": "Candidate master: name, party, office, state, district, status",
    "committees": "Committee master: name, type, party, treasurer, connected org",
    "candidate_committee_links": "Which committees are authorized by which candidates",
    "individual_contributions": "Every individual donation: name, employer, occupation, amount, date",
    "committee_contributions": "PAC/party contributions to candidates",
    "committee_to_committee": "Transfers between committees",
    "operating_expenditures": "Committee operating expenditures: payee, purpose, amount",
    "independent_expenditures": "Independent expenditures for/against candidates",
    "electioneering_communications": "Broadcast ads mentioning candidates near elections",
    "communication_costs": "Internal communications supporting/opposing candidates",
}

# Columns that contain dates in MMDDYYYY format
DATE_COLUMNS = {
    "transaction_dt", "receipt_dt", "cand_election_yr",
    "disb_dt", "receipt_date", "dissemination_dt",
    "communication_dt",
}

# Columns that should be numeric
AMOUNT_COLUMNS = {
    "transaction_amt", "expenditure_amt", "communication_cost",
    "ttl_receipts", "ttl_disb", "coh_cop", "cand_contrib",
    "cand_loans", "other_loans", "cand_loan_repay",
    "other_loan_repay", "debts_owed_by", "debts_owed_to",
    "indiv_contrib", "other_pol_cmte_contrib", "pol_pty_contrib",
    "cvg_end_dt", "indiv_refund", "cmte_refund",
    "ttl_indiv_contrib", "net_contrib", "net_op_exp",
}

YEAR_COLUMNS = {"cand_election_yr"}


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress. Returns True on success."""
    if dest.exists() and dest.stat().st_size > 0:
        return True

    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(url, stream=True, timeout=60)
        if r.status_code == 404:
            return False
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f:
            with tqdm(
                total=total, unit="B", unit_scale=True,
                desc=f"    {desc or dest.name}", leave=False,
            ) as pbar:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    f.write(chunk)
                    pbar.update(len(chunk))
        return True
    except Exception as e:
        print(f"    WARNING: Failed to download {url}: {e}")
        if dest.exists():
            dest.unlink()
        return False


def download_headers(data_dir: Path) -> dict[str, list[str]]:
    """Download all header files and return {header_file: [col_names]}."""
    header_dir = data_dir / "headers"
    header_dir.mkdir(parents=True, exist_ok=True)
    headers = {}

    for _, _, _, header_file in BULK_TABLES:
        url = f"{HEADER_URL}/{header_file}"
        dest = header_dir / header_file
        if download_file(url, dest, header_file):
            cols = dest.read_text().strip().split(",")
            # Clean whitespace from column names
            cols = [c.strip() for c in cols]
            headers[header_file] = cols
        else:
            print(f"    ERROR: Could not download {header_file}")

    return headers


def extract_zip(zip_path: Path, data_file: str, dest_dir: Path) -> Path | None:
    """Extract a specific file from a zip. Returns path to extracted file."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            # Try exact match first, then case-insensitive
            names = zf.namelist()
            match = None
            for name in names:
                if name.lower() == data_file.lower():
                    match = name
                    break
            if not match:
                # Just extract whatever is in there (usually one file)
                txt_files = [n for n in names if n.lower().endswith(".txt")]
                if txt_files:
                    match = txt_files[0]
            if not match and names:
                match = names[0]

            if match:
                dest = dest_dir / data_file
                with zf.open(match) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                return dest
    except Exception as e:
        print(f"    WARNING: Could not extract {zip_path.name}: {e}")
    return None


# ---------------------------------------------------------------------------
# DuckDB loading
# ---------------------------------------------------------------------------


def build_column_spec(columns: list[str]) -> str:
    """Build a DuckDB columns spec dict for read_csv."""
    parts = []
    for col in columns:
        col_clean = col.strip().strip('"').strip("'")
        parts.append(f"'{col_clean}': 'VARCHAR'")
    return "{" + ", ".join(parts) + "}"


def load_bulk_table(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    data_file: Path,
    columns: list[str],
    cycle: int,
) -> int:
    """Load a pipe-delimited FEC bulk file into DuckDB. Returns row count."""
    col_spec = build_column_spec(columns)
    col_names = ", ".join(f'"{c.strip()}"' for c in columns)

    # Check if table exists
    exists = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        f"WHERE table_name = '{table_name}'"
    ).fetchone()[0] > 0

    if not exists:
        con.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT *, {cycle}::INTEGER AS cycle
            FROM read_csv('{data_file}',
                delim='|',
                header=false,
                columns={col_spec},
                ignore_errors=true,
                null_padding=true,
                strict_mode=false
            )
            WHERE 1=0
        """)

    # Insert data
    con.execute(f"""
        INSERT INTO {table_name}
        SELECT *, {cycle}::INTEGER AS cycle
        FROM read_csv('{data_file}',
            delim='|',
            header=false,
            columns={col_spec},
            ignore_errors=true,
            null_padding=true,
            strict_mode=false
        )
    """)

    count = con.execute(
        f"SELECT COUNT(*) FROM {table_name} WHERE cycle = {cycle}"
    ).fetchone()[0]
    return count


def load_standalone_csv(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    csv_path: Path,
    cycle: int,
) -> int:
    """Load a comma-delimited CSV with headers into DuckDB. Returns row count."""
    exists = con.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        f"WHERE table_name = '{table_name}'"
    ).fetchone()[0] > 0

    if not exists:
        con.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT *, {cycle}::INTEGER AS cycle
            FROM read_csv('{csv_path}',
                header=true,
                ignore_errors=true,
                null_padding=true,
                strict_mode=false,
                all_varchar=true,
                parallel=false
            )
            WHERE 1=0
        """)

    # Insert — handle schema differences across cycles
    try:
        con.execute(f"""
            INSERT INTO {table_name} BY NAME
            SELECT *, {cycle}::INTEGER AS cycle
            FROM read_csv('{csv_path}',
                header=true,
                ignore_errors=true,
                null_padding=true,
                strict_mode=false,
                all_varchar=true,
                parallel=false
            )
        """)
    except Exception:
        # Schema mismatch — add missing columns and retry
        temp_cols = con.execute(f"""
            SELECT column_name FROM (
                DESCRIBE SELECT * FROM read_csv('{csv_path}',
                    header=true, ignore_errors=true, null_padding=true,
                    strict_mode=false, all_varchar=true, parallel=false
                )
            )
        """).fetchall()
        existing = {
            r[0] for r in con.execute(f"DESCRIBE {table_name}").fetchall()
        }
        for (col,) in temp_cols:
            if col not in existing:
                con.execute(
                    f'ALTER TABLE {table_name} ADD COLUMN "{col}" VARCHAR'
                )
        con.execute(f"""
            INSERT INTO {table_name} BY NAME
            SELECT *, {cycle}::INTEGER AS cycle
            FROM read_csv('{csv_path}',
                header=true,
                ignore_errors=true,
                null_padding=true,
                strict_mode=false,
                all_varchar=true,
                parallel=false
            )
        """)

    count = con.execute(
        f"SELECT COUNT(*) FROM {table_name} WHERE cycle = {cycle}"
    ).fetchone()[0]
    return count


# ---------------------------------------------------------------------------
# Type casting (post-load)
# ---------------------------------------------------------------------------


def cast_columns(con: duckdb.DuckDBPyConnection, table_name: str):
    """Cast date and amount columns to proper types after loading."""
    cols = {
        r[0].lower(): r[0]
        for r in con.execute(f"DESCRIBE {table_name}").fetchall()
    }

    casts = []
    for col_lower, col_actual in cols.items():
        if col_lower in DATE_COLUMNS or col_lower.endswith("_dt"):
            # FEC dates: MMDDYYYY -> DATE
            casts.append(
                f'TRY_STRPTIME("{col_actual}", \'%m%d%Y\')::DATE AS "{col_actual}"'
            )
        elif col_lower in AMOUNT_COLUMNS or col_lower.endswith("_amt"):
            casts.append(f'TRY_CAST("{col_actual}" AS DOUBLE) AS "{col_actual}"')
        elif col_lower in YEAR_COLUMNS:
            casts.append(f'TRY_CAST("{col_actual}" AS INTEGER) AS "{col_actual}"')
        else:
            casts.append(f'"{col_actual}"')

    select_clause = ", ".join(casts)
    con.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT {select_clause} FROM {table_name}
    """)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

VIEWS = {
    "v_candidate_totals": {
        "deps": {"candidates", "individual_contributions"},
        "sql": """
            CREATE OR REPLACE VIEW v_candidate_totals AS
            SELECT
                c.CAND_ID,
                c.CAND_NAME,
                c.CAND_PTY_AFFILIATION AS party,
                c.CAND_OFFICE AS office,
                c.CAND_OFFICE_ST AS state,
                ic.cycle,
                COUNT(DISTINCT ic.SUB_ID) AS num_contributions,
                SUM(ic.TRANSACTION_AMT) AS total_individual
            FROM candidates c
            LEFT JOIN individual_contributions ic
                ON c.CAND_PCC = ic.CMTE_ID AND c.cycle = ic.cycle
            WHERE ic.TRANSACTION_AMT > 0
            GROUP BY c.CAND_ID, c.CAND_NAME, c.CAND_PTY_AFFILIATION,
                     c.CAND_OFFICE, c.CAND_OFFICE_ST, ic.cycle
        """,
    },
    "v_top_donors": {
        "deps": {"individual_contributions"},
        "sql": """
            CREATE OR REPLACE VIEW v_top_donors AS
            SELECT
                NAME, EMPLOYER, OCCUPATION, STATE,
                COUNT(*) AS num_contributions,
                SUM(TRANSACTION_AMT) AS total_donated,
                MIN(cycle) AS first_cycle,
                MAX(cycle) AS last_cycle,
                COUNT(DISTINCT CMTE_ID) AS num_committees
            FROM individual_contributions
            WHERE TRANSACTION_AMT > 0
            GROUP BY NAME, EMPLOYER, OCCUPATION, STATE
        """,
    },
    "v_pac_to_candidate": {
        "deps": {"committee_contributions", "committees", "candidates"},
        "sql": """
            CREATE OR REPLACE VIEW v_pac_to_candidate AS
            SELECT
                cm.CMTE_NM AS pac_name,
                cm.CONNECTED_ORG_NM AS connected_org,
                cn.CAND_NAME AS candidate_name,
                cn.CAND_PTY_AFFILIATION AS candidate_party,
                cn.CAND_OFFICE AS office,
                cn.CAND_OFFICE_ST AS state,
                cc.TRANSACTION_AMT AS amount,
                cc.TRANSACTION_DT AS date,
                cc.cycle
            FROM committee_contributions cc
            JOIN committees cm ON cc.CMTE_ID = cm.CMTE_ID AND cc.cycle = cm.cycle
            JOIN candidates cn ON cc.CAND_ID = cn.CAND_ID AND cc.cycle = cn.cycle
        """,
    },
    "v_daily_donations": {
        "deps": {"individual_contributions"},
        "sql": """
            CREATE OR REPLACE VIEW v_daily_donations AS
            SELECT
                TRANSACTION_DT AS date,
                cycle,
                COUNT(*) AS num_donations,
                SUM(TRANSACTION_AMT) AS total_amount,
                AVG(TRANSACTION_AMT) AS avg_amount,
                MEDIAN(TRANSACTION_AMT) AS median_amount
            FROM individual_contributions
            WHERE TRANSACTION_DT IS NOT NULL AND TRANSACTION_AMT > 0
            GROUP BY TRANSACTION_DT, cycle
        """,
    },
}


def create_views(con: duckdb.DuckDBPyConnection, built: set[str]) -> list[str]:
    created = []
    for name, info in VIEWS.items():
        missing = info["deps"] - built
        if missing:
            print(f"  Skipping {name} (missing: {missing})")
            continue
        try:
            con.execute(info["sql"])
            created.append(name)
            print(f"  Created: {name}")
        except Exception as e:
            print(f"  WARNING: {name}: {e}")
    return created


# ---------------------------------------------------------------------------
# Metadata & validation
# ---------------------------------------------------------------------------


def build_metadata(con: duckdb.DuckDBPyConnection, built: set[str]):
    con.execute("""
        CREATE OR REPLACE TABLE _metadata (
            table_name VARCHAR,
            description VARCHAR,
            row_count BIGINT,
            column_count INTEGER,
            cycles_covered VARCHAR,
            built_at TIMESTAMP
        )
    """)
    now = datetime.now().isoformat()

    for tbl in sorted(built):
        try:
            rc = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            cc = len(con.execute(f"SELECT * FROM {tbl} LIMIT 0").description)
            try:
                cycles = con.execute(
                    f"SELECT MIN(cycle), MAX(cycle) FROM {tbl}"
                ).fetchone()
                cyc_str = f"{cycles[0]}-{cycles[1]}" if cycles[0] else ""
            except Exception:
                cyc_str = ""
            desc = TABLE_DESCRIPTIONS.get(tbl, "")
            con.execute(
                "INSERT INTO _metadata VALUES (?,?,?,?,?,?)",
                [tbl, desc, rc, cc, cyc_str, now],
            )
        except Exception as e:
            print(f"  WARNING: metadata for {tbl}: {e}")


def run_validation(con: duckdb.DuckDBPyConnection, db_path: Path):
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    try:
        rows = con.execute(
            "SELECT table_name, row_count, column_count, cycles_covered "
            "FROM _metadata ORDER BY row_count DESC"
        ).fetchall()
        total = sum(r[1] for r in rows)
        print(f"\n  {len(rows)} tables, {total:,} total rows\n")
        for name, rc, cc, cyc in rows:
            print(f"    {name:<35s} {rc:>14,} rows  ({cc} cols)  [{cyc}]")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Quick sanity: top candidates by individual contributions (latest cycle)
    try:
        latest = con.execute(
            "SELECT MAX(cycle) FROM individual_contributions"
        ).fetchone()[0]
        print(f"\n  Top 5 candidates by individual $ (cycle {latest}):")
        rows = con.execute(f"""
            SELECT c.CAND_NAME, c.CAND_PTY_AFFILIATION,
                SUM(i.TRANSACTION_AMT) AS total
            FROM individual_contributions i
            JOIN candidates c ON i.CMTE_ID = c.CAND_PCC AND i.cycle = c.cycle
            WHERE i.cycle = {latest} AND i.TRANSACTION_AMT > 0
                AND c.CAND_OFFICE = 'P'
            GROUP BY c.CAND_NAME, c.CAND_PTY_AFFILIATION
            ORDER BY total DESC LIMIT 5
        """).fetchall()
        for name, party, total in rows:
            print(f"    {name:<40s} {party:<5s} ${total:>14,.0f}")
    except Exception as e:
        print(f"  Could not run candidate query: {e}")

    # Date range check
    try:
        print("\n  Date ranges:")
        for tbl, col in [
            ("individual_contributions", "TRANSACTION_DT"),
            ("committee_contributions", "TRANSACTION_DT"),
        ]:
            try:
                r = con.execute(f"""
                    SELECT MIN("{col}"), MAX("{col}")
                    FROM {tbl} WHERE "{col}" IS NOT NULL
                """).fetchone()
                print(f"    {tbl}.{col}: {r[0]} to {r[1]}")
            except Exception:
                pass
    except Exception:
        pass

    size_mb = db_path.stat().st_size / (1024**2)
    print(f"\n  Database size: {size_mb:,.0f} MB ({size_mb/1024:.1f} GB)")


# ---------------------------------------------------------------------------
# Data dictionary
# ---------------------------------------------------------------------------


def build_columns_table(con):
    """Build the _columns data dictionary table."""
    con.execute("DROP TABLE IF EXISTS _columns")

    # Base columns from information_schema
    # FEC _metadata has no source_file column, so we set it to NULL
    con.execute("""
        CREATE TABLE _columns AS
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            NULL::VARCHAR AS source_file
        FROM information_schema.columns c
        WHERE c.table_schema = 'main'
          AND c.table_name NOT IN ('_metadata', '_columns')
    """)

    # Add enrichment columns
    con.execute("ALTER TABLE _columns ADD COLUMN example_value VARCHAR")
    con.execute("ALTER TABLE _columns ADD COLUMN join_hint VARCHAR")
    con.execute("ALTER TABLE _columns ADD COLUMN null_pct DOUBLE")

    # Known join hints for FEC
    join_hints = {
        "CMTE_ID": "Committee ID, joins to committees table and contribution tables",
        "CAND_ID": "Candidate ID, joins across candidates and contribution tables",
        "CAND_PCC": "Candidate principal campaign committee, joins candidates to committees.CMTE_ID",
        "cycle": "Election cycle (even year), present in all FEC tables",
        "SUB_ID": "Unique submission/transaction ID",
        "TRAN_ID": "Transaction identifier within a committee",
        "AMNDT_IND": "Amendment indicator (N=new, A=amendment, T=termination)",
        "RPT_TP": "Report type code",
        "ENTITY_TP": "Entity type (IND=individual, COM=committee, etc.)",
    }

    for col, hint in join_hints.items():
        con.execute(
            "UPDATE _columns SET join_hint = ? WHERE column_name = ?",
            [hint, col],
        )

    # Populate example_value and null_pct for each column
    rows = con.execute(
        "SELECT table_name, column_name FROM _columns"
    ).fetchall()

    for table_name, column_name in rows:
        try:
            result = con.execute(
                f'SELECT CAST("{column_name}" AS VARCHAR) '
                f'FROM "{table_name}" '
                f'WHERE "{column_name}" IS NOT NULL LIMIT 1'
            ).fetchone()
            if result:
                val = result[0]
                if len(val) > 80:
                    val = val[:77] + "..."
                con.execute(
                    "UPDATE _columns SET example_value = ? "
                    "WHERE table_name = ? AND column_name = ?",
                    [val, table_name, column_name],
                )
        except Exception:
            pass

        try:
            result = con.execute(
                f'SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE "{column_name}" IS NULL) '
                f'/ COUNT(*), 1) FROM "{table_name}"'
            ).fetchone()
            if result and result[0] is not None:
                con.execute(
                    "UPDATE _columns SET null_pct = ? "
                    "WHERE table_name = ? AND column_name = ?",
                    [result[0], table_name, column_name],
                )
        except Exception:
            pass


def export_dictionary(con, output_path):
    """Export _columns and _metadata as a readable DICTIONARY.md file."""
    lines = []
    lines.append("# Data Dictionary")
    lines.append("")
    lines.append("Source: [FEC Bulk Data](https://www.fec.gov/data/browse-data/?tab=bulk-data)")
    lines.append("")

    tables = con.execute(
        "SELECT DISTINCT table_name FROM _columns ORDER BY table_name"
    ).fetchall()

    for (table_name,) in tables:
        meta = con.execute(
            "SELECT row_count, description FROM _metadata WHERE table_name = ?",
            [table_name],
        ).fetchone()

        lines.append(f"## {table_name}")
        lines.append("")
        if meta:
            row_count, description = meta
            if description:
                lines.append(f"{description}")
                lines.append("")
            if row_count:
                lines.append(f"Rows: {row_count:,}")
            lines.append("")

        lines.append("| Column | Type | Nulls | Example | Join |")
        lines.append("|--------|------|-------|---------|------|")

        cols = con.execute(
            "SELECT column_name, data_type, null_pct, example_value, join_hint "
            "FROM _columns WHERE table_name = ? ORDER BY rowid",
            [table_name],
        ).fetchall()

        for col_name, dtype, null_pct, example, join_hint in cols:
            null_str = f"{null_pct:.1f}%" if null_pct is not None else ""
            example_str = example if example else ""
            example_str = example_str.replace("|", "\\|")
            join_str = join_hint if join_hint else ""
            lines.append(f"| {col_name} | {dtype} | {null_str} | {example_str} | {join_str} |")

        lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Exported to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Build DuckDB from FEC campaign finance bulk data"
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path(DEFAULT_OUTPUT))
    parser.add_argument("--start-cycle", type=int, default=DEFAULT_START)
    parser.add_argument("--end-cycle", type=int, default=DEFAULT_END)
    parser.add_argument("--tables", nargs="+", help="Build only specific tables")
    args = parser.parse_args()

    cycles = list(range(args.start_cycle, args.end_cycle + 1, 2))
    t_start = time.time()

    print("=" * 60)
    print("FEC Campaign Finance Database Builder")
    print("=" * 60)
    print(f"  Cycles: {cycles[0]}-{cycles[-1]} ({len(cycles)} cycles)")

    # Filter tables if requested
    bulk_tables = BULK_TABLES
    standalone_tables = STANDALONE_TABLES
    if args.tables:
        requested = set(args.tables)
        bulk_tables = [t for t in BULK_TABLES if t[0] in requested]
        standalone_tables = [t for t in STANDALONE_TABLES if t[0] in requested]

    # ------------------------------------------------------------------
    # Step 1: Download headers
    # ------------------------------------------------------------------
    print(f"\n[1/8] Downloading header files")
    headers = download_headers(args.data_dir)
    print(f"  {len(headers)} header files loaded")

    # ------------------------------------------------------------------
    # Step 2: Download and load bulk tables
    # ------------------------------------------------------------------
    print(f"\n[2/8] Downloading and loading bulk tables")
    db_path = args.output
    db_path.unlink(missing_ok=True)
    con = duckdb.connect(str(db_path))
    built: set[str] = set()

    for table_name, zip_name, data_file, header_file in bulk_tables:
        if header_file not in headers:
            print(f"  Skipping {table_name} (no header file)")
            continue

        columns = headers[header_file]
        total_rows = 0
        print(f"\n  {table_name}:")

        for cycle in tqdm(cycles, desc=f"    cycles", unit="cycle", leave=False):
            cycle_dir = args.data_dir / str(cycle)
            cycle_dir.mkdir(parents=True, exist_ok=True)

            # Download zip (FEC uses 2-digit cycle suffix: cn24.zip, cm24.zip, etc.)
            suffix = str(cycle)[-2:]
            zip_url = f"{BASE_URL}/{cycle}/{zip_name}{suffix}.zip"
            zip_path = cycle_dir / f"{zip_name}{suffix}.zip"
            if not download_file(zip_url, zip_path, f"{zip_name}.zip {cycle}"):
                continue

            # Extract
            txt_path = cycle_dir / data_file
            if not txt_path.exists():
                txt_path = extract_zip(zip_path, data_file, cycle_dir)
            if not txt_path or not txt_path.exists():
                continue

            # Load into DuckDB
            try:
                n = load_bulk_table(con, table_name, txt_path, columns, cycle)
                total_rows += n
            except Exception as e:
                print(f"    WARNING: {table_name} cycle {cycle}: {e}")
            finally:
                # Delete extracted txt and zip to save disk space
                if txt_path and txt_path.exists():
                    txt_path.unlink()
                if zip_path.exists():
                    zip_path.unlink()

        if total_rows > 0:
            built.add(table_name)
            print(f"    -> {table_name}: {total_rows:,} rows")

    # ------------------------------------------------------------------
    # Step 3: Download and load standalone CSV tables
    # ------------------------------------------------------------------
    print(f"\n[3/8] Downloading standalone CSV tables")

    for table_name, url_template in standalone_tables:
        total_rows = 0
        print(f"\n  {table_name}:")

        for cycle in tqdm(cycles, desc=f"    cycles", unit="cycle", leave=False):
            cycle_dir = args.data_dir / str(cycle)
            cycle_dir.mkdir(parents=True, exist_ok=True)

            filename = url_template.format(cycle=cycle)
            csv_url = f"{BASE_URL}/{cycle}/{filename}"
            csv_path = cycle_dir / filename

            if not download_file(csv_url, csv_path, f"{filename}"):
                continue

            try:
                n = load_standalone_csv(con, table_name, csv_path, cycle)
                total_rows += n
            except Exception as e:
                print(f"    WARNING: {table_name} cycle {cycle}: {e}")
            finally:
                if csv_path.exists():
                    csv_path.unlink()

        if total_rows > 0:
            built.add(table_name)
            print(f"    -> {table_name}: {total_rows:,} rows")

    # ------------------------------------------------------------------
    # Step 4: Type casting
    # ------------------------------------------------------------------
    print(f"\n[4/8] Casting date and amount columns")
    for tbl in sorted(built):
        try:
            cast_columns(con, tbl)
            print(f"  Cast: {tbl}")
        except Exception as e:
            print(f"  WARNING: casting {tbl}: {e}")

    # ------------------------------------------------------------------
    # Step 5: Views
    # ------------------------------------------------------------------
    print(f"\n[5/8] Creating views")
    create_views(con, built)

    # ------------------------------------------------------------------
    # Step 6: Metadata
    # ------------------------------------------------------------------
    print(f"\n[6/8] Building metadata")
    build_metadata(con, built)
    run_validation(con, db_path)

    # ------------------------------------------------------------------
    # Step 7: Build _columns data dictionary
    # ------------------------------------------------------------------
    print(f"\n[7/8] Building _columns data dictionary")
    build_columns_table(con)
    col_count = con.execute("SELECT COUNT(*) FROM _columns").fetchone()[0]
    print(f"  {col_count} columns cataloged in _columns")

    # ------------------------------------------------------------------
    # Step 8: Export DICTIONARY.md
    # ------------------------------------------------------------------
    print(f"\n[8/8] Exporting DICTIONARY.md")
    export_dictionary(con, db_path.parent / "DICTIONARY.md")

    con.close()

    elapsed = time.time() - t_start
    print(f"\nDone in {int(elapsed // 60)}m {int(elapsed % 60)}s")
    print(f"Database: {db_path.resolve()}")


if __name__ == "__main__":
    main()
