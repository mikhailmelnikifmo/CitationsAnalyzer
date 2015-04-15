__author__ = 'Mishanya'

import requests
import json
import pprint
import random
import datetime
import time

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
max_papers = 1000
# Max recursion deep
max_deep = 3
# Print article data, during crawling process
need_print = True

# Dictionaries for data save
paper_ids = dict()
paper_edges = dict()
paper_authors = dict()
paper_keywords = dict()
paper_cited_count = dict()

# File with json for each article
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
        cit_count = article['citedby-count']
        authors = article['dc:creator']
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
        paper_authors[cur_paper] = authors
        paper_cited_count[cur_paper] = cit_count
        paper_keywords[cur_paper] = keywords
        paper_edges[cur_paper] = []

        have_citations = False
        # Get citations
        if cur_deep < max_deep:
            citations_response = requests.get(api_resource + 'query=refeid(' + str(article['eid']) + ')', headers=headers)
            citations_result = json.loads(citations_response.content.decode("utf-8"))
            citations = citations_result['search-results']['entry']

            # Add edges
            try:
                paper_edges[cur_paper] = [citation['dc:title'] for citation in citations][:max_papers-cur_paper]
                have_citations = True
            except Exception:
                pass

        # Print current article data, if need
        if need_print:
            print("Art index = " + str(cur_paper))
            print("    Title = " + title)
            print("    Authors = " + authors)
            print("    Citations = " + str(cit_count))
            print("    Keywords = " + str(keywords))
            print("    Edges = " + str(paper_edges[cur_paper]))

        # Add citations into article json
        article['citations'] = paper_edges[cur_paper]

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
crawling(articles_list, 0)

# Continue with next found pages
if len(paper_ids) < max_papers and len(response_result['search-results']['link'][2]) > 3:
    # Next page content
    page_url = page_result['search-results']['link'][2]['@href'].replace("http", "https").replace(":80", "")
    page_response = requests.get(page_url, headers=headers)
    page_result = json.loads(page_response.content.decode("utf-8"))

    articles_list = page_result['search-results']['entry']
    crawling(articles_list, 0)

# Close file with json
article_file.close()

# Write result data
#   ids.txt ::
#       index   title
ids_file = open("./articles_data/ids.txt", 'w')
for t, id in paper_ids.items():
   ids_file.write(str(id) + "\t" + t.replace("\\", "|") + "\n")
ids_file.close()

#   edges.txt ::
#       index
#       citation_indexes
edge_file = open("./articles_data/edges.txt", 'w')
for id, edges in paper_edges.items():
    edge_file.write(str(id) + "\n\t")
    for edge in edges:
        if edge in paper_ids.keys():
            edge_idx = paper_ids[edge.replace("\\", "|")]
            edge_file.write(str(edge_idx) + "\t")
    edge_file.write("\n")
edge_file.close()

#   cit_counts.txt ::
#       index   citations_number
cit_file = open("./articles_data/cit_counts.txt", 'w')
for id, cit in paper_cited_count.items():
    cit_file.write(str(id) + "\t" + str(cit) + "\n")
cit_file.close()

#   authors.txt ::
#       index authors
auth_file = open("./articles_data/authors.txt", 'w')
for id, author in paper_authors.items():
    auth_file.write(str(id) + "\n\t" + author.replace("\\", "|") + "\n")
auth_file.close()

#   keys.txt ::
#       index
#           [key]
key_file = open("./articles_data/keys.txt", 'w')
for id, keys in paper_keywords.items():
    key_file.write(str(id) + "\n\t" + str(keys).replace("\\", "|") + "\n")

pass