import json
import time
import requests

INPUT_FILE = "data/restaurants_hotels_enriched.json"
OUTPUT_FILE = "data/restaurants_hotels_geo.json"

session = requests.Session()

session.headers.update({
    "User-Agent": "360EatGuideMap/1.0"
})

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    entries = json.load(f)

results = []

for idx, item in enumerate(entries, start=1):

    print(
        f"[{idx}/{len(entries)}] {item['name']}"
    )

    query = f"{item['name']} {item['country']}"

    lat = None
    lon = None

    try:

        response = session.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "jsonv2",
                "limit": 1
            },
            timeout=60
        )

        data = response.json()

        if data:

            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])

        time.sleep(1)

    except Exception as ex:
        print(ex)

    item["lat"] = lat
    item["lon"] = lon

    results.append(item)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        indent=2,
        ensure_ascii=False
    )
