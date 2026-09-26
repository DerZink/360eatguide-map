import json

INPUT_FILE = "data/restaurants_hotels_geo.json"
OUTPUT_FILE = "docs/index.html"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

markers = []

for item in data:

    if item.get("lat") is None:
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
    {item['url']}
      Eintrag öffnen
    </a>
    """

    markers.append(
        f"""
        L.circleMarker(
            [{item['lat']}, {item['lon']}],
            {{
                color: '{color}',
                fillColor: '{color}',
                fillOpacity: 0.8,
                radius: 7
            }}
        )
        .addTo(map)
        .bindPopup({json.dumps(popup)});
        """
    )

html = f"""
<!DOCTYPE html>
<html lang="de">
<head>

<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

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

</style>

</head>

<body>

<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/script>

<script>

const map = L.map('map')
.setView([47.0,8.0],5);

L.tileLayer(
 'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
 {{
   attribution:'© OpenStreetMap'
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

print("Map created")
