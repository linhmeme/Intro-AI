import osmnx as ox

place_name = "Thịnh Quang, Đống Đa, Hà Nội, Việt Nam"

def load_graph():
    G = ox.graph_from_place(place_name, network_type="walk")
    hwy_speeds = {
        "motorway": 90, "trunk": 80, "primary": 60,
        "secondary": 50, "tertiary": 40, "unclassified": 30,
        "residential": 20, "footway": 5
    }
    G = ox.add_edge_speeds(G, hwy_speeds=hwy_speeds, fallback=30)
    G = ox.add_edge_travel_times(G)
    return G

G = load_graph()

def get_boundary():
    boundary = ox.geocode_to_gdf(place_name)
    return list(boundary.geometry.iloc[0].exterior.coords)