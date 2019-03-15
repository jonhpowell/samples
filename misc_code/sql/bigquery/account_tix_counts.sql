#standardSQL

# Initial Account History Features, V1: ticket counts for last 1, 4, 16 and 30 weeks for the same acccount
# Start by getting the difference from 2016-06-01 in hours (some rounding, but not as bad as weeks) and
#   then go back that many hours counting.

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

# have to get -7 months more data from earliest tickets in master

tickets_secs_number AS
(
SELECT
  tmd.tckt_ticketID,
  tans.Account_Name,
  CAST(TIMESTAMP_DIFF(created, '2016-06-01', SECOND) AS INT64) AS base_secs  -- week from earliest date in history
FROM
  `fluid-door-179122.data_science_dev.xcore_tickets_meta_data_lastQ` tmd
LEFT JOIN
  ticket_account_names tans
ON
  tmd.tckt_ticketID = tans.tckt_ticketID
),

# only include tickets from Damien's original pull & join with ticket history, 
#   getting base_week w/in account partition to make next self-join easier

tickets_to_include AS
(
SELECT
  mct.tckt_ticketID,
--  mct.created,        -- temporary
  tsn.Account_Name,
  tsn.base_secs
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct
LEFT JOIN
  tickets_secs_number tsn
ON
  mct.tckt_ticketID = tsn.tckt_ticketID
),

last_history_as_rows AS
(
SELECT
  tti.tckt_ticketID,
--  tti.created,        -- temporary
  tti.Account_Name,
  tti.base_secs AS base_tix_secs,
  twn.tckt_ticketID as earlier_ticketID,
  twn.base_secs AS earlier_base_secs,
  tti.base_secs - twn.base_secs AS secs_diff
FROM
  tickets_to_include tti
LEFT JOIN
  tickets_secs_number twn
ON
  tti.Account_Name = twn.Account_Name AND
  tti.base_secs > twn.base_secs AND
  tti.base_secs - twn.base_secs < 5136*3600   -- about 7 months/ 30 weeks in seconds; no history before this allowed
--WHERE
--  TRIM(tti.Account_name) = 'EA Internal Managed Infrastructure'
),

/*
SELECT
  *
FROM
  last_history_as_rows
ORDER BY
  Account_Name,
  tckt_ticketID
*/

count_hist_30w AS
(
SELECT
  tckt_ticketID,
--  created,        -- temporary
  Account_Name,
  COUNT(1) as tix_cnt_30w
FROM
  last_history_as_rows
GROUP BY
  tckt_ticketID,
--  created,
  Account_Name
),

/*
SELECT
  *
FROM
  count_hist_30w
ORDER BY
  Account_Name,
  tckt_ticketID
*/

count_hist_16w AS
(
SELECT
  tckt_ticketID,
--  created,        -- temporary
  Account_Name,
  COUNT(1) as tix_cnt_16w
FROM
  last_history_as_rows
WHERE
  secs_diff < 16*168*3600
GROUP BY
  tckt_ticketID,
--  created,
  Account_Name
),

/*
SELECT
  *
FROM
  count_hist_16w
ORDER BY
  Account_Name,
  tckt_ticketID
*/

count_hist_4w AS
(
SELECT
  tckt_ticketID,
--  created,        -- temporary
  Account_Name,
  COUNT(1) as tix_cnt_4w
FROM
  last_history_as_rows
WHERE
  secs_diff < 4*168*3600
GROUP BY
  tckt_ticketID,
--  created,
  Account_Name
),

/*
SELECT
  *
FROM
  count_hist_4w
ORDER BY
  Account_Name,
  tckt_ticketID
*/

count_hist_1w AS
(
SELECT
  tckt_ticketID,
--  created,        -- temporary
  Account_Name,
  COUNT(1) as tix_cnt_1w
FROM
  last_history_as_rows
WHERE
  secs_diff < 1*168*3600
GROUP BY
  tckt_ticketID,
--  created,
  Account_Name
)

SELECT
  lhr.tckt_ticketID,
--  lhr.created,
  lhr.Account_Name,
  IF(h1w.tix_cnt_1w IS NULL, NULL, h1w.tix_cnt_1w) as tix_cnt_1w,
  IF(h4w.tix_cnt_4w IS NULL, NULL, h4w.tix_cnt_4w) as tix_cnt_4w,
  IF(h16w.tix_cnt_16w IS NULL, NULL, h16w.tix_cnt_16w) as tix_cnt_16w,
  IF(h30w.tix_cnt_30w IS NULL, NULL, h30w.tix_cnt_30w) as tix_cnt_30w
FROM
  last_history_as_rows lhr
LEFT JOIN
  count_hist_30w h30w
ON
  lhr.tckt_ticketID = h30w.tckt_ticketID
LEFT JOIN
  count_hist_16w h16w
ON
  lhr.tckt_ticketID = h16w.tckt_ticketID
LEFT JOIN
  count_hist_4w h4w
ON
  lhr.tckt_ticketID = h4w.tckt_ticketID
LEFT JOIN
  count_hist_1w h1w
ON
  lhr.tckt_ticketID = h1w.tckt_ticketID
GROUP BY
  Account_Name,
  tckt_ticketID,
--  created,
  tix_cnt_1w,
  tix_cnt_4w,
  tix_cnt_16w,
  tix_cnt_30w
ORDER BY
  Account_Name ASC,
  tckt_ticketID DESC

