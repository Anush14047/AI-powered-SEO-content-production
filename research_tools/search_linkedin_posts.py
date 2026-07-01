import re
import sys

import requests


for query in sys.argv[1:]:
    url = "https://www.bing.com/search?q=" + requests.utils.quote(query)
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    print("QUERY", query, response.status_code, len(response.text))
    links = re.findall(r"https://www\.linkedin\.com/posts/[^\"&<> ]+", response.text)
    for link in sorted(set(links))[:10]:
        print(link)
