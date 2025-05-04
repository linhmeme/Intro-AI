from flask import Blueprint, request, jsonify
import json
from config import ROADS_FILE, VHC_ALLOWED_FILE, ALLOWED_HIGHWAYS, WEIGHTS_FILE
from utils.sync_geojson import sync_geojson_file
from utils.weighting import compute_weight
from cache.condition_cache import condition_cache
from utils.length import add_length_to_vhc_allowed

condition_bp = Blueprint('condition_bp', __name__)

@condition_bp.route('/filter_routes', methods=['POST'])
def filter_routes():
    data = request.get_json()
    vehicle = data.get('vehicle')

    # Kiểm tra xem phương tiện có hợp lệ không
    if vehicle not in ALLOWED_HIGHWAYS:
        return jsonify({'status': 'error', 'message': 'Phương tiện không hợp lệ'}), 400

    # Lọc các đoạn đường phù hợp với phương tiện
    with open(ROADS_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    allowed_routes = [
    feature for feature in geojson_data['features']
    if feature['properties'].get('highway') in ALLOWED_HIGHWAYS[vehicle]]
    
    # Lưu các đoạn đường được phép vào vhc_allowed.geojson
    with open(VHC_ALLOWED_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": allowed_routes}, f, indent=2, ensure_ascii=False)

    add_length_to_vhc_allowed()    

    #✅ Sau khi ghi xong, đồng bộ sang static/
    sync_geojson_file('vhc_allowed.geojson')
    print(f"[filter_routes] Ghi {len(allowed_routes)} tuyến cho {vehicle}")

    return jsonify({'status': 'success', 'message': 'Đã lọc các đoạn đường cho phương tiện: ' + vehicle}), 200

@condition_bp.route('/update_condition_temp', methods=['POST'])
def update_condition_temp():
    data = request.get_json()
    edge_id = data.get('edge_id')
    condition = data.get('condition')
    
    if not edge_id or condition not in ["normal", "not allowed"]:
        return jsonify({"status": "error", "message": "Thông tin không hợp lệ"}), 400

    condition_cache[edge_id] = condition
    return jsonify({"status": "success", "message": f"Đã ghi tạm điều kiện cho edge {edge_id}"}), 200

@condition_bp.route('/finalize_conditions', methods=['POST'])
def finalize_conditions():
    vehicle = request.get_json().get("vehicle")
    if not vehicle:
        return jsonify({"status": "error", "message": "Thiếu phương tiện"}), 400

    with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    weights = {}
    for feature in geojson_data['features']:
        props = feature['properties']
        edge_id = str(props['id'])
        highway = props.get('highway', '')
        length = props.get('length', 0)
        
        weight, speed_used, condition = compute_weight(length, highway, vehicle, edge_id, condition_cache)

        weights[edge_id] = {
            "vehicle": vehicle,
            "highway": highway,
            "length": length,
            "condition": condition,
            "speed": speed_used,
            "weight": weight
        }

    with open(WEIGHTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)

    print(f"[finalize_conditions] Ghi {len(weights)} dòng vào weights.geojson")
    condition_cache.clear()
    return jsonify({"status": "success", "message": "Đã cập nhật xong weights.geojson"}), 200

