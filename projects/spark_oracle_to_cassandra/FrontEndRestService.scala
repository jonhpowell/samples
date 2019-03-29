package com.mir3.c9queryservice.rest

import java.net.InetSocketAddress

import com.mir3.c9queryservice.data.WideRow
import com.mir3.c9queryservice.rest.RestTransferObjects._
import com.mir3.c9queryservice.spark.job.SparkJobLauncher
import com.twitter.conversions.time._
import com.twitter.finagle.Service
import com.twitter.finagle.http.{HttpMuxer, Response, Status, _}
import com.twitter.logging.Formatter
import com.twitter.server.TwitterServer
import com.twitter.util.{Await, Future, Time}

import scala.reflect.ClassTag

// TODO
//   1. Add status/return codes to HTTP Response
//   2.
//

object FrontEndRestService extends TwitterServer {

  val what = flag("what", "hello", "String to return")
  val addr = flag("bind", new InetSocketAddress(0), "Bind address")
  val durations = flag("alarms", (1.second, 5.second), "2 alarm durations")
  val contactsMetaCounter = statsReceiver.counter("contacts_meta_requests_counter")
  val contactsQueryCounter = statsReceiver.counter("contacts_query_requests_counter")
  val noRestCallError = ""
  override def failfastOnFlagsNotParsed: Boolean = true

  override def defaultFormatter = new Formatter(
    timezone = Some("UTC"),
    prefix = "<yyyy-MM-dd HH:mm:ss.SSS> [%.3s] %s: "
  )

  import scala.reflect.runtime.universe._
  def jsonToCaseClass[T](input:String)(implicit m: TypeTag[T]) = {
    import org.json4s._
    import org.json4s.native.JsonMethods._
    implicit val formats = DefaultFormats
    implicit val cl = ClassTag[T]( m.mirror.runtimeClass( m.tpe ) )

    parse(input).extract[T](formats, manifest[T])
  }

  def toJson(s:Any, prettyFormatting:Boolean = false):String = {
    import org.json4s.jackson.JsonMethods._
    import org.json4s.{DefaultFormats, Extraction}

    implicit val formats = DefaultFormats
    val json = Extraction.decompose(s)
    //log.info(s"${compact(json)}")
    if (prettyFormatting) pretty(json) else compact(json)
  }

  // TODO: clean up common code
  val queryContactsMetaService = new Service[Request, Response] {
    def apply(request: Request) = {
      contactsMetaCounter.incr()
      log.info(s"Received a ${request.method} request at ${Time.now}: ${request.contentString}")
      try {
        val queryMetaRequest = jsonToCaseClass[ContactsQueryMetaRequest](request.contentString)
        println(s"${queryMetaRequest.getClass.getSimpleName}: $queryMetaRequest")
        val metaResponse = ContactsQueryMetaResponse(queryMetaRequest.sessionId, WideRow.generateRows(1), noRestCallError)
        val response = Response(request.version, Status.Ok)
        response.setContentTypeJson()
        response.contentString = toJson(metaResponse)
        log.info(s"json: ${response.contentString}")
        Future.value(response)
      } catch {
        case e: Exception => {
          val response = Response(request.version, Status.BadRequest)
          response.setContentTypeJson()
          val queryResponse = ContactsQueryMetaResponse("unknown", Seq.empty, "Bad Request: " + e.getMessage)
          response.contentString = toJson(queryResponse) + '\n'
          log.info(s"json: ${response.contentString}")
          Future.value(response)
        }
      }
    }
  }

  val queryContactsService = new Service[Request, Response] {
    def apply(request: Request) = {
      contactsQueryCounter.incr()
      log.info(s"Received a ${request.method} request at ${Time.now}: ${request.contentString}")
      try {
        val queryRequest = jsonToCaseClass[ContactsQueryRequest](request.contentString)
        println(s"${queryRequest.getClass.getSimpleName}: $queryRequest")
        // TODO: call Tahoe to get permissions or get in initial request
        val permissions = TahoePermissions(Seq(OrgNodeDescriptor("1", "FirstOrg"), OrgNodeDescriptor("3", "ThirdOrg")), Seq(OrgNodeDescriptor("1", "FirstPrivate")))
        val contactsQueryRequestWithPermissions = ContactsQueryRequestWithPermissions(queryRequest.sessionId, queryRequest.sparkSql, permissions)
        log.info(s"${getClass.getSimpleName}: Submitting queryRequest $contactsQueryRequestWithPermissions request at ${Time.now}")
        val queryResponse = SparkJobLauncher(toJson(contactsQueryRequestWithPermissions))
        log.info(s"${getClass.getSimpleName}: Return from submitting queryRequest $contactsQueryRequestWithPermissions request at ${Time.now} with results $queryResponse")
        val response = Response(request.version, Status.Ok)
        response.setContentTypeJson()
        response.contentString = queryResponse
        log.info(s"json: ${response.contentString}")
        Future.value(response)
      } catch {
        case e: Exception => {
          val response = Response(request.version, Status.BadRequest)
          response.setContentTypeJson()
          val queryResponse = ContactsQueryResponse("unknown", "unknown", Seq.empty, "Bad Request: " + e.getMessage)
          response.contentString = toJson(queryResponse)
          log.info(s"json: ${response.contentString}")
          e.printStackTrace()
          Future.value(response)
        }
      }
    }
  }

