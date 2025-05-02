ROADS_FILE = 'data/geojson/roads.geojson'  # sửa đường dẫn theo project bạn
WEIGHTS_FILE = 'data/geojson/weights.geojson'
VHC_ALLOWED_FILE = 'data/geojson/vhc_allowed.geojson'

DEFAULT_WEIGHT=1.0

ALLOWED_HIGHWAYS = {
    "motor": ["motorway", "primary", "secondary", "residential", "service", "footway", "primary_link"],  # Xe máy đi được tất cả
    "car": ["motorway", "primary", "secondary", "primary_link"],  # Ô tô đi được motorway, primary, secondary
    "foot": ["footway", "residential"]  # Đi bộ chỉ đi được footway và residential
}
#mặc định là xe máy với trọng số các đường là 1.0 
VEHICLE_WEIGHTS = {
    "car": 1.5,
    "motor": 1.0,
    "foot": 4.0
}

CONDITION_WEIGHTS = {
    "normal": 1.0,
    "not allowed": 9999
}