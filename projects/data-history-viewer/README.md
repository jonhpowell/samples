# Historical Viewer Service for Trebuchet Data

Trebuchet service that presents a REST query API for historical data such as
logs, metrics or events.

# Design

[DESIGN](DESIGN.md)

## Overview
A microservice that enables SQL querying of historical data via a Swagger
Python service on top of AWS Athena.

This example uses the [Connexion](https://github.com/zalando/connexion) library
on top of Flask to front the REST API.

To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m app
```

and open your browser to here (given BASE_URL = "http://localhost:8080/v0/data_hist" , or something equivalent where deployed) 


```
$BASE_URL/ui
```

The Swagger definition lives here:

```
$BASE_URL/swagger.json
```
## Query Functionality Requests / Responses

### Sample **query** submission request:
```
$BASE_URL/query

```
with JSON document in POST submission payload:
```
{ "sql_query": "SELECT * from events_v0 LIMIT 10;", "retention_minutes": 1440 }

```
response should contain "query_id", whose value is needed in subsequent requests:

### Sample **status** (polling) request:
```
$BASE_URL/<query_id>

```
The query is complete when the response status is 'FINISHED'.

### Sample **get results** request:

with JSON document in POST submission payload. First request JSON should look like:

{"query_id": "<from initial query call>", "results_per_request": 10}

which returns JSON as:

{ "next_token": "<next_token_token>", "result_set": "<result_set>" }

Requests for more pages of results should look like:

{"query_id": "<from initial query call>", "results_per_request": 10, "next_token": "<next_token_token>"}

```
$BASE_URL/next

```
response should be the resultset as JSON.

