# Data Dictionary

Source: [FEC Bulk Data](https://www.fec.gov/data/browse-data/?tab=bulk-data)

## candidate_committee_links

Which committees are authorized by which candidates

Rows: 74,141

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H0AK00055 | Candidate ID, joins across candidates and contribution tables |
| CAND_ELECTION_YR | INTEGER | 0.0% | 2000 |  |
| FEC_ELECTION_YR | VARCHAR | 0.0% | 2004 |  |
| CMTE_ID | VARCHAR | 0.0% | C00361626 | Committee ID, joins to committees table and contribution tables |
| CMTE_TP | VARCHAR | 0.0% | H |  |
| CMTE_DSGN | VARCHAR | 0.0% | P |  |
| LINKAGE_ID | VARCHAR | 0.0% | 56 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## candidates

Candidate master: name, party, office, state, district, status

Rows: 76,279

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H0AK00055 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | GREENE, CLIFFORD MARK |  |
| CAND_PTY_AFFILIATION | VARCHAR | 0.1% | DEM |  |
| CAND_ELECTION_YR | INTEGER | 0.0% | 2000 |  |
| CAND_OFFICE_ST | VARCHAR | 0.0% | AK |  |
| CAND_OFFICE | VARCHAR | 0.0% | H |  |
| CAND_OFFICE_DISTRICT | VARCHAR | 0.8% | 00 |  |
| CAND_ICI | VARCHAR | 4.5% | C |  |
| CAND_STATUS | VARCHAR | 0.0% | N |  |
| CAND_PCC | VARCHAR | 17.4% | C00361626 | Candidate principal campaign committee, joins candidates to committees.CMTE_ID |
| CAND_ST1 | VARCHAR | 1.3% | PO BOX 20745 |  |
| CAND_ST2 | VARCHAR | 91.2% | PO BOX 374 |  |
| CAND_CITY | VARCHAR | 0.1% | JUNEAU |  |
| CAND_ST | VARCHAR | 1.0% | AK |  |
| CAND_ZIP | VARCHAR | 1.4% | 99802 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committee_contributions

PAC/party contributions to candidates

Rows: 5,261,682

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00422774 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | M5 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.9% | G2020 |  |
| IMAGE_NUM | VARCHAR | 0.0% | 25990878410 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24K |  |
| ENTITY_TP | VARCHAR | 2.4% | CCM | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 1.3% | PETE KING FOR CONGRESS COMMITTEE |  |
| CITY | VARCHAR | 1.4% | CONCORD |  |
| STATE | VARCHAR | 1.4% | IA |  |
| ZIP_CODE | VARCHAR | 1.4% | 12801 |  |
| EMPLOYER | VARCHAR | 100.0% | JIM BUNNING FOR SENATE |  |
| OCCUPATION | VARCHAR | 100.0% | SENATOR |  |
| TRANSACTION_DT | DATE | 0.5% | 2005-04-25 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 1000.0 |  |
| OTHER_ID | VARCHAR | 0.0% | C00238378 |  |
| CAND_ID | VARCHAR | 0.2% | H0IA02040 | Candidate ID, joins across candidates and contribution tables |
| TRAN_ID | VARCHAR | 0.7% | SB23.9921 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.6% | 1494216 |  |
| MEMO_CD | VARCHAR | 98.3% | X |  |
| MEMO_TEXT | VARCHAR | 89.3% | VOID - CONOR LAMB FOR CONGRESS |  |
| SUB_ID | VARCHAR | 0.0% | 4051720051057476207 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2006 | Election cycle (even year), present in all FEC tables |

## committee_to_committee

Transfers between committees

Rows: 46,486,423

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00035600 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | M10 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.8% | P2012 |  |
| IMAGE_NUM | VARCHAR | 0.0% | 13962188750 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15J |  |
| ENTITY_TP | VARCHAR | 0.5% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.2% | ENGEL, MARCY |  |
| CITY | VARCHAR | 0.2% | OGDEN |  |
| STATE | VARCHAR | 0.2% | NY |  |
| ZIP_CODE | VARCHAR | 0.2% | 10583 |  |
| EMPLOYER | VARCHAR | 20.1% | INDIAN TRIBE |  |
| OCCUPATION | VARCHAR | 20.0% | RETIRED |  |
| TRANSACTION_DT | DATE | 0.1% | 2012-03-06 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 25.0 |  |
| OTHER_ID | VARCHAR | 80.2% | C00431445 |  |
| TRAN_ID | VARCHAR | 0.2% | C7790569 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 1440221 |  |
| MEMO_CD | VARCHAR | 19.6% | X |  |
| MEMO_TEXT | VARCHAR | 51.0% | TRANSFER FROM TRUMP MAKE AMERICA GREAT AGAIN COMMITTEE |  |
| SUB_ID | VARCHAR | 0.0% | 4110420091120447618 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |

## committees

Committee master: name, type, party, treasurer, connected org

Rows: 184,883

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00000042 | Committee ID, joins to committees table and contribution tables |
| CMTE_NM | VARCHAR | 0.0% | ILLINOIS TOOL WORKS FOR BETTER GOVERNMENT COMMITTEE |  |
| TRES_NM | VARCHAR | 5.0% | LYNCH, MICHAEL J. MR. |  |
| CMTE_ST1 | VARCHAR | 0.1% | 3600 W. Lake Avenue |  |
| CMTE_ST2 | VARCHAR | 77.8% | MD#288 |  |
| CMTE_CITY | VARCHAR | 0.1% | Glenview |  |
| CMTE_ST | VARCHAR | 0.1% | IL |  |
| CMTE_ZIP | VARCHAR | 0.1% | 60026 |  |
| CMTE_DSGN | VARCHAR | 0.0% | U |  |
| CMTE_TP | VARCHAR | 0.0% | Q |  |
| CMTE_PTY_AFFILIATION | VARCHAR | 59.3% | UNK |  |
| CMTE_FILING_FREQ | VARCHAR | 0.0% | Q |  |
| ORG_TP | VARCHAR | 77.7% | C |  |
| CONNECTED_ORG_NM | VARCHAR | 51.2% | AMERICAN MEDICAL ASSOCIATION |  |
| CAND_ID | VARCHAR | 63.0% | H6TX07029 | Candidate ID, joins across candidates and contribution tables |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## communication_costs

Internal communications supporting/opposing candidates

Rows: 25,590

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
| TRANSACTION_DT | DATE | 0.5% | 2010-10-29 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 17194.83 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24N |  |
| COMMUNICATION_TP | VARCHAR | 1.6% | DM |  |
| COMMUNICATION_CLASS | VARCHAR | 2.2% | M |  |
| SUPPORT_OPPOSE_IND | VARCHAR | 1.2% | O |  |
| IMAGE_NUM | VARCHAR | 0.0% | http://docquery.fec.gov/cgi-bin/fecimg/?11030583334 |  |
| LINE_NUM | VARCHAR | 99.7% | http://docquery.fec.gov/cgi-bin/fecimg/?11030583331 |  |
| FORM_TP_CD | VARCHAR | 0.3% | F7 |  |
| SCHED_TP_CD | VARCHAR | 0.0% | F76 |  |
| TRAN_ID | VARCHAR | 15.2% | F760407131410781 | Transaction identifier within a committee |
| SUB_ID | VARCHAR | 0.0% | 2061420111140795867 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 1.2% | 721035 |  |
| RPT_YR | VARCHAR | 0.0% | 2010 |  |
| CAND_STATE_DESCRIPTION | VARCHAR | 0.0% | NEW YORK |  |
| CAND_PTY_AFFILIATION_DESCRIPTION | VARCHAR | 0.0% | Republican Party |  |
| PURPOSE | VARCHAR | 99.7% | Republican Party |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## electioneering_communications

Broadcast ads mentioning candidates near elections

Rows: 1,577

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CANDIDATE_ID | VARCHAR | 16.7% | S8WI00026 |  |
| CANDIDATE_NAME | VARCHAR | 17.0% | FEINGOLD, RUSSELL D |  |
| CANDIDATE_OFFICE | VARCHAR | 17.0% | S |  |
| CANDIDATE_STATE | VARCHAR | 17.0% | WI |  |
| CANDIDATE_DISTRICT | VARCHAR | 17.0% | 00 |  |
| COMMITTEE_ID | VARCHAR | 0.0% | C30001648 |  |
| COMMITTEE_NAME | VARCHAR | 0.0% | AMERICAN ACTION NETWORK |  |
| SB_IMAGE_NUM | VARCHAR | 0.0% | 10932121746 |  |
| PAYEE_NAME | VARCHAR | 0.0% | SMART MEDIA GROUP |  |
| PAYEE_STREET | VARCHAR | 0.0% | 814 KING STREET STE 400 |  |
| PAYEE_CITY | VARCHAR | 0.0% | ALEXANDRIA |  |
| PAYEE_STATE | VARCHAR | 0.1% | VA |  |
| DISBURSEMENT_DESCRIPTION | VARCHAR | 9.2% | MEDIA TV AD PRODUCTION - BUCKET |  |
| DISBURSEMENT_DATE | DATE | 1.6% | 2010-09-30 |  |
| COMMUNICATION_DATE | DATE | 2.7% | 2010-09-30 |  |
| PUBLIC_DISBURSEMENT_DATE | DATE | 1.6% | 2010-09-30 |  |
| REPORTED_DISBURSEMENT_AMOUNT | DOUBLE | 0.3% | 290395.0 |  |
| NUMBER_OF_CANDIDATES | VARCHAR | 0.0% | 1 |  |
| CALCULATED_CANDIDATE_SHARE | DOUBLE | 1.3% | 290395.0 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## independent_expenditures

Independent expenditures for/against candidates

Rows: 596,985

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cand_id | VARCHAR | 8.9% | H4CO08034 |  |
| cand_name | VARCHAR | 0.0% | Evans, Gabe |  |
| spe_id | VARCHAR | 0.0% | C00018929 |  |
| spe_nam | VARCHAR | 0.0% | House Majority PAC |  |
| ele_type | VARCHAR | 0.0% | G |  |
| can_office_state | VARCHAR | 22.6% | CO |  |
| can_office_dis | VARCHAR | 0.1% | 00 |  |
| can_office | VARCHAR | 0.1% | P |  |
| cand_pty_aff | VARCHAR | 10.1% | REPUBLICAN PARTY |  |
| exp_amo | DOUBLE | 0.1% | 1517.47 |  |
| exp_date | DATE | 11.8% | 2024-09-27 |  |
| agg_amo | DOUBLE | 0.2% | 9000.0 |  |
| sup_opp | VARCHAR | 0.1% | S |  |
| pur | VARCHAR | 0.1% | In Kind Staff |  |
| pay | VARCHAR | 0.1% | TTHM.com |  |
| file_num | VARCHAR | 0.0% | 1845617 |  |
| amndt_ind | VARCHAR | 0.0% | N |  |
| tran_id | VARCHAR | 0.0% | E2D2833410CAA40CB9A5 |  |
| image_num | VARCHAR | 0.0% | 202410319719900778 |  |
| receipt_dat | DATE | 0.2% | 2024-10-31 |  |
| fec_election_yr | VARCHAR | 0.1% | 2024 |  |
| prev_file_num | VARCHAR | 88.1% | 1832140 |  |
| dissem_dt | DATE | 58.0% | 2018-10-24 |  |
| cycle | INTEGER | 0.0% | 2024 | Election cycle (even year), present in all FEC tables |

## individual_contributions

Every individual donation: name, employer, occupation, amount, date

Rows: 275,049,839

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00364497 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | YE | Report type code |
| TRANSACTION_PGI | VARCHAR | 16.7% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 27930558902 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15 |  |
| ENTITY_TP | VARCHAR | 0.2% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.0% | HOTZE, ERNEST |  |
| CITY | VARCHAR | 0.0% | GRANVILLE |  |
| STATE | VARCHAR | 0.1% | NY |  |
| ZIP_CODE | VARCHAR | 0.1% | 43023 |  |
| EMPLOYER | VARCHAR | 4.5% | VERMEER MANFACTURING |  |
| OCCUPATION | VARCHAR | 4.3% | CHAIRMAN AND CEO |  |
| TRANSACTION_DT | DATE | 0.0% | 2012-03-26 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 500.0 |  |
| OTHER_ID | VARCHAR | 42.2% | C00000422 |  |
| TRAN_ID | VARCHAR | 0.2% | C3934388 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 778552 |  |
| MEMO_CD | VARCHAR | 99.4% | X |  |
| MEMO_TEXT | VARCHAR | 42.1% | * IN-KIND: CATERING |  |
| SUB_ID | VARCHAR | 0.0% | 2022320041035988331 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |

## operating_expenditures

Committee operating expenditures: payee, purpose, amount

Rows: 19,413,938

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00378125 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_YR | VARCHAR | 0.0% | 2003 |  |
| RPT_TP | VARCHAR | 0.0% | YE | Report type code |
| IMAGE_NUM | VARCHAR | 0.0% | 202505159761326822 |  |
| LINE_NUM | VARCHAR | 0.0% | 23 |  |
| FORM_TP_CD | VARCHAR | 0.0% | F3P |  |
| SCHED_TP_CD | VARCHAR | 0.0% | SB |  |
| NAME | VARCHAR | 0.1% | RABBIDEAU, ABIGAIL |  |
| CITY | VARCHAR | 0.3% | ANN ARBOR |  |
| STATE | VARCHAR | 0.3% | MN |  |
| ZIP_CODE | VARCHAR | 0.5% | 481042642 |  |
| TRANSACTION_DT | DATE | 0.0% | 2015-07-31 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 850.0 |  |
| TRANSACTION_PGI | VARCHAR | 48.2% | P |  |
| PURPOSE | VARCHAR | 0.5% | CONTRACTOR STIPEND |  |
| CATEGORY | VARCHAR | 72.8% | 001 |  |
| CATEGORY_DESC | VARCHAR | 73.9% | Advertising Expenses  |  |
| MEMO_CD | VARCHAR | 72.9% | X |  |
| MEMO_TEXT | VARCHAR | 78.8% | * IN-KIND RECEIVED |  |
| ENTITY_TP | VARCHAR | 7.6% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| SUB_ID | VARCHAR | 0.0% | 4051620251202939118 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 0.0% | 109872 |  |
| TRAN_ID | VARCHAR | 0.0% | D317625 | Transaction identifier within a committee |
| BACK_REF_TRAN_ID | VARCHAR | 79.3% | SB23-3127 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## v_candidate_totals

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cycle | INTEGER | 0.0% | 2024 | Election cycle (even year), present in all FEC tables |
| CMTE_ID | VARCHAR | 0.0% | C00313247 | Committee ID, joins to committees table and contribution tables |
| cand_ids | VARCHAR | 0.0% | H0CA15171 |  |
| candidate_names | VARCHAR | 0.0% | MOORE, DWIGHT CLINT |  |
| party | VARCHAR | 0.0% | DEM |  |
| office | VARCHAR | 0.0% | S |  |
| state | VARCHAR | 0.0% | CA |  |
| num_contributions | BIGINT | 0.0% | 357 |  |
| net_individual | DOUBLE | 0.0% | 499825.0 |  |

## v_daily_donations

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| date | DATE | 0.0% | 2018-09-25 |  |
| cycle | INTEGER | 0.0% | 2016 | Election cycle (even year), present in all FEC tables |
| num_donations | BIGINT | 0.0% | 45814 |  |
| total_amount | DOUBLE | 0.0% | 7949396.0 |  |
| avg_amount | DOUBLE | 0.0% | 1207.9074702886248 |  |
| median_amount | DOUBLE | 0.0% | 500.0 |  |

## v_pac_to_candidate

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| pac_name | VARCHAR | 0.0% | KPMG PARTNERS/PRINCIPALS & EMPLOYEES POLITICAL ACTION COMMITTEE |  |
| connected_org | VARCHAR | 42.0% | NONE |  |
| candidate_name | VARCHAR | 0.0% | THUNE, JOHN R |  |
| candidate_party | VARCHAR | 0.0% | REP |  |
| office | VARCHAR | 0.0% | H |  |
| state | VARCHAR | 0.0% | KS |  |
| transaction_type | VARCHAR | 0.0% | 24K |  |
| amount | DOUBLE | 0.0% | 1000.0 |  |
| date | DATE | 0.0% | 2004-10-06 |  |
| cycle | INTEGER | 0.0% | 2020 | Election cycle (even year), present in all FEC tables |

## v_top_donors

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| NAME | VARCHAR | 0.0% | STEPHENSON, RICHARD G |  |
| EMPLOYER | VARCHAR | 12.3% | N/A |  |
| OCCUPATION | VARCHAR | 10.1% | INVESTMENT ADVISOR |  |
| STATE | VARCHAR | 0.2% | CA |  |
| num_contributions | BIGINT | 0.0% | 108 |  |
| net_donated | DOUBLE | 0.0% | 3000.0 |  |
| first_cycle | INTEGER | 0.0% | 2016 |  |
| last_cycle | INTEGER | 0.0% | 2018 |  |
| num_committees | BIGINT | 0.0% | 1 |  |
