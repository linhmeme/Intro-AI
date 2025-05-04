from flask import Blueprint, request, jsonify
from graph import G, get_nearest_node
from algorithms import find_shortest_path
import json
import networkx as nx

from config import WEIGHTS_FILE

algo_bp = Blueprint("algorithms", __name__)

@algo_bp.route("/find_route", methods=["POST"])
def find_route():
    """API tìm đường theo thuật toán"""
    data = request.json
    start_lat, start_lng = data["start"]
    end_lat, end_lng = data["end"]
    vehicle = data["vehicle", "car"]
    algorithm = data.get("algorithm", "dijkstra")  # Mặc định dùng Dijkstra

    with open(WEIGHTS_FILE, 'r', encoding='utf-8') as wf:
        weights_data = json.load(wf)

    with open("data/geojson/vhc_allowed.geojson", "r", encoding="utf-8") as vf:
        geojson = json.load(vf)

    for feature in geojson["features"]:
        props = feature["properties"]
        edge_id = str(props["id"])
        coords = feature["geometry"]["coordinates"]

        weight_info = weights_data.get(edge_id)
        if not weight_info:
            continue

        weight = weight_info.get("weight", float("inf"))
        if weight == float("inf"):
            continue

        for i in range(len(coords) - 1):
            coord1 = tuple(coords[i])
            coord2 = tuple(coords[i + 1])
            G.add_node(coord1, x=coord1[0], y=coord1[1])
            G.add_node(coord2, x=coord2[0], y=coord2[1])
            G.add_edge(coord1, coord2, weight=weight)
            G.add_edge(coord2, coord1, weight=weight)

    # Gọi get_nearest_node với direction_check
    orig_node = get_nearest_node(G, start_lat, start_lng, direction_check=True, goal_lat=end_lat, goal_lon=end_lng)
    dest_node = get_nearest_node(G, end_lat, end_lng, direction_check=True, goal_lat=start_lat, goal_lon=start_lng)

    result = find_shortest_path(G, orig_node, dest_node, algorithm)

    if result is None:
        return jsonify({"error": "Thuật toán không hợp lệ!"}), 400

    path, visited_forward, edges_forward, visited_backward, edges_backward = result

    def convert_edges_to_coords(edge_list):
        coords = []
        for u, v in edge_list:
            if u in G.nodes and v in G.nodes:    
                coords.append([(G.nodes[u]["y"], G.nodes[u]["x"]), (G.nodes[v]["y"], G.nodes[v]["x"])])
        
        return coords

    # trả thêm start_node và end_node

    return jsonify({
        "path": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path],
        "visited_forward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_forward],
        "visited_backward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_backward],
        "edges_forward": convert_edges_to_coords(edges_forward),
        "edges_backward": convert_edges_to_coords(edges_backward),
        "start_node": [orig_node[1], orig_node[0]],  # (lat, lon)
        "end_node": [dest_node[1], dest_node[0]]     # (lat, lon)
    })
