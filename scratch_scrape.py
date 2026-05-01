import urllib.request
import re
try:
    html = urllib.request.urlopen('http://spandh.dcs.shef.ac.uk/gridcorpus/').read().decode('utf-8')
    links = re.findall(r'href=["\'](.*?)["\']', html)
    for link in links:
        if 's1' in link:
            print('Link:', link)
except Exception as e:
    print(e)
