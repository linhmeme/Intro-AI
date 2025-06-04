import json
from graph import build_graph_from_geojson, save_graph
from config import GRAPH_PATH

def reset_weights(weights_file, vehicle="default"):
    """
    Reset toàn bộ weights.geojson về trạng thái mặc định:
    - condition = normal
    - speed = None
    - weight = length (mặc định lấy theo độ dài)
    - vehicle = giá trị được truyền vào (nếu có)
    """
    with open(weights_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    reset_count = 0

    for feature in data["features"]:
        props = feature.get("properties", {})
        props.update({
            "vehicle": vehicle,
            "condition": "normal",
            "speed": None,
            "weight": props.get("length", 0),  # fallback: dùng length nếu không có weight
        })
        reset_count += 1

    with open(weights_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Sau khi reset, build lại graph
    G = build_graph_from_geojson(weights_file)
    save_graph(G, GRAPH_PATH)
    print(f" Graph đã reset: {len(G.nodes)} nodes, {len(G.edges)} edges")

    return G
