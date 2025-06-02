import shutil
from config import VHC_ALLOWED_FILE, WEIGHTS_FILE

SOURCE_FILE = VHC_ALLOWED_FILE     
TARGET_FILE = WEIGHTS_FILE     

def reset_weights():
    try:
        shutil.copyfile(SOURCE_FILE, TARGET_FILE)
        print(f"✅ Đã reset lại weights từ {SOURCE_FILE} → {TARGET_FILE}")
    except Exception as e:
        print(f"❌ Lỗi khi reset weights: {e}")