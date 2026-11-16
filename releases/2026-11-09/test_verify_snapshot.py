"""Synthetic in-memory checks. Never opens a published or working FEC database."""
import json
import unittest
import duckdb
from verify_snapshot import scan_table


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect(':memory:')
        self.columns = [['name','VARCHAR'],['amount','DOUBLE'],['day','DATE'],['cycle','INTEGER']]
        self.con.execute('CREATE TABLE example(name VARCHAR,amount DOUBLE,day DATE,cycle INTEGER)')
        self.con.execute("INSERT INTO example VALUES ('a',1.25,'2026-01-01',2026), ('a',1.25,'2026-01-01',2026), (NULL,NULL,NULL,2026)")

    def tearDown(self):
        self.con.close()

    def test_decimal_strings_and_multiplicity(self):
        got, nulls = scan_table(self.con,'example',self.columns)
        value = got['2026']
        self.assertEqual(value['rows'],3)
        self.assertTrue(all(isinstance(x,str) and x.isdecimal() for x in value['sha256_limb_sums']))
        self.assertGreater(max(map(int,value['sha256_limb_sums'])),2**53)
        self.assertEqual(json.loads(json.dumps(value)),value)
        self.assertEqual(nulls,{'name':1,'amount':1,'day':1,'cycle':0})
        self.con.execute('CREATE TABLE distinct_rows AS SELECT DISTINCT * FROM example')
        self.assertNotEqual(got,scan_table(self.con,'distinct_rows',self.columns)[0])

    def test_row_order_independent(self):
        self.con.execute('CREATE TABLE reordered AS SELECT * FROM example ORDER BY name DESC NULLS FIRST')
        self.assertEqual(scan_table(self.con,'example',self.columns),scan_table(self.con,'reordered',self.columns))

    def test_value_mutation_detected(self):
        before = scan_table(self.con,'example',self.columns)[0]
        self.con.execute("UPDATE example SET amount=2.50 WHERE amount IS NOT NULL")
        self.assertNotEqual(before,scan_table(self.con,'example',self.columns)[0])

    def test_column_order_changes_fingerprint(self):
        self.con.execute('CREATE TABLE reordered_columns AS SELECT cycle,name,amount,day FROM example')
        order = [self.columns[-1]] + self.columns[:-1]
        self.assertNotEqual(scan_table(self.con,'example',self.columns)[0],scan_table(self.con,'reordered_columns',order)[0])



class SnapshotTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        from pathlib import Path
        from verify_snapshot import sha
        self.temp = tempfile.TemporaryDirectory(prefix='fec-synthetic-snapshot-')
        self.path = Path(self.temp.name)/'synthetic.duckdb'
        con = duckdb.connect(str(self.path))
        con.execute('CREATE TABLE sample(amount DOUBLE, cycle INTEGER)')
        con.execute('INSERT INTO sample VALUES (12.5,2026),(NULL,2026)')
        con.execute('CREATE TABLE _metadata(table_name VARCHAR,row_count BIGINT,column_count INTEGER,cycles_covered VARCHAR)')
        con.execute("INSERT INTO _metadata VALUES ('sample',2,2,'2026-2026')")
        con.execute('CREATE TABLE _columns(table_name VARCHAR,column_name VARCHAR,data_type VARCHAR,null_pct DOUBLE,example_value VARCHAR)')
        con.execute("INSERT INTO _columns VALUES ('sample','amount','DOUBLE',50.0,NULL),('sample','cycle','INTEGER',0.0,NULL)")
        columns = [['amount','DOUBLE'],['cycle','INTEGER']]
        fingerprints,nulls = scan_table(con,'sample',columns)
        con.close()
        self.lock = {'database':{'bytes':self.path.stat().st_size,'sha256':sha(self.path)},
                     'tables':{'sample':{'rows':2,'columns':columns,'row_fingerprints':fingerprints,
                                        'dictionary_nulls':{'amount':{'null_count':1,'null_pct':50.0},'cycle':{'null_count':0,'null_pct':0.0}}}},
                     'views':{},'dictionary_schema':[['sample','amount','DOUBLE'],['sample','cycle','INTEGER']],
                     'dictionary_entries':2,'unavailable_view_statistics':[]}

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_readonly_snapshot_verification(self):
        from verify_snapshot import verify
        before = self.path.read_bytes()
        self.assertEqual(verify(self.path,self.lock)['status'],'snapshot_verified')
        self.assertEqual(before,self.path.read_bytes())

    def test_wrong_byte_hash_rejected(self):
        from verify_snapshot import verify
        self.lock['database']['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
            verify(self.path,self.lock)

    def test_wal_refused_before_database_open(self):
        from verify_snapshot import verify
        from pathlib import Path
        Path(str(self.path)+'.wal').write_bytes(b'not an actual WAL')
        with self.assertRaisesRegex(ValueError,'Unexpected WAL'):
            verify(self.path,self.lock)

    def test_wrong_fingerprint_rejected(self):
        from verify_snapshot import verify
        self.lock['tables']['sample']['row_fingerprints']['2026']['sha256_limb_sums'][0] = '0'
        with self.assertRaisesRegex(ValueError,'fingerprint mismatch'):
            verify(self.path,self.lock)

if __name__ == '__main__':
    unittest.main()
