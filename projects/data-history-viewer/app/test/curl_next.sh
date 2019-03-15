#!/bin/bash
# $1 is query_id, $2 is next_token
#
if [ -z "$2" ]
then
  echo 'Getting data for Athena query with query_id="'$1'"'
  JSON="{\"query_id\": \"$1\", \"results_per_request\":5}"
else
  echo 'Getting data for Athena query with query_id=' $1 'with next_token=' $2
  JSON="{\"query_id\": \"$1\", \"results_per_request\":5, \"next_token\":\"$2\"}"
fi
echo "JSON=$JSON"

curl -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'X-TREBUCHET-TENANT-ID: X-EXAMPLE' -d "${JSON}" 'http://localhost:8080/v0/data_hist/next' | jq .

