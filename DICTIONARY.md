# Data Dictionary

Source: [FEC Bulk Data](https://www.fec.gov/data/browse-data/?tab=bulk-data)

## candidate_committee_links

Which committees are authorized by which candidates

Rows: 74,481

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

Rows: 76,692

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CAND_ID | VARCHAR | 0.0% | H0AK00055 | Candidate ID, joins across candidates and contribution tables |
| CAND_NAME | VARCHAR | 0.0% | GREENE, CLIFFORD MARK |  |
| CAND_PTY_AFFILIATION | VARCHAR | 0.1% | DEM |  |
| CAND_ELECTION_YR | INTEGER | 0.0% | 2000 |  |
| CAND_OFFICE_ST | VARCHAR | 0.0% | AK |  |
| CAND_OFFICE | VARCHAR | 0.0% | H |  |
| CAND_OFFICE_DISTRICT | VARCHAR | 0.8% | 00 |  |
| CAND_ICI | VARCHAR | 4.6% | C |  |
| CAND_STATUS | VARCHAR | 0.0% | N |  |
| CAND_PCC | VARCHAR | 17.6% | C00361626 | Candidate principal campaign committee, joins candidates to committees.CMTE_ID |
| CAND_ST1 | VARCHAR | 1.3% | PO BOX 20745 |  |
| CAND_ST2 | VARCHAR | 91.0% | PO BOX 374 |  |
| CAND_CITY | VARCHAR | 0.1% | JUNEAU |  |
| CAND_ST | VARCHAR | 1.0% | AK |  |
| CAND_ZIP | VARCHAR | 1.4% | 99802 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committee_contributions

PAC/party contributions to candidates

Rows: 5,304,857

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00255257 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q2 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.9% | G |  |
| IMAGE_NUM | VARCHAR | 0.0% | 23038172115 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 24K |  |
| ENTITY_TP | VARCHAR | 2.4% | CCM | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 1.3% | RODNEY ALEXANDER FOR U.S. CONGRESS |  |
| CITY | VARCHAR | 1.4% | HOPKINSVILLE |  |
| STATE | VARCHAR | 1.4% | LA |  |
| ZIP_CODE | VARCHAR | 1.4% | 42241 |  |
| EMPLOYER | VARCHAR | 100.0% | CANANDAIGUA WINE CO. |  |
| OCCUPATION | VARCHAR | 100.0% | SALES REP. |  |
| TRANSACTION_DT | DATE | 0.5% | 2003-05-14 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 500.0 |  |
| OTHER_ID | VARCHAR | 0.0% | C00313510 |  |
| CAND_ID | VARCHAR | 0.2% | H6NJ08118 | Candidate ID, joins across candidates and contribution tables |
| TRAN_ID | VARCHAR | 0.7% | D24002 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.6% | 136283 |  |
| MEMO_CD | VARCHAR | 98.3% | X |  |
| MEMO_TEXT | VARCHAR | 89.3% | AUGUST VISIT TO ADAMS TELEPHONE COOPERATIVE |  |
| SUB_ID | VARCHAR | 0.0% | 1070820110008496144 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committee_to_committee

Transfers between committees

Rows: 48,118,471

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00386151 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | N | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | Q1 | Report type code |
| TRANSACTION_PGI | VARCHAR | 1.7% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 25971331848 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 16C |  |
| ENTITY_TP | VARCHAR | 0.5% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.2% | BEAUPREZ FOR CONGRESS  (CO/H07) |  |
| CITY | VARCHAR | 0.2% | WHEAT RIDGE |  |
| STATE | VARCHAR | 0.2% | CO |  |
| ZIP_CODE | VARCHAR | 0.2% | 80034 |  |
| EMPLOYER | VARCHAR | 19.5% | SELF |  |
| OCCUPATION | VARCHAR | 19.5% | ARCHITECTURAL HISTORIAN |  |
| TRANSACTION_DT | DATE | 0.1% | 2004-07-22 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 27500.0 |  |
| OTHER_ID | VARCHAR | 80.7% | S4KY00042 |  |
| TRAN_ID | VARCHAR | 0.2% | 0326200333E668 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 189598 |  |
| MEMO_CD | VARCHAR | 19.1% | X |  |
| MEMO_TEXT | VARCHAR | 50.7% | DUES 2003 |  |
| SUB_ID | VARCHAR | 0.0% | 1050520030000101517 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## committees

Committee master: name, type, party, treasurer, connected org

Rows: 185,471

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00000042 | Committee ID, joins to committees table and contribution tables |
| CMTE_NM | VARCHAR | 0.0% | ILLINOIS TOOL WORKS INC. FOR BETTER GOVERNMENT COMMITTEE |  |
| TRES_NM | VARCHAR | 5.0% | LYNCH, MICHAEL J. MR. |  |
| CMTE_ST1 | VARCHAR | 0.1% | 3600 WEST LAKE AVENUE |  |
| CMTE_ST2 | VARCHAR | 77.7% | PO BOX 419580 |  |
| CMTE_CITY | VARCHAR | 0.1% | Glenview |  |
| CMTE_ST | VARCHAR | 0.1% | IL |  |
| CMTE_ZIP | VARCHAR | 0.1% | 60026 |  |
| CMTE_DSGN | VARCHAR | 0.0% | U |  |
| CMTE_TP | VARCHAR | 0.0% | Q |  |
| CMTE_PTY_AFFILIATION | VARCHAR | 59.4% | UNK |  |
| CMTE_FILING_FREQ | VARCHAR | 0.0% | Q |  |
| ORG_TP | VARCHAR | 77.7% | C |  |
| CONNECTED_ORG_NM | VARCHAR | 51.3% | ILLINOIS TOOL WORKS INC |  |
| CAND_ID | VARCHAR | 63.0% | H6TX07029 | Candidate ID, joins across candidates and contribution tables |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## communication_costs

Internal communications supporting/opposing candidates

Rows: 25,631

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

Rows: 1,589

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CANDIDATE_ID | VARCHAR | 17.4% | S8WI00026 |  |
| CANDIDATE_NAME | VARCHAR | 17.6% | FEINGOLD, RUSSELL D |  |
| CANDIDATE_OFFICE | VARCHAR | 17.6% | S |  |
| CANDIDATE_STATE | VARCHAR | 17.6% | WI |  |
| CANDIDATE_DISTRICT | VARCHAR | 17.6% | 00 |  |
| COMMITTEE_ID | VARCHAR | 0.0% | C30001648 |  |
| COMMITTEE_NAME | VARCHAR | 0.0% | AMERICAN ACTION NETWORK |  |
| SB_IMAGE_NUM | VARCHAR | 0.0% | 10932121746 |  |
| PAYEE_NAME | VARCHAR | 0.0% | SMART MEDIA GROUP |  |
| PAYEE_STREET | VARCHAR | 0.0% | 814 KING STREET STE 400 |  |
| PAYEE_CITY | VARCHAR | 0.0% | ALEXANDRIA |  |
| PAYEE_STATE | VARCHAR | 0.1% | VA |  |
| DISBURSEMENT_DESCRIPTION | VARCHAR | 9.1% | MEDIA TV AD PRODUCTION - BUCKET |  |
| DISBURSEMENT_DATE | DATE | 1.6% | 2010-09-30 |  |
| COMMUNICATION_DATE | DATE | 2.6% | 2010-09-30 |  |
| PUBLIC_DISBURSEMENT_DATE | DATE | 1.6% | 2010-09-30 |  |
| REPORTED_DISBURSEMENT_AMOUNT | DOUBLE | 0.3% | 290395.0 |  |
| NUMBER_OF_CANDIDATES | VARCHAR | 0.0% | 1 |  |
| CALCULATED_CANDIDATE_SHARE | DOUBLE | 1.3% | 290395.0 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## independent_expenditures

Independent expenditures for/against candidates

Rows: 602,587

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cand_id | VARCHAR | 8.9% | S4NC00089 |  |
| cand_name | VARCHAR | 0.0% | BISHOP, TIM |  |
| spe_id | VARCHAR | 0.0% | C00348540 |  |
| spe_nam | VARCHAR | 0.0% | Working America |  |
| ele_type | VARCHAR | 0.0% | G |  |
| can_office_state | VARCHAR | 22.4% | NC |  |
| can_office_dis | VARCHAR | 0.1% | 01 |  |
| can_office | VARCHAR | 0.1% | S |  |
| cand_pty_aff | VARCHAR | 10.1% | REPUBLICAN PARTY |  |
| exp_amo | DOUBLE | 0.1% | 17.1 |  |
| exp_date | DATE | 11.9% | 2010-10-14 |  |
| agg_amo | DOUBLE | 0.2% | 246383.11 |  |
| sup_opp | VARCHAR | 0.1% | O |  |
| pur | VARCHAR | 0.1% | MAILERS |  |
| pay | VARCHAR | 0.1% | PERSON 2 PERSON SOLUTIONS LLC |  |
| file_num | VARCHAR | 0.0% | 1121854 |  |
| amndt_ind | VARCHAR | 0.0% | N |  |
| tran_id | VARCHAR | 0.0% | SE.8359 |  |
| image_num | VARCHAR | 0.0% | 201611019037016594 |  |
| receipt_dat | DATE | 0.2% | 2010-10-15 |  |
| fec_election_yr | VARCHAR | 0.1% | 2010 |  |
| prev_file_num | VARCHAR | 88.2% | 496909 |  |
| dissem_dt | DATE | 57.5% | 2020-08-10 |  |
| cycle | INTEGER | 0.0% | 2010 | Election cycle (even year), present in all FEC tables |

## individual_contributions

Every individual donation: name, employer, occupation, amount, date

Rows: 280,827,680

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00387217 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_TP | VARCHAR | 0.0% | YE | Report type code |
| TRANSACTION_PGI | VARCHAR | 16.4% | P |  |
| IMAGE_NUM | VARCHAR | 0.0% | 26020660433 |  |
| TRANSACTION_TP | VARCHAR | 0.0% | 15 |  |
| ENTITY_TP | VARCHAR | 0.2% | IND | Entity type (IND=individual, COM=committee, etc.) |
| NAME | VARCHAR | 0.0% | RODGERS, HAZEL B |  |
| CITY | VARCHAR | 0.0% | CHICAGO |  |
| STATE | VARCHAR | 0.1% | CA |  |
| ZIP_CODE | VARCHAR | 0.1% | 60606 |  |
| EMPLOYER | VARCHAR | 4.5% | GARDNER, CARTON & DOUGLAS |  |
| OCCUPATION | VARCHAR | 4.2% | RETIRED |  |
| TRANSACTION_DT | DATE | 0.0% | 2003-12-19 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 500.0 |  |
| OTHER_ID | VARCHAR | 42.1% | P40002958 |  |
| TRAN_ID | VARCHAR | 0.2% | 0011268932 | Transaction identifier within a committee |
| FILE_NUM | VARCHAR | 0.2% | 122243 |  |
| MEMO_CD | VARCHAR | 99.4% | X |  |
| MEMO_TEXT | VARCHAR | 42.1% | RECEIPT |  |
| SUB_ID | VARCHAR | 0.0% | 4062320041039539581 | Unique submission/transaction ID |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## operating_expenditures

Committee operating expenditures: payee, purpose, amount

Rows: 19,725,971

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| CMTE_ID | VARCHAR | 0.0% | C00382036 | Committee ID, joins to committees table and contribution tables |
| AMNDT_IND | VARCHAR | 0.0% | A | Amendment indicator (N=new, A=amendment, T=termination) |
| RPT_YR | VARCHAR | 0.0% | 2003 |  |
| RPT_TP | VARCHAR | 0.0% | M11 | Report type code |
| IMAGE_NUM | VARCHAR | 0.0% | 23991368379 |  |
| LINE_NUM | VARCHAR | 0.0% | 17 |  |
| FORM_TP_CD | VARCHAR | 0.0% | F3X |  |
| SCHED_TP_CD | VARCHAR | 0.0% | SB |  |
| NAME | VARCHAR | 0.1% | HOWARD'S BARBECUE |  |
| CITY | VARCHAR | 0.3% | MIAMI |  |
| STATE | VARCHAR | 0.3% | FL |  |
| ZIP_CODE | VARCHAR | 0.5% | 27546 |  |
| TRANSACTION_DT | DATE | 0.0% | 2003-10-07 |  |
| TRANSACTION_AMT | DOUBLE | 0.0% | 357.11 |  |
| TRANSACTION_PGI | VARCHAR | 48.1% | O |  |
| PURPOSE | VARCHAR | 0.5% | CATERING EXPENSE |  |
| CATEGORY | VARCHAR | 72.8% | 001 |  |
| CATEGORY_DESC | VARCHAR | 73.9% | Administrative/Salary/Overhead Expenses  |  |
| MEMO_CD | VARCHAR | 72.9% | X |  |
| MEMO_TEXT | VARCHAR | 78.9% | BANK FEES |  |
| ENTITY_TP | VARCHAR | 7.5% | ORG | Entity type (IND=individual, COM=committee, etc.) |
| SUB_ID | VARCHAR | 0.0% | 4121320041046623499 | Unique submission/transaction ID |
| FILE_NUM | VARCHAR | 0.0% | 90044 |  |
| TRAN_ID | VARCHAR | 0.0% | SB17.9538 | Transaction identifier within a committee |
| BACK_REF_TRAN_ID | VARCHAR | 79.2% | B21(B)330 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |

## v_candidate_totals

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |
| CMTE_ID | VARCHAR | 0.0% | C00393090 | Committee ID, joins to committees table and contribution tables |
| cand_ids | VARCHAR | 0.0% | H4MO05192 |  |
| candidate_names | VARCHAR | 0.0% | GEPHARDT, RICHARD A |  |
| party | VARCHAR | 0.0% | DEM |  |
| office | VARCHAR | 0.0% | P |  |
| state | VARCHAR | 0.0% | US |  |
| num_contributions | BIGINT | 0.0% | 1 |  |
| net_individual | DOUBLE | 0.0% | 621.0 |  |

## v_daily_donations

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| date | DATE | 0.0% | 2003-11-24 |  |
| cycle | INTEGER | 0.0% | 2004 | Election cycle (even year), present in all FEC tables |
| num_donations | BIGINT | 0.0% | 3794 |  |
| total_amount | DOUBLE | 0.0% | 2747110.0 |  |
| avg_amount | DOUBLE | 0.0% | 959.5345282024249 |  |
| median_amount | DOUBLE | 0.0% | 500.0 |  |

## v_pac_to_candidate

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| pac_name | VARCHAR | 0.0% | ENTRUST INC POLITICAL ACTION COMMITTEE |  |
| connected_org | VARCHAR | 41.8% | ENTRUST INC |  |
| candidate_name | VARCHAR | 0.0% | JENKINS, LYNN |  |
| candidate_party | VARCHAR | 0.0% | REP |  |
| office | VARCHAR | 0.0% | H |  |
| state | VARCHAR | 0.0% | NC |  |
| transaction_type | VARCHAR | 0.0% | 24K |  |
| amount | DOUBLE | 0.0% | 2000.0 |  |
| date | DATE | 0.0% | 2003-05-14 |  |
| cycle | INTEGER | 0.0% | 2006 | Election cycle (even year), present in all FEC tables |

## v_top_donors

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| NAME | VARCHAR | 0.0% | MARDER, RUTH R MS. |  |
| EMPLOYER | VARCHAR | 12.3% | RETIRED |  |
| OCCUPATION | VARCHAR | 10.1% | INSURANCE AGENT |  |
| STATE | VARCHAR | 0.2% | NM |  |
| num_contributions | BIGINT | 0.0% | 1 |  |
| net_donated | DOUBLE |  | 250.0 |  |
| first_cycle | INTEGER | 0.0% | 2004 |  |
| last_cycle | INTEGER | 0.0% | 2004 |  |
| num_committees | BIGINT | 0.0% | 1 |  |
