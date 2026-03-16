# Data Dictionary

Source: [FEC Bulk Data](https://www.fec.gov/data/browse-data/?tab=bulk-data)

## candidate_committee_links

Which committees are authorized by which candidates

Rows: 73,520

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H0AK00055 | Candidate ID, joins across candidates and contribution tables |
| CAND_ELECTION_YR | DATE | 100.0% |  |  |
| FEC_ELECTION_YR | VARCHAR | 0.0% | 2004 |  |
| CMTE_ID | VARCHAR | 0.0% | C00361626 | Committee ID, joins to committees table and contribution tables |
| CMTE_TP | VARCHAR | 0.0% | H |  |
| CMTE_DSGN | VARCHAR | 0.0% | P |  |
| LINKAGE_ID | VARCHAR | 0.0% | 56 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## candidates

Candidate master: name, party, office, state, district, status

Rows: 76,283

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H0AK00055 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | GREENE, CLIFFORD MARK |  |
| CAND_PTY_AFFILIATION | VARCHAR | 0.1% | DEM |  |
| CAND_ELECTION_YR | DATE | 100.0% |  |  |
| CAND_OFFICE_ST | VARCHAR | 0.0% | AK |  |
| CAND_OFFICE | VARCHAR | 0.0% | H |  |
| CAND_OFFICE_DISTRICT | VARCHAR | 0.8% | 00 |  |
| CAND_ICI | VARCHAR | 4.1% | C |  |
| CAND_STATUS | VARCHAR | 0.0% | N |  |
| CAND_PCC | VARCHAR | 17.3% | C00361626 | Candidate principal campaign committee, joins candidates to committees.CMTE_ID |
| CAND_ST1 | VARCHAR | 1.2% | PO BOX 20745 |  |
| CAND_ST2 | VARCHAR | 91.3% | PO BOX 374 |  |
| CAND_CITY | VARCHAR | 0.1% | JUNEAU |  |
| CAND_ST | VARCHAR | 0.9% | AK |  |
| CAND_ZIP | VARCHAR | 1.4% | 99802 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committee_contributions

PAC/party contributions to candidates

Rows: 5,214,013

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00379735 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q1 | Report type code |
| TRANSACTION_PGI | VARCHAR | 2.0% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 25971574853 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24K |  |
| ENTITY_TP | VARCHAR | 2.5% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 1.4% | BEAUPREZ FOR CONGRESS  (CO/H07) |  |
| CITY | VARCHAR | 1.4% | WHEAT RIDGE |  |
| STATE | VARCHAR | 1.4% | CO |  |
| ZIP_CODE | VARCHAR | 1.4% | 80034 |  |
| EMPLOYER | VARCHAR | 100.0% | SELF-EMPLOYED |  |
| OCCUPATION | VARCHAR | 100.0% | ATTORNEY |  |
| TRANSACTION_DT | DATE | 0.5% | 2003-02-16 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 1000.0 |  |
| OTHER_ID | VARCHAR | 0.0% | C00376152 |  |
| CAND_ID | VARCHAR | 0.2% | H2CO07063 | Candidate ID, joins across candidates and contribution tables |
| TRAN_ID | VARCHAR | 0.7% | 0326200333E668 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.6% | 193080 |  |
| MEMO_CD | VARCHAR | 98.3% | X |  |
| MEMO_TEXT | VARCHAR | 89.3% | * IN-KIND: DOMAIN REGISTRATION |  |
| SUB_ID | VARCHAR | 0.0% | 4120820051062509975 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committee_to_committee

Transfers between committees

Rows: 45,559,049

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00386151 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q1 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.8% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 23020201726 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 16C |  |
| ENTITY_TP | VARCHAR | 0.6% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.2% | BEAUPREZ FOR CONGRESS  (CO/H07) |  |
| CITY | VARCHAR | 0.2% | WHEAT RIDGE |  |
| STATE | VARCHAR | 0.2% | CO |  |
| ZIP_CODE | VARCHAR | 0.2% | 80034 |  |
| EMPLOYER | VARCHAR | 20.3% | SELF |  |
| OCCUPATION | VARCHAR | 20.2% | CONSULTANT |  |
| TRANSACTION_DT | DATE | 0.1% | 2003-03-24 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 27500.0 |  |
| OTHER_ID | VARCHAR | 80.0% | S4KY00042 |  |
| TRAN_ID | VARCHAR | 0.2% | 0326200333E668 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 193080 |  |
| MEMO_CD | VARCHAR | 19.9% | X |  |
| MEMO_TEXT | VARCHAR | 51.6% | DUES 2003 |  |
| SUB_ID | VARCHAR | 0.0% | 1050520030000101517 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committees

Committee master: name, type, party, treasurer, connected org

Rows: 183,599

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00000042 | Committee ID, joins to committees table and contribution tables |
| CMTE_NM | VARCHAR | 0.0% | ILLINOIS TOOL WORKS FOR BETTER GOVERNMENT COMMITTEE |  |
| TRES_NM | VARCHAR | 5.0% | Michael J. Lynch |  |
| CMTE_ST1 | VARCHAR | 0.1% | 3600 W. Lake Avenue |  |
| CMTE_ST2 | VARCHAR | 77.8% | PO BOX 419580 |  |
| CMTE_CITY | VARCHAR | 0.1% | Glenview |  |
| CMTE_ST | VARCHAR | 0.1% | IL |  |
| CMTE_ZIP | VARCHAR | 0.1% | 60025 |  |
| CMTE_DSGN | VARCHAR | 0.0% | U |  |
| CMTE_TP | VARCHAR | 0.0% | Q |  |
| CMTE_PTY_AFFILIATION | VARCHAR | 59.4% | UNK |  |
| CMTE_FILING_FREQ | VARCHAR | 0.0% | Q |  |
| ORG_TP | VARCHAR | 77.6% | C |  |
| CONNECTED_ORG_NM | VARCHAR | 51.1% | ILLINOIS TOOL WORKS INC |  |
| CAND_ID | VARCHAR | 63.1% | H6TX07029 | Candidate ID, joins across candidates and contribution tables |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## communication_costs

Internal communications supporting/opposing candidates

Rows: 25,558

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C70000112 | Committee ID, joins to committees table and contribution tables |
| CMTE_NM | VARCHAR | 0.0% | AFL-CIO COPE POLITICAL CONTRIBUTIONS COMMITTEE |  |
| CAND_ID | VARCHAR | 0.0% | H0NY20095 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | GIBSON, CHRIS P |  |
| CAND_OFFICE | VARCHAR | 0.0% | H |  |
| CAND_STATE | VARCHAR | 0.0% | NY |  |
| CAND_OFFICE_DISTRICT | VARCHAR | 0.0% | 20 |  |
| CAND_PTY_AFFILIATION | VARCHAR | 0.0% | REP |  |
| TRANSACTION_DT | DATE | 100.0% |  |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 17194.83 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24N |  |
| COMMUNICATION_TP | VARCHAR | 1.6% | DM |  |
| COMMUNICATION_CLASS | VARCHAR | 2.2% | M |  |
| SUPPORT_OPPOSE_IND | VARCHAR | 1.2% | O |  |
| IMAGE_NUM | VARCHAR | 0.0% | http://docquery.fec.gov/cgi-bin/fecimg/?11030583334 |  |
| LINE_NUM | VARCHAR | 99.7% | http://docquery.fec.gov/cgi-bin/fecimg/?11030583331 |  |
| FORM_TP_CD | VARCHAR | 0.3% | F7 |  |
| SCHED_TP_CD | VARCHAR | 0.0% | F76 |  |
| TRAN_ID | VARCHAR | 15.3% | F760407131410781 | Transaction identifier within a committee |
| SUB_ID | VARCHAR | 0.0% | 2061420111140795867 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 1.2% | 721035 |  |
| RPT_YR | VARCHAR | 0.0% | 2010 |  |
| CAND_STATE_DESCRIPTION | VARCHAR | 0.0% | NEW YORK |  |
| CAND_PTY_AFFILIATION_DESCRIPTION | VARCHAR | 0.0% | Republican Party |  |
| PURPOSE | VARCHAR | 99.7% | Republican Party |  |
| column25 | VARCHAR | 100.0% |  |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## electioneering_communications

Broadcast ads mentioning candidates near elections

Rows: 1,570

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CANDIDATE_ID | VARCHAR | 16.6% | S8WI00026 |  |
| CANDIDATE_NAME | VARCHAR | 16.8% | FEINGOLD, RUSSELL D |  |
| CANDIDATE_OFFICE | VARCHAR | 16.8% | S |  |
| CANDIDATE_STATE | VARCHAR | 16.8% | WI |  |
| CANDIDATE_DISTRICT | VARCHAR | 16.8% | 00 |  |
| COMMITTEE_ID | VARCHAR | 0.0% | C30001648 |  |
| COMMITTEE_NAME | VARCHAR | 0.0% | AMERICAN ACTION NETWORK |  |
| SB_IMAGE_NUM | VARCHAR | 0.0% | 10932121746 |  |
| PAYEE_NAME | VARCHAR | 0.0% | SMART MEDIA GROUP |  |
| PAYEE_STREET | VARCHAR | 0.0% | 814 KING STREET STE 400 |  |
| PAYEE_CITY | VARCHAR | 0.0% | ALEXANDRIA |  |
| PAYEE_STATE | VARCHAR | 0.1% | VA |  |
| DISBURSEMENT_DESCRIPTION | VARCHAR | 9.2% | MEDIA TV AD PRODUCTION - BUCKET |  |
| DISBURSEMENT_DATE | VARCHAR | 0.0% | 30-SEP-10 |  |
| COMMUNICATION_DATE | VARCHAR | 1.4% | 30-SEP-10 |  |
| PUBLIC_DISBURSEMENT_DATE | VARCHAR | 0.4% | 30-SEP-10 |  |
| REPORTED_DISBURSEMENT_AMOUNT | VARCHAR | 0.0% | 290395 |  |
| NUMBER_OF_CANDIDATES | VARCHAR | 0.0% | 1 |  |
| CALCULATED_CANDIDATE_SHARE | VARCHAR | 0.0% | 290395 |  |
| column19 | VARCHAR | 98.8% | 4200 |  |
| column20 | VARCHAR | 99.1% | WYLL |  |
| column21 | VARCHAR | 99.1% | 25 NORTHWEST POINT BLVD |  |
| column22 | VARCHAR | 99.1% | ELK GROOVE VILLAGE |  |
| column23 | VARCHAR | 99.1% | IL |  |
| column24 | VARCHAR | 99.1% | PLACEMENT OF RADIO AD ST. CHARLES EVENT |  |
| column25 | VARCHAR | 99.1% | 14-SEP-10 |  |
| column26 | VARCHAR | 99.1% | 14-SEP-10 |  |
| column27 | VARCHAR | 99.1% | 24-SEP-10 |  |
| column28 | VARCHAR | 99.1% | 1000 |  |
| column29 | VARCHAR | 99.1% | 1 |  |
| column30 | VARCHAR | 99.1% | 1000 |  |
| column31 | VARCHAR | 99.4% | 10931359199 |  |
| column32 | VARCHAR | 99.4% | MOUNTAINTOP MEDIA |  |
| column33 | VARCHAR | 99.4% | PO BOX 578 |  |
| column34 | VARCHAR | 99.4% | SPARTA |  |
| column35 | VARCHAR | 99.4% | NJ |  |
| column36 | VARCHAR | 99.4% | PLACEMENT OF RADIO SPOT - AFP MCMAHON","29-SEP-10","30-SEP-10","30-SEP-10","4... |  |
| column37 | VARCHAR | 99.4% |  BRYAN ROY" |  |
| column38 | VARCHAR | 99.4% | H |  |
| column39 | VARCHAR | 99.4% | PA |  |
| column40 | VARCHAR | 99.4% | 07 |  |
| column41 | VARCHAR | 99.4% | C30001051 |  |
| column42 | VARCHAR | 99.4% | AMERICANS FOR PROSPERITY |  |
| column43 | VARCHAR | 99.6% | 10931359199 |  |
| column44 | VARCHAR | 99.6% | MOUNTAINTOP MEDIA |  |
| column45 | VARCHAR | 99.6% | PO BOX 578 |  |
| column46 | VARCHAR | 99.6% | SPARTA |  |
| column47 | VARCHAR | 99.6% | NJ |  |
| column48 | VARCHAR | 99.6% | PLACEMENT OF RADIO SPOT - AFP LENTZ","29-SEP-10","30-SEP-10","30-SEP-10","450... |  |
| column49 | VARCHAR | 99.6% |  RON" |  |
| column50 | VARCHAR | 99.6% | H |  |
| column51 | VARCHAR | 99.6% | WI |  |
| column52 | VARCHAR | 99.6% | 03 |  |
| column53 | VARCHAR | 99.6% | C30001051 |  |
| column54 | VARCHAR | 99.6% | AMERICANS FOR PROSPERITY |  |
| column55 | VARCHAR | 99.7% | 10931359200 |  |
| column56 | VARCHAR | 99.7% | MENTZER MEDIA SERVICES |  |
| column57 | VARCHAR | 99.7% | 600 FAIRMOUNT AVENUE SUITE 306 |  |
| column58 | VARCHAR | 99.7% | TOWSON |  |
| column59 | VARCHAR | 99.7% | MD |  |
| column60 | VARCHAR | 99.7% | PLACEMENT OF TV SPOT FIRST - KIND","30-SEP-10","30-SEP-10","30-SEP-10","17016... |  |
| column61 | VARCHAR | 99.7% |  STEVEN L." |  |
| column62 | VARCHAR | 99.7% | H |  |
| column63 | VARCHAR | 99.7% | WI |  |
| column64 | VARCHAR | 99.7% | 08 |  |
| column65 | VARCHAR | 99.7% | C30001051 |  |
| column66 | VARCHAR | 99.7% | AMERICANS FOR PROSPERITY |  |
| column67 | VARCHAR | 99.9% | 10931359200 |  |
| column68 | VARCHAR | 99.9% | MENTZER MEDIA SERVICES |  |
| column69 | VARCHAR | 99.9% | 600 FAIRMOUNT AVENUE SUITE 306 |  |
| column70 | VARCHAR | 99.9% | TOWSON |  |
| column71 | VARCHAR | 99.9% | MD |  |
| column72 | VARCHAR | 99.9% | PLACEMENT OF TV SPOT - FIRST - KAGEN","30-SEP-10","30-SEP-10","30-SEP-10","67... |  |
| column73 | VARCHAR | 99.9% |  CAROL" |  |
| column74 | VARCHAR | 99.9% | H |  |
| column75 | VARCHAR | 99.9% | NH |  |
| column76 | VARCHAR | 99.9% | 01 |  |
| column77 | VARCHAR | 99.9% | C30001051 |  |
| column78 | VARCHAR | 99.9% | AMERICANS FOR PROSPERITY |  |
| column79 | VARCHAR | 99.9% | 10931359213 |  |
| column80 | VARCHAR | 99.9% | MENTZER MEDIA SERVICES |  |
| column81 | VARCHAR | 99.9% | 600 FAIRMOUNT AVENUE SUITE 306 |  |
| column82 | VARCHAR | 99.9% | TOWSON |  |
| column83 | VARCHAR | 99.9% | MD |  |
| column84 | VARCHAR | 99.9% | PLACEMENT OF POODLE TV AD |  |
| column85 | VARCHAR | 99.9% | 30-SEP-10 |  |
| column86 | VARCHAR | 99.9% | 01-OCT-10 |  |
| column87 | VARCHAR | 99.9% | 01-OCT-10 |  |
| column88 | VARCHAR | 99.9% | 74417 |  |
| column89 | VARCHAR | 99.9% | 1 |  |
| column90 | VARCHAR | 99.9% | 74417 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |
| column019 | VARCHAR | 99.6% | 202007109244414082 |  |
| column020 | VARCHAR | 99.6% | TARGETED PLATFORM MEDIA LLC |  |
| column021 | VARCHAR | 99.6% | P.O. BOX 237 |  |
| column022 | VARCHAR | 99.6% | CROWNSVILLE |  |
| column023 | VARCHAR | 99.6% | MD |  |
| column024 | VARCHAR | 99.6% | TELEVISION ADVERTISING BUY - VACATION","07-JUL-20","09-JUL-20","09-JUL-20","2... |  |
| column025 | VARCHAR | 99.6% |  MARTHA" |  |
| column026 | VARCHAR | 99.6% | S |  |
| column027 | VARCHAR | 99.6% | AZ |  |
| column028 | VARCHAR | 99.6% | 00 |  |
| column029 | VARCHAR | 99.6% | C30003032 |  |
| column030 | VARCHAR | 99.6% | ADVANCING AZ |  |
| column031 | VARCHAR | 99.7% | 202007159244653408 |  |
| column032 | VARCHAR | 99.7% | TARGETED PLATFORM MEDIA, LLC |  |
| column033 | VARCHAR | 99.7% | P.O. BOX 237 |  |
| column034 | VARCHAR | 99.7% | CROWNSVILLE |  |
| column035 | VARCHAR | 99.7% | MD |  |
| column036 | VARCHAR | 99.7% | TELEVISION ADVERTISING BUY - VACATION","13-JUL-20","14-JUL-20","14-JUL-20","8... |  |
| column037 | VARCHAR | 99.7% |  MARTHA" |  |
| column038 | VARCHAR | 99.7% | S |  |
| column039 | VARCHAR | 99.7% | AZ |  |
| column040 | VARCHAR | 99.7% | 00 |  |
| column041 | VARCHAR | 99.7% | C30003032 |  |
| column042 | VARCHAR | 99.7% | ADVANCING AZ |  |
| column043 | VARCHAR | 99.7% | 202007159244661899 |  |
| column044 | VARCHAR | 99.7% | MVAR MEDIA LLC |  |
| column045 | VARCHAR | 99.7% | 1421 PRINCE STREET |  |
| column046 | VARCHAR | 99.7% | ALEXANDRIA |  |
| column047 | VARCHAR | 99.7% | VA |  |
| column048 | VARCHAR | 99.7% | MEDIA PRODUCTION - BARTENDER","13-JUL-20","14-JUL-20","14-JUL-20","10345.59",... |  |
| column049 | VARCHAR | 99.7% |  MARTHA" |  |
| column050 | VARCHAR | 99.7% | S |  |
| column051 | VARCHAR | 99.7% | AZ |  |
| column052 | VARCHAR | 99.7% | 00 |  |
| column053 | VARCHAR | 99.7% | C30003032 |  |
| column054 | VARCHAR | 99.7% | ADVANCING AZ |  |
| column055 | VARCHAR | 99.8% | 202007159244661899 |  |
| column056 | VARCHAR | 99.8% | TARGETED PLATFORM MEDIA, LLC |  |
| column057 | VARCHAR | 99.8% | P.O. BOX 237 |  |
| column058 | VARCHAR | 99.8% | CROWNSVILLE |  |
| column059 | VARCHAR | 99.8% | MD |  |
| column060 | VARCHAR | 99.8% | TELEVISION ADVERTISING BUY - BARTENDER","13-JUL-20","14-JUL-20","14-JUL-20","... |  |
| column061 | VARCHAR | 99.8% |  MARTHA" |  |
| column062 | VARCHAR | 99.8% | S |  |
| column063 | VARCHAR | 99.8% | AZ |  |
| column064 | VARCHAR | 99.8% | 00 |  |
| column065 | VARCHAR | 99.8% | C30003032 |  |
| column066 | VARCHAR | 99.8% | ADVANCING AZ |  |
| column067 | VARCHAR | 99.8% | 202007229260727983 |  |
| column068 | VARCHAR | 99.8% | TARGETED PLATFORM MEDIA, LLC |  |
| column069 | VARCHAR | 99.8% | P.O. BOX 237 |  |
| column070 | VARCHAR | 99.8% | CROWNSVILLE |  |
| column071 | VARCHAR | 99.8% | MD |  |
| column072 | VARCHAR | 99.8% | TELEVISION ADVERTISING BUY - VACATION","20-JUL-20","21-JUL-20","21-JUL-20","8... |  |
| column073 | VARCHAR | 99.8% |  MARTHA" |  |
| column074 | VARCHAR | 99.8% | S |  |
| column075 | VARCHAR | 99.8% | AZ |  |
| column076 | VARCHAR | 99.8% | 00 |  |
| column077 | VARCHAR | 99.8% | C30003032 |  |
| column078 | VARCHAR | 99.8% | ADVANCING AZ |  |
| column079 | VARCHAR | 99.8% | 202007229260730228 |  |
| column080 | VARCHAR | 99.8% | TARGETED PLATFORM MEDIA, LLC |  |
| column081 | VARCHAR | 99.8% | P.O. BOX 237 |  |
| column082 | VARCHAR | 99.8% | CROWNSVILLE |  |
| column083 | VARCHAR | 99.8% | MD |  |
| column084 | VARCHAR | 99.8% | TELEVISION ADVERTISING BUY - BARTENDER","20-JUL-20","21-JUL-20","21-JUL-20","... |  |
| column085 | VARCHAR | 99.8% |  MARTHA" |  |
| column086 | VARCHAR | 99.8% | S |  |
| column087 | VARCHAR | 99.8% | AZ |  |
| column088 | VARCHAR | 99.8% | 00 |  |
| column089 | VARCHAR | 99.8% | C30003032 |  |
| column090 | VARCHAR | 99.8% | ADVANCING AZ |  |
| column091 | VARCHAR | 99.8% | 202010179297137465 |  |
| column092 | VARCHAR | 99.8% | MVAR MEDIA LLC |  |
| column093 | VARCHAR | 99.8% | 1421 PRINCE STREET |  |
| column094 | VARCHAR | 99.8% | ALEXANDRIA |  |
| column095 | VARCHAR | 99.8% | VA |  |
| column096 | VARCHAR | 99.8% | RADIO ADVERTISING PRODUCTION  - DR. ORTIZ","16-OCT-20","16-OCT-20","16-OCT-20... |  |
| column097 | VARCHAR | 99.8% |  MARTHA" |  |
| column098 | VARCHAR | 99.8% | S |  |
| column099 | VARCHAR | 99.8% | AZ |  |
| column100 | VARCHAR | 99.8% | 00 |  |
| column101 | VARCHAR | 99.8% | C30003032 |  |
| column102 | VARCHAR | 99.8% | ADVANCING AZ |  |
| column103 | VARCHAR | 99.8% | 202010179297137465 |  |
| column104 | VARCHAR | 99.8% | TARGETED PLATFORM MEDIA, LLC |  |
| column105 | VARCHAR | 99.8% | P.O. BOX 237 |  |
| column106 | VARCHAR | 99.8% | CROWNSVILLE |  |
| column107 | VARCHAR | 99.8% | MD |  |
| column108 | VARCHAR | 99.8% | RADIO ADVERTISING BUY - DR. ORTIZ","15-OCT-20","16-OCT-20","16-OCT-20","86500... |  |
| column109 | VARCHAR | 99.8% |  DONALD J." |  |
| column110 | VARCHAR | 99.8% | P |  |
| column111 | VARCHAR | 99.8% | US |  |
| column112 | VARCHAR | 99.8% | 00 |  |
| column113 | VARCHAR | 99.8% | C30003065 |  |
| column114 | VARCHAR | 99.8% | AFT SOLIDARITY |  |
| column115 | VARCHAR | 99.8% | 202008109261288009 |  |
| column116 | VARCHAR | 99.8% | AL MEDIA |  |
| column117 | VARCHAR | 99.8% | 222 WEST ONTARIO |  |
| column118 | VARCHAR | 99.8% | CHICAGO |  |
| column119 | VARCHAR | 99.8% | IL |  |
| column120 | VARCHAR | 99.8% | TV ADVERTISING: PAUSE BUTTON |  |
| column121 | VARCHAR | 99.8% | 07-AUG-20 |  |
| column122 | VARCHAR | 99.8% | 08-AUG-20 |  |
| column123 | VARCHAR | 99.8% | 08-AUG-20 |  |
| column124 | VARCHAR | 99.8% | 168005 |  |
| column125 | VARCHAR | 99.8% | 1 |  |
| column126 | VARCHAR | 99.8% | 168005 |  |
| column127 | VARCHAR | 99.9% | 202009309284984685 |  |
| column128 | VARCHAR | 99.9% | SKDKNICKERBOCKER, LLC |  |
| column129 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column130 | VARCHAR | 99.9% | WASHINGTON |  |
| column131 | VARCHAR | 99.9% | DC |  |
| column132 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SHORT CUT","29-SEP-20","29-SEP-20","29-SE... |  |
| column133 | VARCHAR | 99.9% |  DONALD J." |  |
| column134 | VARCHAR | 99.9% | P |  |
| column135 | VARCHAR | 99.9% | US |  |
| column136 | VARCHAR | 99.9% | 00 |  |
| column137 | VARCHAR | 99.9% | C30002844 |  |
| column138 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column139 | VARCHAR | 99.9% | 202009309284984685 |  |
| column140 | VARCHAR | 99.9% | SKDKNICKERBOCKER, LLC |  |
| column141 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column142 | VARCHAR | 99.9% | WASHINGTON |  |
| column143 | VARCHAR | 99.9% | DC |  |
| column144 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SHORT CUT","29-SEP-20","29-SEP-20","29-SE... |  |
| column145 | VARCHAR | 99.9% |  DONALD J." |  |
| column146 | VARCHAR | 99.9% | P |  |
| column147 | VARCHAR | 99.9% | US |  |
| column148 | VARCHAR | 99.9% | 00 |  |
| column149 | VARCHAR | 99.9% | C30002844 |  |
| column150 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column151 | VARCHAR | 99.9% | 202010099285099291 |  |
| column152 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column153 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column154 | VARCHAR | 99.9% | WASHINGTON |  |
| column155 | VARCHAR | 99.9% | DC |  |
| column156 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - SWOOP AND SHORT CUT","07-OCT-20","07-OCT-20","07... |  |
| column157 | VARCHAR | 99.9% |  THOM R. SEN." |  |
| column158 | VARCHAR | 99.9% | S |  |
| column159 | VARCHAR | 99.9% | NC |  |
| column160 | VARCHAR | 99.9% | 00 |  |
| column161 | VARCHAR | 99.9% | C30002844 |  |
| column162 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column163 | VARCHAR | 99.9% | 202010099285099291 |  |
| column164 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column165 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column166 | VARCHAR | 99.9% | WASHINGTON |  |
| column167 | VARCHAR | 99.9% | DC |  |
| column168 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - SWOOP AND SHORT CUT","07-OCT-20","07-OCT-20","07... |  |
| column169 | VARCHAR | 99.9% |  MARTHA" |  |
| column170 | VARCHAR | 99.9% | S |  |
| column171 | VARCHAR | 99.9% | AZ |  |
| column172 | VARCHAR | 99.9% | 00 |  |
| column173 | VARCHAR | 99.9% | C30002844 |  |
| column174 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column175 | VARCHAR | 99.9% | 202010099285099291 |  |
| column176 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column177 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column178 | VARCHAR | 99.9% | WASHINGTON |  |
| column179 | VARCHAR | 99.9% | DC |  |
| column180 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - SWOOP AND SHORT CUT","07-OCT-20","07-OCT-20","07... |  |
| column181 | VARCHAR | 99.9% |  JONI K" |  |
| column182 | VARCHAR | 99.9% | S |  |
| column183 | VARCHAR | 99.9% | IA |  |
| column184 | VARCHAR | 99.9% | 00 |  |
| column185 | VARCHAR | 99.9% | C30002844 |  |
| column186 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column187 | VARCHAR | 99.9% | 202010099285099291 |  |
| column188 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column189 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column190 | VARCHAR | 99.9% | WASHINGTON |  |
| column191 | VARCHAR | 99.9% | DC |  |
| column192 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - SWOOP AND SHORT CUT","07-OCT-20","07-OCT-20","07... |  |
| column193 | VARCHAR | 99.9% |  CORY" |  |
| column194 | VARCHAR | 99.9% | S |  |
| column195 | VARCHAR | 99.9% | CO |  |
| column196 | VARCHAR | 99.9% | 00 |  |
| column197 | VARCHAR | 99.9% | C30002844 |  |
| column198 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column199 | VARCHAR | 99.9% | 202010099285099291 |  |
| column200 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column201 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column202 | VARCHAR | 99.9% | WASHINGTON |  |
| column203 | VARCHAR | 99.9% | DC |  |
| column204 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - SWOOP AND SHORT CUT","07-OCT-20","07-OCT-20","07... |  |
| column205 | VARCHAR | 99.9% |  MARTHA" |  |
| column206 | VARCHAR | 99.9% | S |  |
| column207 | VARCHAR | 99.9% | AZ |  |
| column208 | VARCHAR | 99.9% | 00 |  |
| column209 | VARCHAR | 99.9% | C30002844 |  |
| column210 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column211 | VARCHAR | 99.9% | 202010099285099292 |  |
| column212 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column213 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column214 | VARCHAR | 99.9% | WASHINGTON |  |
| column215 | VARCHAR | 99.9% | DC |  |
| column216 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SWOOP","08-OCT-20","08-OCT-20","07-OCT-20... |  |
| column217 | VARCHAR | 99.9% |  JONI K" |  |
| column218 | VARCHAR | 99.9% | S |  |
| column219 | VARCHAR | 99.9% | IA |  |
| column220 | VARCHAR | 99.9% | 00 |  |
| column221 | VARCHAR | 99.9% | C30002844 |  |
| column222 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column223 | VARCHAR | 99.9% | 202010099285099292 |  |
| column224 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column225 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column226 | VARCHAR | 99.9% | WASHINGTON |  |
| column227 | VARCHAR | 99.9% | DC |  |
| column228 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SWOOP","08-OCT-20","08-OCT-20","07-OCT-20... |  |
| column229 | VARCHAR | 99.9% |  CORY" |  |
| column230 | VARCHAR | 99.9% | S |  |
| column231 | VARCHAR | 99.9% | CO |  |
| column232 | VARCHAR | 99.9% | 00 |  |
| column233 | VARCHAR | 99.9% | C30002844 |  |
| column234 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column235 | VARCHAR | 99.9% | 202010099285099292 |  |
| column236 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column237 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column238 | VARCHAR | 99.9% | WASHINGTON |  |
| column239 | VARCHAR | 99.9% | DC |  |
| column240 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SWOOP","08-OCT-20","08-OCT-20","07-OCT-20... |  |
| column241 | VARCHAR | 99.9% |  THOM R. SEN." |  |
| column242 | VARCHAR | 99.9% | S |  |
| column243 | VARCHAR | 99.9% | NC |  |
| column244 | VARCHAR | 99.9% | 00 |  |
| column245 | VARCHAR | 99.9% | C30002844 |  |
| column246 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column247 | VARCHAR | 99.9% | 202010099285099292 |  |
| column248 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column249 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column250 | VARCHAR | 99.9% | WASHINGTON |  |
| column251 | VARCHAR | 99.9% | DC |  |
| column252 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SWOOP","08-OCT-20","08-OCT-20","07-OCT-20... |  |
| column253 | VARCHAR | 99.9% |  DONALD J." |  |
| column254 | VARCHAR | 99.9% | P |  |
| column255 | VARCHAR | 99.9% | US |  |
| column256 | VARCHAR | 99.9% | 00 |  |
| column257 | VARCHAR | 99.9% | C30002844 |  |
| column258 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column259 | VARCHAR | 99.9% | 202010099285099292 |  |
| column260 | VARCHAR | 99.9% | SKDKNICKERBOCKER LLC |  |
| column261 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column262 | VARCHAR | 99.9% | WASHINGTON |  |
| column263 | VARCHAR | 99.9% | DC |  |
| column264 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - SWOOP","08-OCT-20","08-OCT-20","07-OCT-20... |  |
| column265 | VARCHAR | 99.9% |  DONALD J." |  |
| column266 | VARCHAR | 99.9% | P |  |
| column267 | VARCHAR | 99.9% | US |  |
| column268 | VARCHAR | 99.9% | 00 |  |
| column269 | VARCHAR | 99.9% | C30002844 |  |
| column270 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column271 | VARCHAR | 99.9% | 202010179297137450 |  |
| column272 | VARCHAR | 99.9% | SKDKNICKERBOCKER, LLC |  |
| column273 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column274 | VARCHAR | 99.9% | WASHINGTON |  |
| column275 | VARCHAR | 99.9% | DC |  |
| column276 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - EVERYWHERE","16-OCT-20","16-OCT-20","16-OCT-20",... |  |
| column277 | VARCHAR | 99.9% |  DONALD J." |  |
| column278 | VARCHAR | 99.9% | P |  |
| column279 | VARCHAR | 99.9% | US |  |
| column280 | VARCHAR | 99.9% | 00 |  |
| column281 | VARCHAR | 99.9% | C30002844 |  |
| column282 | VARCHAR | 99.9% | DEMAND JUSTICE A PROJECT OF SIXTEEN THIRTY FUND |  |
| column283 | VARCHAR | 99.9% | 202010179297137450 |  |
| column284 | VARCHAR | 99.9% | SKDKNICKERBOCKER, LLC |  |
| column285 | VARCHAR | 99.9% | 1150 18TH STREET NW |  |
| column286 | VARCHAR | 99.9% | WASHINGTON |  |
| column287 | VARCHAR | 99.9% | DC |  |
| column288 | VARCHAR | 99.9% | TELEVISION ADVERTISING PRODUCTION - EVERYWHERE","16-OCT-20","16-OCT-20","16-O... |  |
| column289 | VARCHAR | 99.9% |  MARTHA" |  |
| column290 | VARCHAR | 99.9% | S |  |
| column291 | VARCHAR | 99.9% | AZ |  |
| column292 | VARCHAR | 99.9% | 00 |  |
| column293 | VARCHAR | 99.9% | C30003040 |  |
| column294 | VARCHAR | 99.9% | DEMOCRACY FOR ALL 2021 ACTION A PROJECT OF SIXTEEN THIRTY FUND |  |
| column295 | VARCHAR | 99.9% | 202007149244555580 |  |
| column296 | VARCHAR | 99.9% | CHONG KOSTER LLC |  |
| column297 | VARCHAR | 99.9% | 1640 RHODE ISLAND NW |  |
| column298 | VARCHAR | 99.9% | WASHINGTON |  |
| column299 | VARCHAR | 99.9% | DC |  |
| column300 | VARCHAR | 99.9% | MEDIA PRODUCTION - COVID-19","13-JUL-20","13-JUL-20","13-JUL-20","4798.5","1"... |  |
| column301 | VARCHAR | 99.9% |  MARTHA" |  |
| column302 | VARCHAR | 99.9% | S |  |
| column303 | VARCHAR | 99.9% | AZ |  |
| column304 | VARCHAR | 99.9% | 00 |  |
| column305 | VARCHAR | 99.9% | C30003040 |  |
| column306 | VARCHAR | 99.9% | DEMOCRACY FOR ALL 2021 ACTION A PROJECT OF SIXTEEN THIRTY FUND |  |
| column307 | VARCHAR | 99.9% | 202007149244555580 |  |
| column308 | VARCHAR | 99.9% | CHONG KOSTER LLC |  |
| column309 | VARCHAR | 99.9% | 1640 RHODE ISLAND NW |  |
| column310 | VARCHAR | 99.9% | WASHINGTON |  |
| column311 | VARCHAR | 99.9% | DC |  |
| column312 | VARCHAR | 99.9% | TELEVISION ADVERTISING BUY - COVID-19","13-JUL-20","13-JUL-20","13-JUL-20","1... |  |
| column313 | VARCHAR | 99.9% |  JONATHAN" |  |
| column314 | VARCHAR | 99.9% | 625 SILVER AV. SW SUITE 320 |  |
| column315 | VARCHAR | 99.9% | ALBUQUERQUE |  |
| column316 | VARCHAR | 99.9% | NM |  |
| column317 | VARCHAR | 99.9% | CANVASSING |  |
| column318 | VARCHAR | 99.9% | 15-OCT-20 |  |
| column319 | VARCHAR | 99.9% | 15-OCT-20 |  |
| column320 | VARCHAR | 99.9% | 15-OCT-20 |  |
| column321 | VARCHAR | 99.9% | 60 |  |
| column322 | VARCHAR | 99.9% | 1 |  |
| column323 | VARCHAR | 99.9% | 60 |  |

## independent_expenditures

Independent expenditures for/against candidates

Rows: 664,775

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cand_id | VARCHAR | 9.4% | H0KY06104 |  |
| cand_name | VARCHAR | 0.0% | BISHOP, TIM |  |
| spe_id | VARCHAR | 0.0% | C00348540 |  |
| spe_nam | VARCHAR | 0.0% | 1199 SERVICE EMPLOYEES INTL UNION FEDERAL POLITICAL ACTION FUND |  |
| ele_type | VARCHAR | 0.0% | G |  |
| can_office_state | VARCHAR | 22.2% | NY |  |
| can_office_dis | VARCHAR | 0.1% | 01 |  |
| can_office | VARCHAR | 0.1% | H |  |
| cand_pty_aff | VARCHAR | 10.5% | REPUBLICAN PARTY |  |
| exp_amo | VARCHAR | 0.0% | 98844.72 |  |
| exp_date | VARCHAR | 11.5% | 14-OCT-10 |  |
| agg_amo | VARCHAR | 0.2% | 98844.72 |  |
| sup_opp | VARCHAR | 0.1% | S |  |
| pur | VARCHAR | 0.1% | MAILERS |  |
| pay | VARCHAR | 0.1% | PERSON 2 PERSON SOLUTIONS LLC |  |
| file_num | VARCHAR | 0.0% | 501574 |  |
| amndt_ind | VARCHAR | 0.0% | N |  |
| tran_id | VARCHAR | 0.0% | SE.8359 |  |
| image_num | VARCHAR | 0.0% | 10991375447 |  |
| receipt_dat | VARCHAR | 0.0% | 15-OCT-10 |  |
| fec_election_yr | VARCHAR | 0.0% | 2010 |  |
| prev_file_num | VARCHAR | 87.9% | 496366 |  |
| dissem_dt | DATE | 100.0% | 0001-12-30 (BC) |  |
| column023 | VARCHAR | 100.0% | 02-NOV-09 |  |
| column024 | VARCHAR | 100.0% | 374716.57 |  |
| column025 | VARCHAR | 100.0% | S |  |
| column026 | VARCHAR | 100.0% | IE TV BUY |  |
| column027 | VARCHAR | 100.0% | KNICKERBOCKER SKD |  |
| column028 | VARCHAR | 100.0% | 438581 |  |
| column029 | VARCHAR | 100.0% | N |  |
| column030 | VARCHAR | 100.0% | SE.6923 |  |
| column031 | VARCHAR | 100.0% | 29993305346 |  |
| column032 | VARCHAR | 100.0% | 02-NOV-09 |  |
| column033 | VARCHAR | 100.0% | 2010 |  |
| column034 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column035 | VARCHAR | 100.0% | 3978.58 |  |
| column036 | VARCHAR | 100.0% | 12-OCT-10 |  |
| column037 | VARCHAR | 100.0% | 49701.02 |  |
| column038 | VARCHAR | 100.0% | O |  |
| column039 | VARCHAR | 100.0% | Printing -  Donnelley the Spendificent |  |
| column040 | VARCHAR | 100.0% | Direct Response |  |
| column041 | VARCHAR | 100.0% | 500003 |  |
| column042 | VARCHAR | 100.0% | N |  |
| column043 | VARCHAR | 100.0% | F57.4177 |  |
| column044 | VARCHAR | 100.0% | 10931448798 |  |
| column045 | VARCHAR | 100.0% | 14-OCT-10 |  |
| column046 | VARCHAR | 100.0% | 2010 |  |
| column047 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column048 | VARCHAR | 100.0% | 7882.55 |  |
| column049 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column050 | VARCHAR | 100.0% | 3002964.55 |  |
| column051 | VARCHAR | 100.0% | O |  |
| column052 | VARCHAR | 100.0% | Video Production  - Skipped","Mentzer Media Services Inc.","500216","N","F57.... |  |
| column053 | VARCHAR | 100.0% |  JACK" |  |
| column054 | VARCHAR | 100.0% | C90011289 |  |
| column055 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column056 | VARCHAR | 100.0% | G |  |
| column057 | VARCHAR | 100.0% | TX |  |
| column058 | VARCHAR | 100.0% | 29 |  |
| column059 | VARCHAR | 100.0% | H |  |
| column060 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column061 | VARCHAR | 100.0% | 321952.02 |  |
| column062 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column063 | VARCHAR | 100.0% | 2984864.02 |  |
| column064 | VARCHAR | 100.0% | O |  |
| column065 | VARCHAR | 100.0% | Media Buy  - Going Home","Mentzer Media Services Inc.","500216","N","F57.4226... |  |
| column066 | VARCHAR | 100.0% |  JACK" |  |
| column067 | VARCHAR | 100.0% | C90011289 |  |
| column068 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column069 | VARCHAR | 100.0% | G |  |
| column070 | VARCHAR | 100.0% | TX |  |
| column071 | VARCHAR | 100.0% | 29 |  |
| column072 | VARCHAR | 100.0% | H |  |
| column073 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column074 | VARCHAR | 100.0% | 10217.98 |  |
| column075 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column076 | VARCHAR | 100.0% | 2995082 |  |
| column077 | VARCHAR | 100.0% | O |  |
| column078 | VARCHAR | 100.0% | Video Production  - Going Home","Mentzer Media Services Inc.","500216","N","F... |  |
| column079 | VARCHAR | 100.0% |  JOSEPH A JR" |  |
| column080 | VARCHAR | 100.0% | C90011289 |  |
| column081 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column082 | VARCHAR | 100.0% | G |  |
| column083 | VARCHAR | 100.0% | PA |  |
| column084 | VARCHAR | 100.0% | 00 |  |
| column085 | VARCHAR | 100.0% | S |  |
| column086 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column087 | VARCHAR | 100.0% | 315520.85 |  |
| column088 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column089 | VARCHAR | 100.0% | 315520.85 |  |
| column090 | VARCHAR | 100.0% | O |  |
| column091 | VARCHAR | 100.0% | Media Buy - Gas","Neylan & Partners","500216","N","F57.4210","10931453623","1... |  |
| column092 | VARCHAR | 100.0% |  JOSEPH A JR" |  |
| column093 | VARCHAR | 100.0% | C90011289 |  |
| column094 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column095 | VARCHAR | 100.0% | G |  |
| column096 | VARCHAR | 100.0% | PA |  |
| column097 | VARCHAR | 100.0% | 00 |  |
| column098 | VARCHAR | 100.0% | S |  |
| column099 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column100 | VARCHAR | 100.0% | 320 |  |
| column101 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column102 | VARCHAR | 100.0% | 12872 |  |
| column103 | VARCHAR | 100.0% | O |  |
| column104 | VARCHAR | 100.0% | DG - GAS","UPGRADE FILMS","500216","N","F57.4216","10931453624","15-OCT-10","... |  |
| column105 | VARCHAR | 100.0% |  JOSEPH A JR" |  |
| column106 | VARCHAR | 100.0% | C90011289 |  |
| column107 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column108 | VARCHAR | 100.0% | G |  |
| column109 | VARCHAR | 100.0% | PA |  |
| column110 | VARCHAR | 100.0% | 00 |  |
| column111 | VARCHAR | 100.0% | S |  |
| column112 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column113 | VARCHAR | 100.0% | 1395 |  |
| column114 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column115 | VARCHAR | 100.0% | 1395 |  |
| column116 | VARCHAR | 100.0% | O |  |
| column117 | VARCHAR | 100.0% | Audio Design - GAS","UPGRADE FILMS","500216","N","F57.4212","10931453623","15... |  |
| column118 | VARCHAR | 100.0% |  JOSEPH A JR" |  |
| column119 | VARCHAR | 100.0% | C90011289 |  |
| column120 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column121 | VARCHAR | 100.0% | G |  |
| column122 | VARCHAR | 100.0% | PA |  |
| column123 | VARCHAR | 100.0% | 00 |  |
| column124 | VARCHAR | 100.0% | S |  |
| column125 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column126 | VARCHAR | 100.0% | 1583 |  |
| column127 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column128 | VARCHAR | 100.0% | 12552 |  |
| column129 | VARCHAR | 100.0% | O |  |
| column130 | VARCHAR | 100.0% | Voice Over Talant - GAS","UPGRADE FILMS","500216","N","F57.4215","10931453624... |  |
| column131 | VARCHAR | 100.0% |  JOSEPH A JR" |  |
| column132 | VARCHAR | 100.0% | C90011289 |  |
| column133 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column134 | VARCHAR | 100.0% | G |  |
| column135 | VARCHAR | 100.0% | PA |  |
| column136 | VARCHAR | 100.0% | 00 |  |
| column137 | VARCHAR | 100.0% | S |  |
| column138 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column139 | VARCHAR | 100.0% | 9574 |  |
| column140 | VARCHAR | 100.0% | 13-OCT-10 |  |
| column141 | VARCHAR | 100.0% | 10969 |  |
| column142 | VARCHAR | 100.0% | O |  |
| column143 | VARCHAR | 100.0% | Video Editing - GAS","UPGRADE FILMS","500216","N","F57.4214","10931453623","1... |  |
| column144 | VARCHAR | 100.0% |  ZACHARY T" |  |
| column145 | VARCHAR | 100.0% | C90011289 |  |
| column146 | VARCHAR | 100.0% | AMERICANS FOR TAX REFORM |  |
| column147 | VARCHAR | 100.0% | G |  |
| column148 | VARCHAR | 100.0% | OH |  |
| column149 | VARCHAR | 100.0% | 18 |  |
| column150 | VARCHAR | 100.0% | H |  |
| column151 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column152 | VARCHAR | 100.0% | 250 |  |
| column153 | VARCHAR | 100.0% | 12-OCT-10 |  |
| column154 | VARCHAR | 100.0% | 77623.83 |  |
| column155 | VARCHAR | 100.0% | O |  |
| column156 | VARCHAR | 100.0% | Design -  Zach Space the Spendificent |  |
| column157 | VARCHAR | 100.0% | Direct Response |  |
| column158 | VARCHAR | 100.0% | 500003 |  |
| column159 | VARCHAR | 100.0% | N |  |
| column160 | VARCHAR | 100.0% | F57.4182 |  |
| column161 | VARCHAR | 100.0% | 10931448800 |  |
| column162 | VARCHAR | 100.0% | 14-OCT-10 |  |
| column163 | VARCHAR | 100.0% | 2010 |  |
| column164 | VARCHAR | 100.0% | REPUBLICAN PARTY |  |
| column165 | VARCHAR | 100.0% | 119092 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |
| column166 | VARCHAR | 100.0% | 22-OCT-12 |  |
| column167 | VARCHAR | 100.0% | 194512.74 |  |
| column168 | VARCHAR | 100.0% | O |  |
| column169 | VARCHAR | 100.0% | MPND12016 - Medicare #5 |  |
| column170 | VARCHAR | 100.0% | MACK CROUNSE GROUP, LLC |  |
| column171 | VARCHAR | 100.0% | 824364 |  |
| column172 | VARCHAR | 100.0% | N |  |
| column173 | VARCHAR | 100.0% | SE.274532 |  |
| column174 | VARCHAR | 100.0% | 12940383195 |  |
| column175 | VARCHAR | 100.0% | 23-OCT-12 |  |
| column176 | VARCHAR | 100.0% | 2012 |  |
| column177 | VARCHAR | 100.0% | REPUBLICAN PARTY |  |
| column178 | VARCHAR | 100.0% | 238493.8 |  |
| column179 | VARCHAR | 100.0% | 17-SEP-12 |  |
| column180 | VARCHAR | 100.0% | 238493.8 |  |
| column181 | VARCHAR | 100.0% | O |  |
| column182 | VARCHAR | 100.0% | TV ads Rooster","WATERFRONT STRATEGIES","810567","N","SE.268919","12952944641... |  |
| column183 | VARCHAR | 100.0% |  JEFF" |  |
| column184 | VARCHAR | 100.0% | C00011114 |  |
| column185 | VARCHAR | 100.0% | AMERICAN FEDERATION OF STATE COUNTY & MUNICIPAL EMPLOYEES  P E O P L E |  |
| column186 | VARCHAR | 100.0% | G |  |
| column187 | VARCHAR | 100.0% | CA |  |
| column188 | VARCHAR | 100.0% | 10 |  |
| column189 | VARCHAR | 100.0% | H |  |
| column190 | VARCHAR | 100.0% | REPUBLICAN PARTY |  |
| column191 | VARCHAR | 100.0% | 9450.88 |  |
| column192 | VARCHAR | 100.0% | 15-OCT-12 |  |
| column193 | VARCHAR | 100.0% | 175509.95 |  |
| column194 | VARCHAR | 100.0% | O |  |
| column195 | VARCHAR | 100.0% | Online ad Casa","ADELSTEIN LISTON","819768","N","SE.272674","12972713611","17... |  |
| column196 | VARCHAR | 100.0% |  JEFF" |  |
| column197 | VARCHAR | 100.0% | C00011114 |  |
| column198 | VARCHAR | 100.0% | AMERICAN FEDERATION OF STATE COUNTY & MUNICIPAL EMPLOYEES  P E O P L E |  |
| column199 | VARCHAR | 100.0% | G |  |
| column200 | VARCHAR | 100.0% | CA |  |
| column201 | VARCHAR | 100.0% | 10 |  |
| column202 | VARCHAR | 100.0% | H |  |
| column203 | VARCHAR | 100.0% | REPUBLICAN PARTY |  |
| column204 | VARCHAR | 100.0% | 166059.07 |  |
| column205 | VARCHAR | 100.0% | 15-OCT-12 |  |
| column206 | VARCHAR | 100.0% | 166059.07 |  |
| column207 | VARCHAR | 100.0% | O |  |
| column208 | VARCHAR | 100.0% | TV ads Behind Casa |  |
| column209 | VARCHAR | 100.0% | ADELSTEIN LISTON |  |
| column210 | VARCHAR | 100.0% | 819768 |  |
| column211 | VARCHAR | 100.0% | N |  |
| column212 | VARCHAR | 100.0% | SE.272672 |  |
| column213 | VARCHAR | 100.0% | 12972713611 |  |
| column214 | VARCHAR | 100.0% | 17-OCT-12 |  |
| column215 | VARCHAR | 100.0% | 2012 |  |
| column216 | VARCHAR | 100.0% | DEMOCRATIC PARTY |  |
| column217 | VARCHAR | 100.0% | 204.75 |  |
| column23 | VARCHAR | 99.9% | 06-NOV-16 |  |
| column24 | VARCHAR | 100.0% | 99042.2 |  |
| column25 | VARCHAR | 100.0% | O |  |
| column26 | VARCHAR | 100.0% | Salaries. Various meme posts on social media |  |
| column27 | VARCHAR | 100.0% | 350.org |  |
| column28 | VARCHAR | 100.0% | 1136048 |  |
| column29 | VARCHAR | 100.0% | A1 |  |
| column30 | VARCHAR | 100.0% | F57.000001 |  |
| column31 | VARCHAR | 100.0% | 201612229040900339 |  |
| column32 | VARCHAR | 100.0% | 22-DEC-16 |  |
| column33 | VARCHAR | 100.0% | 2016 |  |
| column34 | VARCHAR | 100.0% | 1125318 |  |
| column35 | VARCHAR | 100.0% | 09-AUG-16 |  |
| column36 | VARCHAR | 100.0% | 11-OCT-16 |  |
| column37 | VARCHAR | 100.0% | 3508975.41 |  |
| column38 | VARCHAR | 100.0% | O |  |
| column39 | VARCHAR | 100.0% | Radio ad  Production Cost Bogus","DIXON/DAVIS MEDIA GROU |  |
| column40 | VARCHAR | 100.0% |  LLC" |  |
| column41 | VARCHAR | 100.0% | 1107047 |  |
| column42 | VARCHAR | 100.0% | N |  |
| column43 | VARCHAR | 100.0% | SE.129395 |  |
| column44 | VARCHAR | 100.0% | 201610149032517121 |  |
| column45 | VARCHAR | 100.0% | 14-OCT-16 |  |
| column46 | VARCHAR | 100.0% | 2016 |  |
| column47 | VARCHAR | 100.0% | REPUBLICAN PARTY |  |
| column48 | VARCHAR | 100.0% | 12-OCT-16 |  |
| column49 | VARCHAR | 100.0% | 22-SEP-16 |  |
| column50 | VARCHAR | 100.0% | 919149 |  |
| column51 | VARCHAR | 100.0% | O |  |
| column52 | VARCHAR | 100.0% | TV ad  Production Cost Weaken Us |  |
| column53 | VARCHAR | 100.0% | AL MEDIA LLC |  |
| column54 | VARCHAR | 100.0% | 1101110 |  |
| column55 | VARCHAR | 100.0% | N |  |
| column56 | VARCHAR | 100.0% | SE.126836 |  |
| column57 | VARCHAR | 100.0% | 201609229032101262 |  |
| column58 | VARCHAR | 100.0% | 22-SEP-16 |  |
| column59 | VARCHAR | 100.0% | 2016 |  |
| column60 | VARCHAR | 100.0% | S |  |
| column61 | VARCHAR | 100.0% | 20-SEP-16 |  |

## individual_contributions

Every individual donation: name, employer, occupation, amount, date

Rows: 268,792,987

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00369926 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q1 | Report type code |
| TRANSACTION_PGI | VARCHAR | 17.1% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 23990740119 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15C |  |
| ENTITY_TP | VARCHAR | 0.2% | CAN | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.0% | STATON, CECIL P. DR. JR. |  |
| CITY | VARCHAR | 0.0% | ROME |  |
| STATE | VARCHAR | 0.1% | GA |  |
| ZIP_CODE | VARCHAR | 0.1% | 30161 |  |
| EMPLOYER | VARCHAR | 4.6% | SMYTH & HELWYS PUBLISHING CO. |  |
| OCCUPATION | VARCHAR | 4.3% | PRESIDENT |  |
| TRANSACTION_DT | DATE | 0.0% | 2003-03-01 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 14000.0 |  |
| OTHER_ID | VARCHAR | 42.4% | H2GA11131 |  |
| TRAN_ID | VARCHAR | 0.2% | SA11D.7240 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 82127 |  |
| MEMO_CD | VARCHAR | 99.5% | X |  |
| MEMO_TEXT | VARCHAR | 42.1% | PARTNERSHIP->DORSEY NATIONAL FUND |  |
| SUB_ID | VARCHAR | 0.0% | 4042320031031003165 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## operating_expenditures

Committee operating expenditures: payee, purpose, amount

Rows: 18,875,347

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00382036 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_YR | VARCHAR | 0.0% | 2003 |  |
| RPT_TP | VARCHAR | 0.0% | M11 | Report type code |
| IMAGE_NUM | VARCHAR | 0.0% | 24971947861 |  |
| LINE_NUM | VARCHAR | 0.0% | 21B |  |
| FORM_TP_CD | VARCHAR | 0.0% | F3X |  |
| SCHED_TP_CD | VARCHAR | 0.0% | SB |  |
| NAME | VARCHAR | 0.1% | CAPITOL GAINS CORP. |  |
| CITY | VARCHAR | 0.3% | MIAMI |  |
| STATE | VARCHAR | 0.3% | FL |  |
| ZIP_CODE | VARCHAR | 0.5% | 33173 |  |
| TRANSACTION_DT | DATE | 100.0% |  |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 4000.0 |  |
| TRANSACTION_PGI | VARCHAR | 48.5% | O |  |
| PURPOSE | VARCHAR | 0.4% | FUNDRAISING FEES |  |
| CATEGORY | VARCHAR | 72.9% | 001 |  |
| CATEGORY_DESC | VARCHAR | 74.1% | Administrative/Salary/Overhead Expenses  |  |
| MEMO_CD | VARCHAR | 72.8% | X |  |
| MEMO_TEXT | VARCHAR | 78.7% | BANK FEES |  |
| ENTITY_TP | VARCHAR | 7.9% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| SUB_ID | VARCHAR | 0.0% | 4121320041046623499 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 0.0% | 152566 |  |
| TRAN_ID | VARCHAR | 0.0% | DISB00021831WJ | Transaction identifier within a committee |
| BACK_REF_TRAN_ID | VARCHAR | 79.4% | B21(B)330 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## v_candidate_totals

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H6MI10284 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | KHANNA, ROHIT |  |
| party | VARCHAR | 0.0% | DEM |  |
| office | VARCHAR | 0.0% | H |  |
| state | VARCHAR | 0.0% | NC |  |
| cycle | INTEGER | 0.0% | 2026 | Election cycle (even year), present in all FEC tables |
| num_contributions | BIGINT | 0.0% | 463 |  |
| total_individual | DOUBLE | 0.0% | 58698.0 |  |

## v_daily_donations

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| date | DATE | 0.0% | 2010-06-30 |  |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |
| num_donations | BIGINT | 0.0% | 1471 |  |
| total_amount | DOUBLE | 0.0% | 10960701.0 |  |
| avg_amount | DOUBLE | 0.0% | 882.1629189647857 |  |
| median_amount | DOUBLE | 0.0% | 500.0 |  |

## v_pac_to_candidate

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| pac_name | VARCHAR | 0.0% | MICHIGAN INDEPENDENT POLITICAL ACTION COMMITTEE |  |
| connected_org | VARCHAR | 46.7% | Business Council Victory Fund |  |
| candidate_name | VARCHAR | 0.0% | BEAUPREZ, ROBERT LOUIS |  |
| candidate_party | VARCHAR | 0.0% | DEM |  |
| office | VARCHAR | 0.0% | S |  |
| state | VARCHAR | 0.0% | CO |  |
| amount | DOUBLE | 0.0% | 5000.0 |  |
| date | DATE | 0.5% | 2012-11-02 |  |
| cycle | INTEGER | 0.0% | 2006 | Election cycle (even year), present in all FEC tables |

## v_top_donors

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| NAME | VARCHAR | 0.0% | STERN, DAVID |  |
| EMPLOYER | VARCHAR | 11.8% | SELF-EMPLOYED |  |
| OCCUPATION | VARCHAR | 9.7% | STUDENT |  |
| STATE | VARCHAR | 0.2% | IL |  |
| num_contributions | BIGINT | 0.0% | 1 |  |
| total_donated | DOUBLE | 0.0% | 500.0 |  |
| first_cycle | INTEGER | 0.0% | 2004 |  |
| last_cycle | INTEGER | 0.0% | 2004 |  |
| num_committees | BIGINT | 0.0% | 1 |  |
