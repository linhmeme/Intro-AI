from flask import Blueprint, request, jsonify
from config import GRAPH_PATH
from graph import get_nearest_node, load_graph
from algorithms import find_shortest_path

algo_bp = Blueprint("algorithms", __name__)

@algo_bp.route("/find_route", methods=["POST"])
def find_route():
    """API tìm đường theo thuật toán"""
    data = request.json
    start_lat, start_lng = data["start"]
    end_lat, end_lng = data["end"]
    vehicle = data.get("vehicle", "car")
    algorithm = data.get("algorithm", "dijkstra")  # Mặc định dùng Dijkstra

    # ✅ Load graph đã build từ weights.geojson
    G = load_graph(GRAPH_PATH)

    orig_node = get_nearest_node(G, start_lat, start_lng, direction_check=True, goal_lat=end_lat, goal_lon=end_lng)
    dest_node = get_nearest_node(G, end_lat, end_lng, direction_check=True, goal_lat=start_lat, goal_lon=start_lng)

    result = find_shortest_path(G, orig_node, dest_node, vehicle, algorithm)

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
