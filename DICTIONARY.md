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
| CMTE_ID | VARCHAR | 0.0% | C00694323 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | M5 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.9% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 26930439860 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24K |  |
| ENTITY_TP | VARCHAR | 2.4% | CAN | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 1.3% | ELISE FOR CONGRESS |  |
| CITY | VARCHAR | 1.4% | MINDEN |  |
| STATE | VARCHAR | 1.4% | IA |  |
| ZIP_CODE | VARCHAR | 1.4% | 12801 |  |
| EMPLOYER | VARCHAR | 100.0% | N/A |  |
| OCCUPATION | VARCHAR | 100.0% | SENATOR |  |
| TRANSACTION_DT | DATE | 0.5% | 2005-04-25 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 5000.0 |  |
| OTHER_ID | VARCHAR | 0.0% | C00721670 |  |
| CAND_ID | VARCHAR | 0.2% | H8IL18043 | Candidate ID, joins across candidates and contribution tables |
| TRAN_ID | VARCHAR | 0.7% | D6226 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.6% | 1494216 |  |
| MEMO_CD | VARCHAR | 98.3% | X |  |
| MEMO_TEXT | VARCHAR | 89.3% | VOID - CONOR LAMB FOR CONGRESS |  |
| SUB_ID | VARCHAR | 0.0% | 4101920061070525498 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2006 | Election cycle (even year), present in all FEC tables |

## committee_to_committee

Transfers between committees

Rows: 46,486,423

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00035600 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | M10 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.8% | G |  |
| IMAGE_NUM | VARCHAR | 0.0% | 25990017791 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15J |  |
| ENTITY_TP | VARCHAR | 0.5% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.2% | OTTER FOR IDAHO |  |
| CITY | VARCHAR | 0.2% | OGDEN |  |
| STATE | VARCHAR | 0.2% | NY |  |
| ZIP_CODE | VARCHAR | 0.2% | 91105 |  |
| EMPLOYER | VARCHAR | 20.1% | INTERNATIONAL BROTHERHOOD OF ELECTR |  |
| OCCUPATION | VARCHAR | 20.0% | RETIRED |  |
| TRANSACTION_DT | DATE | 0.1% | 2012-03-06 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 25.0 |  |
| OTHER_ID | VARCHAR | 80.2% | C00431445 |  |
| TRAN_ID | VARCHAR | 0.2% | C8603996 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 1440221 |  |
| MEMO_CD | VARCHAR | 19.6% | X |  |
| MEMO_TEXT | VARCHAR | 51.0% | TRANSFER FROM TRUMP MAKE AMERICA GREAT AGAIN COMMITTEE |  |
| SUB_ID | VARCHAR | 0.0% | 4053120131190555748 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |

## committees

Committee master: name, type, party, treasurer, connected org

Rows: 184,883

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00000042 | Committee ID, joins to committees table and contribution tables |
| CMTE_NM | VARCHAR | 0.0% | ILLINOIS TOOL WORKS INC. FOR BETTER GOVERNMENT COMMITTEE |  |
| TRES_NM | VARCHAR | 5.0% | LYNCH, MICHAEL J. MR. |  |
| CMTE_ST1 | VARCHAR | 0.1% | 3600 W. Lake Avenue |  |
| CMTE_ST2 | VARCHAR | 77.8% | MD#288 |  |
| CMTE_CITY | VARCHAR | 0.1% | Glenview |  |
| CMTE_ST | VARCHAR | 0.1% | IL |  |
| CMTE_ZIP | VARCHAR | 0.1% | 60025 |  |
| CMTE_DSGN | VARCHAR | 0.0% | U |  |
| CMTE_TP | VARCHAR | 0.0% | Q |  |
| CMTE_PTY_AFFILIATION | VARCHAR | 59.3% | UNK |  |
| CMTE_FILING_FREQ | VARCHAR | 0.0% | Q |  |
| ORG_TP | VARCHAR | 77.7% | C |  |
| CONNECTED_ORG_NM | VARCHAR | 51.2% | AMERICAN MEDICAL ASSOCIATION |  |
| CAND_ID | VARCHAR | 63.0% | H6TX07029 | Candidate ID, joins across candidates and contribution tables |
| cycle | INTEGER | 0.0% | 2014 | Election cycle (even year), present in all FEC tables |

