---

title: Data / Analytics Documentation 

short_desc: designs & specifications relating to architectures, designs, implementations, models & data related to performing analytics on the Trebuchet Platform.

keywords: ['Smart', 'Analytics', 'Service', 'OLAP', 'Data', 'Streaming']

layout: page

featured: images/pic03.jpg

audience: []

---

# Introduction

A differentiating Trebuchet feature is to automatically detect and alert on anomalies on various parameter measurements. 

If we can apply smart limiting to any desired system parameter, we improve monitorability and reduce the need for unnecessary operations attention.

This service will probably run on the LME control plane as a EC2 autoscaled micro-service process written in Python 3.x.

High-level: DataPipe Cloud Analytics [webpage](https://www.datapipe.com/cloud/cloud-analytics)

# Overall requirements
## Anomaly Detection Algorithms
* Easy computability, since we may be watching many customers' parameters.
* Interpretable – prove why we alerted (non-repudiation).
* Handle cyclic daily and longer-term secular trends.
* Minimal need to tune/adjust any parameters, even upon initial turn-on.
* Be able to do retrospective analyses.
* Record alerting events for visualization.
## Anomaly Detection Service
* Well-behaved micro-service incorporating availability, scalability, restartability, testability.
* If auto-scale, need to decide how to partition compute event load by various dimensions of customerId, parameter, etc.
* Design for testability:
     * Introduce simulation mode that gets randomly-generated data vs. real data from Kafka.
     * Try for 80% unit test coverage.
     * Separate concerns and develop cohesive (SRP) modules & classes.

## Questions / Issues

* What if we do auto-scaling for customer based on parameter value? This will offset the values...

# Algorithm(s) Sketch
* Anomaly Detection
  * Build one model per hour of the day = 24 x 7 total ensemble models, each having a mean, stdDev
  * Acquire new event from requisite Kafka subscription:
  * For each parameter in the event: 
    * Calculate new parameter value based on exponential moving average 
    * Compare to appropriate hour's model for this parameter, emitting an alert upon input value outside the model's upper/lower limits 
    * Continue to compute current parameter's hourly model (mean, stdDev) using formula X (need reference link) 
    * Store latest parameter model on hour boundary
    * Aggregate/store metrics on other time interval (hour, day, week...) boundaries as needed

# Storage Design

Keep complete state persistent in fast, cheap, resilient storage.

## Requirements

* Preserve complete, immutable history of original raw records (in our format).
* Keep costs down by utilizing thrift AWS components where possible.
* Store by customer, application & multiple parameters.
* Ability to replay from original raw, fine-grained, initial records.

## Decisions

* First pass
   * Utilize S3 to store all Anomaly Detection Service data.
   * Read/write directly to S3, but if too slow can consider Memcached or REDIS as a cache.
   * Utilize Athena to query data
* Store in a logical directory format / path per table below.
* Data is stored as files as valid JSON documents.

All paths are preceded by a base path of $project/$customerId/$application/$version, per the key below:

| Data Type | Directory Structure | Comments | Notes |
|-----------|---------------------|----------|-------|
| **Raw** | $basePath/${Date:Hour} | Each has unique time stamp as filename? | - Can recreate all others from this stream, Generate this for testing anomaly algorithms, Can replay off this into stream processor for testing|
| **Hourly** | $basePath/${Date:Hour}/$parameter | Contains name:value pairs of mean, stdDev, ...	| |
| **Daily**	| $basePath/${Date}/$parameter | Contains name:value pairs of mean, stdDev, ...| |
| **Model** | $basePath/${DayOfWeek:Hour:Version}/$parameter | Contains name:value pairs of mean, stdDev, ... | Same as Hourly? |
| **Alerts** | $basePath/${Date:Hour}/$parameter | Timestamp, parameter, limits, value, alert text	| |

## Key

* $project: our project name ('analytics')
* $customerId: unique customer id ('example here')
* $application: which customer application
* $version: which application version
* $parameter: name of measurement parameter
* Date: YYYY-MM-DD
* Hour: HH (military time)

## Notes

* Take care to not unwittingly overwrite data. Think about replay behavior.
* S3 storage format needs to be hardened – changing it may result in breaking changes to queries or multiple tables
* Use some sort of compression (Parquet – columnar) compression for efficiency
* Athena
  * Use time partitioning on the data – see DDL here (see Partitioning Data) section.
  * Parquet compression gets > 30x query speed improvement and 99% less data scanned
  * Need to check overall throughput (item arrives written to S3 → viewable in Athena query)

## Proof Of Concept ("POC")
* Write logs, events, metrics files to S3 in proposed formats using Parquet compression. May need to simulate / generate pseudo-random data.
* Read logs, events, metrics using Athena
* Resources
   * https://aws.amazon.com/blogs/big-data/analyzing-data-in-s3-using-amazon-athena/
   * http://docs.aws.amazon.com/athena/latest/ug/athena-ug.pdf

## Questions

* Are all input records homogeneous? Have logs, events, measurements.
* What if replay over existing derived data?
* Are RDS databases cost-effective if we need one?
* Need encryption?

# Processing Design

## Requirements

* Implement as a micro-service
* Consider: availability, scalability, performance, usability, flexibility.
* Streaming – record at a time – easier to reason about.
* Source is probably a Kafka subscription of real-time event/measurement/log stream(s)
* Minimal throughput for hot time edge (current time is 'now').
* Perform aggregations on various intervals such as hour, day, week, month, season, hour, etc. and store to appropriate S3 bucket for later retrieval.
* Must be able to replay from raw data at later time. Raw data is immutable, master data record stream. Should never change.

## Algorithm Pseudo Code (Querying from Athena / Fast Cache)

Thoughts on "realtime" visualizations:
* The term "realtime" is relative. Our visualizations would ideally update the instant the data changes, but UI speed is sufficient when an update occurs every 1-3 seconds
* OLAP databases are not meant for realtime access. If tables are kept small, multi-second delays are not atypical, so with the convenience of being able to do massive queries AND do low-latency queries may be ideal.
* Alternatively, it may not be desirable to directly couple the UI to Athena, so an intermediate buffer (Redis?) may be appropriate from which the UI could update at its leisure, and an Athena query process could update at an independent rate.

## Exponential Moving Average

* Initial SMA: 10-period sum / 10
* Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
* EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day).

