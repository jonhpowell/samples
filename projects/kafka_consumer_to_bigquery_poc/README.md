# Real-Time Universal Monitoring Bus (UMB) Uploader & Visualization Proof of Concept

The project had the following aims:

* Prove we could securely upload data to the Google Cloud.
* Decompose Kafka UMB data into a useful, terse summary that minimizes bandwidth, storage needs and indirectly, cost.
* Prove we can get real-time response/updates through the entire pipeline (whatever is chosen) and
   identify plausible alternatives if not cost-effective in the long term.
* Prove we can emit enterprise-grade, configurable visualizations that allow stakeholders to gain visibility
into cluster events.
* Get a reasonable idea of throughput and cost for the chosen solution, with reasonable alternatives.

# Design

## Data Upload, Transformation & Storage

Simple Python executable that does the following:

* Subscribes and connects securely to the *maas_notifications* Kafka topic.
* Pulls Kafka messages (securely).
* Transforms incoming Kafka JSON maas_notification messages to a *Summary Message*.
* Uploads summary records to a Google BigQuery table.
* Emits periodic, configurable status messages for operational integrity.

Notes:

* We may want to filter on only the tenants (private cloud?) we want to view to save bandwidth & storage costs.
* Big Query may not be the best long-term storage / integration mechanism. It may make 
sense to utilize MemSQL or Redis, assuming there is a Data Studio data connector to view the data (I could not find one.)
* We may want to consider using date-partitioning for the BigQuery tables; however, I could not
get the data uploaded in a realtime manner--it was **really** delayed. Switching to a *memory cache*
type DB such as redis or MemSQL may work--**iff* there is a Google Data Studio connector to import
the data for visualization. 
* Kafka has a *header* feature that can be very helpful for routing/filtering, but it does not 
appear that the Confluent Python driver I used supports headers. This may be a matter of time. Headers are great
for high-volume message systems because the message does not need to be de-serialized to filter or route it.

Known Issues:

* The uploader counter said 100K records, but only 75K were saved in BigQuery. There were some
uploader errors, but they do not look frequent enough to warrant 25% drops. Maybe need to add some
exception handling around the BQ Streaming call.
* Some of the code will need to be refactored for generality, quality, etc. (to be expected for a POC).
* There are issues with *accurately* extracting the tuple {tenant, environ, node, check} from the Kafka
JSON message. It was originally built for the tenant Comcast and awkwardly extended in an attempt to 
include *all* other customers, probably good enough for rough data analysis and for developing 
visualizations. Changing the AttributeExtractor to pull deterministic TURTLES-762 attributes will 
be the correct long-term solution.

File Synopsis:

* SimpleConsumer.py: pulls Kafka records securely and extracts to summary record for examination/testing.
* BatchingConsumerWriter.py: does all the SimpleConsumer tasks AND uploads to Google BigQuery.
* BigQueryStreamer.py: facilitates uploading a batch of summary records to BQ.
* AttributeExtractor.py: parses Kafka JSON message payload into summary record.
* StatsAccumulators.py: provides operational metrics for current or post-priori run analysis.
* TimeUtils.py: mostly time-related utility functions.

## Real-Time Data Visualization

Simple Google Data Studio Graphics

* Cost is ... free!
* Professional-looking, suitable for an enterprise.
* No services to maintain.
* Fairly easy to work with--once you understand their concepts. Very similar conceptually to another industry 
leader (Looker).
* Time resolution down to minutes, which is sufficient for our *realtime* use. Time resolution is configured
on the data source in the Data Studio UI.

### Issues

* If the data source resolution is taken down to its most fine granularity, it seems that the time-series
graphs are a histogram into minute buckets. If we move the resolution to less fine granularity we lose the 
ability to show the latest data in realtime.

## Information Architecture (IA)

We developed a standard summary record that is a minimum set of available data that provides the following:

* Provenance: 
    * When did the data originate (standard timestamp)
    * Where did the data originate (hierarchical representation)
* Content
    * Alert status
    * Alarm information
    
 ### Locating a data source uniquely
 
 A hierarchy consisting of the following would go a long way to identifying *exactly* where the data originated:
 
 * *tenantId*: each customer has a unique RAX-assigned id.
 * *environment*: there may be multiple clouds for the same client.
 * *node*: the unique server or device from where the message originated.
 * *check*: the script from where the event/notification/alarm originated.
 
# Project Setup

Assuming MacOS; adapt for other Operating Systems.

Steps:

* brew install/upgrade librdkafka
* pip install confluent-kafka
* pip install google-cloud-storage
* pip install google-bigquery
* sudo pip install --upgrade google-cloud-bigquery
* SSL configuration: 
    * https://github.com/edenhill/librdkafka/wiki/Using-SSL-with-librdkafka
    * Talk to @itzg (Geoff)
    
Or:

* establish a virtual-env
* install from requirements.txt
