"""Bounded FEC bulk parsing with explicit framing and exact-byte quarantine.

Adapted from the October 2026 maintenance rebuild. A failed load is incomplete:
never publish it, automatically retry the same cycle, or discard its evidence.
"""
import base64,csv,hashlib,io,json,os,pathlib,re
MIB=1024**2
MAX_CHUNK=32*MIB
MAX_RECORD=MIB//2
MAX_ROWS=100000
MAX_QUARANTINE=16*MIB
INVALID_UTF8=re.compile('[\udc80-\udcff]')
INDIVIDUAL_COLUMNS=('CMTE_ID','AMNDT_IND','RPT_TP','TRANSACTION_PGI','IMAGE_NUM','TRANSACTION_TP','ENTITY_TP','NAME','CITY','STATE','ZIP_CODE','EMPLOYER','OCCUPATION','TRANSACTION_DT','TRANSACTION_AMT','OTHER_ID','TRAN_ID','FILE_NUM','MEMO_CD','MEMO_TEXT','SUB_ID')
def ident(value):return '"'+str(value).replace('"','""')+'"'
def literal(value):return "'"+str(value).replace("'","''")+"'"
def typed_expression(column,kind):
    q=ident(column)
    if kind=='DATE':return 'COALESCE('+','.join('TRY_STRPTIME('+q+','+literal(fmt)+')' for fmt in ['%m%d%Y','%Y%m%d','%m/%d/%Y','%d-%b-%y'])+')::DATE AS '+q
    if kind in {'DOUBLE','INTEGER'}:return 'TRY_CAST('+q+' AS '+kind+') AS '+q
    if kind!='VARCHAR':raise ValueError('Unsupported schema type: '+kind)
    return q
def reader_sql(path,columns,delimiter,header):
    spec='{'+','.join(literal(c)+":'VARCHAR'" for c in columns)+'}'
    return f"read_csv({literal(path)}, columns={spec}, delim={literal(delimiter)}, quote='\"', escape='\"', header={'true' if header else 'false'}, auto_detect=false, parallel=false, null_padding=true, strict_mode=true, ignore_errors=false, buffer_size=1048576, max_line_size=1048576)"


class SourceRecordLimitError(ValueError):pass


def recover_anchored_individual_block(lines,columns,repairs):
    """Only after strict parsing fails: recover independently framed FEC rows.

    FEC's individual schema has a required committee ID first and 19-digit
    record ID last. An unmatched literal quote can make CSV consume many whole
    records. Recovery requires EVERY consumed physical line to be a complete
    exact-width record with both anchors. Valid CSV, including valid multiline
    records, never enters this path. No encoding or delimiter ambiguity allowed.
    """
    if tuple(c.upper() for c in columns)!=INDIVIDUAL_COLUMNS or not lines:return None
    recovered=[];changes=[]
    for line in lines:
        if len(line.encode('utf-8',errors='surrogateescape'))>MAX_RECORD or INVALID_UTF8.search(line):return None
        raw=line.removesuffix('\n').removesuffix('\r');fields=raw.split('|')
        if len(fields)!=21 or not re.fullmatch(r'C\d{8}',fields[0]) or not re.fullmatch(r'\d{19}',fields[-1]):return None
        values=[];changed=[]
        for column,field in zip(columns,fields):
            if not field:values.append('');continue
            try:
                parsed=next(csv.reader([field],delimiter='|',quotechar='"',strict=True))
                if len(parsed)!=1:return None
                values.append(parsed[0])
            except csv.Error:
                if not field.startswith('"'):return None
                values.append(field);changed.append({'column':column,'literal_value':field[:200]})
        recovered.append(values)
        if changed:changes.append(changed)
    if not changes:return None
    repairs['records']+=len(changes)
    for changed in changes:
        if len(repairs['examples'])<20:repairs['examples'].append(changed)
    repairs['anchored_individual_blocks']=repairs.get('anchored_individual_blocks',0)+1
    repairs['anchored_physical_records']=repairs.get('anchored_physical_records',0)+len(recovered)
    return recovered


def quarantine_bytes(table, cycle, first_line, last_line, raw):
    item={'table':table,'cycle':cycle,'first_physical_line':first_line,
          'last_physical_line':last_line,'reason':'invalid UTF-8; legacy reader skips this record',
          'sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),
          'raw_base64':base64.b64encode(raw).decode('ascii')}
    return (json.dumps(item,separators=(',',':'))+'\n').encode('ascii')


