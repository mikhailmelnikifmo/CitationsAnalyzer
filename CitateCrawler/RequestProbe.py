__author__ = 'Mishanya'

import requests

api_key = 'b4ecc27393a3e69e638f5efe599787ab'

headers = dict()
headers['X-ELS-APIKey'] = api_key
headers['X-ELS-ResourceVersion'] = 'XOCS'

resource = 'https://api.elsevier.com/content/search/SCIDIR-OBJECT'
url = 'https://api.elsevier.com/content/search/SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)'

# requests
http_proxy = "http://proxy.ifmo.ru/proxy.pac"
proxy_dict = {"http": http_proxy}

request = requests.get(url, proxies=proxy_dict, headers=headers)
print(request.status_code)
print(request.content)