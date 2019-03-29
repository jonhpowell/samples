package com.mir3.c9queryservice.spark.cassandra

import com.datastax.spark.connector._
import com.mir3.c9queryservice.rest.FrontEndRestService
import com.mir3.c9queryservice.rest.RestTransferObjects.{ContactsQueryRequest, ContactsQueryRequestWithPermissions, ContactsQueryResponseSimulated, OrgNodeDescriptor}
import com.twitter.util.Time
import org.apache.spark.rdd.RDD
import org.apache.spark.{SparkConf, SparkContext}

/**
  * Notes:
  *    1) Seems to compile with Scala 2.10.x or 2.11.x; have had weird compilation errors with 2.11 I think related to Spark
  *    2) Spark wants to deploy a jar and doesn't find case classes if don't build artifact jar
  *    3) On successive joins to tables, eliminate case class nesting by mapping to a combined class; otherwise, converter
  *          has trouble converting/accessing nested classes
  * Assumptions:
  *    1) Need to run with Spark 1.6.x
  *    2) Run with local C*
  */

// classes for querying; needed to keep un-nesting joins otherwise had problems unwrapping them
// when start to add a lot of non-structural columns needed for queries use Map in each
case class NotifHist(notifhistid:Int, eventhistids:Seq[Int], yosemiteid:String, initiatorname:String)
case class NotifHistSingle(notifhistid:Int, eventhistid:Int, datacenter:String, initiatorname:String)
case class EventHist(eventhistid:Int, notifhistid:Int, orgnodeids:Set[Int], timesent:String, title:String)
case class NotifEventHist(notifhistid:Int, eventhistid:Int, datacenter:String, initiatorname:String, timesent:String, title:String)
case class RecipHist(eventhistid:Int, reciphistid:Int, userid:String, company:String, devicecontactids:Map[Int,String], callresultids:Map[Int,Int])
case class NotifEventRecipHist(notifhistid:Int, eventhistid:Int, datacenter:String, initiatorname:String, timesent:String, title:String,
                               recipuserid:String, recipcompany:String, devicecontactids:Map[Int,String], callresultids:Map[Int,Int])
case class AllHist(notifhistid:Int, eventhistid:Int, datacenter:String, initiatorname:String, timesent:String,
                   title:String, recipuserid:String, recipcompany:String, devicecontact:String, callresult:Int)

// classes for final JSON output
case class SimTransaction(reportId:Int, dataCenter:String, timesent:String, devicecontact:String, callresult:Int)
case class SimInitiator(initiatorName:String)
case class SimNotification(title:String)
case class SimRecipient(employeeId:String, companyName:String)
case class SimContact(transaction:SimTransaction, initiator:SimInitiator, notification:SimNotification, recipient:SimRecipient)

// WARNING: anything to stdout goes to the results; use System.err for logging

object SparkCassandraConnectorJoins {
  val keyspace = "test"
  val myIp = "172.16.3.10"  // can't connect to localhost!!! (Doal cluster: 172.16.2.23, 172.16.2.150, and 172.16.3.2)
  val cassandraPort = "9042"
  val sparkMasterPort = "7077"
  val sparkDepJar = "/home/jpowell/Projects/Cloud9QueryProxyService/out/artifacts/Cloud9QueryProxyService_jar/Cloud9QueryProxyService.jar"

  def initializeSparkContext():SparkContext = {
    val conf = new SparkConf(true).setAppName("Spark:CassandraTestWithConnector")
      .set("spark.cassandra.connection.host", myIp)
      .set("spark.cassandra.output.consistency.level", "ALL")
      .set("spark.cores.max", "4")
    val sc = new SparkContext(s"spark://$myIp:$sparkMasterPort", "TestApplication", conf)
    sc.addJar(sparkDepJar)
    sc.setLogLevel("WARN")
    sc
  }

  val sc = initializeSparkContext()

  def parseInputArgs(args: Array[String]): Either[String,ContactsQueryRequestWithPermissions] = {
    if ((args == null)||(args.length<1)) {
      return Left(s"$getClass: ContactsQueryRequestWithPermissions JSON request is empty or null...exiting!")
    }
    System.err.println(s"$getClass: Starting Spark Launcher test with arguments")
    val mainArgs = args.zipWithIndex.foreach({ case(idx,arg) => System.err.println(s"$idx: $arg")})
    try {
      Right(FrontEndRestService.jsonToCaseClass[ContactsQueryRequestWithPermissions](args(0)))
    } catch {
      case e: Exception => {
        Left(s"${getClass.getSimpleName}: trouble parsing ContactsQueryRequestWithPermissions: ${e.getMessage}")
      }
    }
  }

  def main(args: Array[String]) {
    System.err.println(s"${getClass.getSimpleName}: MAIN CALLED @ ${Time.now}")
    val queryRequestEither = parseInputArgs(args)
    if (queryRequestEither.isLeft) {
      System.err.println(queryRequestEither.left)
    } else {
      apply(queryRequestEither.right.get)  // SIDE EFFECT: writes to stdout to communicate results since in separate process
    }
  }

