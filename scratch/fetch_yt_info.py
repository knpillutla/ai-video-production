import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
url = 'https://www.youtube.com/watch?v=e57zGlr2h3U'
r = requests.get(url, headers=headers)

desc_match = re.search(r'"shortDescription":"(.*?)"', r.text)
if desc_match:
    desc = desc_match.group(1).encode('utf-8').decode('unicode_escape')
    print('=== DESCRIPTION ===')
    print(desc)

keywords_match = re.search(r'"keywords":(\[.*?\])', r.text)
if keywords_match:
    print('=== KEYWORDS ===')
    print(keywords_match.group(1))

# Check title
title_match = re.search(r'"title":"(.*?)"', r.text)
if title_match:
    print('=== TITLE ===')
    print(title_match.group(1))
