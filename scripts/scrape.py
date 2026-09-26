import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://360eatguide.com/restaurants/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

all_entries = []

for page in range(1, 7):

    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?jpage={page}"

    print(f"Scraping: {url}")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = soup.select(
        "tr.wp-block-j360-blocks-restaurant-list-row"
    )

    print(f"Rows found: {len(rows)}")

    for row in rows:

        onclick = row.get("onclick", "")

        match = re.search(
            r"window\\.location=.*?'(.*?)'",
            onclick
        )

        if not match:
            continue

        detail_url = match.group(1)

        cells = row.find_all("td")

        if len(cells) < 3:
            continue

        name = cells[0].get_text(
            " ",
            strip=True
        )

        country = cells[1].get_text(
            " ",
            strip=True
        )

        category = cells[2].get_text(
            " ",
            strip=True
        )

        all_entries.append({
            "name": name,
            "country": country,
            "category": category,
            "url": detail_url
        })

print(
    f"Total entries: {len(all_entries)}"
)

with open(
    "data/restaurants_hotels.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_entries,
        f,
        indent=2,
        ensure_ascii=False
    )
