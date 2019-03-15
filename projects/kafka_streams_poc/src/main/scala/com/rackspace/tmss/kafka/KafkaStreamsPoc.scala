package com.rackspace.tmss.kafka

import java.lang.Long
import java.util.Properties
import java.util.concurrent.TimeUnit

import org.apache.kafka.common.serialization._
import org.apache.kafka.streams._
import org.apache.kafka.streams.kstream.{KStream, KStreamBuilder, KTable}

import scala.collection.JavaConverters.asJavaIterableConverter

object WordCountApplication extends App {

  val config: Properties = {
    val p = new Properties()
    p.put(StreamsConfig.APPLICATION_ID_CONFIG, "wordcount-application")
    p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092")
    p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass)
    p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass)
    p
  }

  println("Wordcount app starting...")
  val builder: KStreamBuilder = new KStreamBuilder()
  val textLines: KStream[String, String] = builder.stream("TextLinesTopic")
  val wordCounts: KTable[String, Long] = textLines
    .flatMapValues(textLine => textLine.toLowerCase.split("\\W+").toIterable.asJava)
    .groupBy((_, word) => word)
    .count("Counts")
  wordCounts.to(Serdes.String(), Serdes.Long(), "WordsWithCountsTopic")

  val streams: KafkaStreams = new KafkaStreams(builder, config)
  streams.start()

  Runtime.getRuntime.addShutdownHook(new Thread(() => {
    streams.close(10, TimeUnit.SECONDS)
  }))
  println("Wordcount app terminating...")

}

object KafkaStreamsPoc extends App {
  print("Hello world kafka streams POC!")
}


