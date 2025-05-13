from flask import Blueprint 
from flask import request, jsonify
from config import WEIGHTS_FILE, VHC_ALLOWED_FILE, GRAPH_PATH
import json
from utils.weighting import update_weight_file
from graph import build_graph_from_geojson, save_graph
from utils.sync_geojson import sync_geojson_file
from cache.condition_cache import condition_cache

final_bp = Blueprint('finalize_conditions',__name__)

def build_new_graph_from_weights(weights_file):
    # Đọc weights.geojson và xây dựng lại graph mới từ dữ liệu này
    return build_graph_from_geojson(weights_file)

@final_bp.route('/finalize_conditions', methods=['POST'])
def finalize_conditions():
    data = request.get_json()
    vehicle = data.get("vehicle")

    if not vehicle:
        return jsonify({"status": "error", "message": "Thiếu phương tiện"}), 400

    with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    updated_features = []
    weights = {}
    for feature in geojson_data['features']:
        props = feature['properties']
        edge_id = str(props['id'])
        highway = props.get('highway', '')
        length = props.get('length', 0)
    
    # Lấy condition từ condition_cache, nếu không có thì mặc định là "normal"
        condition = condition_cache.get(edge_id, "normal")
        
        weight, speed_used, condition = update_weight_file(edge_id, length, condition, highway, vehicle, condition_cache, weights)

        props.update({
            "vehicle": vehicle,
            "condition": condition,
            "speed": speed_used,
            "weight": weight
        })
        updated_features.append(feature)

    with open(WEIGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": updated_features
        }, f, indent=2, ensure_ascii=False)

    print(f"[finalize_conditions] Ghi {len(weights)} dòng vào weights.geojson")
     # Xây dựng lại đồ thị từ weights.geojson
    G_new = build_new_graph_from_weights(WEIGHTS_FILE)

    # Lưu đồ thị vào GRAPH_PATH
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_graph(G_new, GRAPH_PATH)

    # Đồng bộ file geojson sang static/
    sync_geojson_file('weights.geojson')

    return jsonify({"status": "success", "message": "Đã cập nhật xong weights.geojson"}), 200