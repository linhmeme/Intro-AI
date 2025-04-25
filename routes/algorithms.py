import osmnx as ox
from flask import Blueprint, request, jsonify
from utils.graph import G
from utils.algorithms import find_shortest_path

algo_bp = Blueprint("algorithms", __name__)

@algo_bp.route("/find_route", methods=["POST"])
def find_route():
    """API tìm đường theo thuật toán"""
    data = request.json
    start_lat, start_lng = data["start"]
    end_lat, end_lng = data["end"]
    algorithm = data.get("algorithm", "dijkstra")  # Mặc định dùng Dijkstra

    orig_node = ox.distance.nearest_nodes(G, start_lng, start_lat)
    dest_node = ox.distance.nearest_nodes(G, end_lng, end_lat)

    result = find_shortest_path(G, orig_node, dest_node, algorithm)

    if result is None:
        return jsonify({"error": "Thuật toán không hợp lệ!"}), 400
    
    
    path, visited_forward, edges_forward, visited_backward, edges_backward = result

    def convert_edges_to_coords(edge_list):
        coords = []
        street_names = []
        for u, v in edge_list:
            if u in G.nodes and v in G.nodes:    
                coords.append([(G.nodes[u]["y"], G.nodes[u]["x"]), (G.nodes[v]["y"], G.nodes[v]["x"])])
                #lay ten duong(neu co)
                edge_data = G.get_edge_data(u,v)
                if edge_data:
                    street_name = edge_data[0].get("name", "Unknown")
                else:
                    street_name = "Unknown"

                street_names.append(street_name)
        
        return coords, street_names

    edges_forward_coords, street_names = convert_edges_to_coords(edges_forward)
    edges_backward_coords, _ = convert_edges_to_coords(edges_backward) 

    return jsonify({
        "path": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path],
        "visited_forward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_forward],
        "visited_backward": [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in visited_backward],
        "edges_forward": edges_forward_coords,
        "edges_backward": edges_backward_coords,
        "streets": street_names # tra ve dsach cac duong di qua
    })