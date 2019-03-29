package com.mir3.c9queryservice.spark.job

import java.io.BufferedReader
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader

object InputStreamReaderRunnable {
  def apply(is:InputStream, name: String): InputStreamReaderRunnable = new InputStreamReaderRunnable( is, name)
}

class InputStreamReaderRunnable(val is: InputStream, var name: String) extends Runnable {
  private var reader: BufferedReader = null
  this.reader = new BufferedReader(new InputStreamReader(is))
  private val results = StringBuilder.newBuilder

  var lines = 0
  def getResults:(Int,String) = (lines,results.toString)

  def run() {
    //System.out.println("InputStream " + name + ":")
    try {
      var line: String = reader.readLine
      while (line != null) {
        {
          //System.out.println(String.format("%s:%s", name, line))
          results.append('\n')
          results.append(line)
          lines += 1
          line = reader.readLine
        }
      }
    } catch {
      case e: IOException => e.printStackTrace()
    } finally {
      reader.close()
    }
  }
}

