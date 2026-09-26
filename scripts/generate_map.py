import json

with open(
    "data/restaurants_hotels_geo.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for item in data:

    if item["lat"] is None:
        continue

    geojson["features"].append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [
                item["lon"],
                item["lat"]
            ]
        },
        "properties": {
            "name": item["name"],
            "country": item["country"],
            "category": item["category"],
            "url": item["url"]
        }
    })

with open(
    "data/restaurants_hotels_geojson.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        geojson,
        f,
        ensure_ascii=False
    )
