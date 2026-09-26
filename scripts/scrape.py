import json
import requests
from bs4 import BeautifulSoup

URL = "https://360eatguide.com/restaurants/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127.0 Safari/537.36"
}

print("Lade:", URL)

response = requests.get(URL, headers=headers, timeout=60)

print("Status Code:", response.status_code)
print("Content Length:", len(response.text))

# HTML speichern
with open("debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, "html.parser")

# Alle Links sammeln
links = []

for a in soup.find_all("a", href=True):
    links.append({
        "text": a.get_text(strip=True),
        "href": a["href"]
    })

# Links speichern
with open("debug_links.json", "w", encoding="utf-8") as f:
    json.dump(
        links,
        f,
        indent=2,
        ensure_ascii=False
    )

# Nur Restaurant-Links filtern
restaurant_links = []

for link in links:

    href = link["href"]

    if "/restaurants/" not in href:
        continue

    if href.endswith("/restaurants/"):
        continue

    restaurant_links.append(link)

with open(
    "data/restaurants_hotels.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        restaurant_links,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Gefundene Links:", len(restaurant_links))
