#standardSQL

# Name: acct_work_type_last_period_df_avg.sql
# Description: Initial Account History Features, V1: ticket AVERAGE DIFFICULTY for last 1, 4, 16 and 30 weeks for the same acccount
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

last_30w_work_df AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  AVG(wla.difficulty) as difficulty_avg,
  MAX(wla.difficulty) as difficulty_max
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

order_last_30w_work_df AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(difficulty_avg) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_avg,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_avg DESC) AS ord_df_avg,
  SUM(difficulty_max) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_max,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_max DESC) AS ord_df_max
FROM
  last_30w_work_df
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max
),

-- have to do 2 difficulty types in different tables because may have different ordering

final_30w_rows_df_avg AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg / sum_df_avg AS wrk_typ_df_avg_wt,
  ord_df_avg
FROM
  order_last_30w_work_df
WHERE
  ord_df_avg <= 5  -- only need last 5 highest
),

single_30w_rows_df_avg AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_avg_30w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_avg_30w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_avg_30w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_avg_30w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_avg_30w_5,
  NTH_VALUE(wrk_typ_df_avg_wt, 1) OVER w1 AS wrk_typ_df_avg_30w_wt_1,
  NTH_VALUE(wrk_typ_df_avg_wt, 2) OVER w1 as wrk_typ_df_avg_30w_wt_2,
  NTH_VALUE(wrk_typ_df_avg_wt, 3) OVER w1 as wrk_typ_df_avg_30w_wt_3,
  NTH_VALUE(wrk_typ_df_avg_wt, 4) OVER w1 as wrk_typ_df_avg_30w_wt_4,
  NTH_VALUE(wrk_typ_df_avg_wt, 5) OVER w1 as wrk_typ_df_avg_30w_wt_5
FROM
  final_30w_rows_df_avg fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_avg ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

final_30w_rows_df_max AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_max / sum_df_max AS wrk_typ_df_max_wt,
  ord_df_max
FROM
  order_last_30w_work_df
WHERE
  ord_df_max <= 5  -- only need last 5 highest
),

single_30w_rows_df_max AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_max_30w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_max_30w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_max_30w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_max_30w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_max_30w_5,
  NTH_VALUE(wrk_typ_df_max_wt, 1) OVER w1 AS wrk_typ_df_max_30w_wt_1,
  NTH_VALUE(wrk_typ_df_max_wt, 2) OVER w1 as wrk_typ_df_max_30w_wt_2,
  NTH_VALUE(wrk_typ_df_max_wt, 3) OVER w1 as wrk_typ_df_max_30w_wt_3,
  NTH_VALUE(wrk_typ_df_max_wt, 4) OVER w1 as wrk_typ_df_max_30w_wt_4,
  NTH_VALUE(wrk_typ_df_max_wt, 5) OVER w1 as wrk_typ_df_max_30w_wt_5
FROM
  final_30w_rows_df_max fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_max ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 16-week duration period looking back

last_16w_work_df AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  AVG(wla.difficulty) as difficulty_avg,
  MAX(wla.difficulty) as difficulty_max
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

order_last_16w_work_df AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(difficulty_avg) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_avg,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_avg DESC) AS ord_df_avg,
  SUM(difficulty_max) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_max,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_max DESC) AS ord_df_max
FROM
  last_16w_work_df
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max
),

-- have to do 2 difficulty types in different tables because may have different ordering

final_16w_rows_df_avg AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg / sum_df_avg AS wrk_typ_df_avg_wt,
  ord_df_avg
FROM
  order_last_16w_work_df
WHERE
  ord_df_avg <= 5  -- only need last 5 highest
),

single_16w_rows_df_avg AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_avg_16w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_avg_16w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_avg_16w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_avg_16w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_avg_16w_5,
  NTH_VALUE(wrk_typ_df_avg_wt, 1) OVER w1 AS wrk_typ_df_avg_16w_wt_1,
  NTH_VALUE(wrk_typ_df_avg_wt, 2) OVER w1 as wrk_typ_df_avg_16w_wt_2,
  NTH_VALUE(wrk_typ_df_avg_wt, 3) OVER w1 as wrk_typ_df_avg_16w_wt_3,
  NTH_VALUE(wrk_typ_df_avg_wt, 4) OVER w1 as wrk_typ_df_avg_16w_wt_4,
  NTH_VALUE(wrk_typ_df_avg_wt, 5) OVER w1 as wrk_typ_df_avg_16w_wt_5
FROM
  final_16w_rows_df_avg fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_avg ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

final_16w_rows_df_max AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_max / sum_df_max AS wrk_typ_df_max_wt,
  ord_df_max
FROM
  order_last_16w_work_df
WHERE
  ord_df_max <= 5  -- only need last 5 highest
),

