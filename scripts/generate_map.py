import json
import os

INPUT_FILE = "data/restaurants_hotels_geo.json"
OUTPUT_FILE = "docs/index.html"

os.makedirs("docs", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

markers = []

count = 0

for item in data:

    lat = item.get("lat")
    lon = item.get("lon")

    if lat is None or lon is None:
        continue

    color = (
        "red"
        if item.get("category") == "Hotel"
        else "blue"
    )

    popup = f"""
    <b>{item['name']}</b><br>
    {item['country']}<br>
    {item['category']}<br>
    <a href="{item['url']}" target="_blank">
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
        """
    )

    count += 1

html = f"""
<!DOCTYPE html>
<html lang="de">
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>360EatGuide Map</title>

<link
 rel="stylesheet"
 href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>

<style>

html,
body,
#map {{
    height:100%;
    margin:0;
}}

.info {{
    position:absolute;
    top:10px;
    left:10px;
    z-index:1000;
    background:white;
    padding:10px;
    border-radius:6px;
    box-shadow:0 0 5px rgba(0,0,0,.3);
}}

</style>

</head>

<body>

<div class="info">
<b>360EatGuide</b><br>
Marker: {count}
</div>

<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">\</script>

<script>

const map = L.map("map")
.setView([47.0, 8.0], 5);

L.tileLayer(
    "https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",
    {{
        attribution: "© OpenStreetMap"
    }}
).addTo(map);

{''.join(markers)}

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

print(f"Map created with {count} markers")
