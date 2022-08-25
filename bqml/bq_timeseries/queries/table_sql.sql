SELECT
date,
SUM(volume_sold_liters) total_sold_liters
FROM
`bigquery-public-data.iowa_liquor_sales.sales`
WHERE
EXTRACT (year from date) = 2020 OR EXTRACT (year from date) = 2021
GROUP BY date;