def quarantine_record(path, table, cycle, first_line, last_line, raw):
    """Keep exact rejected bytes; enforce a 16 MiB cap for this source file."""
    encoded=quarantine_bytes(table,cycle,first_line,last_line,raw)
    if (path.stat().st_size if path.exists() else 0)+len(encoded)>MAX_QUARANTINE:
        raise RuntimeError('Invalid UTF-8 quarantine exceeds 16 MiB per-source cap')
    with path.open('ab') as f:f.write(encoded);f.flush();os.fsync(f.fileno())


def make_tables(con, schemas):
    for table, schema in schemas.items():
        if any(t not in {'VARCHAR','DATE','DOUBLE','INTEGER'} for _,t in schema):
            raise ValueError('Unreviewed schema type')
        con.execute(f'CREATE TABLE {ident(table)} ('+
                    ','.join(ident(c)+' '+t for c,t in schema)+')')
    con.execute('CHECKPOINT')


def source_records(source, delimiter, columns, repairs, encoding_errors=None, quarantine=None, framing=None):
    """Strict CSV, plus a narrow literal-quote case in single-line bulk records.

    FEC cn24 has a literal name `"VAL" VALMA PAUL`. Strict CSV rejects it;
    permissive CSV drops quotes, and the old native reader also drops the final
    character. Recover only balanced literal quotes, one physical line, exact
    field count, no embedded delimiter ambiguity. All other errors still stop.
    """
    if framing is None:framing={}
    framing.update(physical_lines=0,logical_records_emitted=0,quarantined_physical_lines=0,accepted_multiline_excess=0)
    class Lines:
        def __init__(self):self.lines=[];self.byte_count=0;self.line_number=0
        def __iter__(self):return self
        def __next__(self):
            line=source.readline(MAX_RECORD+1)
            if not line:raise StopIteration
            self.byte_count+=len(line.encode('utf-8',errors='surrogateescape'))
            # Retain the last consumed physical line even when the logical
            # bound fires, so recovery can never silently lose that line.
            self.lines.append(line);self.line_number+=1;framing['physical_lines']+=1
            if self.byte_count>MAX_RECORD:raise SourceRecordLimitError('Source logical record exceeds byte bound')
            return line
    tracked=Lines();reader=csv.reader(tracked,delimiter=delimiter,quotechar='"',strict=True)
    while True:
        tracked.lines=[];tracked.byte_count=0
        first_line=tracked.line_number+1
        try:record=next(reader)
        except StopIteration:
            if framing['physical_lines']!=framing['logical_records_emitted']+framing['quarantined_physical_lines']+framing['accepted_multiline_excess']:
                raise ValueError('Source physical/logical line accounting mismatch')
            return
        except (csv.Error,SourceRecordLimitError) as parse_error:
            if delimiter=='|' and tracked.lines:
                recovered=recover_anchored_individual_block(tracked.lines,columns,repairs)
                if recovered is not None:
                    reader=csv.reader(tracked,delimiter=delimiter,quotechar='"',strict=True)
                    framing['logical_records_emitted']+=len(recovered)
                    yield from recovered
                    continue
            if isinstance(parse_error,SourceRecordLimitError):raise
            # Encoding and malformed quoting together have no reviewed recovery.
            if any(INVALID_UTF8.search(line) for line in tracked.lines):raise
            if delimiter!='|' or len(tracked.lines)!=1:raise
            raw=tracked.lines[0]
            if raw.endswith('\r\n'):raw=raw[:-2]
            elif raw.endswith(('\r','\n')):raw=raw[:-1]
            fields=raw.split('|')
            if len(fields)!=len(columns):raise
            record=[];changed=[]
            for i,field in enumerate(fields):
                if not field:record.append('');continue
                try:
                    value=next(csv.reader([field],delimiter='|',quotechar='"',strict=True))
                    if len(value)!=1:raise ValueError('Ambiguous fallback field')
                    record.append(value[0])
                except csv.Error:
                    if not field.startswith('"') or field.count('"')<2 or field.count('"')%2:raise
                    record.append(field);changed.append({'column':columns[i],'literal_value':field[:200]})
            if not changed:raise RuntimeError('CSV failure lacks an unambiguous literal-quote explanation')
            repairs['records']+=1
            if len(repairs['examples'])<20:repairs['examples'].append(changed)
            reader=csv.reader(tracked,delimiter=delimiter,quotechar='"',strict=True)
        # A strict CSV parse can still silently combine independently framed
        # FEC records when an unmatched quote closes on a later physical line.
        # Recover only when EVERY physical line has the complete 21-field
        # schema and independent first/last IDs; ordinary multiline CSV stays
        # intact when its continuation is not itself a complete anchored row.
        if delimiter=='|' and len(tracked.lines)>1:
            recovered=recover_anchored_individual_block(tracked.lines,columns,repairs)
            if recovered is not None:
                repairs['successful_multiline_blocks']=repairs.get('successful_multiline_blocks',0)+1
                framing['logical_records_emitted']+=len(recovered)
                yield from recovered
                continue
        if any(INVALID_UTF8.search(line) for line in tracked.lines):
            # Empty trailing separators are already accepted for valid records.
            # They do not make the rejected raw record's field boundary ambiguous.
            if len(record)>len(columns) and all(x=='' for x in record[len(columns):]):
                record=record[:len(columns)]
            if quarantine is None or encoding_errors is None or delimiter!='|' or len(record)!=len(columns):
                raise ValueError('Invalid UTF-8 outside reviewed exact-width bulk record')
            raw=''.join(tracked.lines).encode('utf-8',errors='surrogateescape')
            quarantine(first_line,tracked.line_number,raw)
            encoding_errors['records']+=1
            encoding_errors['raw_bytes']+=len(raw)
            encoding_errors['invalid_bytes']+=sum(len(INVALID_UTF8.findall(line)) for line in tracked.lines)
            framing['quarantined_physical_lines']+=len(tracked.lines)
            continue
        framing['logical_records_emitted']+=1
        framing['accepted_multiline_excess']+=len(tracked.lines)-1
        yield record


