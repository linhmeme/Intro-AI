from flask import Blueprint, request, jsonify
import json
import os
import shutil

condition_bp = Blueprint('condition_bp', __name__)
ROADS_FILE = 'data/geojson/roads.geojson'  # sửa đường dẫn theo project bạn
ROADS_BACKUP = 'data/geojson/roads_original.geojson'
WEIGHTS_FILE = 'data/geojson/weights.geojson'

DEFAULT_WEIGHT=1.0

HIGHWAY_WEIGHTS = {
    "motorway": 1.0,
    "primary": 1.2,
    "secondary": 1.5,
    "residential": 2.0,
    "service": 2.5,
    "footway": 5.0
}

CONDITION_WEIGHTS = {
    "normal": 1.0,
    "flooded": 5.0,
    "congested": 3.0,
    "under_construction": 10.0
}

def compute_weight(highway, condition):
    base_weight = HIGHWAY_WEIGHTS.get(highway, DEFAULT_WEIGHT)
    condition_factor = CONDITION_WEIGHTS.get(condition, 5.0)  # nếu condition lạ thì phạt nặng
    return base_weight * condition_factor

def update_weight_file(edge_id, condition, highway):
    if not os.path.exists(WEIGHTS_FILE):
        weights = {}
    else:
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            weights = json.load(f)

    weight = compute_weight(highway, condition)
    weights[edge_id] = {"highway": highway, "condition": condition, "weight": weight}

    with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)

@condition_bp.route('/update_condition', methods=['POST'])
def update_condition():
    data = request.get_json()
    edge_id = data.get('edge_id')
    condition = data.get('condition')

    if not edge_id or not condition:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    if not os.path.exists(ROADS_FILE):
        return jsonify({'status': 'error', 'message': 'Edges file not found'}), 404

    with open(ROADS_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    updated = False
    for feature in geojson_data['features']:
        if feature['properties'].get('id') == edge_id:
            highway = feature['properties'].get('highway', None)
            weight = compute_weight(highway, condition)

            feature['properties']['condition'] = condition
            update_weight_file(edge_id, condition, highway)

            updated = True
            break

    if not updated:
        return jsonify({'status': 'error', 'message': 'Edge not found'}), 404

    with open(ROADS_FILE, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)

    return jsonify({'status': 'success', 'message': f'Updated condition: {condition}'})
