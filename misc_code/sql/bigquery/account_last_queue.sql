#standardSQL

# Initial Account History Features, V1: final queue for last N tickets on same acccount, where N = 5
# Since history only goes back 6 months from our earliest ticket at 2017-01-01, then trim allowed account history
#   for ALL accounts for each ticket to also 6 months back.

# get account names that include tickets created earlier than 2017-01-01

WITH ticket_account_names AS
(
SELECT
  TCKT_TicketID,
  Account_Name
FROM
  `fluid-door-179122.data_science_dev.core_ticket_account_history_dws_managed`
GROUP BY
  TCKT_TicketID,
  Account_Name
),

# have to get -6 months more data from earliest tickets in master

ticket_history_indexed AS
(
SELECT
  tmd.tckt_ticketID,
  tmd.created,
  tans.Account_Name,
  tmd.y_final_queue,
  ROW_NUMBER() OVER (PARTITION BY tans.Account_Name ORDER BY tmd.created ASC) AS acct_tix_ordinal
FROM
  `fluid-door-179122.data_science_dev.xcore_tickets_meta_data_lastQ` tmd
LEFT JOIN
  ticket_account_names tans
ON
  tmd.tckt_ticketID = tans.tckt_ticketID
),

# only include tickets from Damien's original pull & join with ticket history, 
#   getting ordinal w/in account partition to make next self-join easier

tickets_to_include AS
(
SELECT
  mct.tckt_ticketID,
  thi.Created,
  thi.Account_Name,
  thi.acct_tix_ordinal
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct
LEFT JOIN
  ticket_history_indexed thi
ON
  mct.tckt_ticketID = thi.tckt_ticketID
),

last_queues_as_rows AS 
(
SELECT
  tti.tckt_ticketID,
  tti.created,
  thi.created as older_ticket_created,  -- temporary
  TIMESTAMP_DIFF(tti.created, thi.created, HOUR) as hours_diff,
  tti.acct_tix_ordinal AS base_tix_ordinal,
--  thi.tckt_ticketID as earlier_ticketID,
  thi.created AS earlier_created,
  thi.Account_Name,
  thi.y_final_queue,
  thi.acct_tix_ordinal,
  tti.acct_tix_ordinal - thi.acct_tix_ordinal AS ordinal_diff  -- for row:column pivot
FROM
  tickets_to_include tti
LEFT JOIN
  ticket_history_indexed thi
ON
  tti.Account_Name = thi.Account_Name AND
  tti.created > thi.created AND
  TIMESTAMP_DIFF(tti.created, thi.created, HOUR) < 5136 -- about 6 months in hours; no history before this allowed
WHERE
  thi.acct_tix_ordinal >= tti.acct_tix_ordinal - 5
)

/*
SELECT
  *
FROM
  last_queues_as_rows
*/

SELECT
  tckt_ticketID,
  created,
--  base_tix_ordinal,
  Account_Name,
--  y_final_queue,
--  acct_tix_ordinal,
  MAX(IF(ordinal_diff = 1, y_final_queue, NULL)) as final_q_tix_1,
  MAX(IF(ordinal_diff = 2, y_final_queue, NULL)) as final_q_tix_2,
  MAX(IF(ordinal_diff = 3, y_final_queue, NULL)) as final_q_tix_3,
  MAX(IF(ordinal_diff = 4, y_final_queue, NULL)) as final_q_tix_4,
  MAX(IF(ordinal_diff = 5, y_final_queue, NULL)) as final_q_tix_5
FROM
  last_queues_as_rows
GROUP BY
  Account_Name,
  tckt_ticketID,
  created
ORDER BY
  Account_Name ASC,
  tckt_ticketID DESC

