import osmnx as ox
import networkx as nx
import csv

def load_ward_data():
    """Census CSV se real population load karo"""
    zones = {}
    COORDS = {
        "Hazratganj":   (26.8546, 80.9387),
        "Aminabad":     (26.8487, 80.9280),
        "Gomti Nagar":  (26.8529, 80.9948),
        "Alambagh":     (26.8200, 80.9200),
        "Chowk":        (26.8590, 80.9200),
        "Aliganj":      (26.8870, 80.9630),
        "Indira Nagar": (26.8710, 80.9990),
        "Rajajipuram":  (26.8300, 80.9000),
    }

    with open("data/lucknow_wards.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Key strip karo — spaces ya hidden chars remove honge
            row = {(k.strip() if k else""): (v.strip() if v else"") 
                   for k, v in row.items()
                }
            name = row["zone"]
            zones[name] = {
                "pop":      int(row["population"]),
                "area":     float(row["area_sqkm"]),
                "density":  int(row["density_per_sqkm"]),
                "wards":    row["ward_nos"],
                "mobility": round(int(row["density_per_sqkm"]) / 2500, 1),
                "coords":   COORDS.get(name, (26.8467, 80.9462))
            }
    return zones

def load_hospital_data():
    """NHP + Google Maps hospital data load karo"""
    hospitals = {}
    with open("data/lucknow_hospitals.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            zone = row["zone"]
            if zone not in hospitals:
                hospitals[zone] = []
            hospitals[zone].append({
                "name":     row["name"],
                "lat":      float(row["lat"]),
                "lon":      float(row["lon"]),
                "type":     row["type"],
                "beds":     int(row["beds"]),
                "icu_beds": int(row["icu_beds"]),
                "source":   row["source"],
            })
    return hospitals

def run_mobility_agent(state):
    print("\n[Agent 1] Loading Census 2011 ward data...")
    zones = load_ward_data()
    hospitals = load_hospital_data()

    print(f"[Agent 1] {len(zones)} zones loaded from Census 2011")
    for z, d in zones.items():
        total_beds = sum(h["beds"] for h in hospitals.get(z, []))
        print(f"  {z}: pop={d['pop']:,} | density={d['density']:,}/km² | hospitals_beds={total_beds}")

    print("\n[Agent 1] Loading real Lucknow street network...")
    G_streets = ox.load_graphml("data/lucknow.graphml")
    print(f"[Agent 1] Street network: {len(G_streets.nodes)} nodes, {len(G_streets.edges)} edges")

    # Zone contact graph banao
    G_zones = nx.Graph()
    for zone, data in zones.items():
        nearest = ox.distance.nearest_nodes(
            G_streets,
            data["coords"][1],
            data["coords"][0]
        )
        G_zones.add_node(zone,
            pop=data["pop"],
            mobility=min(9.0, data["mobility"]),
            coords=data["coords"],
            density=data["density"],
            hospitals=hospitals.get(zone, []),
            street_node=nearest
        )

    # Real road distances
    print("[Agent 1] Calculating real road distances...")
    zones_list = list(zones.keys())
    for i in range(len(zones_list)):
        for j in range(i + 1, len(zones_list)):
            za, zb = zones_list[i], zones_list[j]
            na = G_zones.nodes[za]["street_node"]
            nb = G_zones.nodes[zb]["street_node"]
            try:
                dist = nx.shortest_path_length(G_streets, na, nb, weight="length")
                if dist < 8000:
                    ma = G_zones.nodes[za]["mobility"]
                    mb = G_zones.nodes[zb]["mobility"]
                    weight = round((ma + mb) / 2 * (1 - dist / 8000), 2)
                    G_zones.add_edge(za, zb, weight=max(0.1, weight), distance_m=int(dist))
            except:
                pass

    state.contact_graph = G_zones
    state.zone_risks = {z: G_zones.nodes[z]["mobility"] for z in G_zones.nodes}
    state.hospitals = hospitals

    print(f"[Agent 1] Done — {len(G_zones.edges)} real road connections")
    return state