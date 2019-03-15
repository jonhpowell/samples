-- get products ("SKU's") for each device in each ticket to form the basis of a one-hot encoded ticket:product table
--   revised version that treats Device_KEY correctly and joins by time_month_key from tickets
--   should be much faster than r1.
-- NOTE: this version only does 1/2 of the overall time range (easy to fix)

WITH original_tickets AS
(
SELECT --TOP 1000
	dt.tckt_ticketID,
	xrt.computer_number as device_id,
	dt.created,
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

sku_assignments AS
(
SELECT  
	device_key,
	sku_key,
	time_month_key
FROM 
	[DWS_Managed].[dbo].[Fact_SKU_Assignment]
WHERE 
	time_month_key >= 201701 AND
	time_month_key < 201801
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
)

SELECT --TOP 1000
	ot.tckt_ticketID,
	ot.device_id,
	fsa.sku_key --,
--	ot.created,
--	ot.time_month_key
FROM   
	sku_assignments fsa WITH (NOLOCK)
INNER JOIN 
	device_key_number dkn WITH (NOLOCK)
ON 
	fsa.device_key = dkn.Device_key
INNER JOIN 
	original_tickets ot
ON 
	ot.device_id = dkn.device_number AND 
	ot.time_month_key = fsa.time_month_key
-ORDER BY
-ot.tckt_ticketID DESC,
-ot.device_id DESC,
-fsa.sku_key DESC --,
--	ot.created,
--	ot.time_month_key