  def apply(queryRequest:ContactsQueryRequestWithPermissions):Unit = {
    val startTime = Time.now
    System.err.println(s"${getClass.getSimpleName}: Starting Spark Cassandra Connector test with arguments: $queryRequest")
    val jsonResponse = joinQueryAfterMakingExpandedRdd(sc, queryRequest)
    System.err.println(s"${getClass.getSimpleName}: Completed in ${(Time.now - startTime) / 1000}")

    println(jsonResponse)  // emit to stdout so calling process can read results (yeah, kinda funky)
    System.err.println(s"${getClass.getSimpleName}: Finished in ${(Time.now - startTime) / 1000}")
//    System.out.flush()
//    System.out.close()
  }

  // Algorithm:
  //    1. Subselect NotifHist by orgNodeId
  //    2. Unpack 1:N eventhistids in each NotifHist record into N NotifHistSingle record RDD
  //    3. Join EventHist into this RDD by eventhistid, aliasing to final names
  //    4. Join RecipientHist into the accumulated RDD by eventhistid, aliasing to final names
  //    5. Navigate nested data structures, aliasing to final names
  //    6. Emit final Contact records on stdout using println

  // TODO: consider adding try/catch so that marshalled response will have error
  def joinQueryAfterMakingExpandedRdd(sc:SparkContext, queryRequest:ContactsQueryRequestWithPermissions):String = {

    // unpack permissions
    val viewPerms = queryRequest.permissions.viewNodes.map(p => (p.id, p.name)).toMap
    val privatePerms = queryRequest.permissions.privateNodes.map(p => (p.id, p.name)).toMap
    System.err.println(s"${getClass.getSimpleName}: viewPerms: $viewPerms, privatePerms: $privatePerms")

    val orgNodeIds = viewPerms.keys.map(_.toInt)
    System.err.println(s"${getClass.getSimpleName}: orgNodeIds for JOIN: $orgNodeIds")

    def notifHistForOrg(orgNodeId:Int): RDD[NotifHistSingle] = {
      for {
        notifHist <- sc.cassandraTable[NotifHist](keyspace, "notifhist").where("orgnodeid = ?", orgNodeId)
        eventHistId <- notifHist.eventhistids
      } yield NotifHistSingle(notifHist.notifhistid, eventHistId, notifHist.yosemiteid, notifHist.initiatorname)
    }
    val emptyTable:RDD[NotifHistSingle] = sc.emptyRDD[NotifHistSingle]
    val notifHistForAllOrgs:RDD[NotifHistSingle] = orgNodeIds.foldLeft(emptyTable)((accum, oid) => accum ++ notifHistForOrg(oid))
    //notifHistForAllOrgs.collect().foreach(println)

    val eventHistColumns = AllColumns
    val notifHistEventHist = notifHistForAllOrgs.joinWithCassandraTable[EventHist](keyspace, "eventhist", eventHistColumns, SomeColumns("eventhistid"))
    val notifEventHists = notifHistEventHist.map({case (nh,eh) => NotifEventHist(nh.notifhistid, eh.eventhistid, nh.datacenter, nh.initiatorname, eh.timesent, eh.title)})

    val recipHistColumns = AllColumns
    val notifEventHistRecipHists = notifEventHists.joinWithCassandraTable[RecipHist](keyspace, "recipienthist", recipHistColumns, SomeColumns("eventhistid"))
    val notifEventRecipHists = notifEventHistRecipHists.map({ case (nh,eh) =>
      NotifEventRecipHist(nh.notifhistid, eh.eventhistid, nh.datacenter, nh.initiatorname, nh.timesent, nh.title, eh.userid, eh.company, eh.devicecontactids, eh.callresultids)})
    //notifEventRecipHists.collect().foreach(println)

    val allHists = for {
      nh <- notifEventRecipHists
      callResultId <- nh.callresultids.keys
    } yield AllHist(nh.notifhistid, nh.eventhistid, nh.datacenter, nh.initiatorname, nh.timesent, nh.title, nh.recipuserid,
      nh.recipcompany, nh.devicecontactids.getOrElse(callResultId, "NoDeviceName"), nh.callresultids.get(callResultId).get)
    //TODO: do groupBy/sorting on allHists from saved RDD

    //allHists.collect().foreach(println)

    // TODO: could combine --> JSON here to avoid extra data structures unless do sparkSQL query as below...
    val contacts = for {
      ah <- allHists.collect()
      trans = SimTransaction(ah.notifhistid, ah.datacenter, ah.timesent, ah.devicecontact, ah.callresult)
      init = SimInitiator(ah.initiatorname)
      notif = SimNotification(ah.title)
      recip = SimRecipient(ah.recipuserid, ah.recipcompany)
    } yield SimContact(trans, init, notif, recip)
    // TODO: insert SparkSQL query on Contacts row here. Ensure query columns exist in Contact table due to permissions or
    //   just set those columns to blank
    //emitContacts(contacts)
    //contacts
    val response = ContactsQueryResponseSimulated(queryRequest.sessionId, queryRequest.sparkSql, contacts, FrontEndRestService.noRestCallError)
    FrontEndRestService.toJson(response)
  }

}
