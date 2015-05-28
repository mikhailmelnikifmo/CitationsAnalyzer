package com.citation

import java.lang.Double.isNaN
import java.util
import scala.collection.mutable
import scala.collection.mutable.HashMap
import scala.util.parsing.json._
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.SparkContext._
import org.apache.spark.rdd.RDD
import org.apache.spark.util.StatCounter
import com.citation.Article

object CitationsDataProcessing extends Serializable {
  def main(args: Array[String]): Unit = {
    val sparkConf = new SparkConf().setAppName("citation")
    val sc = new SparkContext(sparkConf)
    println("privet")
    val directory = "/home/vagrant/citations/"

    println(directory)
    val jsons = sc.textFile("hdfs://" + directory + "articles_json/*/*").flatMap(_.split("\n")).
                        map(x => JSON.parseFull(x))
    val keywords_rdd_temp = jsons.map(x => x.get.asInstanceOf[Map[String, Any]].get("keywords").get.asInstanceOf[List[String]]).
      flatMap(y => y)
    println("keywords rdd TEMP = ")
    keywords_rdd_temp.take(10).foreach(println)
    println()

//    val keywords_rdd = jsons.map(x => x.get.
//      asInstanceOf[Map[String, Any]].
//      get("keywords").
//      asInstanceOf[String]).
//      distinct().
//      zipWithIndex()
//    val titles_rdd = jsons.map(x => x.get.asInstanceOf[Map[String, Any]].get("keywords").get.asInstanceOf[String].toLowerCase).
//      distinct().zipWithIndex()
//
//    println("keywords rdd = ")
//    keywords_rdd.take(10).foreach(println)
//    println()
//
//    println("titles rdd = ")
//    titles_rdd.take(10).foreach(println)
//    println()

//    val articles = new mutable.HashMap[String, Article]
//    for (x <- jsons) {
//      val title = x.get.asInstanceOf[Map[String,Any]].get("dc:title").asInstanceOf[String]
//
//      if (!articles.contains(title.get.toString())) {
//        val keywords = x.get.asInstanceOf[Map[String,Any]].get("keywords").get.toString().split(", ").map(x => x.replace("\"", "").toLowerCase())
//        val citations = x.get.asInstanceOf[Map[String,Any]].get("citations")
//        val data = x.get.asInstanceOf[Map[String,Any]].get("coverDate")
//        val cit_count = x.get.asInstanceOf[Map[String,Any]].get("citedby-count").get.toString().toInt
//        val author = x.get.asInstanceOf[Map[String,Any]].get("dc:creator")
//        val affilation = x.get.asInstanceOf[Map[String,Any]].get("affilation")
//        val affil_name = affilation.get.asInstanceOf[Map[String, Any]].get("affilname")
//        articles.put(title.get.toString(), new Article())
//      }
//    }
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

