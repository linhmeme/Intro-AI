import json
from geopy.distance import geodesic
from config import VHC_ALLOWED_FILE

def compute_length(coords):
    total = 0
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]
        total += geodesic((p1[1], p1[0]), (p2[1], p2[0])).meters
    return total

def add_length_to_vhc_allowed():
    with open(VHC_ALLOWED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for feature in data['features']:
        geometry = feature['geometry']
        coords = []

        if geometry['type'] == 'LineString':
            coords = geometry['coordinates']
        elif geometry['type'] == 'MultiLineString':
            coords = [pt for line in geometry['coordinates'] for pt in line]
        else:
            continue

        feature['properties']['length'] = compute_length(coords)

    with open(VHC_ALLOWED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[add_length_to_vhc_allowed] ✅ Đã thêm chiều dài cho {len(data['features'])} đoạn đường.")
