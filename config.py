import os
import sys

def get_base_path():
    if getattr(sys, "frozen", False):
        # حالة EXE
        return os.path.dirname(sys.executable)
    else:
        # حالة تشغيل عادي بـ python
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

DB_CAR_PATH = os.path.join(BASE_PATH, "DB_CAR")
PLATE_PATH  = os.path.join(DB_CAR_PATH, "plate")
MODEL_PATH  = os.path.join(PLATE_PATH, "model.weights.h5")

os.makedirs(PLATE_PATH, exist_ok=True)