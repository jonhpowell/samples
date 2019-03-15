#standardSQL

# Initial Account History Features, V1: max & average work difficulty for last N tickets on same acccount, where N = 5 

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

work_difficulty_history AS
(
SELECT
  TCKT_TicketID,
  AVG(y_work_difficulty) AS avg_work_difficulty,
  MAX(y_work_difficulty) AS max_work_difficulty
FROM  
  `fluid-door-179122.data_science_dev.xcore_ticket_work_dws_managed`
GROUP BY
  TCKT_TicketID
),

/*

SELECT
  *
FROM
  `fluid-door-179122.data_science_dev.xcore_ticket_work_dws_managed`
WHERE
  TCKT_TicketID IN (34891440, 34960907, 34960917, 34981873)
ORDER BY
  TCKT_TicketID
*/
/*
SELECT
  *
FROM
  work_difficulty_history
ORDER BY
  TCKT_TicketID
*/
  
# have to get -6 months more data from earliest tickets in master
ticket_history_indexed AS
(
SELECT
  tmd.tckt_ticketID,
  tmd.created,
  tans.Account_Name,
  wdh.max_work_difficulty,
  wdh.avg_work_difficulty,
  ROW_NUMBER() OVER (PARTITION BY tans.Account_Name ORDER BY tmd.created ASC) AS acct_tix_ordinal
FROM
  `fluid-door-179122.data_science_dev.xcore_tickets_meta_data_lastQ` tmd
INNER JOIN    -- not sure why have to do INNER here...maybe timestamps not 100% lined up?
  work_difficulty_history wdh
ON
  tmd.tckt_ticketID = wdh.tckt_ticketID
LEFT JOIN
  ticket_account_names tans
ON
  tmd.tckt_ticketID = tans.tckt_ticketID
),

/*
SELECT
  *
FROM
  ticket_history_indexed
ORDER BY
  Account_Name ASC,
  tckt_ticketID ASC,
  acct_tix_ordinal ASC
*/

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

last_history_as_rows AS
(
SELECT
  tti.tckt_ticketID,
  tti.created,
  tti.acct_tix_ordinal AS base_tix_ordinal,
  thi.tckt_ticketID as earlier_ticketID,
  thi.created AS earlier_created,
  thi.Account_Name,
  thi.max_work_difficulty,
  thi.avg_work_difficulty,
  thi.acct_tix_ordinal,
  tti.acct_tix_ordinal - thi.acct_tix_ordinal AS ordinal_diff  -- for row:column pivot
FROM
  tickets_to_include tti
LEFT JOIN
  ticket_history_indexed thi
ON
  tti.Account_Name = thi.Account_Name AND
  tti.created > thi.created AND
  TIMESTAMP_DIFF(tti.created, thi.created, HOUR) < 5136   -- about 6 months in hours; no history before this allowed
WHERE
--  tti.Account_Name IS NOT NULL AND -- temporary, 32K null account names (earlier on?)
  thi.acct_tix_ordinal >= tti.acct_tix_ordinal - 5 --AND
--  tti.Account_Name = 'Évos Sound Limited' --(BXS) BestXstats'
)


SELECT
  *
FROM
  last_history_as_rows
ORDER BY
  Account_Name,
  tckt_ticketID,
  earlier_ticketID


/*
SELECT
  tckt_ticketID,
  created,
  Account_Name,
  MAX(IF(ordinal_diff = 1, max_work_difficulty, NULL)) as wrk_dfy_max_1,
  MAX(IF(ordinal_diff = 2, max_work_difficulty, NULL)) as wrk_dfy_max_2,
  MAX(IF(ordinal_diff = 3, max_work_difficulty, NULL)) as wrk_dfy_max_3,
  MAX(IF(ordinal_diff = 4, max_work_difficulty, NULL)) as wrk_dfy_max_4,
  MAX(IF(ordinal_diff = 5, max_work_difficulty, NULL)) as wrk_dfy_max_5,
  MAX(IF(ordinal_diff = 1, avg_work_difficulty, NULL)) as wrk_dfy_avg_1,
  MAX(IF(ordinal_diff = 2, avg_work_difficulty, NULL)) as wrk_dfy_avg_2,
  MAX(IF(ordinal_diff = 3, avg_work_difficulty, NULL)) as wrk_dfy_avg_3,
  MAX(IF(ordinal_diff = 4, avg_work_difficulty, NULL)) as wrk_dfy_avg_4,
  MAX(IF(ordinal_diff = 5, avg_work_difficulty, NULL)) as wrk_dfy_avg_5
FROM
  last_history_as_rows
GROUP BY
  Account_Name,
  tckt_ticketID,
  created
ORDER BY
  Account_Name ASC,
  tckt_ticketID DESC
*/
