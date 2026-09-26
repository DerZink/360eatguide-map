import json
import re
import time
import requests
from bs4 import BeautifulSoup

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
})

url = "https://360eatguide.com/restaurants/"

response = session.get(
    url,
    timeout=60,
    allow_redirects=True
)

print("STATUS:", response.status_code)

with open("debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)

if response.status_code != 200:
    print("ERROR PAGE SAVED")
    exit(1)
