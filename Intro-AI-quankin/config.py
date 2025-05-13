ROADS_FILE = 'data/geojson/roads.geojson'  # sửa đường dẫn theo project bạn
WEIGHTS_FILE = 'data/geojson/weights.geojson'
VHC_ALLOWED_FILE = 'data/geojson/vhc_allowed.geojson'
GRAPH_PATH = 'data/graph/graph_data.pkl'

DEFAULT_WEIGHT=1.0

ALLOWED_HIGHWAYS = {
    "motor": ["primary", "secondary", "residential", "service", "footway", "primary_link","secondary_link","cycleway", "tertitary"],  # Xe máy đi được tất cả
    "car": ["secondary_link", "tertiary","residential", "service", "primary", "secondary", "primary_link"],  # Ô tô đi được motorway, primary, secondary
    "foot": ["tertiary", "serive","cycleway", "steps","footway", "residential"]  # Đi bộ chỉ đi được footway và residential
}

CONDITION_SPEED_FACTORS= {
    "normal": 1.0,
    "jam": 0.3,
    "flooded": 0.2,
    "not allowed": 0.01
}
# nhân tốc độ xe theo loại đường với hệ số điều kiện->tốc độ của xe trong đkien đó
DEFAULT_SPEED_BY_VEHICLE = {
    "car": {
        "primary": 60,
        "primary_link": 40,
        "secondary": 50,
        "secondary_link": 40,
        "tertiary": 40,
        "residential": 30,
        "service": 20,
    },
    "motor": {
        "primary": 50,
        "primary_link": 30,
        "secondary": 40,
        "secondary_link": 30,
        "tertiary": 35,
        "residential": 25,
        "service": 20,
        "cycleway": 20
    },
    "foot": {
        "tertiary": 5,
        "residential": 5,
        "service": 5,
        "cycleway": 5,
        "steps": 2
    }
}