#standardSQL

WITH original_tickets AS (
SELECT
  TCKT_TicketID,
  Account_KEY,
  ACCT_AccountID,
  AccountNumber,
  prev_time_month_key as time_month_key
FROM 
  `fluid-door-179122.data_science_ema_dwsmg_upload.Fact_Dim_Ticket_abbrev_fixed`
),

ticket_acct_dev_skus AS (
SELECT
  ot.TCKT_TicketID,
  ot.Account_KEY,
  fsa.device_key,
  fsa.sku_key,
  fsa.time_month_key
FROM   
  `fluid-door-179122.data_science_ema_dwsmg_upload.Fact_SKU_Assignment_abbrev` fsa
INNER JOIN 
    original_tickets ot
ON 
    ot.Account_KEY = fsa.Account_KEY AND 
    ot.time_month_key = fsa.time_month_key
WHERE 
    fsa.time_month_key >= 201701 AND
    fsa.time_month_key <  201901
),

ticket_sku_counts AS (
SELECT
    tckt_ticketID,
    sku_key,
    COUNT(1) as ticket_sku_count
FROM
    ticket_acct_dev_skus
GROUP BY
    tckt_ticketID,
    sku_key
),

ticket_device_counts AS (
SELECT
    tckt_ticketID,
    COUNT(DISTINCT device_key) as ticket_device_count
FROM
    ticket_acct_dev_skus
GROUP BY
    tckt_ticketID
)

SELECT
    tsc.tckt_ticketID,
    tsc.sku_key,
    tsc.ticket_sku_count,
    tdc.ticket_device_count
FROM
    ticket_sku_counts tsc
INNER JOIN
    ticket_device_counts tdc
ON
    tsc.tckt_ticketID = tdc.tckt_ticketID

