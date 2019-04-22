# Coinbase Streaming / Aggregation Project

Summary: pull crypto-currency trade matches from Coinbase, accumulating and
aggregating statistical "candles" by type over 1 minute, 1 hour and 1 day time windows.

Note that this project is a rapid POC (Proof of Concept) and may not rigorously consider
every important software engineering consider, and certain corners were cut in favor of 
completing something end-to-end.

## Options Considered

Fundamentally, this problem is suited to a Time-series database which is
* Structured for fast ingest, lookup & analysis.
* Provides native, simple queries in easy syntax.
* Can host locally, but want up in cloud for DR, low maintenance, etc., but can do local machine for testing 

Technology solutions considered:

1. _InfluxDB_: use hosted version; seems a little shaky, lightweight, non-professional; wouldn’t 
personally build my biz upon it.
2. _MemSQL_: looks professional, but why not use MySQL per https://dom.as/2012/06/26/memsql-rage/ ?
3. _AWS Timestream_: not yet available.
4. _Kafka Streams_: too much work, Java/Scala DSL not trivial to incorporate.
5. _Kafka_: enterprise-ready, easily handles windowing, out-of-order/late arrivals, exactly-once semantics, etc. 

## The Chosen Solution

* Kafka: push publicly-available trade matches from Coinbase into a topic. A full, local environment
including zookeeper is running behind the scenes.
* Python: simple syntax and ubiquitous libraries make this a popular choice. 
* Python Libraries used:
    * dpdk: well-written Kafka interface package
    * cbpro: well-written Coinbase interface package
    * Faust: brilliant use of Python async features in one package. Handles streaming from Kafka, streaming
     tables, Tumbling Window aggregation, Web Service window value access.

Summary: the complete implementation comprises only _two_ very short Python source files that are easy to maintain and probably quite performant.

## To Run It

* Start Zookeeper & Kafka (per below)
* Start CoinbaseProducer.py (via IDE is nice)
* Start CoinbaseConsumer.py
    * venv/bin/faust -A CoinbaseMatchConsumer worker -l info
* Get access to latest stats by product_id:
    * Access is http://localhost:6066/stats1min/<product_id>/

### Notable Caveats / Missing Features

* Only implement 1 aggregation period (1 minute). Others should be simple extensions / cut-paste.
* We don't provide lookup by timestamp, only the latest period.
* Testing is postponed and done by inspection.
* Security concerns are also postponed.

### Component Solution Blocks

### Ingress

A. Subscribe to websocket trade lines from coinbase (subscribes to all channels) by product
* https://buildmedia.readthedocs.org/media/pdf/copra/latest/copra.pdf
* pip install copra

B. Insert tradelines to Timeseries DB by product_id
* Use Coinbase client: https://github.com/coinbase/coinbase-python OR https://github.com/danpaquin/coinbasepro-python
* pip install cbpro
* Python Async IO: https://realpython.com/async-io-python/

C. See CoinbaseMatchProducer.py for the solution. It is short & simple. Faust could have been used
to write to the topic for consistency.

### Persist to "DB"

D. Install/setup Kafka/Zookeeper Ecosystem
* brew upgrade kafka
* To have launchd start zookeeper now and restart at login:
    * brew services start zookeeper
Or, if you don't want/need a background service you can just run:
    * zkServer start
* To have launchd start kafka now and restart at login:
    * brew services start kafka
* Or, if you don't want/need a background service you can just run:
    * zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties & kafka-server-start /usr/local/etc/kafka/server.properties

Example to adapt: https://github.com/confluentinc/kafka-streams-examples/blob/5.2.1-post/src/main/java/io/confluent/examples/streams/interactivequeries/WordCountInteractiveQueriesExample.java

E. Write to Kafka (persistent, streaming state-store):
* brew install rocksdb
* CFLAGS='-std=c++11 -stdlib=libc++ -mmacosx-version-min=10.10'  pip install -U --no-cache python-rocksdb
* pip install kafka-python
* brew services start zookeeper
* brew services start kafka
* cd Downloads/kafka*/
* zookeeper-server-start.sh ../config/zookeeper.properties
* kafka-server-start.sh ../config/server.properties
* From  https://kafka.apache.org/quickstart
    * bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic test
    * bin/kafka-topics.sh --list --bootstrap-server localhost:9092
    * bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test
    * bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
* _Kafka is now functional_

### Pull from Kafka topic, aggregate in tumbling window, provide web service access

D. Install / get Faust Working (https://faust.readthedocs.io/en/latest/playbooks/quickstart.html)
* https://github.com/robinhood/faust
* https://faust.readthedocs.io/en/latest/playbooks/quickstart.html
* bin/kaftopics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic greetings
* bin/kafka-console-producer.sh --broker-list localhost:9092 --topic greetings
* enter some greetings
* venv/bin/faust -A hello_world worker -l info
* _Faust is now functional_

E. Make coinbase_match topic
* bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic coinbase_matches
* bin/kafka-topics.sh --list --bootstrap-server localhost:9092

F. Implement tumbling window as Faust table
* See CoinbaseMatchConsumer.py
    * We implement 2 models: Match and CandleStats to use as input and table structures.
    * We only implement the 1 minute tumbling (fixed-size, non-overlapping, gapless windows); the other time
    intervals can use the same pattern.
        * https://faust.readthedocs.io/en/latest/playbooks/pageviews.html
    * We implement the candle logic (generalizable to all time periods)
    * We insert the transformed aggregation record into the ongoing, streaming table.
    * We then provide Web GET access by product_id to the latest stats.
    

### Notable omissions from the full requirement set

* We only implement 1 minute tumbling window candle stats. The hourly & daily versions are trivial given a correct pattern.
* We leave efficiency / optimization of Kafka (# of partitions, etc.) for later.
* We could use Faust to push the match records in an asyn agent in the consumer.
* Timeouts for the tables are not optimized.
* Only the _latest_ value is available from the web. We will probably want to add a key dimension of time to each 
candle along with product_id.
* The web calls are not yet subscribable, you have to call it explicitly.
* We don't set the TTL for Kafka messages. May only need last 7 days.

## Miscellaneous Research

### InfluxDB

InfluxDB Research

* https://www.influxdata.com/blog/getting-started-python-influxdb/
* https://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdb.InfluxDBClient.write_points
* Write line or JSON?
* Works with Pandas DataFrames - Influxdb.DataFrameClient: see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
    * look at all the types of windows!
* Simple query format: 
* Use ms time_precision
* Can tag data for type of currency









