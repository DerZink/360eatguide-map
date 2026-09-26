import json
import time
import requests

INPUT_FILE = "data/restaurants_hotels_enriched.json"
OUTPUT_FILE = "data/restaurants_hotels_geo.json"

with open(INPUT_FILE,"r",encoding="utf-8") as f:
    data = json.load(f)

session = requests.Session()

session.headers.update({
    "User-Agent":"360EatGuideMap"
})

results = []

for item in data:

    query = (
        f"{item['name']} "
        f"{item['country']}"
    )

    lat = None
    lon = None

    try:

        r = session.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format":"jsonv2",
                "limit":1
            },
            timeout=30
        )

        hits = r.json()

        if hits:

            lat = float(hits[0]["lat"])
            lon = float(hits[0]["lon"])

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
