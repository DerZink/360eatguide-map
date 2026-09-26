import json
import re
import time
import requests
from bs4 import BeautifulSoup

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
})

all_entries = []

for page in range(1, 7):

    if page == 1:
        url = "https://360eatguide.com/restaurants/"
    else:
        url = f"https://360eatguide.com/restaurants/?jpage={page}"

    print("=" * 50)
    print("SCRAPING:", url)

    try:
        response = session.get(
            url,
            timeout=60,
            allow_redirects=True
        )

        print("STATUS:", response.status_code)
        print("SIZE:", len(response.text))

        with open(
            f"debug_page_{page}.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(response.text)

        if response.status_code != 200:
            print(f"Page {page} blocked")
            continue

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        rows = soup.select(
            "tr.wp-block-j360-blocks-restaurant-list-row"
        )

        print("ROWS FOUND:", len(rows))

        for row in rows:

            onclick = row.get("onclick", "")

            match = re.search(
                r"window.location=.*?'(.*?)'",
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

        time.sleep(2)

    except Exception as e:
        print("ERROR:", e)

# Duplikate entfernen
unique = {}

for item in all_entries:
    unique[item["url"]] = item

all_entries = list(unique.values())

all_entries.sort(
    key=lambda x: x["name"].lower()
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

print()
print("TOTAL ENTRIES:", len(all_entries))
