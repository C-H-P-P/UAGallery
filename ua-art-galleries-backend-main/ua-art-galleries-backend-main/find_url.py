import urllib.request
import re

html = urllib.request.urlopen('https://uagalleries.vercel.app/').read().decode('utf-8')
js_files = re.findall(r'src="(/assets/[^"]+\.js)"', html)

for js_file in js_files:
    js_url = 'https://uagalleries.vercel.app' + js_file
    js_content = urllib.request.urlopen(js_url).read().decode('utf-8')
    match = re.search(r'https://[^\"\']*\.onrender\.com', js_content)
    if match:
        print('FOUND BACKEND URL:', match.group(0))
        break
