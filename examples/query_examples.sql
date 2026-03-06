-- =============================================================================
-- FEC Campaign Finance Database - Example Queries
-- =============================================================================
-- Assumes: ATTACH '...' AS fec (READ_ONLY);
-- Or run directly against the local fec.duckdb file.
-- =============================================================================

-- 1. Top 20 presidential candidates by individual donations (2024 cycle)
SELECT c.CAND_NAME, c.CAND_PTY_AFFILIATION AS party,
    SUM(i.TRANSACTION_AMT) AS total_raised,
    COUNT(*) AS num_donations,
    AVG(i.TRANSACTION_AMT) AS avg_donation
FROM individual_contributions i
JOIN candidates c ON i.CMTE_ID = c.CAND_PCC AND i.cycle = c.cycle
WHERE i.cycle = 2024 AND c.CAND_OFFICE = 'P' AND i.TRANSACTION_AMT > 0
GROUP BY 1, 2
ORDER BY total_raised DESC
LIMIT 20;

-- 2. Small-dollar vs large-dollar donations by party (2024)
SELECT c.CAND_PTY_AFFILIATION AS party,
    SUM(CASE WHEN i.TRANSACTION_AMT <= 200 THEN i.TRANSACTION_AMT ELSE 0 END) AS small_dollar,
    SUM(CASE WHEN i.TRANSACTION_AMT > 200 THEN i.TRANSACTION_AMT ELSE 0 END) AS large_dollar,
    COUNT(CASE WHEN i.TRANSACTION_AMT <= 200 THEN 1 END) AS small_count,
    COUNT(CASE WHEN i.TRANSACTION_AMT > 200 THEN 1 END) AS large_count
FROM individual_contributions i
JOIN candidates c ON i.CMTE_ID = c.CAND_PCC AND i.cycle = c.cycle
WHERE i.cycle = 2024 AND c.CAND_OFFICE = 'P' AND i.TRANSACTION_AMT > 0
    AND c.CAND_PTY_AFFILIATION IN ('DEM', 'REP')
GROUP BY 1;

-- 3. Monthly donation trend for a specific cycle
SELECT DATE_TRUNC('month', TRANSACTION_DT) AS month,
    COUNT(*) AS num_donations,
    SUM(TRANSACTION_AMT) AS total_amount
FROM individual_contributions
WHERE cycle = 2024 AND TRANSACTION_DT IS NOT NULL AND TRANSACTION_AMT > 0
GROUP BY 1
ORDER BY 1;

-- 4. Top employers of political donors (2024)
SELECT EMPLOYER, COUNT(*) AS donations, SUM(TRANSACTION_AMT) AS total
FROM individual_contributions
WHERE cycle = 2024 AND EMPLOYER IS NOT NULL
    AND EMPLOYER NOT IN ('RETIRED', 'SELF-EMPLOYED', 'NONE', 'N/A', 'NOT EMPLOYED')
    AND TRANSACTION_AMT > 0
GROUP BY 1
ORDER BY total DESC
LIMIT 20;

-- 5. Top occupations of political donors
SELECT OCCUPATION, COUNT(*) AS donations, SUM(TRANSACTION_AMT) AS total
FROM individual_contributions
WHERE cycle = 2024 AND OCCUPATION IS NOT NULL
    AND OCCUPATION NOT IN ('RETIRED', 'NONE', 'N/A', 'NOT EMPLOYED')
    AND TRANSACTION_AMT > 0
GROUP BY 1
ORDER BY total DESC
LIMIT 20;

-- 6. Donation patterns by state
SELECT STATE, COUNT(*) AS donations,
    SUM(TRANSACTION_AMT) AS total,
    AVG(TRANSACTION_AMT) AS avg_donation,
    MEDIAN(TRANSACTION_AMT) AS median_donation
FROM individual_contributions
WHERE cycle = 2024 AND TRANSACTION_AMT > 0 AND STATE IS NOT NULL
GROUP BY 1
ORDER BY total DESC;