## communication_costs

Internal communications supporting/opposing candidates

Rows: 25,591

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
| DISBURSEMENT_DATE | VARCHAR | 0.0% | 30-SEP-10 |  |
| COMMUNICATION_DATE | VARCHAR | 1.4% | 30-SEP-10 |  |
| PUBLIC_DISBURSEMENT_DATE | VARCHAR | 0.4% | 30-SEP-10 |  |
| REPORTED_DISBURSEMENT_AMOUNT | VARCHAR | 0.0% | 290395 |  |
| NUMBER_OF_CANDIDATES | VARCHAR | 0.0% | 1 |  |
| CALCULATED_CANDIDATE_SHARE | VARCHAR | 0.0% | 290395 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## independent_expenditures

Independent expenditures for/against candidates

Rows: 671,015

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cand_id | VARCHAR | 9.4% | S6OH00254 |  |
| cand_name | VARCHAR | 0.0% | Strickland, Ted |  |
| spe_id | VARCHAR | 0.0% | C90011156 |  |
| spe_nam | VARCHAR | 0.0% | Working America |  |
| ele_type | VARCHAR | 0.0% | G |  |
| can_office_state | VARCHAR | 22.0% | OH |  |
| can_office_dis | VARCHAR | 0.1% | 00 |  |
| can_office | VARCHAR | 0.1% | S |  |
| cand_pty_aff | VARCHAR | 10.5% | DEMOCRATIC PARTY |  |
| exp_amo | DOUBLE | 0.1% | 34.2 |  |
| exp_date | DATE | 100.0% |  |  |
| agg_amo | DOUBLE | 0.3% | 866752.51 |  |
| sup_opp | VARCHAR | 0.1% | S |  |
| pur | VARCHAR | 0.1% | Salary and Benefits |  |
| pay | VARCHAR | 0.1% | Morrow, Alaun |  |
| file_num | VARCHAR | 0.0% | 1124438 |  |
| amndt_ind | VARCHAR | 0.0% | N |  |
| tran_id | VARCHAR | 0.0% | VN7CZA6EKC9 |  |
| image_num | VARCHAR | 0.0% | 201610279036650475 |  |
| receipt_dat | DATE | 100.0% |  |  |
| fec_election_yr | VARCHAR | 0.0% | 2016 |  |
| prev_file_num | VARCHAR | 87.9% | 1832140 |  |
| dissem_dt | DATE | 100.0% | 0776-10-20 |  |
| cycle | INTEGER | 0.0% | 2016 | Election cycle (even year), present in all FEC tables |

## individual_contributions

Every individual donation: name, employer, occupation, amount, date

Rows: 275,049,839

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00401224 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q1 | Report type code |
| TRANSACTION_PGI | VARCHAR | 16.7% | P2012 |  |
| IMAGE_NUM | VARCHAR | 0.0% | 201609129030778849 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15 |  |
| ENTITY_TP | VARCHAR | 0.2% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.0% | FIELDS, CHRIS R DR. |  |
| CITY | VARCHAR | 0.0% | LEBANON |  |
| STATE | VARCHAR | 0.1% | TX |  |
| ZIP_CODE | VARCHAR | 0.1% | 037662639 |  |
| EMPLOYER | VARCHAR | 4.5% | NONE |  |
| OCCUPATION | VARCHAR | 4.3% | DOCTOR OF OPTOMETRY |  |
| TRANSACTION_DT | DATE | 0.0% | 2003-10-03 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 167.0 |  |
| OTHER_ID | VARCHAR | 42.2% | C00000422 |  |
| TRAN_ID | VARCHAR | 0.2% | 39869314 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 778552 |  |
| MEMO_CD | VARCHAR | 99.4% | X |  |
| MEMO_TEXT | VARCHAR | 42.1% | * EARMARKED CONTRIBUTION: SEE BELOW |  |
| SUB_ID | VARCHAR | 0.0% | 4091320161317008123 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |

## operating_expenditures

Committee operating expenditures: payee, purpose, amount

