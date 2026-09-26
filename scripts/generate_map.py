import json
import os

INPUT_FILE = "data/restaurants_hotels_geo.json"
OUTPUT_FILE = "docs/index.html"

os.makedirs("docs", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

markers = []

total_entries = len(data)
mapped_entries = 0
missing_entries = 0

for item in data:

    lat = item.get("lat")
    lon = item.get("lon")

    if lat is None or lon is None:
        missing_entries += 1
        continue

    color = (
        "red"
        if item.get("category") == "Hotel"
        else "blue"
    )

    popup = f"""
    <b>{item['name']}</b><br>
    {item.get('country', '')}<br>
    {item.get('category', '')}<br><br>
    {item['url']}
        Eintrag öffnen
    </a>
    """

    markers.append(
        f"""
        L.circleMarker(
            [{lat}, {lon}],
            {{
                color: "{color}",
                fillColor: "{color}",
                fillOpacity: 0.8,
                radius: 7
            }}
        )
        .addTo(map)
        .bindPopup({json.dumps(popup)});

        bounds.push([{lat}, {lon}]);
        """
    )

    mapped_entries += 1

html = f"""
<!DOCTYPE html>
<html lang="de">
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>360°Eat Guide Map</title>

<link rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<style>

html,
body,
#map {{
    height: 100%;
    margin: 0;
}}

.info {{
    position: absolute;
    top: 10px;
    right: 10px;

    z-index: 1000;

    background: white;

    padding: 12px;

    border-radius: 8px;

    box-shadow: 0 0 10px rgba(0,0,0,.25);

    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;

    min-width: 220px;
}}

.info hr {{
    margin: 8px 0;
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 5px;
}}

.legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
}}

.restaurant {{
    background: blue;
}}

.hotel {{
    background: red;
}}

</style>

</head>

<body>

<div class="info">

    <b>360°Eat Guide</b><br>

    Datensätze: {total_entries}<br>
    Kartiert: {mapped_entries}<br>
    Ohne Koordinaten: {missing_entries}

    <hr>

    <div class="legend-item">
        <span class="legend-dot restaurant"></span>
        Restaurant
    </div>

    <div class="legend-item">
        <span class="legend-dot hotel"></span>
        Hotel
    </div>

</div>

<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">\</script>

<script>

const map = L.map("map");

const bounds = [];

L.tileLayer(
    "https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",
    {{
        attribution: "© OpenStreetMap"
    }}
).addTo(map);

{''.join(markers)}

if (bounds.length > 0) {{
    map.fitBounds(bounds);
}} else {{
    map.setView([47.0, 8.0], 5);
}}

</script>

</body>
</html>
"""

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    f.write(html)

print()
print("=" * 50)
print(f"Total datasets: {total_entries}")
print(f"Mapped: {mapped_entries}")
print(f"Missing coordinates: {missing_entries}")
print("=" * 50)
print("Map created")
