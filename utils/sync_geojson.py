import shutil
from pathlib import Path

def sync_geojson():
    src = Path('data/geojson')
    dst = Path('static/geojson')

    dst.mkdir(parents=True, exist_ok=True)

    for file in src.glob('*.geojson'):
        shutil.copy(file, dst / file.name)
        print(f"[sync_geojson] Copied {file.name} → static/geojson/")