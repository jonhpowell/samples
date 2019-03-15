-- get products ("SKU's") for each device in each ticket to form the basis of a one-hot encoded 
--   ticket:product:count, total_acct_devs table
-- NOTE: this is the 2017 part (1/2 of total needed)

WITH original_tickets AS
(
SELECT --TOP 100
	dt.tckt_ticketID,
	dt.Account_KEY,
--	dt.created,
    YEAR(dt.Created)*100 + MONTH(dt.Created) AS time_month_key
FROM 
	[DWS_Managed].[dbo].[Dimension_Ticket] dt WITH (NOLOCK)
INNER JOIN
	[DWS_Managed].[dbo].[xref_server_Ticket] xrt WITH (NOLOCK)
ON
	dt.TCKT_TicketID = xrt.TCKT_TicketID
WHERE 
	dt.Created >= '20170101' AND
	dt.Created < '20180101'AND 
--	dt.Created < '20181204'AND 
	dt.source IN ('MyRackspace', 'Phone Call', 'Chat Support', 'Rackspace Employee')
),

device_key_number AS
(
SELECT --TOP 100000
	device_number,
	Device_key
FROM 
	[DWS_Managed].[dbo].[Dim_Device] WITH (NOLOCK)
WHERE 
	[Device_Record_Effective_End_Datetime] >= '20170101' AND
	[Device_Record_Effective_End_Datetime] < '20180101'
),

sku_assignments AS
(
SELECT  
	Account_KEY,
	Device_KEY,
	sku_key,
	time_month_key
FROM 
	[DWS_Managed].[dbo].[Fact_SKU_Assignment]
WHERE 
	time_month_key >= 201701 AND
	time_month_key < 201801
),

ticket_acct_dev_skus AS
(
SELECT --TOP 100000
	ot.tckt_ticketID,
	ot.Account_KEY,
	dkn.device_number,
	fsa.sku_key,
	fsa.time_month_key
FROM   
	sku_assignments fsa
INNER JOIN 
	device_key_number dkn WITH (NOLOCK)
ON 
	fsa.device_key = dkn.Device_key
INNER JOIN 
	original_tickets ot
ON 
	ot.Account_KEY = fsa.Account_KEY AND 
	ot.time_month_key = fsa.time_month_key
GROUP BY
	ot.tckt_ticketID,
	ot.Account_KEY,
	dkn.device_number,
	fsa.sku_key,
	fsa.time_month_key
),

ticket_sku_counts AS  -- at time of ticket creation 
(
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

ticket_device_counts AS  -- at time of ticket creation 
(
SELECT
	tckt_ticketID,
	COUNT(DISTINCT device_number) as ticket_device_count
FROM
	ticket_acct_dev_skus
GROUP BY
	tckt_ticketID
)

SELECT --TOP 50000
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
GROUP BY
	tsc.tckt_ticketID,
	tsc.sku_key,
	tsc.ticket_sku_count,
	tdc.ticket_device_count
--ORDER BY
--	tsc.tckt_ticketID DESC,
--	tsc.sku_key DESC

