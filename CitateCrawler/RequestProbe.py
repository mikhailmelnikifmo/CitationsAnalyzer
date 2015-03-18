__author__ = 'Mishanya'

"""
from urllib.request import Request, urlopen

q = Request('http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)')
q.add_header('X-ELS-APIKey', 'b4ecc27393a3e69e638f5efe599787ab')
q.add_header('X-ELS-ResourceVersion', 'XOCS')
q.add_header('Accept', 'text/xml')
a = urlopen(q).read()
"""

import urllib3
import requests

itmo_proxy = True  # If need ITMO proxy, change to true

if (itmo_proxy):
    http = urllib3.ProxyManager('http://proxy.ifmo.ru/proxy.pac')
else:
    http = urllib3.PoolManager()

api_key = 'b4ecc27393a3e69e638f5efe599787ab'
res_version = 'XOCS'
accept = 'text/xml'
#headers_set = urllib3.make_headers({'X-ELS-APIKey': api_key, 'X-ELS-ResourceVersion': res_version, 'Accept': accept})

http.headers['X-ELS-APIKey'] = api_key
http.headers['X-ELS-ResourceVersion'] = res_version
http.headers['Accept'] = accept
url = 'http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)'
url2 = 'http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=heart'

#http.proxy_headers['X-ELS-APIKey'] = api_key
#http.proxy_headers['X-ELS-ResourceVersion'] = res_version
#http.proxy_headers['Accept'] = accept

#req = http.request('GET', 'http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)', headers=headers_set)
req = http.request('GET', url2)
print(req.status)
print(req)


# requests
http_proxy = "http://proxy.ifmo.ru/proxy.pac"
proxy_dict = {"http": http_proxy}
request = requests.get(url2, proxies=proxy_dict, headers=http.headers)
print(request.status_code)