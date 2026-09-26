import json
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://360eatguide.com"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

entries = []
visited_pages = set()
visited_detail_urls = set()

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_detail(url):
    print("  Detail:", url)

    try:
        html = session.get(url, timeout=30).text
        soup = BeautifulSoup(html, "html.parser")

        title = ""

        h1 = soup.find("h1")
        if h1:
            title = clean(h1.get_text())

        text = clean(soup.get_text(" "))

        country = ""
        category = ""

        countries = [
            "Austria","Belgium","Denmark","Estonia","Finland",
            "France","Germany","Italy","Netherlands","Norway",
            "Portugal","Spain","Sweden","Switzerland",
            "United Kingdom"
        ]

        for c in countries:
            if c in text:
                country = c
                break

        if "Hotel" in text:
            category = "Hotel"

        if "Restaurant" in text:
            category = "Restaurant"

        return {
            "name": title,
            "category": category,
            "country": country,
            "url": url
        }

    except Exception as ex:
        print(ex)
        return None


next_page = f"{BASE_URL}/restaurants/"

while next_page:

    if next_page in visited_pages:
        break

    visited_pages.add(next_page)

    print("Page:", next_page)

    html = session.get(next_page).text
    soup = BeautifulSoup(html, "html.parser")

    for link in soup.find_all("a", href=True):

        href = link["href"]

        if "/restaurants/" not in href:
            continue

        full_url = urljoin(BASE_URL, href)

        if full_url.endswith("/restaurants/"):
            continue

        if full_url in visited_detail_urls:
            continue

        visited_detail_urls.add(full_url)

        item = scrape_detail(full_url)

        if item:
            entries.append(item)

        time.sleep(0.5)

    next_link = None

    for a in soup.find_all("a", href=True):

        label = clean(a.get_text()).lower()

        if "next" in label:
            next_link = urljoin(BASE_URL, a["href"])
            break

    next_page = next_link

with open(
    "data/restaurants_hotels.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        sorted(entries, key=lambda x: x["name"]),
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Gespeichert: {len(entries)} Einträge")
