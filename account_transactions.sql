WITH daily_transactions AS (
  SELECT
    DATE("Date") AS "Date",
    "Value" - LAG("Value", 1, "Value") OVER (ORDER BY "Date") AS "Daily_Transactions"
  FROM "dune"."0xsg"."dataset_transactions_growth"
), daily_active_accounts AS (
  SELECT
    DATE("Date") AS "Date",
    "Value" AS "Active_Accounts"
  FROM "dune"."0xsg"."dataset_active_accounts"
), combined_data AS (
  SELECT
    dt."Date",
    dt."Daily_Transactions",
    daa."Active_Accounts"
  FROM daily_transactions AS dt
  JOIN daily_active_accounts AS daa
    ON dt."Date" = daa."Date"
), pre_agg AS (
  SELECT
    "Date",
    "Daily_Transactions",
    "Active_Accounts",
    LAG("Daily_Transactions") OVER (ORDER BY "Date") AS prev_transactions,
    LAG("Active_Accounts") OVER (ORDER BY "Date") AS prev_accounts
  FROM combined_data
), monthly_aggregates AS (
  SELECT
    DATE_TRUNC('month', "Date") AS "Month_Start",
    DATE_TRUNC('month', "Date") + INTERVAL '1' MONTH - INTERVAL '1' day AS "Month_End",
    SUM("Daily_Transactions") AS "Monthly_Transactions",
    SUM("Active_Accounts") AS "Monthly_Active_Accounts",
    AVG(
      TRY_CAST("Daily_Transactions" - "prev_transactions" AS DOUBLE) / NULLIF("prev_transactions", 0)
    ) * 100 AS "Avg_Monthly_Transaction_Growth_Rate",
    AVG(
      TRY_CAST("Active_Accounts" - "prev_accounts" AS DOUBLE) / NULLIF("prev_accounts", 0)
    ) * 100 AS "Avg_Monthly_Account_Growth_Rate"
  FROM pre_agg
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
FROM combined_data AS cd
LEFT JOIN monthly_aggregates AS ma
  ON DATE_TRUNC('month', cd."Date") = ma."Month_Start"
ORDER BY
  cd."Date",
  ma."Month_End"