#!/bin/bash
# Data Service: query Athena tables with query specified by $1

if [ -z "$1" ]
then
  echo "You must supply the query (in quotes) for the call!"
  echo "  Example: 'select * from metrics LIMIT 10;'"
else
  echo 'Initiatiating Athena query "'"$1"'"'
  QUERY="{\"retention_minutes\": 1440, \"sql_query\": \""$1"\"}"
  echo -n "query_id = "
  curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'X-TREBUCHET-TENANT-ID: 1' -d "$QUERY" 'http://localhost:8080/v0/data_hist/query'
fi
