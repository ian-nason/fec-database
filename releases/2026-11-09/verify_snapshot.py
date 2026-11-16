#!/usr/bin/env python3
"""Read-only byte, schema, catalogue and complete typed-multiset snapshot verifier."""
import argparse
import hashlib
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(4 * 1024**2), b''):
            h.update(part)
    return h.hexdigest()


def qi(name):
    return '"' + name.replace('"', '""') + '"'


def fingerprint_query(table, columns):
    sums = ','.join("sum(('0x'||substr(d," + str(1+16*i) + ",16))::UBIGINT::HUGEINT)" for i in range(4))
    nulls = ','.join('count(*) FILTER (WHERE '+qi(c[0])+' IS NULL)' for c in columns)
    # t is the entire ordered typed table row, including cycle. Do not reorder fields.
    return 'WITH r AS (SELECT t.*, sha256(to_json(t)) d FROM '+qi(table)+' t) SELECT cycle,count(*),'+sums+','+nulls+' FROM r GROUP BY cycle ORDER BY cycle'


def scan_table(con, table, columns):
    rows = con.execute(fingerprint_query(table, columns)).fetchall()
    return ({str(r[0]): {'rows':r[1], 'sha256_limb_sums':[str(x) for x in r[2:6]]} for r in rows},
            {c[0]:sum(r[6+i] for r in rows) for i,c in enumerate(columns)})


def verify(db, lock, memory='1GiB'):
    import duckdb
    need(duckdb.__version__ == '1.5.5', 'Install exactly duckdb==1.5.5')
    db = Path(db).resolve()
    need(db.is_file(), 'Snapshot file does not exist')
    need(not Path(str(db)+'.wal').exists(), 'Unexpected WAL; use a closed, checkpointed snapshot')
    before = db.stat()
    need(before.st_size == lock['database']['bytes'], 'Database byte size mismatch')
    need(sha(db) == lock['database']['sha256'], 'Database SHA-256 mismatch')
    con = duckdb.connect(str(db), read_only=True, config={'threads':'1','memory_limit':memory,'max_temp_directory_size':'0B','enable_external_access':'false'})
    try:
        actual = {r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' AND table_type='BASE TABLE'").fetchall()}
        need(actual == set(lock['tables']) | {'_metadata','_columns'}, 'Base-table set mismatch')
        views = dict(con.execute("SELECT view_name,sql FROM duckdb_views() WHERE schema_name='main' AND NOT internal").fetchall())
        need(views == lock['views'], 'View definitions mismatch')
        catalog = sorted(con.execute('SELECT table_name,column_name,data_type FROM _columns').fetchall())
        need(catalog == sorted(map(tuple,lock['dictionary_schema'])), 'Dictionary schema mismatch')
        need(len(catalog) == len(set(catalog)) == lock['dictionary_entries'], 'Duplicate dictionary entries')
        need(con.execute('SELECT count(*),count(DISTINCT table_name) FROM _metadata').fetchone() == (len(lock['tables']),len(lock['tables'])), 'Metadata table inventory mismatch')
        for table, expected in lock['tables'].items():
            columns = [[r[0],r[1]] for r in con.execute('DESCRIBE '+qi(table)).fetchall()]
            need(columns == expected['columns'], 'Schema/order mismatch: '+table)
            got, nulls = scan_table(con, table, columns)
            need(got == expected['row_fingerprints'], 'Complete typed-row fingerprint mismatch: '+table)
            n = sum(x['rows'] for x in got.values())
            need(n == expected['rows'], 'Row-count mismatch: '+table)
            meta = con.execute('SELECT row_count,column_count,cycles_covered FROM _metadata WHERE table_name=?',[table]).fetchall()
            need(meta == [(n,len(columns),min(got)+'-'+max(got))], 'Metadata mismatch: '+table)
            for column, count in nulls.items():
                want = expected['dictionary_nulls'][column]
                pct = con.execute('SELECT ROUND(100.0 * ? / ?, 1)',[count,n]).fetchone()[0]
                need(count == want['null_count'] and pct == want['null_pct'], 'Null statistics mismatch: '+table+'.'+column)
                need(con.execute('SELECT null_pct FROM _columns WHERE table_name=? AND column_name=?',[table,column]).fetchall() == [(pct,)], 'Embedded dictionary null percentage mismatch')
            print(json.dumps({'table':table,'rows':n,'status':'matched'}), flush=True)
        for view in lock['unavailable_view_statistics']:
            need(con.execute('SELECT count(*) FROM _columns WHERE table_name=? AND (null_pct IS NOT NULL OR example_value IS NOT NULL)',[view]).fetchone()[0] == 0, 'Unavailable view statistics/examples present')
    finally:
        con.close()
    after = db.stat()
    need((before.st_ino,before.st_size,before.st_mtime_ns) == (after.st_ino,after.st_size,after.st_mtime_ns), 'Snapshot changed during verification')
    need(not Path(str(db)+'.wal').exists(), 'Unexpected WAL appeared')
    return {'status':'snapshot_verified','database_sha256':lock['database']['sha256'],'rows':sum(x['rows'] for x in lock['tables'].values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database',type=Path)
    parser.add_argument('--source-lock',type=Path,default=Path(__file__).with_name('source-lock.json'))
    parser.add_argument('--memory-limit',default='1GiB')
    args = parser.parse_args()
    print(json.dumps(verify(args.database,json.loads(args.source_lock.read_text()),args.memory_limit)),flush=True)

if __name__ == '__main__':
    main()
