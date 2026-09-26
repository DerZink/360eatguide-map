import json
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://360eatguide.com/restaurants/"

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,"
        "application/xhtml+xml,"
        "application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.google.com/"
})


def get_page(url):
    response = session.get(
        url,
        timeout=60,
        allow_redirects=True
    )

    print(f"STATUS {response.status_code}: {url}")

    return response


def detect_page_count(html):
    soup = BeautifulSoup(html, "html.parser")

    max_page = 1

    for a in soup.select("a.page-numbers"):
        text = a.get_text(strip=True)

        if text.isdigit():
            max_page = max(
                max_page,
                int(text)
            )

    return max_page


# ---------- Erste Seite ----------
first_page = get_page(BASE_URL)

with open(
    "debug_page_1.html",
    "w",
    encoding="utf-8"
) as f:
    f.write(first_page.text)

page_count = detect_page_count(first_page.text)

print(f"Detected pages: {page_count}")

all_entries = []


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select(
        "tr.wp-block-j360-blocks-restaurant-list-row"
    )

    print(f"Rows found: {len(rows)}")

    results = []

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

        results.append({
            "name": name,
            "country": country,
            "category": category,
            "url": detail_url
        })

    return results


all_entries.extend(
    parse_page(first_page.text)
)

# ---------- Restliche Seiten ----------
for page in range(2, page_count + 1):

    url = f"{BASE_URL}?jpage={page}"

    try:

        response = get_page(url)

        with open(
            f"debug_page_{page}.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(response.text)

        if response.status_code == 200:

            all_entries.extend(
                parse_page(response.text)
            )

        else:
            print(
                f"Skipped page {page}"
            )

        time.sleep(2)

    except Exception as ex:
        print(
            f"ERROR page {page}: {ex}"
        )

# ---------- Duplikate entfernen ----------
unique = {}

for item in all_entries:
    unique[item["url"]] = item

final_data = list(
    unique.values()
)

final_data.sort(
    key=lambda x: x["name"].lower()
)

# ---------- JSON speichern ----------
with open(
    "data/restaurants_hotels.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_data,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print("=" * 60)
print("TOTAL ENTRIES:", len(final_data))
print("=" * 60)