def load_records(con, table, cycle, source, columns, schema, chunk, delimiter,
                 boundary=lambda: None, max_rows=MAX_ROWS, max_bytes=MAX_CHUNK, quarantine=None):
    """Strict logical records, typed batches; no table replacement or full text."""
    if con.execute('SELECT count(*) FROM '+ident(table)+' WHERE cycle=?',[cycle]).fetchone()[0]:raise ValueError('Cycle already contains rows; refusing duplicate or partial retry')
    expected = {c.lower(): (c,t) for c,t in schema if c.lower()!='cycle'}
    if not columns or len(set(c.lower() for c in columns)) != len(columns):
        raise ValueError('Empty/duplicate source columns')
    if any(c.lower() not in expected for c in columns):
        raise ValueError('Unexpected source column')
    if chunk.exists(): raise FileExistsError(chunk)
    targets = [expected[c.lower()][0] for c in columns]
    expressions = ','.join(typed_expression(c,expected[c.lower()][1]) for c in columns)
    sql = (f'INSERT INTO {ident(table)} ('+','.join(map(ident,targets))+',cycle) '+
           f'SELECT {expressions},{int(cycle)}::INTEGER FROM '+
           reader_sql(chunk, columns, '|', False))
    csv.field_size_limit(MAX_RECORD)
    repairs={'records':0,'examples':[],'meaning':'Strict-parse failures recovered; not all literal quote-containing fields'}
    encoding_errors={'records':0,'raw_bytes':0,'invalid_bytes':0,
                     'policy':'Exact raw bytes quarantined; entire record excluded, matching legacy ignore_errors=true; no character replacement'}
    framing={}
    reader = source_records(source,delimiter,columns,repairs,encoding_errors,quarantine,framing)
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, delimiter='|', lineterminator='\n', quoting=csv.QUOTE_ALL)
    out = None
    rows = batches = batch = size = trimmed = peak = blank = padded = 0
    typed = {i:c for i,c in enumerate(columns) if expected[c.lower()][1]!='VARCHAR'}
    nonblank = {c:0 for c in typed.values()}
    def flush():
        nonlocal out, batch, size, batches, rows, peak
        if out is None: return
        out.close(); out = None
        if batch:
            boundary()
            con.execute('BEGIN')
            try:
                con.execute(sql)
                con.execute('COMMIT')
            except BaseException:
                try: con.execute('ROLLBACK')
                except Exception: pass
                raise
            con.execute('CHECKPOINT')
            rows += batch; batches += 1; peak = max(peak,size)
            boundary()
            if batches % 25 == 0:
                print(f'{table}/{cycle}: {rows:,} logical records; {batches} batches', flush=True)
        chunk.unlink(); batch = size = 0
    try:
        for record in reader:
            if not record: blank+=1;continue
            if len(record)>len(columns):
                if any(x!='' for x in record[len(columns):]):
                    raise ValueError(f'Extra nonempty fields at {table}/{cycle} record {rows+batch+1}')
                record = record[:len(columns)]; trimmed += 1
            if len(record)<len(columns):padded+=1
            record += [''] * (len(columns)-len(record))
            buffer.seek(0); buffer.truncate(0); writer.writerow(record)
            encoded = buffer.getvalue().encode('utf-8')
            if len(encoded)>MAX_RECORD or len(encoded)>max_bytes:
                raise ValueError('Logical record exceeds explicit byte bound')
            if batch and (batch>=max_rows or size+len(encoded)>max_bytes): flush()
            if out is None: out = chunk.open('xb',buffering=MIB)
            out.write(encoded); size += len(encoded); batch += 1
            for i,c in typed.items():
                if record[i].strip(): nonblank[c] += 1
        flush()
    finally:
        if out is not None: out.close()
        # Keep an incomplete chunk for diagnosis; no automatic retry or deletion.
        buffer.close()
    actual = con.execute(f'SELECT count(*) FROM {ident(table)} WHERE cycle=?',[cycle]).fetchone()[0]
    if rows != actual: raise RuntimeError('Logical-record count mismatch or repeated cycle')
    quality = {}
    for c, n in nonblank.items():
        parsed = con.execute(f'SELECT count({ident(expected[c.lower()][0])}) FROM {ident(table)} WHERE cycle=?',[cycle]).fetchone()[0]
        quality[c] = {'source_nonblank':n,'parsed_nonnull':parsed,'unparsed_nonblank':n-parsed}
    return {'logical_records_read':rows,'batches':batches,'peak_chunk_bytes':peak,
            'max_chunk_bytes':max_bytes,'max_chunk_rows':max_rows,
            'trailing_empty_padding_records':trimmed,'conversion_quality':quality,
            'literal_quote_recovery':repairs,'blank_lines_ignored':blank,'short_records_padded':padded,'source_framing':framing,
            'invalid_utf8_quarantined':encoding_errors,'logical_records_including_quarantine':rows+encoding_errors['records']}


