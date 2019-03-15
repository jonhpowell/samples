#standardSQL

# Initial Account History Features, V1: aggregate together the feature results we have so far into 
#  a single wide table.

# only include tickets from Damien's original pull & join with all other result tables 

SELECT
  mct.tckt_ticketID,
  mct.created,
  mct.Account_Name,
  afq.final_q_tix_1,
  afq.final_q_tix_2,
  afq.final_q_tix_3,
  afq.final_q_tix_4,
  afq.final_q_tix_5,
  awd.wrk_dfy_max_1,
  awd.wrk_dfy_max_2,
  awd.wrk_dfy_max_3,
  awd.wrk_dfy_max_4,
  awd.wrk_dfy_max_5,
  awd.wrk_dfy_avg_1,
  awd.wrk_dfy_avg_2,
  awd.wrk_dfy_avg_3,
  awd.wrk_dfy_avg_4,
  awd.wrk_dfy_avg_5,
  atc.tix_cnt_1w,
  atc.tix_cnt_4w,
  atc.tix_cnt_16w,
  atc.tix_cnt_30w
FROM
  `fluid-door-179122.data_science_dev.master_core_tickets_meta_data` mct
LEFT JOIN
  `fluid-door-179122.data_science_train.account_final_queue_tix` afq
ON
  mct.tckt_ticketID = afq.tckt_ticketID
LEFT JOIN
  `fluid-door-179122.data_science_train.account_work_difficulty` awd
ON
  mct.tckt_ticketID = awd.tckt_ticketID
LEFT JOIN
  `fluid-door-179122.data_science_train.account_tix_counts` atc
ON
  mct.tckt_ticketID = atc.tckt_ticketID
ORDER BY
  Account_Name ASC,
  tckt_ticketID DESC

