import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_URL = "https://360eatguide.com"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT = DATA_DIR / "locations.json"

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0 Safari/537.36"
}


# -----------------------------
# Session mit Retry
# -----------------------------

session = requests.Session()

retry = Retry(
    total=5,
    connect=5,
    read=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
)

session.mount("https://", HTTPAdapter(max_retries=retry))
session.mount("http://", HTTPAdapter(max_retries=retry))

session.headers.update(HEADERS)


# -----------------------------
# Geocoding Cache
# -----------------------------

CACHE_FILE = DATA_DIR / "geocode_cache.json"

if CACHE_FILE.exists():
    geocode_cache = json.loads(
        CACHE_FILE.read_text(encoding="utf-8")
    )
else:
    geocode_cache = {}


def save_cache():
    CACHE_FILE.write_text(
        json.dumps(
            geocode_cache,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# -----------------------------
# Nominatim Geocoder
# -----------------------------

def geocode(query):

    if not query:
        return None, None

    if query in geocode_cache:
        return (
            geocode_cache[query]["lat"],
            geocode_cache[query]["lng"]
        )

    print("Geocoding:", query)

    try:
        r = session.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": HEADERS["User-Agent"]
            },
            timeout=30
        )

        data = r.json()

        if data:

            lat = float(data[0]["lat"])
            lng = float(data[0]["lon"])

            geocode_cache[query] = {
                "lat": lat,
                "lng": lng
            }

            save_cache()

            time.sleep(1)

            return lat, lng

    except Exception as e:
        print("Geocode error:", e)

    return None, None


# -----------------------------
# Listen scrape
# -----------------------------

def scrape_list_pages():

    results = []

    for page in range(1, 7):

        if page == 1:
            url = f"{BASE_URL}/restaurants/"
        else:
            url = f"{BASE_URL}/restaurants/?jpage={page}"

        print("LIST:", url)

        html = session.get(
            url,
            timeout=30
        ).text

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select(
            "tr.wp-block-j360-blocks-restaurant-list-row"
        )

        for row in rows:

            onclick = row.get("onclick", "")

            match = re.search(
                r"'(https://[^']+)'",
                onclick
            )

            if not match:
                continue

            entry_url = match.group(1)

            cols = row.find_all("td")

            if len(cols) < 3:
                continue

            name = cols[0].get_text(
                " ",
                strip=True
            )

            country = cols[1].get_text(
                " ",
                strip=True
