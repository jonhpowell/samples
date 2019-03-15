#standardSQL

# file name: account_work_type_base.sql
# Account History Features, V2: work types for last N tickets with their relative weighting by count
# and duration, all while on the same acccount, where N = 5
# Since history only goes back 6 months from our earliest ticket at 2017-01-01, then trim allowed account history
#   for ALL accounts for each ticket to also 7 months back.

# get account names, including tickets created earlier than 2017-01-01 with order by acct_ticket_ordinal
#   for later ordering.

WITH tickets_acct_indexed AS
(
SELECT
  TCKT_TicketID,
  Account_Name,
  Created,
  ROW_NUMBER() OVER (PARTITION BY Account_Name ORDER BY Created ASC) AS acct_ticket_ordinal
FROM
  `fluid-door-179122.data_science_dev.core_ticket_account_history_dws_managed`
GROUP BY
  Account_Name,
  TCKT_TicketID,
  Created
),

# only include tickets from Damien's original pull & join with ticket history, 
#   getting ordinal w/in account partition to make next self-join easier

tickets_to_include AS
(
SELECT
  mct.tckt_ticketID,
  mct.Created,
  tai.Account_Name,
  tai.acct_ticket_ordinal
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct
LEFT JOIN
  tickets_acct_indexed tai
ON
  mct.tckt_ticketID = tai.tckt_ticketID
),

prev_tickets_to_include AS
(
SELECT
  tti.Account_Name,
  tti.tckt_ticketID,
  tti.Created,
  tai.tckt_ticketID as earlier_ticket_id,
--  tai.Created as earlier_created,
--  tti.acct_ticket_ordinal,
--  tai.acct_ticket_ordinal as earlier_ordinal
  tti.acct_ticket_ordinal - tai.acct_ticket_ordinal as earlier_ordinal
FROM
  tickets_to_include tti
INNER JOIN
  tickets_acct_indexed tai
ON  -- same account and ordinal is in the last 5 tickets
  tti.Account_Name = tai.Account_Name AND
  tti.acct_ticket_ordinal > tai.acct_ticket_ordinal AND
  tti.acct_ticket_ordinal-5 <= tai.acct_ticket_ordinal
),

join_prev_with_work_types AS
(
SELECT
  pt.tckt_ticketID,
  --pt.Created, -- helpful for debugging
  pt.earlier_ticket_id,
  pt.earlier_ordinal,
  tw.log_work_date,
  tw.work_type,
  tw.Duration,
  tw.y_work_difficulty
FROM
  prev_tickets_to_include pt
LEFT JOIN
  `fluid-door-179122.data_science_dev.xcore_ticket_work_dws_managed` tw
ON
  pt.earlier_ticket_id = tw.tckt_ticketID  -- for current ticket get N previous tickets on same acct
WHERE
  pt.Created > tw.log_work_date  -- ensure no future work is included in case of overlap
),

/*
SELECT 
  *
FROM
  join_prev_with_work_types
ORDER BY
  tckt_ticketID DESC,
  earlier_ordinal DESC
*/

work_type_by_aggregates AS
(
SELECT
  tckt_ticketID,
  earlier_ordinal,
  work_type,
  COUNT(1) as work_type_count,
  SUM(Duration) as duration_sum,
  MAX(y_work_difficulty) as max_work_difficulty,
  AVG(y_work_difficulty) as avg_work_difficulty
FROM
  join_prev_with_work_types
GROUP BY
  tckt_ticketID,
  earlier_ordinal,
  work_type
),

prep_work_type_aggregates AS
(
SELECT
  tckt_ticketID,
  earlier_ordinal,
  SUM(work_type_count) as per_ticket_count,
  SUM(duration_sum) as per_ticket_duration_sum, 
  SUM(max_work_difficulty) as per_ticket_max_dfcl_sum,
  SUM(avg_work_difficulty) as per_ticket_avg_dfcl_sum  
FROM
  work_type_by_aggregates
GROUP BY
  tckt_ticketID,
  earlier_ordinal
),

work_type_aggregate_weights AS
(
SELECT
  wta.tckt_ticketID,
  wta.earlier_ordinal,
  wta.work_type,
--  wtd.work_type_count,
--  wtd.duration_sum,
--  pwt.per_ticket_count,
--  pwt.per_ticket_duration_sum,
--  pwt.per_ticket_max_dfcl_sum,
--  pwt.per_ticket_avg_dfcl_sum,
  wta.work_type_count / pwt.per_ticket_count as work_type_cnt_wt,
  wta.duration_sum / pwt.per_ticket_duration_sum as work_type_dur_wt,
  wta.max_work_difficulty / pwt.per_ticket_max_dfcl_sum as work_type_max_df_wt,
  wta.avg_work_difficulty / pwt.per_ticket_avg_dfcl_sum as work_type_avg_df_wt
FROM
  work_type_by_aggregates wta
LEFT JOIN
  prep_work_type_aggregates pwt
ON
  wta.tckt_ticketID = pwt.tckt_ticketID AND
  wta.earlier_ordinal = pwt.earlier_ordinal
)

-- now we have each ticket with the last N work_types ordered by count, duration & max/avg difficulty and we
--   can order within last1,2,3... by their weight since that is its contribution/sorting condition for the labels

SELECT
  tckt_ticketID,
  earlier_ordinal,
  ROW_NUMBER() OVER (PARTITION BY tckt_ticketID, earlier_ordinal ORDER BY work_type_cnt_wt DESC) AS work_cnt_ordinal,
  ROW_NUMBER() OVER (PARTITION BY tckt_ticketID, earlier_ordinal ORDER BY work_type_dur_wt DESC) AS work_dur_ordinal,
  ROW_NUMBER() OVER (PARTITION BY tckt_ticketID, earlier_ordinal ORDER BY work_type_max_df_wt DESC) AS work_max_df_ordinal,
  ROW_NUMBER() OVER (PARTITION BY tckt_ticketID, earlier_ordinal ORDER BY work_type_avg_df_wt DESC) AS work_avg_df_ordinal,
  work_type,
  work_type_cnt_wt,
  work_type_dur_wt,
  work_type_max_df_wt,
  work_type_avg_df_wt
FROM
  work_type_aggregate_weights
ORDER BY
  tckt_ticketID,
  earlier_ordinal

