#standardSQL

# Initial Account History Features, V1: ticket DURATION for last 1, 4, 16 and 30 weeks for the same acccount
# Start by getting the difference from 2016-06-01 in hours (some rounding, but not as bad as weeks) and 
#   then go back that many hours counting.
#
# Algorithm:
#   1. Build acct name, work type, work end, duration & difficulty table back to earliest work data
#   2. Over Damien's original ticket range get last 30w, 16w, 4w, 1w from above table by ticket creation date
#         by each attribute (count, duration, difficulty).

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

all_tickets_by_acct AS
(
SELECT
  tmd.tckt_ticketID,
  tmd.created,
  tans.Account_Name
FROM
  `fluid-door-179122.data_science_dev.xcore_tickets_meta_data_lastQ` tmd 
LEFT JOIN
  ticket_account_names tans
ON
  tmd.tckt_ticketID = tans.tckt_ticketID
),

# Build account name, work type, work end, duration & difficulty table back to earliest work data

work_log_by_account AS
(
SELECT
  ata.Account_Name,
--  ata.tckt_ticketID,  -- for debugging
  twm.work_type,
  TIMESTAMP_ADD(twm.log_work_date, INTERVAL twm.Duration MINUTE) AS work_end,
  twm.Duration as duration_mins,
  twm.y_work_difficulty as difficulty
FROM 
  all_tickets_by_acct ata
INNER JOIN
  `fluid-door-179122.data_science_dev.xcore_ticket_work_dws_managed` twm
ON
  ata.tckt_ticketID = twm.TCKT_TicketID
),

# only include tickets from Damien's original pull & join with ticket work history by work date that is
#   before the ticket created date...
# Do 30 week summaries

last_30w_work_dur AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  SUM(wla.duration_mins) as duration_sum
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  work_log_by_account wla 
ON
  mct.Account_Name = wla.Account_Name
WHERE
  mct.created > wla.work_end AND
  TIMESTAMP_DIFF(mct.created, wla.work_end, SECOND) < 5136*3600 -- about 7 months/30 weeks in seconds; no history before this allowed
GROUP BY
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type
),

order_last_30w_work_dur AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(duration_sum) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_total_dur,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY duration_sum DESC) AS acct_tkt_ord
FROM
  last_30w_work_dur
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum
),

final_30w_rows AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum / acct_tkt_total_dur AS wrk_typ_dur_wt,
  acct_tkt_ord
FROM
  order_last_30w_work_dur
WHERE
  acct_tkt_ord <= 5  -- only need last 5 highest
),

single_30w_rows AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_dur_30w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_dur_30w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_dur_30w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_dur_30w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_dur_30w_5,
  NTH_VALUE(wrk_typ_dur_wt, 1) OVER w1 AS wrk_typ_dur_30w_wt_1,
  NTH_VALUE(wrk_typ_dur_wt, 2) OVER w1 as wrk_typ_dur_30w_wt_2,
  NTH_VALUE(wrk_typ_dur_wt, 3) OVER w1 as wrk_typ_dur_30w_wt_3,
  NTH_VALUE(wrk_typ_dur_wt, 4) OVER w1 as wrk_typ_dur_30w_wt_4,
  NTH_VALUE(wrk_typ_dur_wt, 5) OVER w1 as wrk_typ_dur_30w_wt_5
FROM
  final_30w_rows fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY acct_tkt_ord ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 16-week duration period looking back

last_16w_work_dur AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  SUM(wla.duration_mins) as duration_sum
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  work_log_by_account wla 
ON
  mct.Account_Name = wla.Account_Name
WHERE
  mct.created > wla.work_end AND
  TIMESTAMP_DIFF(mct.created, wla.work_end, SECOND) < 16*168*3600 -- 16 weeks in seconds; no history before this allowed
GROUP BY
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type
),

order_last_16w_work_dur AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(duration_sum) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_total_dur,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY duration_sum DESC) AS acct_tkt_ord
FROM
  last_16w_work_dur
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum
),

