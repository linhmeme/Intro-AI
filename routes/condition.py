from flask import Blueprint, request, jsonify
import json
import os
import shutil
from config import ROADS_FILE, VHC_ALLOWED_FILE, ALLOWED_HIGHWAYS
from utils.sync_geojson import sync_geojson_file
# from utils.weighting import compute_weight, update_weight_file

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

    #✅ Sau khi ghi xong, đồng bộ sang static/
    sync_geojson_file('vhc_allowed.geojson')
    print(f"[filter_routes] Ghi {len(allowed_routes)} tuyến cho {vehicle}")

    return jsonify({'status': 'success', 'message': 'Đã lọc các đoạn đường cho phương tiện: ' + vehicle}), 200

# @condition_bp.route('/update_condition', methods=['POST'])
# def update_condition():
#     """
#     Cập nhật điều kiện và trọng số cho đoạn đường, sau đó lưu vào weights.geojson.
#     """
#     data = request.get_json()
#     edge_id = data.get('edge_id')
#     condition = data.get('condition')
#     vehicle = data.get('vehicle')

#     if not edge_id or not condition:
#         return jsonify({'status': 'error', 'message': 'Thiếu edge_id hoặc condition'}), 400

#     if vehicle not in VEHICLE_WEIGHTS:
#         return jsonify({'status': 'error', 'message': 'Loại phương tiện không hợp lệ'}), 400

#     # Đọc từ vhc_allowed.geojson
#     with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
#         geojson_data = json.load(f)

#     updated = False
#     for feature in geojson_data['features']:
#         if feature['properties'].get('id') == edge_id:
#             # Tính trọng số và cập nhật condition
#             highway_type = feature['properties'].get('highway', '')
#             weight = compute_weight(vehicle, highway_type, condition)

#             # Cập nhật trọng số vào weights.geojson
#             update_weight_file(edge_id, condition, highway_type, vehicle, weight)
#             updated = True
#             break

#     if not updated:
#         return jsonify({'status': 'error', 'message': 'Edge not found'}), 404

    # return jsonify({'status': 'success', 'message': f'Cập nhật condition và trọng số cho đoạn đường {edge_id}'}), 200
