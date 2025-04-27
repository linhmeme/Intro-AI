import json
import pickle
import networkx as nx
import numpy as np
from geopy.distance import geodesic
from scipy.spatial import KDTree
from pathlib import Path

ROADS_PATH = Path("data/geojson/roads.geojson")
GRAPH_PATH = Path("data/graph/graph_data.pkl")
# NODES_PATH = Path("data/geojson/nodes.geojson")

def calculate_distance(lat1, lon1, lat2, lon2):#distance between two nearest nodes
    return geodesic((lat1, lon1), (lat2, lon2)).meters

def build_graph_from_geojson(geojson_file, snap_threshold=1):
    with open(geojson_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    coord_list = []#List to store coordinates of nodes
    coord_to_node = {}#Helps map coordinates to nodes when adding edges.
    tree = None

    def find_or_add_node(coord):
        nonlocal coord_list, coord_to_node, tree

        # Đổi thứ tự thành (lat, lon) để dùng geodesic
        lat, lon = coord[1], coord[0]

        if tree is not None and len(coord_list) > 0:
            # Tìm điểm gần nhất theo KDTree (vẫn là [lon, lat])
            dist_deg, idx = tree.query([lon, lat], distance_upper_bound=0.00015)  # Đơn vị là degrees

            if dist_deg != float("inf") and idx < len(coord_list):
                snapped_coord = coord_list[idx]
                snapped_lat, snapped_lon = snapped_coord[1], snapped_coord[0]

                # Tính khoảng cách thực tế theo mét
                dist_m = geodesic((lat, lon), (snapped_lat, snapped_lon)).meters

                if dist_m < snap_threshold:
                    return tuple(snapped_coord)

        # Thêm node mới  # Đảo lại [lat, lon] để KDTree hiểu đúng
        coord_list.append(coord)
        coord_to_node[tuple(coord)] = tuple(coord)   # lưu node theo (lon, lat)

        # Cập nhật lại KDTree
        if len(coord_list) > 1:
            tree = KDTree(coord_list)

        return tuple(coord)

    print(f"Đang xử lý {len(data['features'])} feature từ GeoJSON")
    for feature in data["features"]:
        geometry = feature.get("geometry", {})
        coords_list = []

        if geometry["type"] == "LineString":
            coords_list = [geometry["coordinates"]]

        elif geometry["type"] == "MultiLineString":
            coords_list = geometry["coordinates"]

        else:
            print("Không hỗ trợ geometry:", geometry["type"])
            continue

        for line in coords_list:
            for i in range(len(line) - 1):
                x1, y1 = line[i]
                x2, y2 = line[i + 1]

                node1 = find_or_add_node([x1, y1])
                node2 = find_or_add_node([x2, y2])

                G.add_node(node1, x=node1[0], y=node1[1])
                G.add_node(node2, x=node2[0], y=node2[1])

                dist = geodesic((node1[1], node1[0]), (node2[1], node2[0])).meters

                G.add_edge(node1, node2, length=dist)

    return G

def save_graph(G, output_file):
    with open(output_file, "wb") as f:
        pickle.dump(G, f)
        print(f"Saved graph with {len(G.nodes)} nodes, {len(G.edges)} edges → {output_file}")

# def save_nodes_to_geojson(G, output_file):
#     features = []
#     for node in G.nodes:
#         lon, lat = node
#         feature = {
#             "type": "Feature",
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [lon, lat]
#             },
#             "properties": {}
#         }
#         features.append(feature)

#     geojson = {
#         "type": "FeatureCollection",
#         "features": features
#     }

#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(geojson, f, ensure_ascii=False, indent=2)
#         print(f"Saved {len(features)} nodes to {output_file}")

def load_graph(pkl_file):
    with open(pkl_file, "rb") as f:
        return pickle.load(f)

def get_nearest_node(G, lat, lon):
    min_dist = float("inf")
    nearest_node = None

    for node in G.nodes:
        node_lon, node_lat = node  # node là (x, y) = (lon, lat)
        dist = geodesic((lat, lon), (node_lat, node_lon)).meters
        if dist < min_dist:
            min_dist = dist
            nearest_node = node

    return nearest_node

G = build_graph_from_geojson(ROADS_PATH)
GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
save_graph(G, GRAPH_PATH)
# save_nodes_to_geojson(G, NODES_PATH)