import json
import re
import time
import requests
from bs4 import BeautifulSoup

INPUT_FILE = "data/restaurants_hotels.json"
OUTPUT_FILE = "data/restaurants_hotels_enriched.json"

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    )
})

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    entries = json.load(f)

enriched = []

for idx, item in enumerate(entries, start=1):

    print(
        f"[{idx}/{len(entries)}] {item['name']}"
    )

    try:

        response = session.get(
            item["url"],
            timeout=60
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        text_blocks = []

        for p in soup.find_all("p"):

            txt = p.get_text(
                " ",
                strip=True
            )

            if len(txt) > 40:
                text_blocks.append(txt)

        description = " ".join(
            text_blocks[:8]
        )

        image = ""

        meta_image = soup.find(
            "meta",
            property="og:image"
        )

        if meta_image:
            image = meta_image.get(
                "content",
                ""
            )

        enriched.append({
            "name": item["name"],
            "country": item["country"],
            "category": item["category"],
            "url": item["url"],
            "description": description,
            "image": image,
            "address": "",
            "city": "",
            "lat": None,
            "lon": None
        })

        if idx % 10 == 0:

            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    enriched,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        time.sleep(1)

    except Exception as ex:

        print(ex)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        enriched,
        f,
        indent=2,
        ensure_ascii=False
    )

print(
    f"Saved {len(enriched)} records"
)
