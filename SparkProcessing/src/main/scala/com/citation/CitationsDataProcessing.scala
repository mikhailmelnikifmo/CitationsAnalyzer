package com.citation

import scala.collection.mutable
import scala.util.parsing.json._
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.fs.{FileSystem, Path}
import org.apache.spark.{SparkConf, SparkContext}

object CitationsDataProcessing extends Serializable {
  def main(args: Array[String]): Unit = {
    val sparkConf = new SparkConf().setAppName("citation")
    val sc = new SparkContext(sparkConf)
    val conf = new Configuration()
    conf.addResource(new Path("/etc/hadoop/conf/core-site.xml"))
    val fs = FileSystem.get(conf)

    println("privet")
    val directory = "/home/vagrant/citations/"

    val jsons = sc.textFile("hdfs://" + directory + "articles_json/*/*").flatMap(_.split("\n")).
                        map(x => JSON.parseFull(x))
    val keywords_rdd = jsons.filter(x => x.isDefined).
      map(x => x.get.asInstanceOf[Map[String, Any]].
      get("keywords").get.asInstanceOf[List[String]]).flatMap(y => y).
      map(x => x.toLowerCase()).distinct().zipWithIndex()

    val keywords_map = new mutable.HashMap[String, Int]()
    for (x <- keywords_rdd) {
      keywords_map.put(x._1, x._2.toInt)
    }

    val titles_rdd = jsons.filter(x => x.isDefined).
      map(x => x.get.asInstanceOf[Map[String, Any]].
      get("dc:title").get.asInstanceOf[String]).distinct().zipWithIndex()

    val title_map = new mutable.HashMap[String, Int]()
    for (x <- titles_rdd) {
      title_map.put(x._1, x._2.toInt)
    }

    val articles = new mutable.HashMap[String, Article]()
    for (j <- jsons.filter(x => x.isDefined)) {
      val title = j.get.asInstanceOf[Map[String,Any]].get("dc:title").get.asInstanceOf[String]
      print("title = " + title)
      if (!articles.contains(title)) {
        println(" is new")
        val keywords = j.get.asInstanceOf[Map[String,Any]].get("keywords").get.asInstanceOf[List[String]].
          map(x => x.toLowerCase()).map(x => keywords_map.get(x)).asInstanceOf[List[Int]]
        println("keywords = " + keywords)
        val citations = j.get.asInstanceOf[Map[String,Any]].get("citations").get.asInstanceOf[List[String]].
        map(x => title_map.get(x)).asInstanceOf[List[Int]]
        println("citations = " + citations)
        val data = j.get.asInstanceOf[Map[String,Any]].get("prism:coverDate").get.asInstanceOf[String]
        println("data = " + data)
        val cit_count = j.get.asInstanceOf[Map[String,Any]].get("citedby-count").get.asInstanceOf[String]
        println("cit_count = " + cit_count)
        val author = j.get.asInstanceOf[Map[String,Any]].get("dc:creator").get.asInstanceOf[String]
        println("author = " + author)
        articles.put(title, new Article(title, keywords, citations, cit_count.toInt, data, author))
        println("article has been put")
        println()
      }
    }
    val articles_arr = titles_rdd.map(x => x._1 + "\t" + x._2).collect()
    val path = new Path(directory + "titlesIndex.txt")

    val art_file = fs.create(path)
    articles_arr.foreach(x => art_file.writeChars(x + "\n"))
    art_file.close()

    fs.close()
  }
}

