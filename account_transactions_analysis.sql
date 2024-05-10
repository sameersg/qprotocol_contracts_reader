WITH daily_transactions AS (
  SELECT
    CAST("Date" AS TIMESTAMP) AS "Date",
    "Value" AS "Transaction_Value",
    COALESCE("Value" - LAG("Value", 1) OVER (ORDER BY "Date"), 0) AS "Daily_Transactions"
  FROM (
    SELECT "Date", "Value",
           ROW_NUMBER() OVER (PARTITION BY CAST("Date" AS DATE) ORDER BY "Date") AS rn
    FROM "dune"."0xsg"."transactions_growth"
  ) AS raw_transactions
  WHERE raw_transactions.rn = 1
), daily_active_accounts AS (
  SELECT
    CAST("Date" AS TIMESTAMP) AS "Date",
    "Value" AS "Active_Accounts"
  FROM (
    SELECT "Date", "Value",
           ROW_NUMBER() OVER (PARTITION BY CAST("Date" AS DATE) ORDER BY "Date") AS rn
    FROM "dune"."0xsg"."active_accounts"
  ) AS raw_accounts
  WHERE raw_accounts.rn = 1
), combined_data AS (
  SELECT
    dt."Date",
    dt."Transaction_Value",
    dt."Daily_Transactions",
    daa."Active_Accounts"
  FROM daily_transactions dt
  JOIN daily_active_accounts daa ON dt."Date" = daa."Date"
), daily_growth AS (
  SELECT
    "Date",
    "Daily_Transactions",
    "Active_Accounts",
    TRY_CAST(("Daily_Transactions" - LAG("Daily_Transactions", 1) OVER (ORDER BY "Date")) AS DOUBLE) / NULLIF(LAG("Daily_Transactions", 1) OVER (ORDER BY "Date"), 0) * 100 AS "Transaction_Growth_Rate",
    TRY_CAST(("Active_Accounts" - LAG("Active_Accounts", 1) OVER (ORDER BY "Date")) AS DOUBLE) / NULLIF(LAG("Active_Accounts", 1) OVER (ORDER BY "Date"), 0) * 100 AS "Account_Growth_Rate"
  FROM combined_data
), monthly_aggregates AS (
  SELECT
    DATE_TRUNC('month', "Date") AS "Month_Start",
    (DATE_TRUNC('month', "Date") + INTERVAL '1' MONTH - INTERVAL '1' DAY) AS "Month_End",
    SUM("Daily_Transactions") AS "Monthly_Transactions",
    SUM("Active_Accounts") AS "Monthly_Active_Accounts",
    AVG("Transaction_Growth_Rate") AS "Avg_Monthly_Transaction_Growth_Rate",
    AVG("Account_Growth_Rate") AS "Avg_Monthly_Account_Growth_Rate"
  FROM daily_growth
  GROUP BY
    DATE_TRUNC('month', "Date")
)
SELECT
  cd."Date",
  cd."Daily_Transactions",
  cd."Active_Accounts",
  ma."Month_End",
  ma."Monthly_Transactions",
  ma."Monthly_Active_Accounts",
  ma."Avg_Monthly_Transaction_Growth_Rate",
  ma."Avg_Monthly_Account_Growth_Rate"
FROM daily_growth cd
LEFT JOIN monthly_aggregates ma
  ON DATE_TRUNC('month', cd."Date") = ma."Month_Start"
ORDER BY
  cd."Date", ma."Month_End";
