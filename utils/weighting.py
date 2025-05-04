from config import WEIGHTS_FILE
import json
import os
from config import DEFAULT_SPEED_BY_VEHICLE, CONDITION_SPEED_FACTORS

def compute_weight(length, highway, vehicle, edge_id=None, condition_cache=None):
    """
    Tính trọng số (thời gian di chuyển) cho một đoạn đường:
    - Nếu không có condition → mặc định "normal"
    - Nếu bị jam, flooded → giảm tốc độ theo hệ số
    """
    if not length or length <= 0:
        return float('inf')

    base_speed = DEFAULT_SPEED_BY_VEHICLE.get(vehicle, {}).get(highway, 0)
    if base_speed <= 0:
        return float('inf')

    # Lấy condition từ cache hoặc mặc định
    if condition_cache and edge_id:
        condition = condition_cache.get(str(edge_id), "normal")
    else:
        condition = "normal"

    # Lấy hệ số tốc độ tương ứng với điều kiện
    factor = CONDITION_SPEED_FACTORS.get(condition, 1.0)
    adjusted_speed = base_speed * factor

    if adjusted_speed <= 0:
        return float('inf')

    travel_time = length / (adjusted_speed * 1000 / 3600)  # m / (m/s) = s

    return round(travel_time, 2), round(adjusted_speed, 1), condition

def update_weight_file(edge_id, length, condition, highway, vehicle, condition_cache):
    weight, speed_used, condition = compute_weight(length, highway, vehicle, edge_id, condition_cache)
    if not os.path.exists(WEIGHTS_FILE):
        weights = {}
    else:
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            weights = json.load(f)
 
    weights[edge_id] = {
        "vehicle": vehicle,
        "highway": highway,
        "length": length,
        "condition": condition,
        "speed": speed_used,
        "weight": weight
    }

    with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)