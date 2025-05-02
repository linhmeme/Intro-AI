from config import ROADS_FILE, VHC_ALLOWED_FILE, WEIGHTS_FILE, ALLOWED_HIGHWAYS, VEHICLE_WEIGHTS, CONDITION_WEIGHTS
import json
import os

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