-- 7. Top PAC-to-candidate contributions (2024)
SELECT cm.CMTE_NM AS pac_name,
    cn.CAND_NAME AS candidate,
    cn.CAND_PTY_AFFILIATION AS party,
    cn.CAND_OFFICE AS office,
    SUM(cc.TRANSACTION_AMT) AS total_given
FROM committee_contributions cc
JOIN committees cm ON cc.CMTE_ID = cm.CMTE_ID AND cc.cycle = cm.cycle
JOIN candidates cn ON cc.CAND_ID = cn.CAND_ID AND cc.cycle = cn.cycle
WHERE cc.cycle = 2024 AND cc.TRANSACTION_AMT > 0
GROUP BY 1, 2, 3, 4
ORDER BY total_given DESC
LIMIT 20;

-- 8. Committee-to-committee transfers (top flows)
SELECT
    src.CMTE_NM AS from_committee,
    dst.CMTE_NM AS to_committee,
    SUM(ot.TRANSACTION_AMT) AS total_transferred
FROM committee_to_committee ot
JOIN committees src ON ot.CMTE_ID = src.CMTE_ID AND ot.cycle = src.cycle
JOIN committees dst ON ot.OTHER_ID = dst.CMTE_ID AND ot.cycle = dst.cycle
WHERE ot.cycle = 2024 AND ot.TRANSACTION_AMT > 0
GROUP BY 1, 2
ORDER BY total_transferred DESC
LIMIT 20;

-- 9. Independent expenditures for/against candidates (2024)
SELECT can_nam AS candidate, sup_opp AS support_oppose,
    SUM(TRY_CAST(exp_amo AS DOUBLE)) AS total_spent,
    COUNT(*) AS num_expenditures
FROM independent_expenditures
WHERE cycle = 2024
GROUP BY 1, 2
ORDER BY total_spent DESC
LIMIT 20;

-- 10. Top operating expenditure payees
SELECT NAME AS payee, COUNT(*) AS payments,
    SUM(TRANSACTION_AMT) AS total_paid
FROM operating_expenditures
WHERE cycle = 2024 AND TRANSACTION_AMT > 0 AND NAME IS NOT NULL
GROUP BY 1
ORDER BY total_paid DESC
LIMIT 20;

-- 11. Fundraising by cycle over time
SELECT cycle,
    COUNT(*) AS num_individual_donations,
    SUM(TRANSACTION_AMT) AS total_individual
FROM individual_contributions
WHERE TRANSACTION_AMT > 0
GROUP BY cycle
ORDER BY cycle;

-- 12. Candidates with most unique donors (2024 presidential)
SELECT c.CAND_NAME, c.CAND_PTY_AFFILIATION AS party,
    COUNT(DISTINCT i.NAME) AS unique_donors,
    SUM(i.TRANSACTION_AMT) AS total_raised
FROM individual_contributions i
JOIN candidates c ON i.CMTE_ID = c.CAND_PCC AND i.cycle = c.cycle
WHERE i.cycle = 2024 AND c.CAND_OFFICE = 'P' AND i.TRANSACTION_AMT > 0
GROUP BY 1, 2
ORDER BY unique_donors DESC
LIMIT 10;

-- 13. Repeat donors: people who gave to multiple cycles
SELECT NAME, STATE,
    COUNT(DISTINCT cycle) AS num_cycles,
    SUM(TRANSACTION_AMT) AS lifetime_total,
    MIN(cycle) AS first_cycle,
    MAX(cycle) AS last_cycle
FROM individual_contributions
WHERE TRANSACTION_AMT > 0 AND NAME IS NOT NULL
GROUP BY 1, 2
HAVING COUNT(DISTINCT cycle) >= 5
ORDER BY lifetime_total DESC
LIMIT 20;

-- 14. Electioneering communications spend by cycle
SELECT cycle, COUNT(*) AS filings,
    SUM(TRY_CAST(communication_cost AS DOUBLE)) AS total_spend
FROM electioneering_communications
GROUP BY cycle
ORDER BY cycle;

-- 15. Database overview from metadata
SELECT table_name, description, row_count, column_count, cycles_covered
FROM _metadata
ORDER BY row_count DESC;
