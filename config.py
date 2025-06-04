from pathlib import Path

ROADS_FILE = 'data/geojson/roads.geojson'  # sửa đường dẫn theo project bạn
WEIGHTS_FILE = 'data/geojson/weights.geojson'
VHC_ALLOWED_FILE = 'data/geojson/vhc_allowed.geojson'
GRAPH_PATH = Path('data/graph/graph_data.pkl')

DEFAULT_WEIGHT=1.0

ALLOWED_HIGHWAYS = {
    "car": [
        "primary", "primary_link", "secondary", "tertiary",
        "residential", "service",
        "default"
    ],
    "motor": [
        "primary", "primary_link", "secondary", "tertiary",
        "residential", "service", "cycleway", "path", 
        "default"
    ],
    "foot": [
        "primary", "primary_link", "secondary", "tertiary", "residential", 
        "service", "footway", "path", "steps", "cycleway", "pedestrian", 
        "default"
    ]
}


CONDITION_SPEED_FACTORS= {
    "normal": 1.0,
    "jam": 0.3,
    "flooded": 0.5,
    "not allowed": 0.00000001
}
# nhân tốc độ xe theo loại đường với hệ số điều kiện->tốc độ của xe trong đkien đó
DEFAULT_SPEED_BY_VEHICLE = {
    "car": {
        "primary": 60,
        "primary_link": 40,
        "secondary": 50,
        "tertiary": 40,
        "residential": 30,
        "service": 20,
        "default": 40
    },
    "motor": {
        "primary": 50,
        "primary_link": 30,
        "secondary": 40,
        "tertiary": 35,
        "residential": 25,
        "service": 20,
        "cycleway": 20,
        "path": 15,
        "default": 30
    },
    "foot": {
        "primary": 4,          
        "primary_link": 3,
        "secondary": 4,
        "tertiary": 5,
        "residential": 5,
        "service": 5,
        "footway": 5,
        "path": 4,
        "steps": 2,
        "cycleway": 5,
        "pedestrian": 5,
        "default": 5
    }
}