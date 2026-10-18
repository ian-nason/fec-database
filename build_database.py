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
import os
import io
import re
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import json
import requests
from tqdm import tqdm


def tune_session(con, db_path, memory_limit: str = "512MiB", threads: int = 1) -> None:
    """Use one thread and a modest buffer pool; bound local spill storage.

    Override with DATAPOND_MEMORY_LIMIT / DATAPOND_THREADS / DATAPOND_MAX_TEMP_SIZE.
    Spills go to <db>.tmp. Process RAM can exceed DuckDB's buffer-pool limit.
    """
    con.execute("SET memory_limit = ?", [os.environ.get('DATAPOND_MEMORY_LIMIT', memory_limit)])
    con.execute(f"SET threads = {int(os.environ.get('DATAPOND_THREADS', threads))}")
    con.execute("SET temp_directory = ?", [str(Path(db_path).resolve())+'.tmp'])
    con.execute("SET max_temp_directory_size = ?", [os.environ.get("DATAPOND_MAX_TEMP_SIZE", "1GiB")])
    con.execute("SET preserve_insertion_order = false")


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

# Columns that contain dates (MMDDYYYY in bulk files, MM/DD/YYYY in
# standalone CSVs — cast_columns tries both formats)
DATE_COLUMNS = {
    "transaction_dt", "receipt_dt",
    "disb_dt", "receipt_date", "dissemination_dt",
    "communication_dt", "exp_date", "receipt_dat",
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
    "exp_amo", "agg_amo",
    "reported_disbursement_amount", "calculated_candidate_share",
}

YEAR_COLUMNS = {"cand_election_yr"}


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------


def _remote_identity(url: str) -> dict:
    """ETag / Last-Modified / Content-Length of ``url`` (HEAD); {} on failure."""
    try:
        r = requests.head(url, timeout=60, allow_redirects=True)
        r.raise_for_status()
    except requests.RequestException:
        return {}
    h = r.headers
    out = {}
    if h.get("etag"):
        out["etag"] = h["etag"].strip('"').replace("W/", "")
    if h.get("last-modified"):
        out["last_modified"] = h["last-modified"]
    if h.get("content-length"):
        out["size"] = int(h["content-length"])
    return out


def _meta_path(dest: Path) -> Path:
    return dest.with_name(dest.name + ".meta.json")


