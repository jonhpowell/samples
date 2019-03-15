#!/bin/bash
# $1 is query_id
#
if [ -z $1 ]
then
  echo "You must supply the query_id from the query call!"
else
  echo 'Checking on Athena query status for query_id="'$1'"'
  URL="http://localhost:8080/v0/data_hist/status/$1"
  echo "Retrieving status with URL='"$URL"'"
curl -X GET --header 'Accept: application/json' --header 'X-TREBUCHET-TENANT-ID: some-example-tenant-id' $URL
fi
