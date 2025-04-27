import json
import pickle
import networkx as nx
import numpy as np
from geopy.distance import geodesic
from scipy.spatial import KDTree
from pathlib import Path

GEOJSON_PATH = Path("data/geojson/roads.geojson")
GRAPH_PATH = Path("data/graph/graph_data.pkl")

def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters

def build_graph_from_geojson(geojson_file, snap_threshold=3):  # ✅ (1) Sửa: tăng snap_threshold mặc định từ 1m → 3m
    with open(geojson_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()

    coord_list = []
    coord_to_node = {}
    tree = None

    def find_or_add_node(coord):
        nonlocal coord_list, coord_to_node, tree

        lat, lon = coord[1], coord[0]

        if tree is not None and len(coord_list) > 0:
            dist_deg, idx = tree.query([lon, lat], distance_upper_bound=0.00015)

            if dist_deg != float("inf") and idx < len(coord_list):
                snapped_coord = coord_list[idx]
                snapped_lat, snapped_lon = snapped_coord[1], snapped_coord[0]

                dist_m = geodesic((lat, lon), (snapped_lat, snapped_lon)).meters

                if dist_m < snap_threshold:
                    return tuple(snapped_coord)

        coord_list.append(coord)
        coord_to_node[tuple(coord)] = tuple(coord)

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
                G.add_edge(node2, node1, length=dist)  # ✅ (2) Sửa: thêm chiều ngược lại để graph đi được 2 chiều

    return G


def save_graph(G, output_file):
    with open(output_file, "wb") as f:
        pickle.dump(G, f)
        print(f"Saved graph with {len(G.nodes)} nodes, {len(G.edges)} edges → {output_file}")

def load_graph(pkl_file):
    with open(pkl_file, "rb") as f:
        return pickle.load(f)

def get_nearest_node(G, lat, lon, direction_check=False, goal_lat=None, goal_lon=None):
    """
    - Nếu direction_check = False: tìm node gần nhất bình thường.
    - Nếu direction_check = True: chỉ tìm node có hướng ra hợp với hướng đến goal.
    """
    min_dist = float("inf")
    nearest_node = None

    for node in G.nodes:
        node_lon, node_lat = node

        dist = geodesic((lat, lon), (node_lat, node_lon)).meters

        if direction_check and goal_lat is not None and goal_lon is not None:
            # Kiểm tra hướng di chuyển
            angle_from_here = np.arctan2(goal_lat - node_lat, goal_lon - node_lon)
            found_direction = False

            for succ in G.successors(node):
                succ_lon, succ_lat = succ
                angle_to_succ = np.arctan2(succ_lat - node_lat, succ_lon - node_lon)

                delta = abs(angle_from_here - angle_to_succ)
                if delta < np.pi / 2:  # Sai lệch hướng dưới 90 độ thì chấp nhận
                    found_direction = True
                    break

            if not found_direction:
                continue  # Bỏ node này nếu không hợp hướng

        if dist < min_dist:
            min_dist = dist
            nearest_node = node

    return nearest_node


G = build_graph_from_geojson(GEOJSON_PATH)
GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
save_graph(G, GRAPH_PATH)