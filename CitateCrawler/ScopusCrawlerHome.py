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

total_start_time = time.clock()

def crawling(articles, cur_deep):
    """
    Recursive function for crawling.
    Write data for each article in articles,
     and further crawling with citations list.
    :param articles: List of articles
    :param cur_deep: Current recursion deep
    """
    global cur_paper
    global key_index
    print("Start crawling at level " + str(cur_deep))

    for article in articles:
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
            # del(paper_ids[title])
            continue

        article_url = article['prism:url'].replace("http", "https").replace(":80", "")

        # Find keywords of this article
        try:
            # print("Keywords started")
            start = time.clock()
            article_keywords = requests.get(article_url + "?field=authkeywords", headers=headers)

            article_keywords = json.loads(article_keywords.content.decode("utf-8"))
            keywords = [keyword['$'] for keyword in article_keywords['abstracts-retrieval-response']['authkeywords']['author-keyword']]
            # print("Keywords request: " + str(time.clock() - start))
        except Exception:
            print("Keywords request FAIL: " + str(time.clock() - start))
            continue

        # Add keywords data
        paper_keys[cur_paper] = []
        article['keywords'] = keywords
        keyset = []
        for keyword in keywords:
            if keyword not in paper_keys.keys():
                paper_keys[keyword] = key_index
                key_file.write(str(key_index) + "\t" + keyword + "\n")
                keyset.append(paper_keys[keyword])
                key_index += 1

        # Write article data to dictionaries
        paper_ids[title] = cur_paper

        # Get citations
        citations = []
        citations_names = []
        have_citations = False
        if cur_deep < max_deep:
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
        paper_edges[cur_paper] = citations_names

        # Write other data in files
        try:
            ids_file.write(str(cur_paper) + "\t" + title + "\n")
            auth_file.write(str(cur_paper) + "\t" + authors + "\n")
            date_file.write(str(cur_paper) + "\t" + date + "\n")
            cit_file.write(str(cur_paper) + "\t" + str(cit_count) + "\n")
            keys_idx_file.write(str(cur_paper) + "\n\t")
            for key in keyset:
                keys_idx_file.write(str(key) + "\t")
            keys_idx_file.write("\n")
            edge_file.write(str(cur_paper) + "\t" + str(citations_names) + "\n")
        except Exception:
            print("WRONG ARTICLE!!!")
            del(paper_ids[title])
            continue

        # Write current json into file
        json.dump(article, article_file)
        article_file.write("\n")

        # Increase papers' counter
        cur_paper += 1

        # Continue crawling, if this article has citations
        try:
            if cur_deep < max_deep and len(paper_ids) < max_papers and have_citations:
                crawling(citations, cur_deep + 1)
        except Exception:
            print("Deep crawling error")
            citations_names = []

        idx_edges_file.write(str(paper_ids[title]) + "\n\t")
        for cit_name in citations_names:
            if cit_name in paper_ids.keys():
                idx_edges_file.write(str(paper_ids[cit_name]) + "\t")
        idx_edges_file.write("\n")

        pass
    pass
""" END FUNCTION """

start = time.clock()

api_key = 'b4ecc27393a3e69e638f5efe599787ab'

# Request' headers
headers = dict()
headers['X-ELS-APIKey'] = api_key
headers['X-ELS-ResourceVersion'] = 'XOCS'
headers['Accept'] = 'application/json'

api_resource = "https://api.elsevier.com/content/search/scopus?"
""" Searching parameters """
search_params = ['query=title-abs-key(workflow scheduling)', 'query=title-abs-key(grid computing)', 'query=title-abs-key(harmonic search)']

# Maximum amount of papers
max_papers = 30000
# Max recursion deep
max_deep = 4
# Print article data, during crawling process
need_print = False

# Dictionaries for data save
paper_ids = dict()
paper_edges = dict()
paper_keys = dict()

# Create files
json_dir = "./articles_json/"
data_dir = "./articles_data/"
if not os.path.exists(json_dir):
    os.makedirs(json_dir)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
# Create data files
ids_file = open("./articles_data/ids.txt", 'w')
edge_file = open("./articles_data/edges.txt", 'w')
cit_file = open("./articles_data/cit_counts.txt", 'w')
auth_file = open("./articles_data/authors.txt", 'w')
key_file = open("./articles_data/keys.txt", 'w')
keys_idx_file = open("./articles_data/keys_idxs.txt", 'w')
date_file = open("./articles_data/years.txt", 'w')
idx_edges_file = open("./articles_data/idx_edges.txt", 'w')
# Create json file
dt = time.strftime("%d%b%Y%H%M", time.gmtime())
article_file = open("./articles_json/" + dt + ".txt", 'w')

# Start index
cur_paper = 2194
key_index = 8286

print("Preprocessing time = " + str(time.clock() - start))

fields = '&field=authkeywords'
# fields = ''

for search_query in search_params:
    if cur_paper >= max_papers:
        break
    # Result request' url
    url = api_resource + search_query + "&sort=citedby-count"

    # Main response (Search by parameters)
    try:
        print("First search started")
        start = time.clock()
        response = requests.get(url, headers=headers)
        print("First search request: " + str(time.clock() - start))

        response_result = json.loads(response.content.decode("utf-8"))

        # Page content (Articles on the first page)
        print("Page content started")
        start = time.clock()
        page_url = response_result['search-results']['link'][0]['@href'].replace("http", "https").replace(":80", "")
        print("Page_articles request: " + str(time.clock() - start))
        page_response = requests.get(page_url, headers=headers)
        page_result = json.loads(page_response.content.decode("utf-8"))

        # First list
        articles_list = page_result['search-results']['entry']
    except Exception:
        continue

    """ Start crawling """
    try:
        crawling(articles_list, 0)
        print("PAGE FINISH")
        # Continue with next found pages
        if len(paper_ids) < max_papers and len(response_result['search-results']['link'][2]) > 3:
            # Next page content
            page_url = page_result['search-results']['link'][2]['@href'].replace("http", "https").replace(":80", "")
            page_response = requests.get(page_url, headers=headers)
            page_result = json.loads(page_response.content.decode("utf-8"))
            articles_list = page_result['search-results']['entry']
            crawling(articles_list, 0)
            print("PAGE FINISH")
    except Exception:
        pass


# Close files
article_file.close()
ids_file.close()
edge_file.close()
cit_file.close()
auth_file.close()
key_file.close()
keys_idx_file.close()
date_file.close()
idx_edges_file.close()

finish_time = time.clock()
print("ARTICLES COUNT = " + str(cur_paper))
print("FULL CRAWLING TIME = " + str(finish_time - total_start_time))
pass