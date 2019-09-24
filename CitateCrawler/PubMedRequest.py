import os
import json
import time
import requests
import threading

import mysql.connector
cnx = mysql.connector.connect(user='root', password='tmppwd',
                              host='127.0.0.1',
                              database='pubmeddb'
                              )
cursor = cnx.cursor()


search_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
sum_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
abstract_api = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"


class Article():
    def __init__(self):
        self.title = None
        self.keywords = None
        self.authors = None
        self.pmid = None
        self.publication_date = None
        self.publication_type = None
        self.publication_title = None
        self.publication_issue = None
        self.doi = None
        self.abstract = None

    def fill(self, pmid, summary, abs):
        self.title = summary['title']
        self.keywords = ""
        self.authors = ""
        authors = summary['authors']
        for a in authors:
            self.authors += ", " + a['name']
        self.authors = self.authors[1:]
        self.pmid = pmid
        self.publication_date = summary['pubdate']
        if len(summary['pubtype']) == 0:
            self.publication_type = ""
        else:
            self.publication_type = summary['pubtype'][0]
        self.publication_title = summary['fulljournalname']
        self.publication_issue = "{} {} {}".format(summary['volume'], summary['issue'], summary['pages'])
        self.doi = summary['articleids'][1]['value']
        abs_arr = abs.split("\n\n")
        abs_valid_arr = []
        if 'Has Abstract' in summary['attributes']:
            for row in abs_arr:
                try:
                    if authors[0]['name'] not in row and row[0:10] != "Author inf" and self.doi not in row:
                        abs_valid_arr.append(row)
                except Exception:
                    print("Not valid row: {}".format(row))
            abs_arr = abs_valid_arr
            if not abs_arr:
                self.abstract = None
                print("pmid: {}, abstract: None\n".format(self.pmid))
            else:
                self.abstract = sorted(abs_arr, key=len, reverse=True)[0]
                print("pmid: {}, abstract: {}\n".format(self.pmid, self.abstract[0:300]))
        else:
            self.abstract = ""

    def put(self, cursor):
        add = ("INSERT INTO articles "
              "(pmid, authors, title, abstract, publication_date, "
               "publication_type, publication_title, publication_issue, doi) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        data = (self.pmid, self.authors, self.title, self.abstract,
                self.publication_date, self.publication_type,
                self.publication_title, self.publication_issue, self.doi)

        cursor.execute(add, data)

def abstract_url(art_id):
    return abstract_api + "db=pubmed&id={}&retmode=text&rettype=abstract".format(art_id)


def abstract_urls(art_ids):
    id_list = ""
    for id in art_ids:
        id_list += ",{}".format(id)
    id_list = id_list[1:]
    return abstract_url(id_list)


def sum_url(art_id):
    return sum_api + "db=pubmed&id={}&retmode=json".format(art_id)


def sum_urls(art_ids):
    id_list = ""
    for id in art_ids:
        id_list += ",{}".format(id)
    id_list = id_list[1:]
    return sum_url(id_list)


def search_url(term, field=None, reldate=None, retstart=None, retmax=None):
    url = search_api + "db=pubmed&datetype=edat&retmode=json"
    url += "&term={}".format(term)
    if field is not None:
        url += "&field={}".format(field)
    if reldate is not None:
        url += "&reldate={}".format(reldate)
    if retstart is not None:
        url += "&retstart={}".format(retstart)
    if retmax is not None:
        url += "&retmax={}".format(retmax)
    return url


term = "cardiology"
retmax = 50
ret_cur = 0

# initial
pubmed_ids_url = search_url(term, None, None, ret_cur, 0)
pubmed_ids_req = requests.get(pubmed_ids_url)
pubmed_ids = json.loads(pubmed_ids_req.content.decode("utf-8"))['esearchresult']
count = int(pubmed_ids['count'])

# get existed ids
used_ids = set()
query = ("SELECT pmid FROM pubmeddb.articles")
cursor.execute(query)
for used_id in cursor:
    used_ids.add(used_id[0])

while ret_cur + retmax < count:
    # normal loop
    print("crawling of {}-{} / {}".format(ret_cur, ret_cur+retmax, count))
    pubmed_ids_url = search_url(term, "journal", None, ret_cur, retmax)
    # pubmed_ids_url = search_url(term, None, None, ret_cur, retmax)
    pubmed_ids_req = requests.get(pubmed_ids_url)
    pubmed_ids = json.loads(pubmed_ids_req.content.decode("utf-8"))['esearchresult']
    ids_list = pubmed_ids['idlist']

    sum_list_req = requests.get(sum_urls(ids_list))
    sum_list = json.loads(sum_list_req.content.decode("utf-8"))['result']
    abs_list_req = requests.get(abstract_urls(ids_list))
    abs_list = abs_list_req.content.decode("utf-8").split("\n\n\n")

    new_arts = 0
    for idx in range(retmax):
        art_id = ids_list[idx]
        if art_id not in used_ids:
            new_arts += 1
            art_sum = sum_list[art_id]
            art_abs = abs_list[idx]
            article = Article()
            article.fill(art_id, art_sum, art_abs)
            article.put(cursor)
    # print("new articles: {}".format(new_arts))

    cnx.commit()
    ret_cur += retmax
    time.sleep(1)

cursor.close()
cnx.close()
