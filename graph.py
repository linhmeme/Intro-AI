import json
import pickle
import networkx as nx
import numpy as np
from geopy.distance import geodesic
from pathlib import Path
from config import WEIGHTS_FILE, GRAPH_PATH
from utils.weighting import compute_weight

def build_graph_from_geojson(geojson_file, snap_threshold=1):
    with open(geojson_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    banned_nodes = set()

    for feature in data["features"]:
        geometry = feature.get("geometry", {})
        props = feature.get("properties", {})
        edge_id = props.get("id")
        highway = props.get("highway", "")
        condition = props.get("condition", "normal")
        speed = props.get("speed", None)
        vehicle = props.get("vehicle", None)

        if edge_id is None:
            continue

        coords_list = []
        if geometry["type"] == "LineString":
            coords_list = [geometry["coordinates"]]
        elif geometry["type"] == "MultiLineString":
            coords_list = geometry["coordinates"]  # list of lines
        else:
            print("Không hỗ trợ geometry:", geometry["type"])
            continue

        for line in coords_list:
            # Xử lý đoạn cấm (not allowed)
            if condition == "not allowed":
                if len(line) > 2:
                    for pt in line[1:-1]:  # loại node giữa
                        banned_nodes.add(tuple(pt))
                continue

            for i in range(len(line) - 1):
                x1, y1 = line[i]
                x2, y2 = line[i + 1]

                G.add_node((x1, y1), x=x1, y=y1)
                G.add_node((x2, y2), x=x2, y=y2)

                # Tính lại độ dài từng segment nhỏ thay vì dùng length tổng của feature
                segment_length = geodesic((y1, x1), (y2, x2)).meters
                travel_time, speed_used, _ = compute_weight(segment_length, highway, vehicle, condition)

                edge_attrs = {
                    "weight": travel_time,  # Nếu bạn muốn dùng lại weight thì cần tính lại
                    "length": segment_length,
                    "id": f"{edge_id}_{i}",  # tạo id segment riêng
                    "highway": highway,
                    "condition": condition,
                    "speed": speed_used,
                    "vehicle": vehicle
                }

                G.add_edge((x1, y1), (x2, y2), **edge_attrs)
                G.add_edge((x2, y2), (x1, y1), **edge_attrs)

    G.remove_nodes_from(banned_nodes)

    print(f"Đã xây dựng graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
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

        dist = np.linalg.norm([lat - node_lat, lon - node_lon]) * 111139

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

