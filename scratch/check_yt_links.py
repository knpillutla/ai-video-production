import urllib.request
import re

links = [
    "https://www.youtube.com/watch?v=snhZRt2awgA",
    "https://www.youtube.com/watch?v=q__EtjKCnK4"
]

for url in links:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        title_match = re.search(r'<title>(.*?)</title>', html)
        t = title_match.group(1) if title_match else 'Unknown'
        print(f"URL: {url}")
        print(f"TITLE: {t.encode('ascii', 'replace').decode()}")
        
        desc_match = re.search(r'"shortDescription":"(.*?)"', html)
        if desc_match:
            print(f"DESC: {desc_match.group(1)[:200]}...")
        print("-" * 50)
    except Exception as e:
        print(f"Error {url}: {e}")
