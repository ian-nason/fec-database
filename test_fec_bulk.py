import base64,csv,io,json,pathlib,sys,tempfile,unittest,zipfile
from unittest.mock import patch
import duckdb
import build_database as build
import fec_bulk as bulk

class BulkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.temp.name)
        self.db=self.base/'fixture.duckdb';self.con=duckdb.connect(str(self.db),config={'memory_limit':'128MiB','threads':'1'})
        self.columns=['name','TRANSACTION_DT','TRANSACTION_AMT']
    def tearDown(self):self.con.close();self.temp.cleanup()
    def archive(self,name,raw,member='data.txt'):
        path=self.base/name
        with zipfile.ZipFile(path,'w',zipfile.ZIP_STORED) as z:z.writestr(member,raw)
        return path
    def load(self,path,cycle=2026,**kw):return build.load_bulk_table(self.con,'sample',path,self.columns,cycle,**kw)
    def test_literal_quotes_preserved_and_values_typed(self):
        path=self.archive('source.zip',b'"VAL" VALMA PAUL|01012026|12.5\n"ordinary"|20260102|-1|\n')
        self.assertEqual(self.load(path,member='data.txt'),2)
        rows=self.con.execute('SELECT name,cast(TRANSACTION_DT as varchar),TRANSACTION_AMT FROM sample ORDER BY TRANSACTION_AMT').fetchall()
        self.assertEqual(rows,[('ordinary','2026-01-02',-1.),('"VAL" VALMA PAUL','2026-01-01',12.5)])
        receipt=json.loads(path.with_name(path.name+'.load.json').read_text())
        self.assertTrue(receipt['crc_verified']);self.assertEqual(receipt['source_framing']['physical_lines'],2)
        self.assertEqual(receipt['literal_quote_recovery']['records'],1)
        self.assertFalse((self.base/'data.txt').exists())
    def test_invalid_utf8_exact_bytes_quarantined(self):
        path=self.archive('source.zip',b'good|01012026|1\nbad\xbf|01022026|2\nafter|01032026|3\n')
        self.assertEqual(self.load(path,member='data.txt'),2)
        item=json.loads(path.with_name(path.name+'.invalid-utf8.jsonl').read_text())
        self.assertEqual(base64.b64decode(item['raw_base64']),b'bad\xbf|01022026|2\n')
        self.assertEqual(item['first_physical_line'],2)
    def test_quarantine_byte_cap_fails_before_any_insert(self):
        raw=b'bad\xbf|01022026|2\n';path=self.archive('too-many-invalid.zip',raw*2)
        cap=len(bulk.quarantine_bytes('sample',2026,1,1,raw))+1
        with patch.object(bulk,'MAX_QUARANTINE',cap):
            with self.assertRaisesRegex(RuntimeError,'during preflight'):self.load(path,member='data.txt')
        self.assertEqual(self.con.execute('SELECT count(*) FROM sample').fetchone()[0],0)
        self.assertFalse(path.with_name(path.name+'.invalid-utf8.jsonl').exists())
    def test_crc_corruption_fails_and_retains_source(self):
        path=self.archive('bad.zip',b'good|01012026|1\n');raw=path.read_bytes();path.write_bytes(raw.replace(b'good',b'evil',1))
        with self.assertRaises(zipfile.BadZipFile):self.load(path,member='data.txt')
        self.assertTrue(path.exists());self.assertFalse(path.with_name(path.name+'.load.json').exists())
    def test_exact_root_member_required(self):
        path=self.archive('nested.zip',b'good|01012026|1\n',member='nested/data.txt')
        with self.assertRaisesRegex(ValueError,'root member'):self.load(path,member='data.txt')
    def test_repeated_cycle_refused_before_insert(self):
        first=self.archive('a.zip',b'old|01012026|1\n');second=self.archive('b.zip',b'new|01012026|2\n')
        self.load(first,member='data.txt')
        with self.assertRaisesRegex(ValueError,'already contains'):self.load(second,member='data.txt')
        self.assertEqual(self.con.execute('SELECT name FROM sample').fetchall(),[('old',)])
    def test_two_cycles_keep_schema_and_previous_rows(self):
        self.load(self.archive('a.zip',b'old|01012024|1\n'),2024,member='data.txt')
        self.load(self.archive('b.zip',b'new|01012026|2\n'),2026,member='data.txt')
        self.assertEqual(self.con.execute('SELECT cycle,count(*) FROM sample GROUP BY cycle ORDER BY cycle').fetchall(),[(2024,1),(2026,1)])
    def test_bounded_batch_failure_preserves_prior_cycles(self):
        schema=build.bulk_schema(self.columns);bulk.make_tables(self.con,{'sample':schema})
        self.con.execute("INSERT INTO sample VALUES ('old','2024-01-01',1,2024)")
        chunk=self.base/'chunk'
        with self.assertRaisesRegex(ValueError,'Extra nonempty'):
            bulk.load_records(self.con,'sample',2026,io.StringIO('a|01012026|1\nb|01012026|2\nbad|01012026|3|extra\n'),self.columns,schema,chunk,'|',max_rows=1)
        self.assertEqual(self.con.execute('SELECT name FROM sample WHERE cycle=2024').fetchall(),[('old',)])
        self.assertTrue(chunk.exists())
    def test_byte_limit_and_null_conversion_accounting(self):
        schema=build.bulk_schema(self.columns);bulk.make_tables(self.con,{'sample':schema})
        result=bulk.load_records(self.con,'sample',2026,io.StringIO('a|bad|bad\nb||\n'),self.columns,schema,self.base/'chunk','|',max_bytes=25)
        self.assertEqual(result['batches'],2);self.assertLessEqual(result['peak_chunk_bytes'],25)
        self.assertEqual(result['conversion_quality']['TRANSACTION_DT']['unparsed_nonblank'],1)
    def test_unresolved_multiline_is_not_publishable(self):
        path=self.archive('multiline.zip',b'"first\nsecond"|01012026|1\n')
        with self.assertRaisesRegex(ValueError,'Unresolved multiline'):self.load(path,member='data.txt')
        self.assertFalse(path.with_name(path.name+'.load.json').exists());self.assertTrue(path.exists())
        self.assertEqual(self.con.execute('SELECT count(*) FROM sample').fetchone()[0],0)
    def test_quote_merge_recovers_each_independently_anchored_record(self):
        def row(value,subid):
            values=['C00401224','N','30G','','202012049352730694','24T','IND','FIXTURE','CITY','WA','98041','NONE',value,'10212020','25','C00000935','TRAN1','1481637','','MEMO',subid]
            return '|'.join(values)+'\n'
        text=row('"OPEN','4010420211993597626')+row('CLOSE"','4010420211993597627')
        path=self.archive('quotes.zip',text)
        self.assertEqual(build.load_bulk_table(self.con,'individual_contributions',path,list(bulk.INDIVIDUAL_COLUMNS),2020,member='data.txt'),2)
        self.assertEqual(self.con.execute('SELECT OCCUPATION FROM individual_contributions ORDER BY SUB_ID').fetchall(),[('"OPEN',),('CLOSE"',)])
    def test_memory_thread_and_temp_limits(self):
        build.tune_session(self.con,self.db)
        self.assertEqual(self.con.execute("SELECT current_setting('threads')").fetchone()[0],1)
        self.assertEqual(self.con.execute("SELECT current_setting('max_temp_directory_size')").fetchone()[0],'1.0 GiB')
        self.assertEqual(self.con.execute("SELECT current_setting('memory_limit')").fetchone()[0],'512.0 MiB')
    def test_batch_typing_matches_original_postload_cast_chain(self):
        columns=['NAME','event_dt','value_amt','CAND_ELECTION_YR']
        values=[['a','01022026','12.5','2026'],['b','20260103','-2','2024'],['c','04-JAN-26','bad','bad'],['d','01/05/2026','','']]
        path=self.archive('typed.zip',''.join('|'.join(row)+'\n' for row in values))
        build.load_bulk_table(self.con,'typed',path,columns,2026,member='data.txt')
        self.con.execute('CREATE TABLE legacy(NAME VARCHAR,event_dt VARCHAR,value_amt VARCHAR,CAND_ELECTION_YR VARCHAR,cycle INTEGER)')
        self.con.executemany('INSERT INTO legacy VALUES (?,?,?,?,2026)',[[v or None for v in row] for row in values])
        build.cast_columns(self.con,'legacy')
        self.assertEqual(self.con.execute('DESCRIBE typed').fetchall(),self.con.execute('DESCRIBE legacy').fetchall())
        self.assertEqual(self.con.execute('SELECT * FROM typed EXCEPT ALL SELECT * FROM legacy').fetchall(),[])
        self.assertEqual(self.con.execute('SELECT * FROM legacy EXCEPT ALL SELECT * FROM typed').fetchall(),[])

