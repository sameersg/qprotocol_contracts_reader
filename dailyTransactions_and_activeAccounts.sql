WITH Transactions_Delta AS (
    SELECT 
        current.date,
        current.value - COALESCE(previous.value, 0) AS daily_transaction_growth
    FROM 
        (
            SELECT date, value,
                   ROW_NUMBER() OVER (PARTITION BY date ORDER BY date ASC) AS rn
            FROM "dune"."0xsg"."transactions_growth"
        ) AS current
    LEFT JOIN 
        (
            SELECT date, value,
                   ROW_NUMBER() OVER (PARTITION BY date ORDER BY date ASC) AS rn
            FROM "dune"."0xsg"."transactions_growth"
        ) AS previous ON DATE_ADD('day', 1, previous.date) = current.date AND previous.rn = 1
    WHERE current.rn = 1
),
Active_Accounts AS (
    SELECT 
        date,
        value AS daily_active_accounts
    FROM 
        (
            SELECT date, value,
                   ROW_NUMBER() OVER (PARTITION BY date ORDER BY date ASC) AS rn
            FROM "dune"."0xsg"."active_accounts"
        ) AS filtered
    WHERE filtered.rn = 1
)

SELECT 
    t.date,
    t.daily_transaction_growth,
    a.daily_active_accounts
FROM 
    Transactions_Delta t
JOIN 
    Active_Accounts a ON t.date = a.date
WHERE 
    t.date >= TIMESTAMP '2024-01-01 00:00:00'  -- Updated to handle timestamp explicitly
ORDER BY 
    t.date;
