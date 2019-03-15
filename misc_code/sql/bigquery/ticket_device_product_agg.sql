-- UNION smaller ticket:device:product tables into a single one, joining to the SKU/Product table

WITH all_ticket_device_sku_keys AS
(
SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed1` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed2` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed3` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed4` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed5` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed6` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed7` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed8` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed9` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed10` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed11` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed12` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed13` tdp

UNION ALL

SELECT
  tdp.TCKT_TicketID,
  tdp.device_id,
  tdp.SKU_KEY
FROM
  `fluid-door-179122.data_science_dev.ticket_device_products_dws_managed14` tdp
)

SELECT
  atds.TCKT_TicketID,
  atds.device_id,
  atds.SKU_KEY,
  sku.SKU_Number,
  sku.SKU_Name,
  sku.SKU_Description,
  sku.SKU_Product_Category,
  sku.SKU_Product_Sub_Category
FROM
  all_ticket_device_sku_keys atds
INNER JOIN
  `fluid-door-179122.data_science_dev.sku_all_dws_managed` sku
ON
  atds.SKU_KEY = sku.SKU_KEY
GROUP BY
  atds.TCKT_TicketID,
  atds.device_id,
  atds.SKU_KEY,
  sku.SKU_Number,
  sku.SKU_Name,
  sku.SKU_Description,
  sku.SKU_Product_Category,
  sku.SKU_Product_Sub_Category


--ORDER BY
--  atds.TCKT_TicketID DESC,
--  atds.device_id ASC,
--  atds.SKU_KEY ASC