def cached_is_current(url: str, dest: Path) -> bool:
    """True when the cached file's recorded identity matches what the server reports now."""
    if not dest.exists() or dest.stat().st_size == 0:
        return False
    try:
        local = json.loads(_meta_path(dest).read_text())
    except (OSError, ValueError):
        return False
    remote = _remote_identity(url)
    for key in ("etag", "last_modified", "size"):
        if local.get(key) and remote.get(key):
            return local[key] == remote[key]
    return False


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress. Returns True on success (or when the cached copy is current).

    Refresh vs resume: an existing file is reused only when its recorded ETag / Last-Modified /
    size (``<file>.meta.json``) equals what the FEC server reports now, so a rebuild picks up
    re-issued bulk files; ``DATAPOND_REFRESH=skip`` reuses whatever is on disk (offline).
    The download goes to ``<file>.part`` and replaces the destination atomically.
    """
    if dest.exists() and dest.stat().st_size > 0:
        if os.environ.get("DATAPOND_REFRESH") == "skip" or cached_is_current(url, dest):
            return True
        print(f"    {desc or dest.name}: cached copy differs from the source or has no record; re-downloading")

    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    if part.exists():raise FileExistsError("Existing partial download preserved: "+str(part))
    for attempt in range(3):
        try:
            r = requests.get(url, stream=True, timeout=60)
            if r.status_code == 404:
                return False
            r.raise_for_status()

            total = int(r.headers.get("content-length", 0))
            identity = {"url": url}
            if r.headers.get("etag"):
                identity["etag"] = r.headers["etag"].strip('"').replace("W/", "")
            if r.headers.get("last-modified"):
                identity["last_modified"] = r.headers["last-modified"]
            received = 0
            with open(part, "wb") as f:
                with tqdm(
                    total=total, unit="B", unit_scale=True,
                    desc=f"    {desc or dest.name}", leave=False,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        f.write(chunk)
                        received += len(chunk)
                        pbar.update(len(chunk))
            # A dropped connection can end iter_content without raising;
            # an incomplete zip then fails extraction (or worse, a truncated
            # .txt silently loads partial rows). Verify length and retry.
            if total and received != total:
                raise IOError(f"truncated download: {received}/{total} bytes")
            identity["size"] = received
            os.replace(part, dest)
            _meta_path(dest).write_text(json.dumps(identity, indent=1))
            return True
        except Exception as e:
            print(f"    WARNING: download attempt {attempt + 1}/3 for {url}: {e}")
            part.unlink(missing_ok=True)
    raise RuntimeError(f'Download failed after three attempts: {url}')


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
                # Stream the decompression: src.read() would hold the whole
                # member (10GB+ for indiv files) in RAM and can take down
                # the machine before the OOM killer reacts.
                with zf.open(match) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024 * 16)
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


def bulk_schema(columns):
    from fec_bulk import ident
    if not columns or len(set(c.lower() for c in columns))!=len(columns) or any(not c or c.lower()=='cycle' for c in columns):
        raise ValueError('Invalid, duplicate or reserved bulk column')
    def kind(c):
        c=c.lower()
        if c in DATE_COLUMNS or c.endswith(('_dt','_date')):return 'DATE'
        if c in AMOUNT_COLUMNS or c.endswith('_amt'):return 'DOUBLE'
        if c in YEAR_COLUMNS:return 'INTEGER'
        return 'VARCHAR'
    return [[c,kind(c)] for c in columns]+[['cycle','INTEGER']]


def load_bulk_table(con, table_name, data_file, columns, cycle, *, member=None):
    """Stream an exact ZIP member or text file in typed 32 MiB/100k-row batches.

    Raises on ambiguity, CRC failure or a repeated/partial cycle. Completed
    batches and original failed bytes remain available for manual inspection.
    """
    import fec_bulk as bulk
    import contextlib,csv,hashlib
    data_file=Path(data_file);schema=bulk_schema(columns)
    if not con.execute('SELECT count(*) FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema=current_schema() AND lower(table_name)=lower(?)',[table_name]).fetchone()[0]:
        bulk.make_tables(con,{table_name:schema})
    actual=[[x[0],x[1]] for x in con.execute('DESCRIBE '+bulk.ident(table_name)).fetchall()]
    if actual!=schema:raise ValueError('Bulk schema changed: '+table_name)
    receipt=data_file.with_name(data_file.name+'.load.json')
    quarantine=data_file.with_name(data_file.name+'.invalid-utf8.jsonl')
    if receipt.exists() or quarantine.exists():raise FileExistsError('Prior source evidence exists; inspect before retrying')
    chunk=data_file.with_name(data_file.name+'.batch.csv')
    digest=hashlib.sha256()
    before=data_file.stat()
    with data_file.open('rb') as raw:
        for block in iter(lambda:raw.read(1024**2),b''):digest.update(block)
    @contextlib.contextmanager
    def open_source():
        with contextlib.ExitStack() as stack:
            details={}
            if member:
                archive=stack.enter_context(zipfile.ZipFile(data_file))
                matches=[x for x in archive.infolist() if x.filename.lower()==member.lower()]
                if len(matches)!=1:raise ValueError('Exact ZIP root member missing or ambiguous')
                selected=matches[0];raw=archive.open(selected)
                details={'member':selected.filename,'crc32':f'{selected.CRC:08x}','uncompressed_bytes':selected.file_size}
            else:raw=data_file.open('rb')
            source=stack.enter_context(io.TextIOWrapper(raw,encoding='utf-8-sig',errors='surrogateescape',newline=''))
            yield source,details
    with open_source() as (source,_):preflight=bulk.preflight_records(source,columns,table_name,cycle)
    with open_source() as (source,details):
        rejected=lambda first,last,value:bulk.quarantine_record(quarantine,table_name,cycle,first,last,value)
        result=bulk.load_records(con,table_name,cycle,source,columns,schema,chunk,'|',quarantine=rejected)
        if (result['logical_records_read'],result['blank_lines_ignored'],result['short_records_padded'],result['trailing_empty_padding_records'])!=(preflight['rows'],preflight['blank'],preflight['padded'],preflight['trimmed']):raise ValueError('Preflight/load record counts differ')
        if result['source_framing']!=preflight['source_framing'] or result['invalid_utf8_quarantined']['records']!=preflight['invalid_utf8']['records']:raise ValueError('Preflight/load framing differs')
        if member:details['crc_verified']=True
    result['preflight']=preflight
    if (quarantine.stat().st_size if quarantine.exists() else 0)!=preflight['quarantine_bytes']:raise ValueError('Preflight/load quarantine bytes differ')
    result['quarantine_file']=quarantine.name if quarantine.exists() else None
    after=data_file.stat()
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('Bulk source changed during load')
    result.update(status='loaded',source_sha256=digest.hexdigest(),source_bytes=before.st_size,table=table_name,cycle=cycle,**details)
    with receipt.open('x') as output:json.dump(result,output,indent=2);output.flush();os.fsync(output.fileno())
    return result['logical_records_read']


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


def dedupe_ie_amendments(con: duckdb.DuckDBPyConnection) -> int:
    """Keep only the latest version of each independent-expenditure filing.

    Amendments chain via prev_file_num -> file_num within a cycle; a filing
    whose file_num appears as another filing's prev_file_num has been
    superseded. Without this, N/A1/A2/... versions all coexist and totals
    are inflated several-fold (July 2026 audit).
    """
    before = con.execute(
        "SELECT COUNT(*) FROM independent_expenditures"
    ).fetchone()[0]
    con.execute("""
        DELETE FROM independent_expenditures ie
        WHERE ie.file_num IS NOT NULL AND ie.file_num <> ''
          AND EXISTS (
            SELECT 1 FROM independent_expenditures newer
            WHERE newer.cycle = ie.cycle
              AND newer.prev_file_num = ie.file_num
              AND (newer.file_num IS NULL OR newer.file_num <> ie.file_num)
          )
    """)
    after = con.execute(
        "SELECT COUNT(*) FROM independent_expenditures"
    ).fetchone()[0]
    return before - after


def cast_columns(con: duckdb.DuckDBPyConnection, table_name: str):
    """Cast date and amount columns to proper types after loading."""
    cols = {
        r[0].lower(): r[0]
        for r in con.execute(f"DESCRIBE {table_name}").fetchall()
    }

    casts = []
    for col_lower, col_actual in cols.items():
        if (
            col_lower in DATE_COLUMNS
            or col_lower.endswith("_dt")
            or col_lower.endswith("_date")
        ):
            # FEC date formats vary by file family: MMDDYYYY in bulk files,
            # YYYYMMDD in CommunicationCosts, DD-MON-YY in independent
            # expenditures / electioneering, MM/DD/YYYY in some older CSVs.
            # Ambiguity is safe: an 8-digit value valid in one format is
            # invalid in the other (month > 12 / year sanity).
            casts.append(
                f'COALESCE(TRY_STRPTIME("{col_actual}", \'%m%d%Y\'), '
                f'TRY_STRPTIME("{col_actual}", \'%Y%m%d\'), '
                f'TRY_STRPTIME("{col_actual}", \'%m/%d/%Y\'), '
                f'TRY_STRPTIME("{col_actual}", \'%d-%b-%y\'))::DATE '
                f'AS "{col_actual}"'
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

# Money-summing rules baked into every view (July 2026 audit):
# - Exclude TRANSACTION_TP = '24T' (conduit/earmark rows: ActBlue and WinRed
#   report each earmarked donation once as 24T and the recipient committee
#   reports it again as 15E — summing both double counts 14-22% of every
#   cycle since 2018; MEMO_CD does NOT flag these).
# - Exclude memo-only rows (MEMO_CD = 'X').
# - Net out refunds: 20Y/21Y/22Y rows are REFUNDS stored as positive
#   amounts, so they are subtracted, not filtered by sign.
VIEWS = {
    "v_candidate_totals": {
        "deps": {"candidates", "individual_contributions"},
        "sql": """
            CREATE OR REPLACE VIEW v_candidate_totals AS
            -- Receipts aggregated per principal campaign committee (PCC).
            -- A PCC can be shared by several candidate records (e.g. Biden
            -- and Harris 2024), so candidate identities are aggregated into
            -- one row per committee instead of fanned out; summing this view
            -- never double counts a committee's receipts.
            WITH per_cmte AS (
                SELECT
                    cycle,
                    CMTE_ID,
                    COUNT(*) FILTER (
                        WHERE TRANSACTION_TP NOT IN ('20Y', '21Y', '22Y')
                    ) AS num_contributions,
                    SUM(CASE WHEN TRANSACTION_TP IN ('20Y', '21Y', '22Y')
                             THEN -TRANSACTION_AMT
                             ELSE TRANSACTION_AMT END) AS net_individual
                FROM individual_contributions
                WHERE TRANSACTION_TP <> '24T'
                  AND (MEMO_CD IS NULL OR MEMO_CD <> 'X')
                  AND TRANSACTION_AMT IS NOT NULL
                GROUP BY 1, 2
            )
            SELECT
                p.cycle,
                p.CMTE_ID,
                STRING_AGG(DISTINCT c.CAND_ID, '; ') AS cand_ids,
                STRING_AGG(DISTINCT c.CAND_NAME, '; ') AS candidate_names,
                ANY_VALUE(c.CAND_PTY_AFFILIATION) AS party,
                ANY_VALUE(c.CAND_OFFICE) AS office,
                ANY_VALUE(c.CAND_OFFICE_ST) AS state,
                p.num_contributions,
                p.net_individual
            FROM per_cmte p
            JOIN candidates c
              ON c.CAND_PCC = p.CMTE_ID AND c.cycle = p.cycle
            GROUP BY p.cycle, p.CMTE_ID, p.num_contributions, p.net_individual
        """,
    },
    "v_top_donors": {
        "deps": {"individual_contributions"},
        "sql": """
            CREATE OR REPLACE VIEW v_top_donors AS
            -- Donor identity is by raw (NAME, EMPLOYER, OCCUPATION, STATE)
            -- string match; the same person appears under spelling variants.
            SELECT
                NAME, EMPLOYER, OCCUPATION, STATE,
                COUNT(*) FILTER (
                    WHERE TRANSACTION_TP NOT IN ('20Y', '21Y', '22Y')
                ) AS num_contributions,
                SUM(CASE WHEN TRANSACTION_TP IN ('20Y', '21Y', '22Y')
                         THEN -TRANSACTION_AMT
                         ELSE TRANSACTION_AMT END) AS net_donated,
                MIN(cycle) AS first_cycle,
                MAX(cycle) AS last_cycle,
                COUNT(DISTINCT CMTE_ID) AS num_committees
            FROM individual_contributions
            WHERE TRANSACTION_TP <> '24T'
              AND (MEMO_CD IS NULL OR MEMO_CD <> 'X')
              AND TRANSACTION_AMT IS NOT NULL
            GROUP BY NAME, EMPLOYER, OCCUPATION, STATE
        """,
    },
    "v_pac_to_candidate": {
        "deps": {"committee_contributions", "committees", "candidates"},
        "sql": """
            CREATE OR REPLACE VIEW v_pac_to_candidate AS
            -- Direct contributions only: 24K (contribution to candidate
            -- committee) and 24Z (in-kind). Independent expenditures
            -- (24A = AGAINST the candidate, 24E = for) are deliberately
            -- excluded — counting attack ads as "PAC support" was the
            -- worst defect of the previous version of this view.
            SELECT
                cm.CMTE_NM AS pac_name,
                cm.CONNECTED_ORG_NM AS connected_org,
                cn.CAND_NAME AS candidate_name,
                cn.CAND_PTY_AFFILIATION AS candidate_party,
                cn.CAND_OFFICE AS office,
                cn.CAND_OFFICE_ST AS state,
                cc.TRANSACTION_TP AS transaction_type,
                cc.TRANSACTION_AMT AS amount,
                cc.TRANSACTION_DT AS date,
                cc.cycle
            FROM committee_contributions cc
            JOIN committees cm ON cc.CMTE_ID = cm.CMTE_ID AND cc.cycle = cm.cycle
            JOIN candidates cn ON cc.CAND_ID = cn.CAND_ID AND cc.cycle = cn.cycle
            WHERE cc.TRANSACTION_TP IN ('24K', '24Z')
              AND (cc.MEMO_CD IS NULL OR cc.MEMO_CD <> 'X')
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
            WHERE TRANSACTION_DT IS NOT NULL
              AND TRANSACTION_AMT > 0
              AND TRANSACTION_TP <> '24T'
              AND (MEMO_CD IS NULL OR MEMO_CD <> 'X')
              AND TRANSACTION_TP NOT IN ('20Y', '21Y', '22Y')
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

    # ---- Regression guards from the July 2026 audit (audit/2026-07) ----
    print("\n  Audit regression checks:")
    failures = 0

    def check(name, ok, detail=""):
        nonlocal failures
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
        if not ok:
            failures += 1

    def q(sql):
        return con.execute(sql).fetchone()[0]

    # Every cycle must be present: download_file() failures are skipped with
    # `continue`, which would silently drop a cycle.
    try:
        n = q("SELECT COUNT(DISTINCT cycle) FROM individual_contributions")
        check("individual_contributions covers 12 cycles (2004-2026)", n == 12, f"{n} cycles")
    except Exception as e:
        check("individual_contributions covers 12 cycles (2004-2026)", False, str(e)[:80])
    # Standalone-table dates were 100% NULL before the audit.
    for tbl, col in [
        ("independent_expenditures", "exp_date"),
        ("communication_costs", "TRANSACTION_DT"),
        ("electioneering_communications", "COMMUNICATION_DATE"),
    ]:
        try:
            tot = q(f"SELECT COUNT(*) FROM {tbl}")
            nn = q(f'SELECT COUNT(*) FROM {tbl} WHERE "{col}" IS NOT NULL')
            share = nn / tot if tot else 0
            check(f"{tbl}.{col} > 85% non-null", share > 0.85, f"{share:.1%} of {tot:,}")
        except Exception as e:
            check(f"{tbl}.{col} > 85% non-null", False, str(e)[:80])
    try:
        t = q("""SELECT data_type FROM information_schema.columns
                 WHERE table_name = 'electioneering_communications'
                 AND column_name = 'CALCULATED_CANDIDATE_SHARE'""")
        check("electioneering_communications.CALCULATED_CANDIDATE_SHARE is DOUBLE", t == "DOUBLE", str(t))
    except Exception as e:
        check("electioneering_communications.CALCULATED_CANDIDATE_SHARE is DOUBLE", False, str(e)[:80])
    try:
        n = q("""SELECT COUNT(*) FROM (SELECT cycle, CMTE_ID FROM v_candidate_totals
                 GROUP BY 1, 2 HAVING COUNT(*) > 1)""")
        check("v_candidate_totals has one row per (cycle, committee)", n == 0, f"{n} duplicates")
    except Exception as e:
        check("v_candidate_totals has one row per (cycle, committee)", False, str(e)[:80])
    try:
        types = {r[0] for r in con.execute(
            "SELECT DISTINCT transaction_type FROM v_pac_to_candidate").fetchall()}
        check("v_pac_to_candidate uses only 24K/24Z", types <= {"24K", "24Z"}, ",".join(sorted(map(str, types))))
    except Exception as e:
        check("v_pac_to_candidate uses only 24K/24Z", False, str(e)[:80])
    try:
        n = q("SELECT COUNT(*) FROM individual_contributions WHERE TRANSACTION_TP = '24T'")
        check("conduit (24T) rows are excluded from v_candidate_totals",
              q("SELECT COUNT(*) FROM v_candidate_totals") > 0, f"{n:,} conduit rows in raw table")
    except Exception as e:
        check("conduit (24T) rows are excluded from v_candidate_totals", False, str(e)[:80])

    print(f"\n  Audit checks: {failures} failure(s)")
    return failures


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
    if args.output.exists() or Path(str(args.output)+'.wal').exists() or args.output.with_suffix('.manifest.json').exists():
        parser.error('Output or recovery evidence exists; choose a fresh --output path. Existing output databases are never overwritten.')
    if args.start_cycle>args.end_cycle or args.start_cycle%2 or args.end_cycle%2:
        parser.error('Cycles must be even and start must not exceed end.')
    if args.tables and not set(args.tables).issubset({t[0] for t in BULK_TABLES+STANDALONE_TABLES}):
        parser.error('Unknown table requested.')

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

    # Existing receipts and partial diagnostics belong to earlier attempts.
    for cycle in cycles:
        names=[f'{prefix}{str(cycle)[-2:]}.zip' for _,prefix,_,_ in bulk_tables]
        names += [template.format(cycle=cycle) for _,template in standalone_tables]
        for name in names:
            for suffix in ['.load.json','.invalid-utf8.jsonl','.batch.csv','.part']:
                evidence=args.data_dir/str(cycle)/(name+suffix)
                if evidence.exists():parser.error('Prior source evidence exists; choose a fresh --data-dir: '+str(evidence))

    manifest_path=args.output.with_suffix('.manifest.json')
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
    manifest={'status':'incomplete','started_utc':datetime.now(timezone.utc).isoformat(),'sources':[]}
    with manifest_path.open('x') as output:json.dump(manifest,output,indent=2)

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
    if db_path.exists() or Path(str(db_path)+'.wal').exists():raise FileExistsError("Output appeared during source preparation; preserved unchanged")
    con = duckdb.connect(str(db_path))
    tune_session(con, db_path)
    built: set[str] = set()

    for table_name, zip_name, data_file, header_file in bulk_tables:
        if header_file not in headers:
            raise RuntimeError(f'Missing required header: {header_file}')

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
                raise RuntimeError(f'Required bulk source unavailable: {zip_url}')

            # Stream the exact root member; never materialize the full text file.
            n = load_bulk_table(con, table_name, zip_path, columns, cycle, member=data_file)
            total_rows += n
            manifest['sources'].append({'table':table_name,'cycle':cycle,'rows':n,'receipt':str(zip_path)+'.load.json'})
            manifest_path.write_text(json.dumps(manifest,indent=2))
            zip_path.unlink()  # Only after EOF/CRC, row accounting and durable source receipt.

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
                if cycle < 2010:
                    manifest['sources'].append({'table':table_name,'cycle':cycle,'status':'expected_absent'})
                    continue
                raise RuntimeError(f'Required CSV source unavailable: {csv_url}')

            n = load_standalone_csv(con, table_name, csv_path, cycle)
            total_rows += n
            manifest['sources'].append({'table':table_name,'cycle':cycle,'rows':n})
            manifest_path.write_text(json.dumps(manifest,indent=2))
            csv_path.unlink()

        if total_rows > 0:
            built.add(table_name)
            print(f"    -> {table_name}: {total_rows:,} rows")

            # null_padding + ignore_errors on ragged CSVs can invent
            # anonymous columnNNN columns holding spillover junk; drop them
            cols = [r[0] for r in con.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
            ).fetchall()]
            junk = [c for c in cols if re.fullmatch(r"column\d+", c)]
            for c in junk:
                con.execute(f'ALTER TABLE {table_name} DROP COLUMN "{c}"')
            if junk:
                print(f"    -> dropped {len(junk)} junk column(s) from {table_name}")

            if table_name == "independent_expenditures":
                n_amend = dedupe_ie_amendments(con)
                print(f"    -> removed {n_amend:,} superseded amendment rows")

    # ------------------------------------------------------------------
    # Step 4: Type casting
    # ------------------------------------------------------------------
    print(f"\n[4/8] Casting date and amount columns")
    for tbl in sorted(built):
        if tbl not in {t[0] for t in BULK_TABLES}:
            cast_columns(con, tbl)
        print(f"  Typed: {tbl}")

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
    failures = run_validation(con, db_path)

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
    if failures:
        print(f"\nBUILD FAILED: {failures} audit check(s) failed -- do not publish this file")
        sys.exit(1)
    manifest.update(status='validated',finished_utc=datetime.now(timezone.utc).isoformat())
    manifest_path.write_text(json.dumps(manifest,indent=2))


if __name__ == "__main__":
    main()
