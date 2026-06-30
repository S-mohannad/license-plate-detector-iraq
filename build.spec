# build.spec
# لبناء البرنامج: شغّل بـ Terminal من D:\programing
#   pyinstaller build.spec
import cv2
import os

cv2_data_path = os.path.join(os.path.dirname(cv2.__file__), 'data')
from PyInstaller.utils.hooks import collect_all

# ── جمع كل ملفات/مكتبات TensorFlow و Keras و OpenCV تلقائياً ──
tf_datas, tf_binaries, tf_hiddenimports = collect_all('tensorflow')
keras_datas, keras_binaries, keras_hiddenimports = collect_all('keras')
cv2_datas, cv2_binaries, cv2_hiddenimports = collect_all('cv2')

a = Analysis(
    ['License_Plate_Detector_Program.py'],   # ← الملف الرئيسي لتشغيل البرنامج
    pathex=['.'],
    binaries=tf_binaries + keras_binaries + cv2_binaries,
    datas=[
        # ── ملف كشف اللوحات الجاهز من OpenCV (haarcascade) ──
        (cv2_data_path, 'cv2/data'),
    ] + tf_datas + keras_datas + cv2_datas,
    hiddenimports=[
        'tensorflow',
        'tensorflow.python',
        'keras',
        'cv2',
        'sklearn',
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.tree._utils',
        'scipy',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'error_handler',
    ] + tf_hiddenimports + keras_hiddenimports + cv2_hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CarPlateDetector',   # ← اسم ملف الـ EXE النهائي
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # ← False يخفي نافذة Terminal السوداء تماماً عن المستخدم
    icon='car_icon.ico',   # ← أيقونة السيارة المخصصة
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CarPlateDetector',   # ← اسم المجلد النهائي اللي راح يحتوي كل شي
)
