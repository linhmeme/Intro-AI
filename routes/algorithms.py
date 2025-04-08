from flask import Blueprint, request, jsonify
from utils.graph import G, get_nearest_node
from utils.algorithms import find_shortest_path

algo_bp = Blueprint("algorithms", __name__)

@algo_bp.route("/find_route", methods=["POST"])
def find_route():
    """API tìm đường theo thuật toán"""
    data = request.json
    start_lat, start_lng = data["start"]
    end_lat, end_lng = data["end"]
    algorithm = data.get("algorithm", "dijkstra")  # Mặc định dùng Dijkstra

    orig_node = get_nearest_node(G, start_lat, start_lng)
    dest_node = get_nearest_node(G, end_lat, end_lng)

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

    return jsonify({
        "path": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path],
        "visited_forward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_forward],
        "visited_backward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_backward],
        "edges_forward": convert_edges_to_coords(edges_forward),
        "edges_backward": convert_edges_to_coords(edges_backward)
    })