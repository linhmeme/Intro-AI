from flask import Blueprint, request, jsonify
from cache.condition_cache import condition_cache

update_bp = Blueprint('update_condition_temp',__name__)
@update_bp.route('/update_condition_temp', methods=['POST'])
def update_condition_temp():
    data = request.get_json()
    edge_id = data.get('edge_id')
    condition = data.get('condition')
    
    if not edge_id or condition not in ["normal", "jam", "flooded", "not allowed"]:
        return jsonify({"status": "error", "message": "Thông tin không hợp lệ"}), 400

    condition_cache[str(edge_id)] = condition
    return jsonify({"status": "success", "message": f"Đã ghi tạm điều kiện cho edge {edge_id}"}), 200

