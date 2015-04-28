__author__ = 'Mishanya'

import requests
import json
import pprint
import random
import datetime
import time
import os
import os.path
import time

def crawling(articles, cur_deep):
    """
    Recursive function for crawling.
    Write data for each article in articles,
     and further crawling with citations list.
    :param articles: List of articles
    :param cur_deep: Current recursion deep
    """
    global cur_paper
    # print("Start crawling at level " + str(cur_deep))
    start = time.clock()
    for article in articles:
        finish = time.clock()
        print("Article time = " + str(finish - start))
        start = finish
        if len(paper_ids) >= max_papers:
            break

        # Article data
        title = article['dc:title']
        if title in paper_ids.keys():
            continue
        try:
            cit_count = article['citedby-count']
            authors = article['dc:creator']
            date = article['prism:coverDisplayDate']
        except Exception:
            print("WRONG ARTICLE!!!")
            continue

        article_url = article['prism:url'].replace("http", "https").replace(":80", "")

        # Find keywords of this article
        try:
            # print("Keywords started")
            article_keywords = requests.get(article_url + "?field=authkeywords", headers=headers)

            article_keywords = json.loads(article_keywords.content.decode("utf-8"))
            keywords = [keyword['$'] for keyword in article_keywords['abstracts-retrieval-response']['authkeywords']['author-keyword']]
        except Exception:
            print("Key words error")
            continue

        # Add keywords data
        article['keywords'] = keywords

        # Write article data to dictionaries
        paper_ids[title] = cur_paper

        # Get citations
        citations = []
        citations_names = []
        have_citations = False
        if cur_deep < max_deep and not cit_count == '0':
            try:
                # print("Citations search started")
                start = time.clock()
                citations_response = requests.get(api_resource + 'query=refeid(' + str(article['eid']) + ')', headers=headers)
                # print("Citations request: " + str(time.clock() - start))
                citations_result = json.loads(citations_response.content.decode("utf-8"))
                citations = citations_result['search-results']['entry']
                # Add edges
                citations_names = [citation['dc:title'] for citation in citations][:max_papers-cur_paper]
                have_citations = True
            except Exception:
                print("citations error")
                pass

        # Print current article data, if need
        if need_print:
            print("Art index = " + str(cur_paper))
            print("    Title = " + title)
            print("    Authors = " + authors)
            print("    Year = " + date)
            print("    Citations = " + str(cit_count))
            print("    Keywords = " + str(keywords))
            print("    Edges = " + str(citations_names))

        # Add citations into article json
        article['citations'] = citations_names

        # Write current json into file
        json.dump(article, article_file)
        article_file.write("\n")
        print("article has been written")

        # Increase papers' counter
        cur_paper += 1

        # Continue crawling, if this article has citations
        try:
            if cur_deep < max_deep and len(paper_ids) < max_papers and have_citations:
                crawling(citations, cur_deep + 1)
        except Exception:
            print("Deep crawling error")
            citations_names = []

        pass
    pass
""" END FUNCTION """

if __name__ == "__main__":

    total_start_time = time.clock()

    api_key = 'b4ecc27393a3e69e638f5efe599787ab'

    # Request' headers
    headers = dict()
    headers['X-ELS-APIKey'] = api_key
    headers['X-ELS-ResourceVersion'] = 'XOCS'
    headers['Accept'] = 'application/json'

    api_resource = "https://api.elsevier.com/content/search/scopus?"
    # api_resource = "http://api.elsevier.com/content/search/index:SCOPUS?"
    """ Searching parameters """
    search_params = ['query=title-abs-key(harmonic search)', 'query=title-abs-key(machine learning)',
                     'query=title-abs-key(gravitation search algorithm)', 'query=title-abs-key(hyper-heuristics)',
                     'query=title-abs-key(mapreduce)']

    # Maximum amount of papers
    max_papers = 20000
    # Max recursion deep
    max_deep = 4
    # Print article data, during crawling process
    need_print = False

    # Dictionaries for data save
    paper_ids = dict()

    # Create files
    json_dir = "./articles_json/"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    # Create data files
    dt = time.strftime("%d%b%Y%H%M", time.gmtime())
    article_file = open("./articles_json/" + dt + ".txt", 'w')

    # Start index
    cur_paper = 0

    fields = '&field=authkeywords'
    # fields = ''

    for search_query in search_params:
        print("SEARCH QUERY = " + search_query)
        if cur_paper >= max_papers:
            break
        # Result request' url
        url = api_resource + search_query + "&sort=citedby-count"

        # Main response (Search by parameters)
        try:
            print("First search started")
            response = requests.get(url, headers=headers)

            response_result = json.loads(response.content.decode("utf-8"))

            # Page content (Articles on the first page)
            print("Page content started")
            page_url = response_result['search-results']['link'][0]['@href'].replace("http", "https").replace(":80", "")
            page_response = requests.get(page_url, headers=headers)
            page_result = json.loads(page_response.content.decode("utf-8"))

            # First list
            articles_list = page_result['search-results']['entry']
            print("First search finished successful")
        except Exception:
            print("Error during first search")
            continue

        """ Start crawling """
        try:
            print("Start crawling FIRST page")
            crawling(articles_list, 0)
            print("PAGE FINISH")
            # Continue with next found pages
            if len(paper_ids) < max_papers and len(response_result['search-results']['link'][2]) > 3:
                # Next page content
                print("Start crawling NEXT page")
                page_url = page_result['search-results']['link'][2]['@href'].replace("http", "https").replace(":80", "")
                page_response = requests.get(page_url, headers=headers)
                page_result = json.loads(page_response.content.decode("utf-8"))
                articles_list = page_result['search-results']['entry']
                crawling(articles_list, 0)
                print("PAGE FINISH")
        except Exception:
            print("!!! global crawling exception !!!")
            pass

    # Close files
    article_file.close()

    finish_time = time.clock()
    print("ARTICLES COUNT = " + str(cur_paper))
    print("FULL CRAWLING TIME = " + str(finish_time - total_start_time))
    pass