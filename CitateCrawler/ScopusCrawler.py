__author__ = 'Mishanya'

import os
import json
import time
import requests
import threading

# topic = 'comp_science'
# topic = 'high performance computing'

""" choose your topic and year """
topic = 'medicine'
year = '2014-2018'

api_resource = "https://api.elsevier.com/content/search/scopus?"
# add_params = "&sort=citedby-count"
add_params = "&subj=MEDI"
# search_param = 'query=title-abs-key(' + topic + ')' + add_params
# search_param = "query=DOCTYPE(ab) AND PUBYEAR > 2014" + add_params #title-abs-key(' + topic + ')' + " AND
# search_param = "query=title(\'workflow scheduling\') AND AUTHLASTNAME(zvartau AND semakova)" #title-abs-key(' + topic + ')' + " AND
search_param = "query=DOI(10.1097/01.hjh.0000467353.66660.d4)" #title-abs-key(' + topic + ')' + " AND
json_dir = "./articles_json/" + topic + "/" + year + "/"

api_keys = ['3d9af39cf3b78b446bbe67f0ae9211e1',
            '084a711782598832418b7a32cb0cc238',
            'e92c7a096a234b90ee6464e6ec97a68f',
            '92df4c5e1cfb69791af53475ae5dc3f9',
            'a47f385551fac70f80924b0f2c1f60e6',
            '3867c342511ef26ab41bdb8e565539e3',
            'fbcca056906b509902273220b5709086',
            '139b98ffca1f8436d2a28e53e3f7563f',
            '88aff94a8084f9ee48df6789274b92f2',
            '66c7807f257afeaa816d193df9d90baf']

api_keys2 = ['9e51e3083f4405b0e8f428214d609274',
            '94af4543bfbf66b0fed37866f8f1fc90',
            '6a625406c8a4cd21b3eab2770a7ab344',
            '448d5deaeec6fd9633765d12c83853cf',
            'b9d8b56bccb7be24e9881bba9f923eb2',
            '4eed08cdfe43b6c131eedb32faa9cd67',
            'dee4d7135708c1d16c1eec57f3c3ef42',
            '86999368e9386ea73f6fc6fb9f8a2a33',
            'ede60b2419e3635c090a1f174edff09d',
            '351b595cc4dbcb05a8f4ff0cac383dba']


need_print = True

def articles_mining(page, file, headers):
    try:
        articles = page['search-results']['entry']

        start_time = time.clock()
        for article in articles:
            finish_time = time.clock()
            #print("Article time = " + str(finish_time - start_time))
            start_time = finish_time

            # Article data
            title = article['dc:title']
            try:
                cit_count = article['citedby-count']
                authors = article['dc:creator']
                date = article['prism:coverDate']
            except Exception:
                # print("WRONG ARTICLE!!!")
                continue

            article_url = article['prism:url'].replace("http", "https").replace(":80", "")
            # Find keywords of this article
            try:
                # print("Keywords started")
                # article_keywords = requests.get(article_url + "?field=authkeywords", headers=headers)
                article_keywords = requests.get(article_url + "?field=dc:description", headers=headers)
                article_keywords = json.loads(article_keywords.content.decode("utf-8"))
                keywords = [keyword['$'] for keyword in article_keywords['abstracts-retrieval-response']['authkeywords']['author-keyword']]
            except Exception:
                # print("Key words error")
                try:
                    if article_keywords['service-error']['status']['statusCode'] == 'QUOTA_EXCEEDED':
                        print("QUOTA EXCEEDED!!!")
                        break
                except Exception:
                    pass
                continue

            # Add keywords data
            article['keywords'] = keywords

            # Get citations
            citations_names = []
            if int(cit_count) > 0:
                try:
                    citations_response = requests.get(api_resource + 'query=refeid(' + str(article['eid']) + ')', headers=headers)
                    citations_result = json.loads(citations_response.content.decode("utf-8"))
                    citations = citations_result['search-results']['entry']
                    citations_names.extend([citation['dc:title'] for citation in citations])
                    next_cit_page = next_page(citations_result)
                    while next_cit_page is not None:
                        citations = citations_result['search-results']['entry']
                        citations_names.extend([citation['dc:title'] for citation in citations])
                        next_cit_page = next_page(next_cit_page)
                except Exception:
                    # print("citations error")
                    continue

            # Print current article data, if need
            if need_print:
                print("    Title = " + title)
                print("    Authors = " + authors)
                print("    Year = " + date)
                print("    Citations = " + str(cit_count))
                print("    Keywords = " + str(keywords))
                print("    Edges = " + str(citations_names))

            # Add citations into article json
            article['citations'] = citations_names

            # Write current json into file
            json.dump(article, file)
            file.write("\n")
            # print("article has been written")
            pass
        pass
    except Exception:
        print("no entry")

def next_page(page):
    links = page['search-results']['link']
    next = None
    for link in links:
        if link['@ref'] == 'next':
            next_url = link['@href'].replace("http", "https").replace(":80", "")
            next_req = requests.get(next_url + "?field=authkeywords", headers=headers)
            next = json.loads(next_req.content.decode("utf-8"))
            break
    return next

def range_crawling(api_key, start, count, index):
    print("Start crawling " + str(start) + " - " + str(start + count))

    file = open(os.path.join(json_dir, "articles" + str(start) + " - " + str(start + count)), 'w')

    max_pages = count / 25
    page_counter = 0

    headers = dict()
    headers['X-ELS-APIKey'] = api_key
    headers['X-ELS-ResourceVersion'] = 'XOCS'
    headers['Accept'] = 'application/json'

    while page_counter == 0 or page_counter < max_pages:
        # print("PAGE #" + str(page_counter))
        page_url = api_resource + search_param + "&date=" + year + "&start=" + str(start + 25 * page_counter)
        page_request = requests.get(page_url, headers=headers)
        current_page = json.loads(page_request.content.decode("utf-8"))
        articles_mining(current_page, file, headers)
        page_counter += 1

    file.close()
    pass

if __name__ == '__main__':
    total_time = time.clock()
    main_key = 'b4ecc27393a3e69e638f5efe599787ab'
    # Request' headers
    headers = dict()
    headers['X-ELS-APIKey'] = main_key
    headers['X-ELS-ResourceVersion'] = 'XOCS'
    headers['Accept'] = 'application/json'

    # Create files
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    first_url = api_resource + search_param + "&date=" + year
    print("First search started")
    response = requests.get(first_url, headers=headers)
    response_result = json.loads(response.content.decode("utf-8"))

    articles_count = int(response_result['search-results']['opensearch:totalResults'])
    articles_portion = 250

    portions_count = int(articles_count / articles_portion)
    if articles_count % articles_portion != 0:
        portions_count += 1

    thread_list = []
    for i in range(portions_count):
        start = i * articles_portion
        # range_crawling(api_keys2[0], start, articles_portion, i)
        thread = threading.Thread(target=range_crawling, args=((api_keys2 + api_keys)[i], start, articles_portion, i))
        thread.start()
        thread_list.append(thread)

    for thr in thread_list:
       thr.join()

    print("FINISH time=" + str(time.clock() - total_time))