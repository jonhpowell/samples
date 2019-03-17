package com.corelogic.model_table_updates

import scala.xml.{NodeSeq}
import scala.Some
import java.text.SimpleDateFormat
import java.util.Date
import java.sql.Timestamp
import java.io.{File, PrintWriter}
import scala.io.Source
import java.net.InetAddress

object Util {
  def safeDiv(n:Double, d:Double):Option[Double] = if (d.compareTo(0.0) == 0) None else Some(n / d)
  def safeDiv(numer:Option[Double], denom:Option[Double]):Option[Double] = (numer,denom) match {
    case (Some(n), Some(d)) => if (d.compareTo(0.0) == 0.0) None else Some(n / d)
    case _ => None
  }
  def safeToInt(s: String, i: Int): Int = try {s.trim.toInt} catch {case e: Exception => i}
  def safeToLong(s: String, i: Long): Long = try {s.trim.toLong} catch {case e: Exception => i}
  def safeToDouble(s: String, d: Double): Double = try {s.trim.toDouble} catch {case e: Exception => d}
  def toDoubleOpt(sOpt: Option[String]): Option[Double] = try {if (sOpt.isDefined) Some(sOpt.get.trim.toDouble) else None} catch {case e: Exception => None}
  def toIntWithException(s: String, msg:String): Int = try {s.trim.toInt} catch {case e: Exception => throw new RuntimeException(msg)}
  def toDoubleWithException(s: String, msg:String): Double = try {s.trim.toDouble} catch {case e: Exception => throw new RuntimeException(msg)}
  def safeDiv(numerator: Int, denominator: Int) = if (denominator == 0) 0.0 else numerator.toDouble / denominator.toDouble
  def removeXmlWhiteSpace(s:String) = if (s == null) "" else s.replaceAllLiterally("\n", "").replaceAll(">\\s+", ">").replaceAll("\\s+<", "<")
  def limit(value: Double, lowLimit: Double, highLimit: Double): Double = {
    return if (value < lowLimit) lowLimit else if (value > highLimit) highLimit else value
  }

  // in bin if (low <= x < high); assumes bin boundaries are sorted ascending; binBoundaries.length+1 bins
  def binValue(binBoundaries:List[Double])(value:Double):Int = {
    if (value <= Double.NegativeInfinity) 0
    else (binBoundaries :+ Double.PositiveInfinity).zipWithIndex.find(t => value < t._1).map(_._2).get
  }

  def getDoubleFromHead(seq:NodeSeq, name:String) = {
    if (seq.isEmpty) None
    else try { ((seq.head \ name).text).toDouble } catch { case e:Throwable => None}
  }

  def getHostName = InetAddress.getLocalHost.getHostName

  def dBtoCamelCase(s:String) = {
    val res = s.foldLeft((false,""))((a:(Boolean,String),c:Char) => (a._1, a._2, c) match {
      case (true,acc,ch) => (false, acc + ch.toUpper)
      case (false,acc,ch) if (c=='_') => (true, acc)
      case (false,acc,ch) => (false, acc + ch)
    })._2
    if (res.size > 0 && res(0).isUpper) res(0).toLower + res.tail
    else res
  }

  // distance determination
  val EARTH_RADIUS_MILES: Double = 3959.0

  def toRadians(degrees: Double): Double = {
    return degrees * Math.PI / 180.0
  }

  def milesDistance(latitude1Degrees: Double, longitude1Degrees: Double, latitude2Degrees: Double, longitude2Degrees: Double): Double = {
//println("(lat1,lon1,lat2,lon2)=(%f,%f,%f,%f)".format(latitude1Degrees, longitude1Degrees, latitude2Degrees, longitude2Degrees))
    val lat1Radians = toRadians(latitude1Degrees)
    val lon1Radians = toRadians(longitude1Degrees)
    val lat2Radians = toRadians(latitude2Degrees)
    val lon2Radians = toRadians(longitude2Degrees)
    val angleCos = (Math.sin(lat1Radians) * Math.sin(lat2Radians)) + (Math.cos(lat1Radians) * Math.cos(lat2Radians) * Math.cos(lon1Radians - lon2Radians))
    return EARTH_RADIUS_MILES * Math.acos(limit(angleCos, -1.0, 1.0))
  }

  def concatenateStringStringMaps(maps:Map[String, String]*) = maps.flatten.toMap

  def splitNameValuePair(nameValuePair:String, delim:String="="):(String,String) = {
    val tokens = nameValuePair.split(delim)
    val name = if (tokens.size > 0) tokens(0) else ""
    val value = if (tokens.size > 1) tokens(1) else ""
    (name, value)
  }

  def csvNameValuePairsToMap(line:String, lineDelim:String = "|", varDelim:String = "="):Map[String,String] = {
    if (line == null || line.trim.length < 1) {
      Map.empty
    } else {
      val lineTokens:List[String] = line.split("[" + lineDelim + "]").toList
      //println("lineTokens="+lineTokens.toList.mkString(","))
      lineTokens.map(nvp => splitNameValuePair(nvp, "[" + varDelim + "]")).toMap
    }
  }

  /*
    def time[R](f:R):R = {
      val t0 = System.nanoTime()
      val result = f
      val t1 = System.nanoTime()
      println("Elapsed time: " + (t1 - t0) / 1000000 + "ms")
      result
    }
  */
}


