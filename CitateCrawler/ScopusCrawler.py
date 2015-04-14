__author__ = 'Mishanya'

import requests
import json
import pprint

api_key = 'b4ecc27393a3e69e638f5efe599787ab'

headers = dict()
headers['X-ELS-APIKey'] = api_key
headers['X-ELS-ResourceVersion'] = 'XOCS'
headers['Accept'] = 'application/json'

api_resource = "https://api.elsevier.com/content/search/scopus?"
params = 'query=title-abs-key(porn video)&sort=-citedby-count'
url = api_resource + params

max_papers = 2
cur_paper = 0
max_deep = 0

paper_ids = dict()
paper_edges = dict()
paper_authors = dict()
paper_keywords = dict()
paper_cited_count = dict()

# Main response
response = requests.get(url, headers=headers)
response_result = json.loads(response.content.decode("utf-8"))

# Page content
page_url = response_result['search-results']['link'][0]['@href'].replace("http", "https").replace(":80", "")
page_response = requests.get(page_url, headers=headers)
page_result = json.loads(page_response.content.decode("utf-8"))

# First list
articles_list = page_result['search-results']['entry']

def crawling(articles, cur_deep):
    global cur_paper
    print("Start crawling at level " + str(cur_deep))

    for article in articles:
        print('    get article ' + str(cur_paper))
        if len(paper_ids) >= max_papers:
            break

        # article data
        title = article['dc:title']
        if title in paper_ids.keys():
            continue
        cit_count = article['citedby-count']
        authors = article['dc:creator']
        article_url = article['prism:url'].replace("http", "https").replace(":80", "")

        # find keywords of this article
        article_keywords = requests.get(article_url + "?field=authkeywords", headers=headers)
        article_keywords = json.loads(article_keywords.content.decode("utf-8"))
        keywords = []
        try:
            keywords = [keyword['$'] for keyword in article_keywords['abstracts-retrieval-response']['authkeywords']['author-keyword']]
        except Exception:
            pass
        article['keywords'] = keywords

        # write full json file
        article_file = open("./articles_json/" + str(cur_paper) + ".json", 'w')
        json.dump(article, article_file)
        article_file.close()

        # write article data to dictionaries
        paper_ids[title] = cur_paper
        paper_authors[cur_paper] = authors
        paper_cited_count[cur_paper] = cit_count
        paper_keywords[cur_paper] = keywords
        paper_edges[cur_paper] = []

        have_citations = False
        # get citations
        if cur_deep < max_deep:
            citations_response = requests.get(api_resource + 'query=refeid(' + str(article['eid']) + ')', headers=headers)
            citations_result = json.loads(citations_response.content.decode("utf-8"))
            citations = citations_result['search-results']['entry']

            # add edges
            try:
                paper_edges[cur_paper] = [citation['dc:title'] for citation in citations][:max_papers-cur_paper]
                have_citations = True
            except Exception:
                pass

        cur_paper += 1

        # continue crawling
        if cur_deep < max_deep and len(paper_ids) < max_papers and have_citations:
            crawling(citations, cur_deep + 1)

        pass
    pass

crawling(articles_list, 0)

# Continue with next found pages
if len(paper_ids) < max_papers and len(response_result['search-results']['link'][2]) > 3:
    # Next page content
    page_url = page_result['search-results']['link'][2]['@href'].replace("http", "https").replace(":80", "")
    page_response = requests.get(page_url, headers=headers)
    page_result = json.loads(page_response.content.decode("utf-8"))

    articles_list = page_result['search-results']['entry']
    crawling(articles_list, 0)

# Write result data
ids_file = open("./articles_data/ids.txt", 'w')
for t, id in paper_ids.items():
   ids_file.write(str(id) + "\t" + t + "\n")
ids_file.close()

edge_file = open("./articles_data/edges.txt", 'w')
for id, edges in paper_edges.items():
    edge_file.write(str(id) + "\n\t")
    for edge in edges:
        edge_idx = paper_ids[edge]
        edge_file.write(str(edge_idx) + "\t")
    edge_file.write("\n")
edge_file.close()

cit_file = open("./articles_data/cit_counts.txt", 'w')
for id, cit in paper_cited_count.items():
    cit_file.write(str(id) + "\t" + str(cit) + "\n")
cit_file.close()

auth_file = open("./articles_data/authors.txt", 'w')
for id, author in paper_authors.items():
    auth_file.write(str(id) + "\n\t" + str(author) + "\n")
auth_file.close()

key_file = open("./articles_data/keys.txt", 'w')
for id, keys in paper_keywords.items():
    key_file.write(str(id) + "\n\t" + str(keys) + "\n")

pass