Rows: 19,413,938

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00431171 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_YR | VARCHAR | 0.0% | 2003 |  |
| RPT_TP | VARCHAR | 0.0% | M10 | Report type code |
| IMAGE_NUM | VARCHAR | 0.0% | 14970072888 |  |
| LINE_NUM | VARCHAR | 0.0% | 23 |  |
| FORM_TP_CD | VARCHAR | 0.0% | F3P |  |
| SCHED_TP_CD | VARCHAR | 0.0% | SB |  |
| NAME | VARCHAR | 0.1% | THE DUKE MANSION |  |
| CITY | VARCHAR | 0.3% | CHARLOTTE |  |
| STATE | VARCHAR | 0.3% | MN |  |
| ZIP_CODE | VARCHAR | 0.5% | 28207 |  |
| TRANSACTION_DT | DATE | 0.0% | 2015-07-31 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 440.98 |  |
| TRANSACTION_PGI | VARCHAR | 48.2% | P |  |
| PURPOSE | VARCHAR | 0.5% | TRAVEL: LODGING |  |
| CATEGORY | VARCHAR | 72.8% | 001 |  |
| CATEGORY_DESC | VARCHAR | 73.9% | Advertising Expenses  |  |
| MEMO_CD | VARCHAR | 72.9% | X |  |
| MEMO_TEXT | VARCHAR | 78.8% | MEMO |  |
| ENTITY_TP | VARCHAR | 7.6% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| SUB_ID | VARCHAR | 0.0% | 4030820111137036715 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 0.0% | 715409 |  |
| TRAN_ID | VARCHAR | 0.0% | D317625 | Transaction identifier within a committee |
| BACK_REF_TRAN_ID | VARCHAR | 79.3% | D317567 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## v_candidate_totals

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H8VA06138 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | BUONGIORNO, JEFFREY D |  |
| party | VARCHAR | 0.0% | REP |  |
| office | VARCHAR | 0.0% | H |  |
| state | VARCHAR | 0.0% | OH |  |
| cycle | INTEGER | 0.0% | 2022 | Election cycle (even year), present in all FEC tables |
| num_contributions | BIGINT | 0.0% | 488 |  |
| total_individual | DOUBLE | 0.0% | 5896146.0 |  |

## v_daily_donations

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| date | DATE | 0.0% | 2016-07-18 |  |
| cycle | INTEGER | 0.0% | 2008 | Election cycle (even year), present in all FEC tables |
| num_donations | BIGINT | 0.0% | 938 |  |
| total_amount | DOUBLE | 0.0% | 40940469.0 |  |
| avg_amount | DOUBLE | 0.0% | 197.93787342489028 |  |
| median_amount | DOUBLE | 0.0% | 79.0 |  |

## v_pac_to_candidate

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| pac_name | VARCHAR | 0.0% | PACIFICARE HEALTH SYSTEMS INC. EMPLOYEES' POLITICAL ACTION COMMITTEE |  |
| connected_org | VARCHAR | 46.2% | SCHIFF LEADS PAC |  |
| candidate_name | VARCHAR | 0.0% | KLACIK, KIMBERLY |  |
| candidate_party | VARCHAR | 0.0% | REP |  |
| office | VARCHAR | 0.0% | H |  |
| state | VARCHAR | 0.0% | MD |  |
| amount | DOUBLE | 0.0% | 50.0 |  |
| date | DATE | 0.5% | 2014-06-04 |  |
| cycle | INTEGER | 0.0% | 2020 | Election cycle (even year), present in all FEC tables |

## v_top_donors

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| NAME | VARCHAR | 0.0% | MILLER, AMANDA A. |  |
| EMPLOYER | VARCHAR | 11.7% | ALLIED CONSTRUCTION |  |
| OCCUPATION | VARCHAR | 9.7% | SCIENCE EDUCATOR |  |
| STATE | VARCHAR | 0.2% | IL |  |
| num_contributions | BIGINT | 0.0% | 2 |  |
| total_donated | DOUBLE | 0.0% | 700.0 |  |
| first_cycle | INTEGER | 0.0% | 2018 |  |
| last_cycle | INTEGER | 0.0% | 2024 |  |
| num_committees | BIGINT | 0.0% | 1 |  |