single_16w_rows_df_max AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_max_16w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_max_16w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_max_16w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_max_16w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_max_16w_5,
  NTH_VALUE(wrk_typ_df_max_wt, 1) OVER w1 AS wrk_typ_df_max_16w_wt_1,
  NTH_VALUE(wrk_typ_df_max_wt, 2) OVER w1 as wrk_typ_df_max_16w_wt_2,
  NTH_VALUE(wrk_typ_df_max_wt, 3) OVER w1 as wrk_typ_df_max_16w_wt_3,
  NTH_VALUE(wrk_typ_df_max_wt, 4) OVER w1 as wrk_typ_df_max_16w_wt_4,
  NTH_VALUE(wrk_typ_df_max_wt, 5) OVER w1 as wrk_typ_df_max_16w_wt_5
FROM
  final_16w_rows_df_max fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_max ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 4-week duration period looking back

last_4w_work_df AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  AVG(wla.difficulty) as difficulty_avg,
  MAX(wla.difficulty) as difficulty_max
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

order_last_4w_work_df AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(difficulty_avg) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_avg,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_avg DESC) AS ord_df_avg,
  SUM(difficulty_max) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_max,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_max DESC) AS ord_df_max
FROM
  last_4w_work_df
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max
),

-- have to do 2 difficulty types in different tables because may have different ordering

final_4w_rows_df_avg AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg / sum_df_avg AS wrk_typ_df_avg_wt,
  ord_df_avg
FROM
  order_last_4w_work_df
WHERE
  ord_df_avg <= 5  -- only need last 5 highest
),

single_4w_rows_df_avg AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_avg_4w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_avg_4w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_avg_4w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_avg_4w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_avg_4w_5,
  NTH_VALUE(wrk_typ_df_avg_wt, 1) OVER w1 AS wrk_typ_df_avg_4w_wt_1,
  NTH_VALUE(wrk_typ_df_avg_wt, 2) OVER w1 as wrk_typ_df_avg_4w_wt_2,
  NTH_VALUE(wrk_typ_df_avg_wt, 3) OVER w1 as wrk_typ_df_avg_4w_wt_3,
  NTH_VALUE(wrk_typ_df_avg_wt, 4) OVER w1 as wrk_typ_df_avg_4w_wt_4,
  NTH_VALUE(wrk_typ_df_avg_wt, 5) OVER w1 as wrk_typ_df_avg_4w_wt_5
FROM
  final_4w_rows_df_avg fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_avg ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

final_4w_rows_df_max AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_max / sum_df_max AS wrk_typ_df_max_wt,
  ord_df_max
FROM
  order_last_4w_work_df
WHERE
  ord_df_max <= 5  -- only need last 5 highest
),

single_4w_rows_df_max AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_max_4w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_max_4w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_max_4w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_max_4w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_max_4w_5,
  NTH_VALUE(wrk_typ_df_max_wt, 1) OVER w1 AS wrk_typ_df_max_4w_wt_1,
  NTH_VALUE(wrk_typ_df_max_wt, 2) OVER w1 as wrk_typ_df_max_4w_wt_2,
  NTH_VALUE(wrk_typ_df_max_wt, 3) OVER w1 as wrk_typ_df_max_4w_wt_3,
  NTH_VALUE(wrk_typ_df_max_wt, 4) OVER w1 as wrk_typ_df_max_4w_wt_4,
  NTH_VALUE(wrk_typ_df_max_wt, 5) OVER w1 as wrk_typ_df_max_4w_wt_5
FROM
  final_4w_rows_df_max fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_max ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

# Now do 1-week duration period looking back

last_1w_work_df AS
(
SELECT
  wla.Account_Name,
  mct.tckt_ticketID,
  wla.work_type,
  AVG(wla.difficulty) as difficulty_avg,
  MAX(wla.difficulty) as difficulty_max
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

order_last_1w_work_df AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max,
  COUNT(1) OVER (PARTITION BY Account_Name, tckt_ticketID) AS acct_tkt_cnt,
  SUM(difficulty_avg) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_avg,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_avg DESC) AS ord_df_avg,
  SUM(difficulty_max) OVER (PARTITION BY Account_Name, tckt_ticketID) AS sum_df_max,
  ROW_NUMBER() OVER (PARTITION BY Account_Name, tckt_ticketID ORDER BY difficulty_max DESC) AS ord_df_max
FROM
  last_1w_work_df
GROUP BY
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg,
  difficulty_max
),

-- have to do 2 difficulty types in different tables because may have different ordering

final_1w_rows_df_avg AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_avg / sum_df_avg AS wrk_typ_df_avg_wt,
  ord_df_avg
FROM
  order_last_1w_work_df
WHERE
  ord_df_avg <= 5  -- only need last 5 highest
),

