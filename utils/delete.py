from pathlib import Path
import shutil

WEIGHTS_FILE = Path("data/geojson/weights.geojson")
ROADS_FILE = Path("data/geojson/roads.geojson")
ROADS_BACKUP = Path("data/geojson/roads_original.geojson")

def reset_files():
    # Xóa weights.geojson nếu có
    if WEIGHTS_FILE.exists():
        WEIGHTS_FILE.unlink()
        print("Đã xoá weights.geojson.")

    # Phục hồi roads.geojson từ roads_original.geojson
    if ROADS_BACKUP.exists():
        shutil.copy(ROADS_BACKUP, ROADS_FILE)
        print("Đã phục hồi roads.geojson từ bản gốc.")
    else:
        print("Không tìm thấy roads_original.geojson để phục hồi!")
