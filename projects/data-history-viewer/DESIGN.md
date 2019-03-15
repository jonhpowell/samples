# Historical Event Viewer Service

## Prerequisites

This document assumes familiarity with Web Services, [Amazon S3] and [Amazon Athena].

## Background

S3 is a high-reliability, low-cost AWS keyed object store that interfaces well with much of the AWS ecosystem, including the new Analytics database, Athena. 

Athena is a Big Data / Analytics querable store (OLAP) for unstructured S3 data. When partnered with S3 and *[AWS Glue]* it comprises a powerful system for archiving, transforming and querying large amounts of historical data. 

Athena's strengths are its powerful SQL interface, ease of integration with S3 and its ability to scan, aggregate and return absolutely huge amounts of data. Other cloud providers offer similar OLAP stores.

Its weaknesses (as for most OLAP databases) are indeterminate query times and aggregate time latency over the entire data pipeline (not "realtime").

Glue auto-discovers S3 data schemas using **Crawlers**, producing a catalog, which Athena then uses to run OLAP queries. Glue can run also schedulable/configurable ETL **Jobs** on S3 data and import it into SQL-queryable Athena tables.

### Trebuchet Monitoring Data Flow

* The LME Team gathers Logs, Events & Metrics from the enterprise and streams it into Kafka. 
* From Kafka, data is periodically transferred into AWS S3 using the [Pinterest Secor] connector in a time-partitioned manner by year-month-day, hour & minute. Partitioning enables greater query efficiency and storage cost reduction.
* Events currently have two versions .v0 and .v1, which differ by schema
  (structure and naming). The REST API can specify version explicitly and change
exact query parameters as necessary.
* Data Acquisition Services (of which this service will be one) could pull directly from Kafka (less latency) or from S3,
  perhaps using AWS tools or a programmatic interface (Python & the Boto3 library).

## Objectives

This service's design is motivated by the following needs:

* Query historical events for data analysis purposes.
* Provide query data access to other Trebuchet control-plane services by running in the same environment as a microservice.
* Provide a generally-accessible HTTP/REST interface that abstracts an SQL interface to an OLAP client.

Secondary needs:

* Start developing a nascent data pipeline to enable retrospective data analysis and realtime alerting (see Roadmap below).

## Approach

We will use an iterative agile approach to implementation by doing these tasks in order, assessing
fit/interest from consumers and adjusting remaining tasks as needed upon completion.

1. Implement Swagger-specified HTTP/REST query service that sits behind the gateway protected by simple auth.
2. Initially, only events (version 0) and metrics are handled. 
3. The service receives a SQL query that can comprise LME outer envelope attributes. A query_id is returned.
4. A polling mechanism based on query_id will enable knowing when query results are available.
5. Query result sets up to 1000 records can be retrieved per **next** request (Athena limit).

## Not In Scope / Future Work

* Raise events & metrics *data* JSON element up to the top level in Athena tables for general ease of use.
* Implement v1 event interface (once v1 events are visible in S3).
* Implement additional security beyond simple gateway auth.
* Implement cleanup/expiration of query results based on initial query 'retention_minutes' parameter.
* Provide ability to query for logs.

## Related work

* Query recent historical events with a minimum and repeatable query latency and with minimum data time lag from event occurrence time to data availability. 
[This is probably a task that is better implemented with a fast in-memory cache and encompassing service facade inside the LME ecosystem.]

## REST API

The api-version is currently "v0".

* Submit query
    * HTTP Method/URI: POST to /<api-version>/data_hist/query
    * Request: JSON doc with **query** and **retention_minutes** as POST parameters
    * Response: 
         * HTTP code: 200 upon success, 4xx on error.
         * Content: JSON doc with **query_id** that uniquely identifies this query.
* Get query status (since query times are indeterminate with Athena)
    * HTTP Method: GET to /<api-version>/data_hist/status/{query-id}
    * Request: **query_id** as a simple path parameter.
    * Response: 
         * HTTP code: 200 upon success, 4xx on error. Note that some 4xx errors
           could be related to the original SQL query, such as InvalidQuerySyntax.
         * Content: JSON doc with **query_id** that uniquely identifies this query
* Get results (once status method returns 'FINISHED')
    * HTTP Method: POST to /<api-version>/data_hist/next
    * Request: **query_id**, **paging_token**, **results_per_page**
    * Response: 
         * HTTP code: 200 upon success, 4xx on error. 
         * Content: JSON doc with **query_id** query resultSet. NOTE: future task is to implement simple pagination.

### Quality of Service (SLA's)

* *Query Response time*: Cannot provide any guarantees since Athena offers no guarantees.
* *Data Recency*: Worst case could be at least 10 minutes old due to the sum of both Kafka and Glue/Athena minimum batch job frequencies (5 minutes each). Other miscellaneous latencies will also add to the overall total.
* *Data Time Range*: Will be able to access the full time range of Event data in S3. 
* *Resultset Size*: Will be able to return arbitrarily-sized result sets depending on the query parameters.

### Data Storage Policy

Default AWS Policy
* S3: 365 days
* Glacier: 2555 days (7 years)

Individual customers may choose a different custom policy.

## Design overview

* Stand up a simple Python service that supports a REST-style HTTP query interface endpoint define by Swagger in the Trebuchet control cluster. POST/GET parameters will be used to communicate query shape.
* Document the interface in swagger to support documentation tools

### Available Data

Data Dictionary

* Events (Version 0): 

    * *resourceid*: unique identifier for this entity (is usually blank--not allowed in SQL queries)

    * *customerid*: unique customer identifier (int), 1 is Datapipe and actual customers start at 11000.

    * *operationid*: operation (is usually blank--not allowed in SQL queries)
    
    * *servicename*: service identifier as text identifier such as 'iam-admin' or 'filebeat'.
 
    * *createdtimestamp*: originating timestamp in msecs since 1970 epoch (Unix time).

    * *data tags*: tags that augment data description/context

    * *arrivaltimestamp*: when message was consumed in Unix time msecs.

    * *service*: name of service, indistinguishable from *servicename* field.

## Design Decisions / Why

* Use Python as implementation language
    * Ubiquitous, fairly efficient language that is well-understood by our data team.
* Use Boto3 as the Athena AWS client library
    * AWS recommends it.
    * It's a really complete implementation.
    * The API's seem very intuitive, allowing us to be very productive.
* Use `connexion` as the WebService library
    * One of easy-to-use, recently-maintained, quality libraries that allow us
      to stand up an HTTP/REST service very quickly. A deployed example exists.

# Roadmap Ideas

As a Trebuchet Project we want to provide data access and processing capability that allow us to:

* Compare incoming metrics to thresholds for alerting with minimum data latency ("realtime pathway"). [@rlonstein & I discussed possibly moving this function to LME--client sets metric limits, alerts on TMS bus, consumer reads bus].
* Provide reliable storage of all historic LME data [LME currently handles].
* Provide projection & aggregation capabilities on historic LME data. Queryable attributes include creation time, customer, resource id, service name and possible 'data' section unpacking and filtering. Possible use cases include development of model development or global reports.
* Provide LME data access for answering ad hoc queries. This could be done via a SQL interface over top of the OLAP store.

[Amazon Athena]:http://aws.amazon.com/athena/
[Amazon S3]:http://aws.amazon.com/s3/
[Apache Kafka]:http://kafka.apache.org/
[Pinterest Secor]:https://github.com/pinterest/secor
[Kafka]:http://kafka.apache.org/
[S3]:http://aws.amazon.com/s3/
[Hive]:http://hive.apache.org/
