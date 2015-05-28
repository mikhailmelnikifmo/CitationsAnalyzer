package com.citation

/**
 * Created by Mishanya on 28.05.2015.
 */
class Article(title: String, keywords: Array[Int], citations: Array[Int], cit_count: Int, year: String, author: String) {
  var this.title = title
  var this.keywords = keywords
  var this.citations = citations
  var this.cit_count = cit_count
  val this.year = year
  val this.author = author
}