class MainTests(unittest.TestCase):
    def test_existing_output_refused_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/'old.duckdb';path.write_bytes(b'untouched')
            with patch.object(sys,'argv',['build_database.py','--output',str(path)]),patch.object(build,'download_headers') as network:
                with self.assertRaises(SystemExit) as error:build.main()
                self.assertEqual(error.exception.code,2);network.assert_not_called()
            self.assertEqual(path.read_bytes(),b'untouched')
    def test_main_load_failure_keeps_source_and_incomplete_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);db=root/'new.duckdb';data=root/'raw'
            def download(url,dest,*args):
                with zipfile.ZipFile(dest,'w') as z:z.writestr('cn.txt','"broken|x\n')
                return True
            args=['build_database.py','--output',str(db),'--data-dir',str(data),'--tables','candidates','--start-cycle','2026','--end-cycle','2026']
            with patch.object(sys,'argv',args),patch.object(build,'download_headers',return_value={'cn_header_file.csv':['ID','NAME']}),patch.object(build,'download_file',side_effect=download):
                with self.assertRaises(csv.Error):build.main()
            self.assertTrue((data/'2026/cn26.zip').exists());self.assertTrue(db.exists())
            self.assertEqual(json.loads(db.with_suffix('.manifest.json').read_text())['status'],'incomplete')
    def test_download_failure_is_not_a_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(build.requests,'get',side_effect=RuntimeError('unavailable')):
            with self.assertRaisesRegex(RuntimeError,'three attempts'):build.download_file('https://example.invalid/source',pathlib.Path(tmp)/'source')
    def test_existing_partial_is_not_overwritten_or_downloaded(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(build.requests,'get') as network:
            path=pathlib.Path(tmp)/'source';part=path.with_name('source.part');part.write_bytes(b'preserve')
            with self.assertRaises(FileExistsError):build.download_file('https://example.invalid/source',path)
            network.assert_not_called();self.assertEqual(part.read_bytes(),b'preserve')
    def test_existing_source_receipt_refused_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);data=root/'raw';(data/'2026').mkdir(parents=True);receipt=data/'2026/cn26.zip.load.json';receipt.write_bytes(b'preserve')
            args=['build_database.py','--output',str(root/'new.duckdb'),'--data-dir',str(data),'--tables','candidates','--start-cycle','2026','--end-cycle','2026']
            with patch.object(sys,'argv',args),patch.object(build,'download_headers') as network:
                with self.assertRaises(SystemExit):build.main()
                network.assert_not_called();self.assertEqual(receipt.read_bytes(),b'preserve')
if __name__=='__main__':unittest.main(verbosity=2)