  /**
    **
    * Valid service requests
    * Meta Query: curl -X POST 'http://localhost:9990/contacts/meta' --header "Content-Type:application/json;charset=UTF-8"
    *    --data '{"sessionId" : "5ac65b92-a739-4b83-877b-e7339353308a"}'
    * Query: curl -X POST 'http://localhost:9990/contacts' --header "Content-Type:application/json;charset=UTF-8"
    *    --data '{"sessionId" : "5ac65b92-a739-4b83-877b-e7339353308a", "sparkSql" : "select * from Contacts group by transactionId, startTime"}'
    * Health Check: curl -s http://localhost:9990/health
    * Metrics: curl -s localhost:9990/admin/metrics.json | jq '.requests_counter', get jq: `sudo apt-get install jq`
    *
    **/

  def main() {
    // Create a new http server, profiting from the one already started for /admin/*
    // The `TwitterServer` trait exposes an `adminHttpServer` that serves all routes registered in the HttpMuxer object,
    //    we just have to add our own.
    HttpMuxer.addHandler("/contacts/meta", queryContactsMetaService)
    HttpMuxer.addHandler("/contacts/meta/", queryContactsMetaService)
    HttpMuxer.addHandler("/contacts", queryContactsService)
    HttpMuxer.addHandler("/contacts/", queryContactsService)
    Await.ready(adminHttpServer)
  }

  //  // Objects to produce some standard http responses.
  //  object Responses {
  //
  //    // Used to convert objects into json
  //    val mapper = new ObjectMapper
  //
  //    // Create an HttpResponse from a status and some content.
  //    private def respond(status: HttpResponseStatus, content: ChannelBuffer): HttpResponse = {
  //      val response = new DefaultHttpResponse(HTTP_1_1, status)
  //      response.setHeader("Content-Type", "application/json")
  //      response.setHeader("Cache-Control", "no-cache")
  //      response.setContent(content)
  //      response
  //    }
  //
  //    object OK {
  //      def apply(req: HttpRequest, service: (HttpRequest) => Object): HttpResponse =
  //        respond(HttpResponseStatus.OK,
  //          copiedBuffer(mapper.writeValueAsBytes(service(req))))
  //    }
  //
  //    object NotFound {
  //      def apply(): HttpResponse  =
  //        respond(NOT_FOUND,
  //          copiedBuffer("{\"status\":\"NOT_FOUND\"}", UTF_8))
  //    }
  //
  //    object InternalServerError {
  //      def apply(message: String): HttpResponse =
  //        respond(INTERNAL_SERVER_ERROR,
  //          copiedBuffer("{\"status\":\"INTERNAL_SERVER_ERROR\", " +
  //            "\"message\":\"" + message + "\"}", UTF_8))
  //    }
  //  }
  //  val echoService = new Service[Request, Response] {
  //    def apply(request: Request) = {
  //      echoCounter.incr()
  //      log.info(s"Received a ${request.method} request at ${Time.now}: ${request.contentString}")
  //      val queryInput = jsonToInputParms[QueryInput](request.contentString)
  //      println(s"QueryInput: $queryInput")
  //      val queryResponse = QueryResponse(UUID.randomUUID().toString, queryInput.divisions, queryInput.query, noRestCallError)
  //
  //      // raw input parms GET/POST
  //      //      val nameValues = for {
  //      //        name <- request.getParamNames()
  //      //      } yield NameValuePair(name, request.getParam(name))
  //      val response = Response(request.version, Status.Ok)
  //      response.setContentTypeJson()   // TODO: make conditional???
  //      response.contentString = toJson(queryResponse) + '\n'
  //      log.info(s"json: ${response.contentString}")
  //      Future.value(response)
  //    }
  //  }

}

