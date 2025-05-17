import shutil
from pathlib import Path
import hashlib

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open('rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return ''

def sync_geojson_file(filename: str, force: bool = False):
    src = Path('data/geojson') / filename
    dst = Path('static/geojson') / filename

    if not src.exists():
        print(f"[sync_geojson] ❌ Không tìm thấy: {src}")
        return

    src_hash = hash_file(src)
    dst_hash = hash_file(dst)

    if force or src_hash != dst_hash:
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(src, dst)
            print(f"[sync_geojson] 🔁 Cập nhật {filename}")
        except Exception as e:
            print(f"[sync_geojson] ❌ Lỗi khi copy {filename}: {e}")
    else:
        print(f"[sync_geojson] ✅ {filename} không thay đổi")

def sync_geojson_selected(filenames):
    for filename in filenames:
        sync_geojson_file(filename)
