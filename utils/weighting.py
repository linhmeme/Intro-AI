import json
import os
from config import DEFAULT_SPEED_BY_VEHICLE, CONDITION_SPEED_FACTORS

def compute_weight(length, highway, vehicle, condition):
    if not length or length <= 0:
        return float('inf'), 0, "normal"

    base_speed = DEFAULT_SPEED_BY_VEHICLE.get(vehicle, {}).get(highway, 0)

    # Nếu không lấy được tốc độ, gán mặc định là 5 km/h
    if base_speed <= 0:
        base_speed = 5

    factor = CONDITION_SPEED_FACTORS.get(condition, 1.0)
    speed_used = base_speed * factor

    # Nếu speed_used = 0, fallback tối thiểu
    if speed_used <= 0:
        speed_used = 5

    travel_time = (length / 1000) / speed_used  # thời gian theo giờ

    return round(travel_time, 5), round(speed_used, 1), condition

def update_weight_file(edge_id, length, condition, highway, vehicle, weights):
    # Tính trọng số, tốc độ sử dụng và condition từ condition_cache
    weight, speed_used, condition = compute_weight(length, highway, vehicle, condition)

    weights[edge_id] = {
        "vehicle": vehicle,
        "highway": highway,
        "length": length,
        "condition": condition,
        "speed": speed_used,
        "weight": weight
    }

    return weight, speed_used, condition