final_16w_rows AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum / acct_tkt_total_dur AS wrk_typ_dur_wt,
  acct_tkt_ord
FROM
  order_last_16w_work_dur
WHERE
  acct_tkt_ord <= 5  -- only need last 5 highest
),

single_16w_rows AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_dur_16w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_dur_16w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_dur_16w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_dur_16w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_dur_16w_5,
  NTH_VALUE(wrk_typ_dur_wt, 1) OVER w1 AS wrk_typ_dur_16w_wt_1,
  NTH_VALUE(wrk_typ_dur_wt, 2) OVER w1 as wrk_typ_dur_16w_wt_2,
  NTH_VALUE(wrk_typ_dur_wt, 3) OVER w1 as wrk_typ_dur_16w_wt_3,
  NTH_VALUE(wrk_typ_dur_wt, 4) OVER w1 as wrk_typ_dur_16w_wt_4,
  NTH_VALUE(wrk_typ_dur_wt, 5) OVER w1 as wrk_typ_dur_16w_wt_5
FROM
  final_16w_rows fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY acct_tkt_ord ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 4-week duration period looking back

last_4w_work_dur AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  SUM(wla.duration_mins) as duration_sum
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  work_log_by_account wla 
ON
  mct.Account_Name = wla.Account_Name
WHERE
  mct.created > wla.work_end AND
  TIMESTAMP_DIFF(mct.created, wla.work_end, SECOND) < 4*168*3600 -- 4 weeks in seconds; no history before this allowed
GROUP BY
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type
),

order_last_4w_work_dur AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(duration_sum) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_total_dur,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY duration_sum DESC) AS acct_tkt_ord
FROM
  last_4w_work_dur
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum
),

final_4w_rows AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum / acct_tkt_total_dur AS wrk_typ_dur_wt,
  acct_tkt_ord
FROM
  order_last_4w_work_dur
WHERE
  acct_tkt_ord <= 5  -- only need last 5 highest
),

single_4w_rows AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_dur_4w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_dur_4w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_dur_4w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_dur_4w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_dur_4w_5,
  NTH_VALUE(wrk_typ_dur_wt, 1) OVER w1 AS wrk_typ_dur_4w_wt_1,
  NTH_VALUE(wrk_typ_dur_wt, 2) OVER w1 as wrk_typ_dur_4w_wt_2,
  NTH_VALUE(wrk_typ_dur_wt, 3) OVER w1 as wrk_typ_dur_4w_wt_3,
  NTH_VALUE(wrk_typ_dur_wt, 4) OVER w1 as wrk_typ_dur_4w_wt_4,
  NTH_VALUE(wrk_typ_dur_wt, 5) OVER w1 as wrk_typ_dur_4w_wt_5
FROM
  final_4w_rows fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY acct_tkt_ord ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 1-week duration period looking back

last_1w_work_dur AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  SUM(wla.duration_mins) as duration_sum
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  work_log_by_account wla 
ON
  mct.Account_Name = wla.Account_Name
WHERE
  mct.created > wla.work_end AND
  TIMESTAMP_DIFF(mct.created, wla.work_end, SECOND) < 1*168*3600 -- 1 week in seconds; no history before this allowed
GROUP BY
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type
),

order_last_1w_work_dur AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(duration_sum) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_total_dur,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY duration_sum DESC) AS acct_tkt_ord
FROM
  last_1w_work_dur
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum
),

final_1w_rows AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  duration_sum / acct_tkt_total_dur AS wrk_typ_dur_wt,
  acct_tkt_ord
FROM
  order_last_1w_work_dur
WHERE
  acct_tkt_ord <= 5  -- only need last 5 highest
),

