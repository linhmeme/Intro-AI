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
    from .config import VHC_ALLOWED_FILE, DEFAULT_SPEED_BY_VEHICLE, CONDITION_SPEED_FACTORS
    import json

    # Nếu không có độ dài, lấy lại từ file geojson
    if (not length or length <= 0) and edge_id:
        with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        for feature in geojson_data['features']:
            props = feature['properties']
            if str(props.get('id')) == str(edge_id):
                length = props.get('length', 0)
                break

    if not length or length <= 0:
        return float('inf'), 0, "normal"

    base_speed = DEFAULT_SPEED_BY_VEHICLE.get(vehicle, {}).get(highway, 0)

    # Nếu không lấy được tốc độ, gán mặc định là 5 km/h
    if base_speed <= 0:
        base_speed = 5

    # Lấy condition từ cache hoặc mặc định
    condition = "normal"
    if condition_cache and edge_id:
        condition = condition_cache.get(str(edge_id), "normal")

    factor = CONDITION_SPEED_FACTORS.get(condition, 1.0)
    speed_used = base_speed * factor

    # Nếu speed_used = 0, fallback tối thiểu
    if speed_used <= 0:
        speed_used = 5

    travel_time = (length / 1000) / speed_used  # thời gian theo giờ

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