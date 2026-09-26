import json
import time
import re
import requests

INPUT_FILE = "data/restaurants_hotels_enriched.json"
OUTPUT_FILE = "data/restaurants_hotels_geo.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

session = requests.Session()

session.headers.update({
    "User-Agent": "360EatGuideMap"
})

results = []


def clean_words(text):
    words = re.findall(r"\w+", text)

    words = [
        w for w in words
        if len(w) > 2
    ]

    return words


def geocode(query):

    r = session.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": query,
            "format": "jsonv2",
            "limit": 1
        },
        timeout=60
    )

    data = r.json()

    if data:
        return data[0]

    return None


for idx, item in enumerate(data, start=1):

    print(
        f"[{idx}/{len(data)}] {item['name']}"
    )

    lat = None
    lon = None

    used_query = None
    display_name = None

    search_variants = []

    # Variante 1
    search_variants.append(
        f"{item['name']} {item['country']}"
    )

    # Variante 2
    search_variants.append(
        f"{item['name']} "
        f"{item.get('category','')} "
        f"{item['country']}"
    )

    # Variante 3
    words = clean_words(item["name"])

    if words:

        search_variants.append(
            " ".join(words[:2])
            + " "
            + item["country"]
        )

        search_variants.append(
            words[0]
            + " "
            + item["country"]
        )

    # Variante 4
    try:

        slug = (
            item["url"]
            .rstrip("/")
            .split("/")[-1]
            .replace("-", " ")
        )

        search_variants.append(
            slug
            + " "
            + item["country"]
        )

    except Exception:
        pass

    hit = None

    for query in search_variants:

        try:

            hit = geocode(query)

            if hit:

                used_query = query

                display_name = hit.get(
                    "display_name"
                )

                lat = float(hit["lat"])
                lon = float(hit["lon"])

                break

            time.sleep(1)

        except Exception as ex:

            print(ex)

    item["lat"] = lat
    item["lon"] = lon

    item["geocode_query"] = used_query
    item["geocode_display_name"] = display_name

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

# Analyse fehlgeschlagener Treffer

failed = [
    x for x in results
    if x["lat"] is None
]

with open(
    "data/geocode_failed.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        failed,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print("=" * 60)
print("TOTAL:", len(results))
print("SUCCESS:", len(results) - len(failed))
print("FAILED:", len(failed))
print("=" * 60)
