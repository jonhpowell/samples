#standardSQL

# Master meta-data table for Smart Ticket Routing

# get account info at time ticket was created
WITH ticket_account_names AS
(
SELECT
  TCKT_TicketID,
  Account_Name,
  Account_SLA_Type,
  Account_Business_Type,
  Account_Customer_Type,
  Account_IsPartner,
  Account_High_Profile_Flag,
  Account_Service_Level,
  Account_Annual_Revenue,
  Account_Number_Of_Employees,
  x_days_since_acct_creation,
  Account_Billing_Country,
  Account_Billing_State,
  Account_Region,
  Account_Backup_Device_Count,
  Account_Storage_Device_Count,
  Account_Other_Network_Device_Count,
  Account_Server_Count,
  priority
FROM
  `fluid-door-179122.data_science_dev.core_ticket_account_history_dws_managed`
GROUP BY
  TCKT_TicketID,
  Account_Name,
  Account_SLA_Type,
  Account_Business_Type,
  Account_Customer_Type,
  Account_IsPartner,
  Account_High_Profile_Flag,
  Account_Service_Level,
  Account_Annual_Revenue,
  Account_Number_Of_Employees,
  x_days_since_acct_creation,
  Account_Billing_Country,
  Account_Billing_State,
  Account_Region,
  Account_Backup_Device_Count,
  Account_Storage_Device_Count,
  Account_Other_Network_Device_Count,
  Account_Server_Count,
  priority
),

# only include tickets from Damien's original pull

tickets_to_include AS
(
SELECT
  tmd.tckt_ticketID,
  tmd.created,
  tmd.source,
  tmd.team,
  atn.priority,
  tmd.severity,
  tmd.status,  -- probably not that useful since only contains mostly terminal states
  tmd.category,
  tmd.subcategory,
  tmd.Windows,
  tmd.Linux,
  tmd.Plesk,
  atn.Account_Name,
  atn.Account_SLA_Type,
  atn.Account_Business_Type,
  atn.Account_Customer_Type,
  atn.Account_IsPartner,
  atn.Account_High_Profile_Flag,
  atn.Account_Service_Level,
  atn.Account_Annual_Revenue,
  atn.Account_Number_Of_Employees,
  atn.x_days_since_acct_creation,
  atn.Account_Billing_Country,
  atn.Account_Billing_State,
  atn.Account_Region,
  atn.Account_Backup_Device_Count,
  atn.Account_Storage_Device_Count,
  atn.Account_Other_Network_Device_Count,
  atn.Account_Server_Count
FROM
  `fluid-door-179122.data_science_dev.core_tickets_meta_data_lastQ` tmd
LEFT JOIN
  ticket_account_names atn
ON
  tmd.tckt_ticketID = atn.TCKT_TicketID
)

SELECT
  *
FROM
  tickets_to_include
ORDER BY
  tckt_ticketID

