import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://360eatguide.com"
START_URL = f"{BASE_URL}/restaurants/"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

results = []
visited = set()

url = START_URL

while url and url not in visited:
    print("Scraping", url)

    visited.add(url)

    html = session.get(url, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")

    cards = soup.select("a[href*='/restaurants/']")

    for card in cards:
        href = card.get("href")
        text = card.get_text(" ", strip=True)

        if not href:
            continue

        if "/restaurants/" not in href:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url.endswith("/restaurants/"):
            continue

        results.append({
            "name": text,
            "url": full_url
        })

    next_link = None

    for a in soup.select("a"):
        label = a.get_text(" ", strip=True).lower()

        if "next" in label or "older" in label:
            next_link = urljoin(BASE_URL, a["href"])
            break

    url = next_link
    time.sleep(1)

# Duplikate entfernen
unique = {}

for item in results:
    unique[item["url"]] = item

results = list(unique.values())

results.sort(key=lambda x: x["name"])

with open("data/restaurants_hotels.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"{len(results)} entries written")
