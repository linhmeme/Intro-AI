from flask import Blueprint 
from config import ROADS_FILE, VHC_ALLOWED_FILE, ALLOWED_HIGHWAYS
import json
from utils.sync_geojson import sync_geojson_file
from flask import request, jsonify
from graph import build_graph_from_geojson

filter_bp = Blueprint('filter_routes',__name__)

@filter_bp.route('/filter_routes', methods=['POST'])
def filter_routes():
    data = request.get_json()
    vehicle = data.get('vehicle')
    print(f"Vehicle: {vehicle}")

    # Kiểm tra xem phương tiện có hợp lệ không
    if vehicle not in ALLOWED_HIGHWAYS:
        return jsonify({'status': 'error', 'message': 'Phương tiện không hợp lệ'}), 400

    # Lọc các đoạn đường phù hợp với phương tiện
    with open(ROADS_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    allowed_routes = [
    feature for feature in geojson_data['features']
    if feature['properties'].get('highway') in ALLOWED_HIGHWAYS[vehicle]]

    for feature in allowed_routes:
        # Thêm trọng số mặc định (1) vào từng đoạn đường
        feature['properties']['weight'] = 1
    
    # Lưu các đoạn đường được phép vào vhc_allowed.geojson
    with open(VHC_ALLOWED_FILE, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": allowed_routes}, f, indent=2, ensure_ascii=False) 

    #✅ Sau khi ghi xong, đồng bộ sang static/
    sync_geojson_file('vhc_allowed.geojson')
    print(f"[filter_routes] Ghi {len(allowed_routes)} tuyến cho {vehicle}")

    G = build_graph_from_geojson(VHC_ALLOWED_FILE)

    return jsonify({'status': 'success', 'message': 'Đã lọc các đoạn đường cho phương tiện: ' + vehicle}), 200


