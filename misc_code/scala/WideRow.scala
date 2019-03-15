package com.mir3.c9queryservice.data

import java.util.UUID

import org.joda.time.DateTime
import org.joda.time.format.ISODateTimeFormat

import scala.util.Random

/*
 * Converting relational data model to a series of wide rows--denormalization of relational schema
 */

object WideRow {

  case class CallResponse(number: Int, text: String, success: Boolean)

  case class Address(`type`: String, street1: String, building: String, floor: Int, city: String, state: String, zip: String,
                     country: String, latitude: Double, longitude: Double)

  case class Device(`type`: String, address: String, description: String, `private`: Boolean)

  case class Initiator(username: String, firstName: String, lastName: String, id: Int, alias: String)

  case class Notification(title: String, division: String, deliveryMethod: String)

  case class Recipient(firstName: String, lastName: String, employeeId: String, addresses: Seq[Address], sourceType: String,
                       sourceName: String, notificationTier: Int)

  case class Transaction(reportId: Int, eventHistId: String, deliveryMethodId: Int, timeSent: String, timeClosed: String,
                         billingTime: String, billableDurationSeconds: Int, priceModel: String, costPerUnit: Double,
                         costThisTransaction: Double, segments: Int, dataCenter: String, localeUsed: String, message: String,
                         selectedResponses: Seq[CallResponse], deliveryStatus: String, contactAttempts: Int,
                         leftMessageStatus: String, callAnalysisResult: String, validateRecipient: Boolean)

  case class Contact(transaction: Transaction, device: Device, initiator: Initiator, notification: Notification, recipient: Recipient)

  val random = Random
  def nextBoolean = random.nextBoolean
  def nextInt(ceiling:Int) = random.nextInt(ceiling)
  def nextNonZeroInt(ceiling:Int) = random.nextInt(ceiling-1) + 1
  def nextDouble = random.nextDouble()
  def nextDouble(ceiling:Double):Double = ceiling * nextDouble
  def randomUsaLatitude = 25.0 * ( 1 + random.nextDouble())
  def randomUsaLongitude = -123.0 + (30.0 * ( 1 + random.nextDouble()))

  val addressTypes = Seq("work", "home", "workout", "vacation")
  def randomAddressType:String = addressTypes(nextInt(addressTypes.length))

  val deliveryMethod = Seq("BROADCAST", "CALLOUT", "FIRST_RESPONSE", "BULLETIN_BOARD")
  def randomDeliveryMethod:String = deliveryMethod(nextInt(deliveryMethod.length))

  val cityStates = Seq(("San Diego", "CA"), ("San Francisco", "CA"), ("Atlanta", "GA"), ("Seattle", "WA"), ("Tuscon", "AZ"), ("Kansas City", "KS"))
  def randomCityState:(String,String) = cityStates(nextInt(cityStates.length))

  val dataCenters = Seq("San Diego", "Denver", "Slough", "UAE")
  def randomDataCenter:String = dataCenters(nextInt(dataCenters.length))

  val timeFormatter = ISODateTimeFormat.dateTime()
  def dateTimeToString(dateTime:DateTime) = timeFormatter.print(dateTime)
  def generateTimeStrings:(String,String,String) = {
    val baseDateTime = new DateTime(2015, 1, 1, 0, 0, 0)
    val randomPlusTime = baseDateTime.plus(random.nextInt(2000000000))
    val timeSent = randomPlusTime
    val timeClosed = randomPlusTime.plus(random.nextInt(2400000))
    val billedTime = timeClosed.plus(random.nextInt(36450))
    (dateTimeToString(timeSent), dateTimeToString(timeClosed), dateTimeToString(billedTime))
  }

  def generateAddresses(baseIndex:Int, count:Int) = {
    for {
      iter <- 1 to count
      (city,state) = randomCityState
      zipCode = nextInt(99999)
    } yield Address(randomAddressType, s"street$baseIndex-$count", "building"+iter, nextInt(32), city, state, f"$zipCode%05d",
      "USA", randomUsaLatitude, randomUsaLongitude)
  }

  def generateSelectedResponses(baseIndex:Int, minCount:Int, maxCount:Int) = {
    val totalCount = nextInt(maxCount - minCount) + 1
    //println(s"minCount: $minCount, maxCount: $maxCount, totalCount: $totalCount")
    val selectedMessage = 1 + (if (totalCount < 2) 1 else nextInt(totalCount-1))
    for {
      iter <- 1 to totalCount
      (city,state) = randomCityState
    } yield CallResponse(iter, "messageText"+iter, iter == selectedMessage)
  }

  def generateRows(count:Int):Seq[Contact] = {
    for {
      iter <- 1 to count
      device = Device("device"+iter, "address"+iter, "description"+iter, iter%2==0)
      initiator = Initiator("user"+iter, "firstName"+iter, "lastName"+iter, iter, "alias"+iter)
      notification = Notification("notification"+iter, "division"+iter, "deliveryMethod"+iter)
      recipient = Recipient("firstName"+iter, "lastName"+iter, (iter*1000).toString, generateAddresses(iter, nextNonZeroInt(3)),
        "sourceType"+iter, "sourceName"+iter, iter)
      (timeSent, timeClosed, billedTime) = generateTimeStrings
      transaction = Transaction(iter, UUID.randomUUID().toString, nextInt(4), timeSent, timeClosed, billedTime, nextInt(2000),
        "priceModel"+iter, nextDouble(13.0), nextDouble(3345.0), nextInt(4), randomDataCenter, "en-us", "Notify message " + iter,
        generateSelectedResponses(iter, 1, 4), "deliveryStatus"+iter, nextNonZeroInt(3), "leftMessageStatus"+iter, "callAnalysisResult"+iter, nextBoolean)
    } yield Contact(transaction, device, initiator, notification, recipient)
  }

}
