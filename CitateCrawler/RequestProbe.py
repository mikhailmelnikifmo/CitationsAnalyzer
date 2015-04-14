__author__ = 'Mishanya'

import requests
import json
import pprint

api_key = 'b4ecc27393a3e69e638f5efe599787ab'

headers = dict()
headers['X-ELS-APIKey'] = api_key
headers['X-ELS-ResourceVersion'] = 'XOCS'
headers['Accept'] = 'application/json'

http_proxy = "http://proxy.ifmo.ru/proxy.pac"
proxies = {"http": http_proxy}

api_resource = "https://api.elsevier.com/content/search/scopus?"
title = 'Real-time monitoring station for production systems'
url = api_resource + "query=title(" + title + ")"

paper_titles = []
paper_edges = dict()

# requests

response = requests.get(url, headers=headers, proxies=proxies)

result = json.loads(response.content.decode("utf-8"))

article_url = result['search-results']['entry'][0]['prism:url'].replace("http", "https")

response2 = requests.get(article_url, headers=headers, proxies=proxies)
result2 = json.loads(response2.content.decode("utf-8"))

cur_paper = result2['abstracts-retrieval-response']['coredata']['dc:title']
paper_titles.append((result2['abstracts-retrieval-response']['coredata']['dc:title'], result2['abstracts-retrieval-response']['coredata']['citedby-count']))

cited_url = result2['abstracts-retrieval-response']['coredata']['link'][2]['@href'].replace("http", "https")

response3 = requests.get(cited_url, headers=headers, proxies=proxies)
result3 = json.loads(response3.content.decode("utf-8"))

references = result3['search-results']['entry']

paper_edges[cur_paper] = set()
for ref in references:
    paper_titles.append((ref['dc:title'], ref['citedby-count']))
    paper_edges[cur_paper].add(ref['dc:title'])

print("NODES:")
pprint.pprint(paper_titles)

print("----====++++====----")

print("EDGES")
pprint.pprint(paper_edges)


pass