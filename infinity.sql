WITH FilteredData AS (
  SELECT
    "date",
    DATE_TRUNC('day', "date") AS "Day",
    bridged_usdc,
    bridged_weth,
    bridged_elk,
    weth_in_usd,
    elk_in_usd,
    ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC('day', "date") ORDER BY "date") AS row_num
  FROM dune."0xsg".token_and_contract_data
  WHERE
    "date" >= TRY_CAST('2024-04-30' AS TIMESTAMP) /* Starting from the last day of April */
    AND EXTRACT(HOUR FROM "date") = 9
    AND EXTRACT(MINUTE FROM "date") = 0
), DailyData AS (
  SELECT
    "Day",
    bridged_usdc AS Total_USDC_Bridged,
    bridged_weth AS Total_WETH_Bridged,
    bridged_elk AS Total_ELK_Bridged,
    weth_in_usd,
    elk_in_usd
  FROM FilteredData
  WHERE
    row_num = 1
), DailyChanges AS (
  SELECT
    "Day",
    Total_USDC_Bridged,
    Total_WETH_Bridged,
    Total_ELK_Bridged,
    weth_in_usd,
    elk_in_usd,
    Total_USDC_Bridged - LAG(Total_USDC_Bridged, 1) OVER (ORDER BY "Day") AS New_USDC_Bridged,
    Total_WETH_Bridged - LAG(Total_WETH_Bridged, 1) OVER (ORDER BY "Day") AS New_WETH_Bridged,
    Total_ELK_Bridged - LAG(Total_ELK_Bridged, 1) OVER (ORDER BY "Day") AS New_ELK_Bridged
  FROM DailyData AS a
), CalculatedTotals AS (
  SELECT
    "Day",
    COALESCE(New_USDC_Bridged, Total_USDC_Bridged) AS New_USDC_Bridged,
    COALESCE(New_WETH_Bridged, Total_WETH_Bridged) AS New_WETH_Bridged,
    COALESCE(New_ELK_Bridged, Total_ELK_Bridged) AS New_ELK_Bridged,
    (
      COALESCE(New_USDC_Bridged, Total_USDC_Bridged) + COALESCE(New_WETH_Bridged, Total_WETH_Bridged) * weth_in_usd + COALESCE(New_ELK_Bridged, Total_ELK_Bridged) * elk_in_usd
    ) AS Total_New_Bridged_Value_USD
  FROM DailyChanges
), WeeklyTotals AS (
  SELECT
    DATE_TRUNC('week', "Day") AS "Week",
    SUM(Total_New_Bridged_Value_USD) AS Weekly_Total_Bridged_Value_USD
  FROM CalculatedTotals
  GROUP BY
    DATE_TRUNC('week', "Day")
)
SELECT
  c."Day",
  c.New_USDC_Bridged,
  c.New_WETH_Bridged,
  c.New_ELK_Bridged,
  c.Total_New_Bridged_Value_USD,
  w.Weekly_Total_Bridged_Value_USD
FROM CalculatedTotals AS c
LEFT JOIN WeeklyTotals AS w
  ON DATE_TRUNC('week', c."Day") = w."Week"
WHERE
  c."Day" >= TRY_CAST('2024-05-01' /* Displaying data starting from May 1st */ AS TIMESTAMP)
ORDER BY
  c."Day"