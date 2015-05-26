/*
 * Copyright 2015 Sanford Ryza, Uri Laserson, Sean Owen and Joshua Wills
 *
 * See LICENSE file for further information.
 */

package com.citation

import java.lang.Double.isNaN
import scala.util.parsing.json._
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.SparkContext._
import org.apache.spark.rdd.RDD
import org.apache.spark.util.StatCounter

object CitationsDataProcessing extends Serializable {
  def main(args: Array[String]): Unit = {
    val sparkConf = new SparkConf().setAppName("citation")
    val sc = new SparkContext(sparkConf)

    val directory = "/home/vagrant/citations/"
//    val jsons = sc.textFile("hdfs://" + directory + "articles_json/*").flatMap(_.split("\n")).
//                        map(x => JSON.parseFull(x))
    writeToHdfs(sparkConf, directory + "test_output.txt", "privet")
  }

  def writeToHdfs(sparkConf:SparkConf, filePath: String, text: String): Unit = {
   val path = new Path(filePath)
    val conf = new Configuration()
    conf.set("fs.defaultFS", sparkConf.getOption("hdfs.uri").toString)
    val fs = FileSystem.get(conf)
    val os = fs.create(path)
    os.writeChars(text)
    fs.close()
  }
}

