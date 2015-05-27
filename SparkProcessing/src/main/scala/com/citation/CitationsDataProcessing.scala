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
    println("privet")
    val directory = "/home/vagrant/citations/"

//    println(directory)
//    val jsons = sc.textFile("hdfs://" + directory + "articles_json/comp_science/2011/articles0 - 500").flatMap(_.split("\n")).
//                        map(x => JSON.parseFull(x))
//    jsons.take(10).foreach(println)
//    println("articles")
//    try {
//      val articles = jsons.map(x => x.get("dc:title"))
//    val sizes = jsons.map(x => x.size)
//    println("sizes")
//    sizes.take(10).foreach(println)
//      articles.take(10).foreach(println)
//    } catch {
//      case e:Exception => println("opa")
//    }
//    jsons.saveAsTextFile("hdfs://" + directory + "json_out4/")
//    jsons.coalesce(1, true).saveAsTextFile("hdfs://" + directory + "json_out5/")

      println("Titles:")
      val titles_file = sc.textFile("hdfs://" + directory + "artData/titles.txt").flatMap(_.split("\n"))
      val titles = titles_file.map(x => (x.split("\t")(0), x.split("\t")(1)))
      titles.take(20).foreach(println)
  }

  def writeToHdfs(sparkConf:SparkConf, filePath: String, text: String): Unit = {
   val path = new Path(filePath)
    val conf = new Configuration()
    conf.addResource(new Path("/etc/hadoop/conf/core-site.xml"))
    val fs = FileSystem.get(conf)
    val os = fs.create(path)
    os.writeChars(text)
    fs.close()
  }
}

