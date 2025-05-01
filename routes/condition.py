from flask import Blueprint, request, jsonify
import json
import os
import shutil

condition_bp = Blueprint('condition_bp', __name__)
ROADS_FILE = 'data/geojson/roads.geojson'  # sửa đường dẫn theo project bạn
WEIGHTS_FILE = 'data/geojson/weights.geojson'
VHC_ALLOWED_FILE = 'data/geojson/vhc_allowed.geojson'

DEFAULT_WEIGHT=1.0

ALLOWED_HIGHWAYS = {
    "motor": ["motorway", "primary", "secondary", "residential", "service", "footway"],  # Xe máy đi được tất cả
    "car": ["motorway", "primary", "secondary"],  # Ô tô đi được motorway, primary, secondary
    "foot": ["footway", "residential"]  # Đi bộ chỉ đi được footway và residential
}
#mặc định là xe máy với trọng số các đường là 1.0 
VEHICLE_WEIGHTS = {
    "car": 1.5,
    "motor": 1.0,
    "foot": 4.0
}

CONDITION_WEIGHTS = {
    "normal": 1.0,
    "not allowed": 9999
}

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

    allowed_routes = []

    # Lọc các đoạn đường theo các loại đường cho phép phương tiện đi
    for feature in geojson_data['features']:
        highway_type = feature['properties'].get('highway', '')
        if highway_type in ALLOWED_HIGHWAYS[vehicle]:
            allowed_routes.append(feature)

    # Lưu các đoạn đường được phép vào vhc_allowed.geojson
    with open(VHC_ALLOWED_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": allowed_routes}, f, indent=2, ensure_ascii=False)

    return jsonify({'status': 'success', 'message': 'Đã lọc các đoạn đường cho phương tiện: ' + vehicle}), 200


def compute_weight(vehicle, highway, condition):
    """
    Tính trọng số dựa trên phương tiện, các phương tiện được phép và điều kiện của đường.
    Trọng số càng cao => đoạn đường càng ít được chọn.
    """
    allowed_highways = ALLOWED_HIGHWAYS.get(vehicle, [])
    if highway not in allowed_highways:
        return float('inf')  # Trọng số vô cùng nếu không được phép đi qua

    # Nếu phương tiện được phép đi qua, trọng số theo loại phương tiện
    vehicle_weight = VEHICLE_WEIGHTS.get(vehicle, 1.0)  # Trọng số phương tiện (mặc định là 1.0 nếu không có)

    # Thêm yếu tố condition
    condition_factor = CONDITION_WEIGHTS.get(condition, 1.0)  # Nếu condition là "not allowed" thì trọng số rất cao

    return vehicle_weight * condition_factor

def update_weight_file(edge_id, condition, highway, vehicle):
    if not os.path.exists(WEIGHTS_FILE):
        weights = {}
    else:
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            weights = json.load(f)
#mỗi weights ứng vs id trong geojson(từ roads_origin) có 3 trường 
    weight = compute_weight(highway, vehicle, condition)
    weights[edge_id] = {"vehicle": vehicle, "highway": highway, "condition": condition, "weight": weight, }

    with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)
#load từ geojson, sau đó cập nhật 
@condition_bp.route('/update_condition', methods=['POST'])
def update_condition():
    """
    Cập nhật điều kiện và trọng số cho đoạn đường, sau đó lưu vào weights.geojson.
    """
    data = request.get_json()
    edge_id = data.get('edge_id')
    condition = data.get('condition')
    vehicle = data.get('vehicle')

    if not edge_id or not condition:
        return jsonify({'status': 'error', 'message': 'Thiếu edge_id hoặc condition'}), 400

    if vehicle not in VEHICLE_WEIGHTS:
        return jsonify({'status': 'error', 'message': 'Loại phương tiện không hợp lệ'}), 400

    # Đọc từ vhc_allowed.geojson
    with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    updated = False
    for feature in geojson_data['features']:
        if feature['properties'].get('id') == edge_id:
            # Tính trọng số và cập nhật condition
            highway_type = feature['properties'].get('highway', '')
            weight = compute_weight(vehicle, highway_type, condition)

            # Cập nhật trọng số vào weights.geojson
            update_weight_file(edge_id, condition, highway_type, vehicle, weight)
            updated = True
            break

    if not updated:
        return jsonify({'status': 'error', 'message': 'Edge not found'}), 404

    return jsonify({'status': 'success', 'message': f'Cập nhật condition và trọng số cho đoạn đường {edge_id}'}), 200
