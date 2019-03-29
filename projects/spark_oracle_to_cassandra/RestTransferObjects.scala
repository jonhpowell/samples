package com.mir3.c9queryservice.rest

import java.util.UUID

import com.mir3.c9queryservice.data.WideRow
import com.mir3.c9queryservice.data.WideRow.Contact
import com.mir3.c9queryservice.spark.cassandra.SimContact

object RestTransferObjects extends App {
  // In case wanted to pre-parse query on client side
  //  case class QueryColumnSpecifier(name:String, asName:String)
  //  case class QuerySortSpecifier(name:String, ascending:Boolean)
  //  case class QueryInput(sessionId:String, projectionColumns:List[QueryColumnSpecifier], fromTable:String,
  //                        groupByColumns:List[String], sortColumns:List[QuerySortSpecifier], optLimit:Option[Int])

  // client request for meta data (sample results)
  case class ContactsQueryMetaRequest(sessionId:String)
  case class ContactsQueryMetaResponse(sessionId:String, contacts:Seq[Contact], error:String)

  // query IN (Tahoe) for permissions given user's sessionId
  case class OrgNodeDescriptor(id:String, name:String)
  case class TahoePermissions(viewNodes:Seq[OrgNodeDescriptor], privateNodes:Seq[OrgNodeDescriptor])
  case class TahoePermissionRequest(sessionId:String)
  case class TahoePermissionResponse(sessionId:String, permissions:TahoePermissions, error:String)

  // client request for data
  case class ContactsQueryRequest(sessionId:String, sparkSql:String)
  // marge of ContactsQuery and TahoePermissionResponse
  case class ContactsQueryRequestWithPermissions(sessionId:String, sparkSql:String, permissions:TahoePermissions)
  case class ContactsQueryResponse(sessionId:String, sparkSql:String, contacts:Seq[Contact], error:String)
  // TODO: temporary until move to real schema
  case class ContactsQueryResponseSimulated(sessionId:String, sparkSql:String, contacts:Seq[SimContact], error:String)

  val sessionId = UUID.randomUUID().toString
  val metaRequest = ContactsQueryMetaRequest(sessionId)
  val metaResponse = ContactsQueryMetaResponse(sessionId, WideRow.generateRows(1), FrontEndRestService.noRestCallError)
  val sparkSql = "SELECT username, COUNT(*) AS cnt FROM contacts WHERE username <> '' GROUP BY username ORDER BY cnt DESC LIMIT 10"
  val queryRequest = ContactsQueryRequest(sessionId, sparkSql)
  val queryResponse = ContactsQueryResponse(sessionId, sparkSql, WideRow.generateRows(2), FrontEndRestService.noRestCallError)

  // self-documenting REST interface documentation
  println("\n---REST call to get query Cloud9QueryProxy metaData---")
  println("\nPOST to http://<service-host>:<service-port>/contacts/meta")
  println(s"\nSample ContactsQueryMetaRequest JSON:\n${FrontEndRestService.toJson(metaRequest, prettyFormatting = true)}")
  println(s"\nSample ContactsQueryMetaResponse JSON:\n${FrontEndRestService.toJson(metaResponse, prettyFormatting = true)}")

  println("\n---REST call to query for Cloud9QueryProxy data---")
  println("\nPOST to http://<service-host>:<service-port>/contacts")
  println(s"\nSample ContactsQueryRequest JSON:\n${FrontEndRestService.toJson(queryRequest, prettyFormatting = true)}")
  println(s"\nSample ContactsQueryResponse JSON:\n${FrontEndRestService.toJson(queryResponse, prettyFormatting = true)}")

  val permissions = TahoePermissions(Seq(OrgNodeDescriptor("1", "FirstOrg"), OrgNodeDescriptor("3", "ThirdOrg")), Seq(OrgNodeDescriptor("1", "FirstPrivate")))
  val contactsQueryRequestWithPermissions = ContactsQueryRequestWithPermissions(sessionId, sparkSql, permissions)
  println(s"\nSample contactsQueryRequestWithPermissions:\n${FrontEndRestService.toJson(contactsQueryRequestWithPermissions, prettyFormatting = true)}")

}