single_1w_rows_df_avg AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_avg_1w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_avg_1w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_avg_1w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_avg_1w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_avg_1w_5,
  NTH_VALUE(wrk_typ_df_avg_wt, 1) OVER w1 AS wrk_typ_df_avg_1w_wt_1,
  NTH_VALUE(wrk_typ_df_avg_wt, 2) OVER w1 as wrk_typ_df_avg_1w_wt_2,
  NTH_VALUE(wrk_typ_df_avg_wt, 3) OVER w1 as wrk_typ_df_avg_1w_wt_3,
  NTH_VALUE(wrk_typ_df_avg_wt, 4) OVER w1 as wrk_typ_df_avg_1w_wt_4,
  NTH_VALUE(wrk_typ_df_avg_wt, 5) OVER w1 as wrk_typ_df_avg_1w_wt_5
FROM
  final_1w_rows_df_avg fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_avg ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

final_1w_rows_df_max AS
(
SELECT
  Account_Name,
  tckt_ticketID,
  work_type,
  difficulty_max / sum_df_max AS wrk_typ_df_max_wt,
  ord_df_max
FROM
  order_last_1w_work_df
WHERE
  ord_df_max <= 5  -- only need last 5 highest
),

single_1w_rows_df_max AS
(
SELECT DISTINCT
  Account_Name,
  tckt_ticketID,
  NTH_VALUE(work_type, 1) OVER w1 AS wrk_typ_df_max_1w_1,
  NTH_VALUE(work_type, 2) OVER w1 as wrk_typ_df_max_1w_2,
  NTH_VALUE(work_type, 3) OVER w1 as wrk_typ_df_max_1w_3,
  NTH_VALUE(work_type, 4) OVER w1 as wrk_typ_df_max_1w_4,
  NTH_VALUE(work_type, 5) OVER w1 as wrk_typ_df_max_1w_5,
  NTH_VALUE(wrk_typ_df_max_wt, 1) OVER w1 AS wrk_typ_df_max_1w_wt_1,
  NTH_VALUE(wrk_typ_df_max_wt, 2) OVER w1 as wrk_typ_df_max_1w_wt_2,
  NTH_VALUE(wrk_typ_df_max_wt, 3) OVER w1 as wrk_typ_df_max_1w_wt_3,
  NTH_VALUE(wrk_typ_df_max_wt, 4) OVER w1 as wrk_typ_df_max_1w_wt_4,
  NTH_VALUE(wrk_typ_df_max_wt, 5) OVER w1 as wrk_typ_df_max_1w_wt_5
FROM
  final_1w_rows_df_max fr
WINDOW w1 AS (PARTITION BY Account_Name, tckt_ticketID ORDER BY ord_df_max ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

/*
SELECT
  *
FROM
  --single_1w_rows_df_avg
  single_1w_rows_df_max
WHERE
  Account_Name = 'zulily, LLC'
ORDER BY
  Account_Name DESC,
  tckt_ticketID DESC
*/

final_all_periods_rows AS
(
SELECT
  mct.Account_Name,
  mct.tckt_ticketID,
  
  r1wa.wrk_typ_df_avg_1w_1,
  r1wa.wrk_typ_df_avg_1w_2,
  r1wa.wrk_typ_df_avg_1w_3,
  r1wa.wrk_typ_df_avg_1w_4,
  r1wa.wrk_typ_df_avg_1w_5,
  r1wa.wrk_typ_df_avg_1w_wt_1,
  r1wa.wrk_typ_df_avg_1w_wt_2,
  r1wa.wrk_typ_df_avg_1w_wt_3,
  r1wa.wrk_typ_df_avg_1w_wt_4,
  r1wa.wrk_typ_df_avg_1w_wt_5,

  r1wm.wrk_typ_df_max_1w_1,
  r1wm.wrk_typ_df_max_1w_2,
  r1wm.wrk_typ_df_max_1w_3,
  r1wm.wrk_typ_df_max_1w_4,
  r1wm.wrk_typ_df_max_1w_5,
  r1wm.wrk_typ_df_max_1w_wt_1,
  r1wm.wrk_typ_df_max_1w_wt_2,
  r1wm.wrk_typ_df_max_1w_wt_3,
  r1wm.wrk_typ_df_max_1w_wt_4,
  r1wm.wrk_typ_df_max_1w_wt_5,
  
  r4wa.wrk_typ_df_avg_4w_1,
  r4wa.wrk_typ_df_avg_4w_2,
  r4wa.wrk_typ_df_avg_4w_3,
  r4wa.wrk_typ_df_avg_4w_4,
  r4wa.wrk_typ_df_avg_4w_5,
  r4wa.wrk_typ_df_avg_4w_wt_1,
  r4wa.wrk_typ_df_avg_4w_wt_2,
  r4wa.wrk_typ_df_avg_4w_wt_3,
  r4wa.wrk_typ_df_avg_4w_wt_4,
  r4wa.wrk_typ_df_avg_4w_wt_5,

  r4wm.wrk_typ_df_max_4w_1,
  r4wm.wrk_typ_df_max_4w_2,
  r4wm.wrk_typ_df_max_4w_3,
  r4wm.wrk_typ_df_max_4w_4,
  r4wm.wrk_typ_df_max_4w_5,
  r4wm.wrk_typ_df_max_4w_wt_1,
  r4wm.wrk_typ_df_max_4w_wt_2,
  r4wm.wrk_typ_df_max_4w_wt_3,
  r4wm.wrk_typ_df_max_4w_wt_4,
  r4wm.wrk_typ_df_max_4w_wt_5,
  
  r16wa.wrk_typ_df_avg_16w_1,
  r16wa.wrk_typ_df_avg_16w_2,
  r16wa.wrk_typ_df_avg_16w_3,
  r16wa.wrk_typ_df_avg_16w_4,
  r16wa.wrk_typ_df_avg_16w_5,
  r16wa.wrk_typ_df_avg_16w_wt_1,
  r16wa.wrk_typ_df_avg_16w_wt_2,
  r16wa.wrk_typ_df_avg_16w_wt_3,
  r16wa.wrk_typ_df_avg_16w_wt_4,
  r16wa.wrk_typ_df_avg_16w_wt_5,

  r16wm.wrk_typ_df_max_16w_1,
  r16wm.wrk_typ_df_max_16w_2,
  r16wm.wrk_typ_df_max_16w_3,
  r16wm.wrk_typ_df_max_16w_4,
  r16wm.wrk_typ_df_max_16w_5,
  r16wm.wrk_typ_df_max_16w_wt_1,
  r16wm.wrk_typ_df_max_16w_wt_2,
  r16wm.wrk_typ_df_max_16w_wt_3,
  r16wm.wrk_typ_df_max_16w_wt_4,
  r16wm.wrk_typ_df_max_16w_wt_5,

  r30wa.wrk_typ_df_avg_30w_1,
  r30wa.wrk_typ_df_avg_30w_2,
  r30wa.wrk_typ_df_avg_30w_3,
  r30wa.wrk_typ_df_avg_30w_4,
  r30wa.wrk_typ_df_avg_30w_5,
  r30wa.wrk_typ_df_avg_30w_wt_1,
  r30wa.wrk_typ_df_avg_30w_wt_2,
  r30wa.wrk_typ_df_avg_30w_wt_3,
  r30wa.wrk_typ_df_avg_30w_wt_4,
  r30wa.wrk_typ_df_avg_30w_wt_5,

  r30wm.wrk_typ_df_max_30w_1,
  r30wm.wrk_typ_df_max_30w_2,
  r30wm.wrk_typ_df_max_30w_3,
  r30wm.wrk_typ_df_max_30w_4,
  r30wm.wrk_typ_df_max_30w_5,
  r30wm.wrk_typ_df_max_30w_wt_1,
  r30wm.wrk_typ_df_max_30w_wt_2,
  r30wm.wrk_typ_df_max_30w_wt_3,
  r30wm.wrk_typ_df_max_30w_wt_4,
  r30wm.wrk_typ_df_max_30w_wt_5

FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct 
LEFT JOIN
  single_1w_rows_df_avg r1wa
ON
  mct.tckt_ticketID = r1wa.tckt_ticketID
LEFT JOIN
  single_1w_rows_df_max r1wm
ON
  mct.tckt_ticketID = r1wm.tckt_ticketID
LEFT JOIN
  single_4w_rows_df_avg r4wa
ON
  mct.tckt_ticketID = r4wa.tckt_ticketID
LEFT JOIN
  single_4w_rows_df_max r4wm
ON
  mct.tckt_ticketID = r4wm.tckt_ticketID
LEFT JOIN
  single_16w_rows_df_avg r16wa
ON
  mct.tckt_ticketID = r16wa.tckt_ticketID
LEFT JOIN
  single_16w_rows_df_max r16wm
ON
  mct.tckt_ticketID = r16wm.tckt_ticketID
LEFT JOIN
  single_30w_rows_df_avg r30wa
ON
  mct.tckt_ticketID = r30wa.tckt_ticketID
LEFT JOIN
  single_30w_rows_df_max r30wm
ON
  mct.tckt_ticketID = r30wm.tckt_ticketID
)

SELECT
  *
FROM
  final_all_periods_rows
--ORDER BY    -- runs out of memory
--  Account_Name DESC,
--  tckt_ticketID DESC
  
