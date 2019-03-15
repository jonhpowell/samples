#standardSQL

# File name: acct_hist_last5_df_max.sql
# Account History Features, V2: work types on each account for last 5 tickets with their relative weighting by 
# max work difficulty. Uses staging table with intermediate results to reduce complexity and combine common operations.

WITH work_type_df_max_var_rows_dups AS
(
SELECT
  tckt_ticketID,
  earlier_ordinal,
  NTH_VALUE(work_type, 1) OVER w1 AS work_type_df_max_1,
  NTH_VALUE(work_type, 2) OVER w1 as work_type_df_max_2,
  NTH_VALUE(work_type, 3) OVER w1 as work_type_df_max_3,
  NTH_VALUE(work_type, 4) OVER w1 as work_type_df_max_4,
  NTH_VALUE(work_type, 5) OVER w1 as work_type_df_max_5,
  NTH_VALUE(work_type_max_df_wt, 1) OVER w1 AS work_type_df_max_wt_1,
  NTH_VALUE(work_type_max_df_wt, 2) OVER w1 as work_type_df_max_wt_2,
  NTH_VALUE(work_type_max_df_wt, 3) OVER w1 as work_type_df_max_wt_3,
  NTH_VALUE(work_type_max_df_wt, 4) OVER w1 as work_type_df_max_wt_4,
  NTH_VALUE(work_type_max_df_wt, 5) OVER w1 as work_type_df_max_wt_5
FROM
    `fluid-door-179122.data_science_dev.account_work_type_base` wts
WINDOW w1 AS (PARTITION BY tckt_ticketID, earlier_ordinal ORDER BY work_max_df_ordinal ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
),

-- take out dups, but still have N earlier_ordinal for each ticket; want to splay out into more columns
work_type_df_max_var_rows AS
(
SELECT
  *
FROM
  work_type_df_max_var_rows_dups
GROUP BY
  tckt_ticketID,
  earlier_ordinal,
  work_type_df_max_1,
  work_type_df_max_2,
  work_type_df_max_3,
  work_type_df_max_4,
  work_type_df_max_5,
  work_type_df_max_wt_1,
  work_type_df_max_wt_2,
  work_type_df_max_wt_3,
  work_type_df_max_wt_4,
  work_type_df_max_wt_5
),

final_df_max_rows_dups AS
(
SELECT
  tckt_ticketID,
  earlier_ordinal,
  NTH_VALUE(work_type_df_max_1, 1) OVER w1 AS work_type_df_max_1_1,
  NTH_VALUE(work_type_df_max_2, 1) OVER w1 as work_type_df_max_1_2,
  NTH_VALUE(work_type_df_max_3, 1) OVER w1 as work_type_df_max_1_3,
  NTH_VALUE(work_type_df_max_4, 1) OVER w1 as work_type_df_max_1_4,
  NTH_VALUE(work_type_df_max_5, 1) OVER w1 as work_type_df_max_1_5,
  NTH_VALUE(work_type_df_max_wt_1, 1) OVER w1 AS work_type_df_max_wt_1_1,
  NTH_VALUE(work_type_df_max_wt_2, 1) OVER w1 as work_type_df_max_wt_1_2,
  NTH_VALUE(work_type_df_max_wt_3, 1) OVER w1 as work_type_df_max_wt_1_3,
  NTH_VALUE(work_type_df_max_wt_4, 1) OVER w1 as work_type_df_max_wt_1_4,
  NTH_VALUE(work_type_df_max_wt_5, 1) OVER w1 as work_type_df_max_wt_1_5,

  NTH_VALUE(work_type_df_max_1, 2) OVER w1 AS work_type_df_max_2_1,
  NTH_VALUE(work_type_df_max_2, 2) OVER w1 as work_type_df_max_2_2,
  NTH_VALUE(work_type_df_max_3, 2) OVER w1 as work_type_df_max_2_3,
  NTH_VALUE(work_type_df_max_4, 2) OVER w1 as work_type_df_max_2_4,
  NTH_VALUE(work_type_df_max_5, 2) OVER w1 as work_type_df_max_2_5,
  NTH_VALUE(work_type_df_max_wt_1, 2) OVER w1 AS work_type_df_max_wt_2_1,
  NTH_VALUE(work_type_df_max_wt_2, 2) OVER w1 as work_type_df_max_wt_2_2,
  NTH_VALUE(work_type_df_max_wt_3, 2) OVER w1 as work_type_df_max_wt_2_3,
  NTH_VALUE(work_type_df_max_wt_4, 2) OVER w1 as work_type_df_max_wt_2_4,
  NTH_VALUE(work_type_df_max_wt_5, 2) OVER w1 as work_type_df_max_wt_2_5,

  NTH_VALUE(work_type_df_max_1, 3) OVER w1 AS work_type_df_max_3_1,
  NTH_VALUE(work_type_df_max_2, 3) OVER w1 as work_type_df_max_3_2,
  NTH_VALUE(work_type_df_max_3, 3) OVER w1 as work_type_df_max_3_3,
  NTH_VALUE(work_type_df_max_4, 3) OVER w1 as work_type_df_max_3_4,
  NTH_VALUE(work_type_df_max_5, 3) OVER w1 as work_type_df_max_3_5,
  NTH_VALUE(work_type_df_max_wt_1, 3) OVER w1 AS work_type_df_max_wt_3_1,
  NTH_VALUE(work_type_df_max_wt_2, 3) OVER w1 as work_type_df_max_wt_3_2,
  NTH_VALUE(work_type_df_max_wt_3, 3) OVER w1 as work_type_df_max_wt_3_3,
  NTH_VALUE(work_type_df_max_wt_4, 3) OVER w1 as work_type_df_max_wt_3_4,
  NTH_VALUE(work_type_df_max_wt_5, 3) OVER w1 as work_type_df_max_wt_3_5,

  NTH_VALUE(work_type_df_max_1, 4) OVER w1 AS work_type_df_max_4_1,
  NTH_VALUE(work_type_df_max_2, 4) OVER w1 as work_type_df_max_4_2,
  NTH_VALUE(work_type_df_max_3, 4) OVER w1 as work_type_df_max_4_3,
  NTH_VALUE(work_type_df_max_4, 4) OVER w1 as work_type_df_max_4_4,
  NTH_VALUE(work_type_df_max_5, 4) OVER w1 as work_type_df_max_4_5,
  NTH_VALUE(work_type_df_max_wt_1, 4) OVER w1 AS work_type_df_max_wt_4_1,
  NTH_VALUE(work_type_df_max_wt_2, 4) OVER w1 as work_type_df_max_wt_4_2,
  NTH_VALUE(work_type_df_max_wt_3, 4) OVER w1 as work_type_df_max_wt_4_3,
  NTH_VALUE(work_type_df_max_wt_4, 4) OVER w1 as work_type_df_max_wt_4_4,
  NTH_VALUE(work_type_df_max_wt_5, 4) OVER w1 as work_type_df_max_wt_4_5,

  NTH_VALUE(work_type_df_max_1, 5) OVER w1 AS work_type_df_max_5_1,
  NTH_VALUE(work_type_df_max_2, 5) OVER w1 as work_type_df_max_5_2,
  NTH_VALUE(work_type_df_max_3, 5) OVER w1 as work_type_df_max_5_3,
  NTH_VALUE(work_type_df_max_4, 5) OVER w1 as work_type_df_max_5_4,
  NTH_VALUE(work_type_df_max_5, 5) OVER w1 as work_type_df_max_5_5,
  NTH_VALUE(work_type_df_max_wt_1, 5) OVER w1 AS work_type_df_max_wt_5_1,
  NTH_VALUE(work_type_df_max_wt_2, 5) OVER w1 as work_type_df_max_wt_5_2,
  NTH_VALUE(work_type_df_max_wt_3, 5) OVER w1 as work_type_df_max_wt_5_3,
  NTH_VALUE(work_type_df_max_wt_4, 5) OVER w1 as work_type_df_max_wt_5_4,
  NTH_VALUE(work_type_df_max_wt_5, 5) OVER w1 as work_type_df_max_wt_5_5
FROM
  work_type_df_max_var_rows
WINDOW w1 AS (PARTITION BY tckt_ticketID ORDER BY earlier_ordinal ASC
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
)

SELECT
  tckt_ticketID,
  work_type_df_max_1_1,
  work_type_df_max_1_2,
  work_type_df_max_1_3,
  work_type_df_max_1_4,
  work_type_df_max_1_5,
  work_type_df_max_wt_1_1,
  work_type_df_max_wt_1_2,
  work_type_df_max_wt_1_3,
  work_type_df_max_wt_1_4,
  work_type_df_max_wt_1_5,
  work_type_df_max_2_1,
  work_type_df_max_2_2,
  work_type_df_max_2_3,
  work_type_df_max_2_4,
  work_type_df_max_2_5,
  work_type_df_max_wt_2_1,
  work_type_df_max_wt_2_2,
  work_type_df_max_wt_2_3,
  work_type_df_max_wt_2_4,
  work_type_df_max_wt_2_5,
  work_type_df_max_3_1,
  work_type_df_max_3_2,
  work_type_df_max_3_3,
  work_type_df_max_3_4,
  work_type_df_max_3_5,
  work_type_df_max_wt_3_1,
  work_type_df_max_wt_3_2,
  work_type_df_max_wt_3_3,
  work_type_df_max_wt_3_4,
  work_type_df_max_wt_3_5,
  work_type_df_max_4_1,
  work_type_df_max_4_2,
  work_type_df_max_4_3,
  work_type_df_max_4_4,
  work_type_df_max_4_5,
  work_type_df_max_wt_4_1,
  work_type_df_max_wt_4_2,
  work_type_df_max_wt_4_3,
  work_type_df_max_wt_4_4,
  work_type_df_max_wt_4_5,
  work_type_df_max_5_1,
  work_type_df_max_5_2,
  work_type_df_max_5_3,
  work_type_df_max_5_4,
  work_type_df_max_5_5,
  work_type_df_max_wt_5_1,
  work_type_df_max_wt_5_2,
  work_type_df_max_wt_5_3,
  work_type_df_max_wt_5_4,
  work_type_df_max_wt_5_5
FROM
  final_df_max_rows_dups
GROUP BY
  tckt_ticketID,
  work_type_df_max_1_1,
  work_type_df_max_1_2,
  work_type_df_max_1_3,
  work_type_df_max_1_4,
  work_type_df_max_1_5,
  work_type_df_max_wt_1_1,
  work_type_df_max_wt_1_2,
  work_type_df_max_wt_1_3,
  work_type_df_max_wt_1_4,
  work_type_df_max_wt_1_5,
  work_type_df_max_2_1,
  work_type_df_max_2_2,
  work_type_df_max_2_3,
  work_type_df_max_2_4,
  work_type_df_max_2_5,
  work_type_df_max_wt_2_1,
  work_type_df_max_wt_2_2,
  work_type_df_max_wt_2_3,
  work_type_df_max_wt_2_4,
  work_type_df_max_wt_2_5,
  work_type_df_max_3_1,
  work_type_df_max_3_2,
  work_type_df_max_3_3,
  work_type_df_max_3_4,
  work_type_df_max_3_5,
  work_type_df_max_wt_3_1,
  work_type_df_max_wt_3_2,
  work_type_df_max_wt_3_3,
  work_type_df_max_wt_3_4,
  work_type_df_max_wt_3_5,
  work_type_df_max_4_1,
  work_type_df_max_4_2,
  work_type_df_max_4_3,
  work_type_df_max_4_4,
  work_type_df_max_4_5,
  work_type_df_max_wt_4_1,
  work_type_df_max_wt_4_2,
  work_type_df_max_wt_4_3,
  work_type_df_max_wt_4_4,
  work_type_df_max_wt_4_5,
  work_type_df_max_5_1,
  work_type_df_max_5_2,
  work_type_df_max_5_3,
  work_type_df_max_5_4,
  work_type_df_max_5_5,
  work_type_df_max_wt_5_1,
  work_type_df_max_wt_5_2,
  work_type_df_max_wt_5_3,
  work_type_df_max_wt_5_4,
  work_type_df_max_wt_5_5
ORDER BY
  tckt_ticketID DESC

