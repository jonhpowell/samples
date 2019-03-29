package com.mir3.c9queryservice.spark.job

import java.io.InputStream

import com.mir3.c9queryservice.rest.FrontEndRestService
import com.mir3.c9queryservice.rest.RestTransferObjects.{ContactsQueryRequest, ContactsQueryResponse}
import com.mir3.c9queryservice.spark.cassandra.SparkCassandraConnectorJoins._
import org.apache.spark.launcher
import org.apache.spark.launcher.{SparkAppHandle, SparkLauncher}

import scala.collection.JavaConverters._

// TODO:
//    1. Efficiency: Spark C* job takes 12 seconds--share contexts or use Spark Job Server
//    2. Minimal set of divisions passed in: each needs to include its name (use Map)
object SparkJobLauncher {
  val SPARK_BASE: String = "/home/jpowell/Downloads/spark-1.6.0-bin-hadoop2.6"
  val extraJars = Seq(
    SPARK_BASE + "/lib/spark-cassandra-connector_2.10-1.6.0-M1-SNAPSHOT.jar",
    SPARK_BASE + "/lib/spark-cassandra-connector-assembly-1.6.0-M1-SNAPSHOT.jar"
  ).mkString(":")
  val applicationJar = "/home/jpowell/Projects/Cloud9QueryProxyService/out/artifacts/Cloud9QueryProxyService_jar/Cloud9QueryProxyService.jar"

  def main(args: Array[String]) {
    if ((args == null) || (args.length < 1) || (args(0).trim.length == 0)) {
      println(s"${getClass.getSimpleName}: required list of orgNodeIds is null or empty...exiting!")
      sys.exit(1)
    }
    //val mainArgs = args(0).split(",").map(_.toInt).toSet
    println(s"${getClass.getSimpleName}: Starting Spark Launcher with queryRequest: ")
    args.foreach(println)

    apply(args(0))
  }

  def apply(jsonRequest:String):String = {
    val mainStartTime = System.currentTimeMillis()

    def printWithDeltaTime(message:String): Unit = {
      val currentTimeMillis = System.currentTimeMillis()
      println(s"${currentTimeMillis-mainStartTime}: $message")
    }

    class SparkLauncherListener extends launcher.SparkAppHandle.Listener {
      override def infoChanged(sparkAppHandle: SparkAppHandle): Unit = {
        printWithDeltaTime(s"[LaunchListener] infoChanged event: ${sparkAppHandle.getState}")
      }
      override def stateChanged(sparkAppHandle: SparkAppHandle): Unit = {
        printWithDeltaTime(s"[LaunchListener] stateChanged event: ${sparkAppHandle.getState}")
      }
    }

    try {
      printWithDeltaTime(s"${getClass.getSimpleName}: Creating spark launcher...")
      val sparkLauncher = createSparkLauncherProcess(jsonRequest)
      val iterStartMillis = System.currentTimeMillis
      //printWithDeltaTime(s"##### $getClass: Starting spark application iteration $iter...")
      //      val spark = sparkLauncher.startApplication(new SparkLauncherListener())
      val spark = sparkLauncher.launch
      printWithDeltaTime(s"${getClass.getSimpleName}: Started spark application...")
      // TODO: convert to use: SparkAppHandle startApplication(SparkAppHandle.Listener... listeners)
      // TODO: how to determine status and to delete job (REST support)?

      //      def checkState(prev:SparkAppHandle.State) {
      //        Thread.sleep(50L)
      //        val curr = spark.getState
      //        if (prev != curr) printWithDeltaTime(s"[Polling]: $prev -> $curr")
      //        if (curr != SparkAppHandle.State.FINISHED) checkState(curr)
      //      }
      //      checkState(spark.getState)
      //      printWithDeltaTime(s"[Final]: ${spark.getAppId}: ${spark.getState}")

      val (inputStream, inputThread) = createInputStreamReaderThread(spark.getInputStream, "input")
      inputThread.start()

      val (errorStream, errorThread) = createInputStreamReaderThread(spark.getErrorStream, "error")
      errorThread.start()

      printWithDeltaTime(f"${getClass.getSimpleName}: right before spark.waitFor")
      val exitCode: Int = spark.waitFor
      printWithDeltaTime(f"${getClass.getSimpleName}: finished! Exit code: $exitCode")
      val (inputStreamLines, inputStreamResults) = inputStream.getResults
      printWithDeltaTime(s"$inputStreamLines query result lines: $inputStreamResults")
      val (errorStreamLines, errorStreamResults) = errorStream.getResults
      printWithDeltaTime(s"\n\n$errorStreamLines run result lines: $errorStreamResults")
      System.err.println(s"##### elapsed query iteration time: ${System.currentTimeMillis-iterStartMillis}")

      inputStreamResults
    }
    catch {
      case t: Throwable => System.err.println("Threw exception: " + t.getMessage)
        "[]"
    } finally {
      printWithDeltaTime("Finished Spark Launcher test...")
    }
  }

  def createSparkLauncherProcess(jsonRequest:String):SparkLauncher = {
    val env = Map[String,String](
      "SPARK_CLASSPATH" -> extraJars
    )
    new SparkLauncher(env.asJava).
      setSparkHome(SPARK_BASE).
      addAppArgs(jsonRequest). // should be JSON ContactsQueryRequestWithPermissions at this point; only use arg(0)
      setMaster("spark://172.16.3.10:7077").
      setAppResource(applicationJar).
      setMainClass("com.mir3.c9queryservice.spark.cassandra.SparkCassandraConnectorJoins").
      setDeployMode("client"). // client or cluster
      setVerbose(false).
      //setConf(SparkLauncher.CHILD_CONNECTION_TIMEOUT, "2").
      setConf("spark.driver.allowMultipleContexts","true").
      setConf("spark.executor.cores", "4").
      setConf("spark.executor.memory", "8g").
      setConf("spark.driver.cores", "4").
      setConf("spark.driver.memory", "8g")
    }

    def createInputStreamReaderThread(inputStream:InputStream, name:String):(InputStreamReaderRunnable,Thread) = {
      val inputStreamReaderRunnable:InputStreamReaderRunnable = new InputStreamReaderRunnable(inputStream, name)
      val thread = new Thread(inputStreamReaderRunnable, "LogStreamReader input")
      (inputStreamReaderRunnable,thread)
    }

}