def preflight_records(source, columns, table, cycle):
    """Validate source framing and record bounds before inserting any rows."""
    csv.field_size_limit(MAX_RECORD)
    repairs={'records':0,'examples':[]};encoding={'records':0,'raw_bytes':0,'invalid_bytes':0};framing={}
    rows=blank=padded=trimmed=quarantine_size=0
    def count_quarantine(first,last,raw):
        nonlocal quarantine_size
        quarantine_size+=len(quarantine_bytes(table,cycle,first,last,raw))
        if quarantine_size>MAX_QUARANTINE:raise RuntimeError('Invalid UTF-8 quarantine exceeds per-source cap during preflight')
    buffer=io.StringIO(newline='');writer=csv.writer(buffer,delimiter='|',lineterminator='\n',quoting=csv.QUOTE_ALL)
    for record in source_records(source,'|',columns,repairs,encoding,count_quarantine,framing):
        if not record:blank+=1;continue
        if len(record)>len(columns):
            if any(x!='' for x in record[len(columns):]):raise ValueError('Extra nonempty fields in source preflight')
            record=record[:len(columns)];trimmed+=1
        if len(record)<len(columns):padded+=1;record+=['']*(len(columns)-len(record))
        buffer.seek(0);buffer.truncate(0);writer.writerow(record)
        if len(buffer.getvalue().encode('utf-8'))>MAX_RECORD:raise ValueError('Logical record exceeds explicit byte bound')
        rows+=1
    if framing['accepted_multiline_excess']:raise ValueError('Unresolved multiline bulk framing; inspect preserved source before loading')
    return {'rows':rows,'blank':blank,'padded':padded,'trimmed':trimmed,'source_framing':framing,'literal_quote_recovery':repairs,'invalid_utf8':encoding,'quarantine_bytes':quarantine_size}