The Algorithm (generalizes to logs, events & metrics)

* Keeping track of last hour, exponential moving average & stdDev]
* For each parameter (can scale up/down here by partitioning by customer, application & parameter)
  * Query for parameter value 
  * Ensure have right model for current hour 
  * Compute new exponential moving average, stdDev values from parameter value (can do simple SMA, StdDev via SQL functions)
  * Persist it (for auditing, ...?)
  * if raw record parameter value exceeds threshold for this parameter & hour's model
  * Emit alert to S3/event bus
  * Compute base stats on hour interval (just mean & stdDev?)
  * Compute other stats on other desired intervals
  * Store any to their respective S3 buckets on time boundaries

## Algorithm Pseudo Code (Streaming from Kafka Source)

* Get raw JSON event record from Kafka subscription
* Store to Raw S3 bucket (for non-repudiation & later replay)
* For each parameter (can scale up/down here by partitioning by customer, application & parameter)
  * Ensure have right model for hour 
  * Compute new exponential moving average, stdDev values
  * if raw record parameter value exceeds threshold for this parameter & hour's model
  * Emit alert to S3/event bus
  * Compute base stats on hour interval (just mean & stdDev?)
  * Compute other stats on other desired intervals
  * Store any to their respective S3 buckets on time boundaries

## Implementation

* Language: Python 3.x – easier learning curve for team, and we are probably not performance-dependent that we know of
* IDE: Pycharm?
* Major pieces of work
  * Kafka reader
  * S3 writer: status = writeToS3(path, json)   // not so important if can reuse LME S3 data & converge on directory structure
  * S3 reader status, json = readFromS3(path)   // same
  * Import Arti's Python input data simulation code
  * Main controller as something in which Arti can experiment (see algorithm pseudocode)
  * Stats interval calculator – incremental methods?

## Questions

* How does auto-scaling, restarting, monitoring work on AWS? EC2 does a lot

