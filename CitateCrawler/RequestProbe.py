__author__ = 'Mishanya'

import urllib3

#from urllib.request import Request, urlopen
"""
q = Request('http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)')
q.add_header('X-ELS-APIKey', 'b4ecc27393a3e69e638f5efe599787ab')
q.add_header('X-ELS-ResourceVersion', 'XOCS')
q.add_header('Accept', 'text/xml')
a = urlopen(q).read()
"""
http = urllib3.PoolManager()

headers = urllib3.make_headers({'X-ELS-APIKey': 'b4ecc27393a3e69e638f5efe599787ab', 'X-ELS-ResourceVersion': 'XOCS', 'Accept': 'text/xml'})
req = http.request('GET', 'http://api.elsevier.com/content/search/index:SCIDIR-OBJECT?query=DOI(10.1016/j.bbabio.2008.10.005)', headers=headers)
print(req.status)
print(req)
