import osmnx as ox
import folium
import json
import csv

ZONE_COORDS = {
    "Hazratganj":   (26.8546, 80.9387),
    "Aminabad":     (26.8487, 80.9280),
    "Gomti Nagar":  (26.8529, 80.9948),
    "Alambagh":     (26.8200, 80.9200),
    "Chowk":        (26.8590, 80.9200),
    "Aliganj":      (26.8870, 80.9630),
    "Indira Nagar": (26.8710, 80.9990),
    "Rajajipuram":  (26.8300, 80.9000),
}

COLORS = {"red": "#FF4444", "orange": "#FF9900", "yellow": "#FFD700"}

def generate_map(state=None):
    # Report load karo
    with open("output/report.json", "r", encoding="utf-8") as f:
        report = json.load(f)

    print("Loading real Lucknow street network...")
    G = ox.load_graphml("data/lucknow.graphml")

    m = folium.Map(location=[26.8467, 80.9462], zoom_start=13,
                   tiles="CartoDB positron")

    # Real streets draw karo
    print("Drawing real streets...")
    nodes, edges = ox.graph_to_gdfs(G)
    for _, edge in edges.iterrows():
        if edge.geometry is not None:
            coords = [(lat, lon) for lon, lat in edge.geometry.coords]
            folium.PolyLine(
                coords,
                color="#AAAAAA",
                weight=0.8,
                opacity=0.4
            ).add_to(m)

    # Zones add karo
    print("Adding zones to map...")
    for zone in report["containment_zones"]:
        name   = zone["name"]
        level  = zone["level"]
        coords = ZONE_COORDS.get(name)
        if not coords:
            continue

        color = COLORS.get(level, "#888888")
        emoji = "🔴" if level=="red" else "🟠" if level=="orange" else "🟡"

        popup_html = f"""
        <div style='font-family:Arial;min-width:200px'>
            <h4 style='color:{color};margin:0 0 6px'>{emoji} {name}</h4>
            <b>Level: {level.upper()}</b><br><br>
            <b>Restrictions:</b><br>
            {'<br>'.join(['• ' + r for r in zone['restrictions']])}
            <br><br>
            <b>Testing Centers:</b> {zone['testing_centers']}<br>
            <b>Reason:</b> {zone['reason']}
        </div>
        """

        folium.CircleMarker(
            location=list(coords),
            radius=40,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.45,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{emoji} {name} — {level.upper()}"
        ).add_to(m)

        folium.Marker(
            location=[coords[0], coords[1]],
            icon=folium.DivIcon(
                html=f'<div style="font-size:11px;font-weight:bold;'
                     f'color:{color};text-shadow:1px 1px white;">{name}</div>',
                icon_size=(120, 20),
                icon_anchor=(60, 10)
            )
        ).add_to(m)

    # Resources
    if report.get("resource_plan"):
        for zone_name, res in report["resource_plan"].items():
            coords = ZONE_COORDS.get(zone_name)
            if coords:
                folium.Marker(
                    location=[coords[0] + 0.004, coords[1]],
                    icon=folium.DivIcon(
                        html=f"""<div style='font-size:10px;background:white;
                        border:1px solid #ccc;padding:2px 6px;
                        border-radius:4px;white-space:nowrap;
                        box-shadow:1px 1px 3px rgba(0,0,0,0.2)'>
                        👨‍⚕️{res['doctors']} 
                        🧪{res['testing_kits']} 
                        🚑{res['ambulances']}
                        </div>""",
                        icon_size=(140, 25),
                        icon_anchor=(70, 12)
                    )
                ).add_to(m)

    # Hospitals
    print("Adding hospitals to map...")
    with open("data/lucknow_hospitals.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for h in reader:
            color = "red" if h["type"] == "Government" else "blue"
            folium.Marker(
                location=[float(h["lat"]), float(h["lon"])],
                popup=folium.Popup(
                    f"<b>{h['name']}</b><br>"
                    f"Type: {h['type']}<br>"
                    f"Beds: {h['beds']}<br>"
                    f"ICU: {h['icu_beds']}<br>"
                    f"Source: {h['source']}",
                    max_width=200
                ),
                tooltip=f"🏥 {h['name']}",
                icon=folium.Icon(color=color, icon="plus", prefix="fa")
            ).add_to(m)

    # Immediate actions
    if report.get("immediate_actions"):
        actions_html = "<b>⚡ Immediate Actions:</b><br>" + \
                      "<br>".join(["• " + a for a in report["immediate_actions"]])
        folium.Marker(
            location=[26.920, 80.940],
            icon=folium.DivIcon(
                html=f"""<div style='background:white;border:2px solid red;
                padding:8px;border-radius:6px;max-width:220px;
                font-size:11px;box-shadow:2px 2px 5px rgba(0,0,0,0.3)'>
                {actions_html}</div>""",
                icon_size=(230, 120),
                icon_anchor=(115, 60)
            )
        ).add_to(m)

    m.save("output/lucknow_map.html")
    print("✅ Map saved!")

if __name__ == "__main__":
    generate_map()