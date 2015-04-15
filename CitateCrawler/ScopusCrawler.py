__author__ = 'Mishanya'

import requests
import json
import pprint
import random
import datetime
import time
import os
import os.path

api_key = 'b4ecc27393a3e69e638f5efe599787ab'

# Request' headers
headers = dict()
headers['X-ELS-APIKey'] = api_key
headers['X-ELS-ResourceVersion'] = 'XOCS'
headers['Accept'] = 'application/json'

api_resource = "https://api.elsevier.com/content/search/scopus?"
""" Searching parameters """
params = 'query=title-abs-key(porn video AND NOT gay)&sort=-citedby-count'
# Result request' url
url = api_resource + params

# Maximum amount of papers
max_papers = 100
# Max recursion deep
max_deep = 3
# Print article data, during crawling process
need_print = True

# Dictionaries for data save
paper_ids = dict()
paper_edges = dict()

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
date_file = open("./articles_data/years.txt", 'w')
# Create json file
dt = time.strftime("%d%b%Y%H%M", time.gmtime())
article_file = open("./articles_json/" + dt + ".txt", 'w')

# Main response (Search by parameters)
response = requests.get(url, headers=headers)
response_result = json.loads(response.content.decode("utf-8"))

# Page content (Articles on the first page)
page_url = response_result['search-results']['link'][0]['@href'].replace("http", "https").replace(":80", "")
page_response = requests.get(page_url, headers=headers)
page_result = json.loads(page_response.content.decode("utf-8"))

# First list
articles_list = page_result['search-results']['entry']

# Start index
cur_paper = 0

def correct_string(name):
    shit_cymbols = {"\xe1": "a", '\xe8': 'e'}
    for cymb in shit_cymbols:
        name.replace(cymb, shit_cymbols[cymb])
    return name

def crawling(articles, cur_deep):
    """
    Recursive function for crawling.
    Write data for each article in articles,
     and further crawling with citations list.
    :param articles: List of articles
    :param cur_deep: Current recursion deep
    """
    global cur_paper
    print("Start crawling at level " + str(cur_deep))

    for article in articles:
        if len(paper_ids) >= max_papers:
            break

        # Article data
        title = article['dc:title']
        if title in paper_ids.keys():
            continue
        cit_count = 0
        try:
            cit_count = article['citedby-count']
        except Exception:
            pass
        authors = ""
        try:
            authors = article['dc:creator']
        except Exception:
            pass
        date = ""
        try:
            date = article['prism:coverDisplayDate']
        except Exception:
            pass

        article_url = article['prism:url'].replace("http", "https").replace(":80", "")

        # Find keywords of this article
        keywords = []
        try:
            article_keywords = requests.get(article_url + "?field=authkeywords", headers=headers)
            article_keywords = json.loads(article_keywords.content.decode("utf-8"))
            keywords = [keyword['$'] for keyword in article_keywords['abstracts-retrieval-response']['authkeywords']['author-keyword']]
        except Exception:
            pass
        # Add keywords into article json
        article['keywords'] = keywords

        # Write article data to dictionaries
        paper_ids[title] = cur_paper

        # Get citations
        citations = []
        citations_names = []
        have_citations = False
        if cur_deep < max_deep:
            try:
                citations_response = requests.get(api_resource + 'query=refeid(' + str(article['eid']) + ')', headers=headers)
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
            try:
                auth_file.write(str(cur_paper) + "\t" + correct_string(authors) + "\n")
            except Exception:
                auth_file.write(str(cur_paper) + "\t" + "" + "\n")
            try:
                date_file.write(str(cur_paper) + "\t" + date + "\n")
            except Exception:
                date_file.write(str(cur_paper) + "\t" + "" + "\n")
            try:
                cit_file.write(str(cur_paper) + "\t" + str(cit_count) + "\n")
            except Exception:
                cit_file.write(str(cur_paper) + "\t" + "" + "\n")
            try:
                key_file.write(str(cur_paper) + "\t" + str(keywords) + "\n")
            except Exception:
                key_file.write(str(cur_paper) + "\t" + "" + "\n")
            try:
                edge_file.write(str(cur_paper) + "\t" + str(citations_names) + "\n")
            except Exception:
                edge_file.write(str(cur_paper) + "\t" + "" + "\n")
        except Exception:
            print("WRONG TITLE!!!")
            del(paper_ids[title])
            continue

        # Write current json into file
        json.dump(article, article_file)
        article_file.write("\n")

        # Increase papers' counter
        cur_paper += 1

        # Continue crawling, if this article has citations
        if cur_deep < max_deep and len(paper_ids) < max_papers and have_citations:
            crawling(citations, cur_deep + 1)

        pass
    pass


""" Start crawling """
try:
    crawling(articles_list, 0)
    # Continue with next found pages
    if len(paper_ids) < max_papers and len(response_result['search-results']['link'][2]) > 3:
        # Next page content
        page_url = page_result['search-results']['link'][2]['@href'].replace("http", "https").replace(":80", "")
        page_response = requests.get(page_url, headers=headers)
        page_result = json.loads(page_response.content.decode("utf-8"))
        articles_list = page_result['search-results']['entry']
        crawling(articles_list, 0)
except Exception:
    pass

# Close files
article_file.close()
ids_file.close()
edge_file.close()
cit_file.close()
auth_file.close()
key_file.close()
date_file.close()

# Convert edges to indexes
idx_edges_file = open("./articles_data/idx_edges.txt", 'w')
for title, idx in paper_ids.items():
    idx_edges_file.write(str(idx) + "\n\t")
    edges = paper_edges[idx]
    for edge in edges:
        if edge in paper_ids.keys():
            idx_edges_file.write(str(paper_ids[edge]) + "\t")
    idx_edges_file.write("\n")
idx_edges_file.close()

pass