single_1w_rows AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_dur_1w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_dur_1w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_dur_1w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_dur_1w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_dur_1w_5,
  NTH_VALUE(wrk_typ_dur_wt, 1) OVER w1 AS wrk_typ_dur_1w_wt_1,
  NTH_VALUE(wrk_typ_dur_wt, 2) OVER w1 as wrk_typ_dur_1w_wt_2,
  NTH_VALUE(wrk_typ_dur_wt, 3) OVER w1 as wrk_typ_dur_1w_wt_3,
  NTH_VALUE(wrk_typ_dur_wt, 4) OVER w1 as wrk_typ_dur_1w_wt_4,
  NTH_VALUE(wrk_typ_dur_wt, 5) OVER w1 as wrk_typ_dur_1w_wt_5
FROM
  final_1w_rows fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY acct_tkt_ord ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

/*
SELECT
  *
FROM
  single_1w_rows
--WHERE
--  Account_Name = 'zulily, LLC' AND
--  tckt_ticketID = 45708311
ORDER BY
  Account_Name DESC,
  tckt_ticketID DESC 
*/

final_all_periods_rows AS
(
SELECT
  mct.Account_Name,
  mct.tckt_ticketID,
  
  r1w.wrk_typ_dur_1w_1,
  r1w.wrk_typ_dur_1w_2,
  r1w.wrk_typ_dur_1w_3,
  r1w.wrk_typ_dur_1w_4,
  r1w.wrk_typ_dur_1w_5,
  r1w.wrk_typ_dur_1w_wt_1,
  r1w.wrk_typ_dur_1w_wt_2,
  r1w.wrk_typ_dur_1w_wt_3,
  r1w.wrk_typ_dur_1w_wt_4,
  r1w.wrk_typ_dur_1w_wt_5,
  
  r4w.wrk_typ_dur_4w_1,
  r4w.wrk_typ_dur_4w_2,
  r4w.wrk_typ_dur_4w_3,
  r4w.wrk_typ_dur_4w_4,
  r4w.wrk_typ_dur_4w_5,
  r4w.wrk_typ_dur_4w_wt_1,
  r4w.wrk_typ_dur_4w_wt_2,
  r4w.wrk_typ_dur_4w_wt_3,
  r4w.wrk_typ_dur_4w_wt_4,
  r4w.wrk_typ_dur_4w_wt_5,

  r16w.wrk_typ_dur_16w_1,
  r16w.wrk_typ_dur_16w_2,
  r16w.wrk_typ_dur_16w_3,
  r16w.wrk_typ_dur_16w_4,
  r16w.wrk_typ_dur_16w_5,
  r16w.wrk_typ_dur_16w_wt_1,
  r16w.wrk_typ_dur_16w_wt_2,
  r16w.wrk_typ_dur_16w_wt_3,
  r16w.wrk_typ_dur_16w_wt_4,
  r16w.wrk_typ_dur_16w_wt_5,
  
  r30w.wrk_typ_dur_30w_1,
  r30w.wrk_typ_dur_30w_2,
  r30w.wrk_typ_dur_30w_3,
  r30w.wrk_typ_dur_30w_4,
  r30w.wrk_typ_dur_30w_5,
  r30w.wrk_typ_dur_30w_wt_1,
  r30w.wrk_typ_dur_30w_wt_2,
  r30w.wrk_typ_dur_30w_wt_3,
  r30w.wrk_typ_dur_30w_wt_4,
  r30w.wrk_typ_dur_30w_wt_5
  
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  single_1w_rows r1w
ON
  mct.tckt_ticketID = r1w.tckt_ticketID
LEFT JOIN
  single_4w_rows r4w
ON
  mct.tckt_ticketID = r4w.tckt_ticketID
LEFT JOIN
  single_16w_rows r16w
ON
  mct.tckt_ticketID = r16w.tckt_ticketID
LEFT JOIN
  single_30w_rows r30w
ON
  mct.tckt_ticketID = r30w.tckt_ticketID
)

SELECT
  *
FROM
  final_all_periods_rows
ORDER BY
  Account_Name DESC,
  tckt_ticketID DESC

