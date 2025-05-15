from config import VHC_ALLOWED_FILE
import json
import os
from config import DEFAULT_SPEED_BY_VEHICLE, CONDITION_SPEED_FACTORS

def compute_weight(length, highway, vehicle, edge_id=None, condition_cache=None):
    """
    Tính trọng số (thời gian di chuyển) cho một đoạn đường:
    - Nếu không có condition → mặc định "normal"
    - Nếu bị jam, flooded → giảm tốc độ theo hệ số
    """
    with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    length = 0
    for feature in geojson_data['features']:
        props = feature['properties']
        if str(props['id']) == edge_id:
            length = props.get('length', 0)
            break
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
    speed_used = base_speed * factor

    if speed_used <= 0:
        return float('inf')

    travel_time = (length / 1000) / speed_used # km / (km/h) = h

    return round(travel_time, 2), round(speed_used, 1), condition

def update_weight_file(edge_id, length, condition, highway, vehicle, condition_cache, weights):
    # Tính trọng số, tốc độ sử dụng và condition từ condition_cache
    weight, speed_used, condition = compute_weight(length, highway, vehicle, edge_id, condition_cache)

    weights[edge_id] = {
        "vehicle": vehicle,
        "highway": highway,
        "length": length,
        "condition": condition,
        "speed": speed_used,
        "weight": weight
    }

    return weight, speed_used, condition