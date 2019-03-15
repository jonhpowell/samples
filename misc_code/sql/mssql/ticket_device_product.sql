-- get products ("SKU's") for each device in each ticket to form the basis of a one-hot encoded ticket:product table

WITH original_tickets AS
(
SELECT --TOP 10
	dt.tckt_ticketID,
	dt.created 
FROM 
	[DWS_Managed].[dbo].[Dimension_Ticket] dt WITH (NOLOCK)
WHERE 
	dt.Created >= '20171001' AND 
	dt.Created < '20180101'AND 
--	dt.Created < '20181204'AND 
	dt.source IN ('MyRackspace', 'Phone Call', 'Chat Support', 'Rackspace Employee')
),

ticket_devices AS
(
SELECT --TOP 10000
	oti.TCKT_TicketID,
	xrt.computer_number as device_id,
	oti.created
FROM
	original_tickets oti WITH (NOLOCK)
INNER JOIN
	[DWS_Managed].[dbo].[xref_server_Ticket] xrt WITH (NOLOCK)
ON
	oti.TCKT_TicketID = xrt.TCKT_TicketID
),

ticket_devices_keys AS
(
SELECT --TOP 10000
	tdv.TCKT_TicketID,
	tdv.device_id,
	ddv.Device_KEY,
	ROW_NUMBER() OVER (PARTITION BY tdv.TCKT_TicketID, tdv.device_id ORDER BY ddv.Rec_Updated DESC) AS row_num
FROM
	ticket_devices tdv
INNER JOIN
	[DWS_Managed].[dbo].[Dim_Device] ddv WITH (NOLOCK) 
ON
	tdv.device_id = ddv.Device_Number
WHERE
	ddv.Rec_Updated < tdv.Created
),

reduced_ticket_device_keys AS
(
SELECT
	TCKT_TicketID,
	device_id,
	device_KEY
FROM
	ticket_devices_keys
WHERE
	row_num = 1
)

SELECT --TOP 1000
	td.TCKT_TicketID,
	td.device_id,
	fsa.SKU_KEY
FROM
	reduced_ticket_device_keys td
INNER JOIN
	[DWS_Managed].[dbo].[Fact_SKU_Assignment] fsa WITH (NOLOCK)
ON
	td.Device_KEY = fsa.Device_KEY

