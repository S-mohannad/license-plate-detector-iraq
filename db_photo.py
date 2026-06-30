import cv2
import os
import tkinter as tk
from kerasss import get_trained_model, predict_plate_from_symbols
from config import DB_CAR_PATH, PLATE_PATH
folder_path = DB_CAR_PATH
# 🖼️ الامتدادات المسموحة
supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
# 📁 مجلد لحفظ اللوحات المستخرجة
save_folder = os.path.join(folder_path, "plate")
os.makedirs(save_folder, exist_ok=True)

# تحميل وتدريب الموديل مرة وحدة
model = get_trained_model(PLATE_PATH)
# 🧾 قراءة الصور
images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)if f.lower().endswith(supported_formats)]
if not images: print("⚠️ لا توجد صور في المجلد المحدد."); exit()

# 🔢 مؤشر الصورة الحالية
index = 0
total = len(images)  # عدد الصور الكلي
# ⚙️ الحجم الثابت المطلوب لكل الصور (يمكنك تعديله)
img = cv2.imread(images[index])
scale_percent = 78.8    # نسبة التصغير
target_width  = int(img.shape[1] * scale_percent / 69.5)
target_height = int(img.shape[0] * scale_percent / 98)

# 🧠 تحميل مصنف كشف لوحات السيارات من OpenCV
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")
_tk_root ,_tk_title ,_tk_frame = None,None,None

# --- الدالة 1 : تحميل قواعد البيانات ---
def load_databases(base_folder):
    db_user, db_city = {}, {}
    user_file = os.path.join(base_folder, "DB_USER.txt")
    city_file = os.path.join(base_folder, "DB_CITY.txt")
    # قراءة قواعد البيانات (المسجلين,المدن) من الملفات النصية
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or ";" not in line: continue
                plate_key, info_part = line.split(";", 1)
                db_user[plate_key.strip()] = [x.strip() for x in info_part.split(",")]
    if os.path.exists(city_file):
        with open(city_file, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or ";" not in line: continue
                parts = line.split(";", 1)
                db_city[parts[0].strip()] = parts[1].strip()
    return db_user, db_city

# --- الدالة 2 : تهيئة نافذة المعلومات و العرض ---
def init_info_window():
    # تهيئة نافذة TKinter لعرض معلومات السيارة
    global _tk_root, _tk_title, _tk_frame
    _tk_root = tk.Tk()
    _tk_root.title("معلومات السيارة")
    _tk_root.configure(bg="#1e1e2e")
    _tk_root.geometry("460x400")
    _tk_root.resizable(False, False)
    _tk_root.bind("<Escape>", lambda e: _tk_root.destroy())   
    _tk_title = tk.Label(_tk_root, text="في انتظار الكشف...", font=("Arial", 20, "bold"), bg="#1e1e2e", fg="#cdd6f4", anchor="center")
    _tk_title.pack(pady=14, fill="x")
    tk.Frame(_tk_root, height=2, bg="#89b4fa").pack(fill="x", padx=20)
    _tk_frame = tk.Frame(_tk_root, bg="#1e1e2e")
    _tk_frame.pack(fill="both", expand=True, padx=24, pady=12)
    _tk_root.update()

# --- الدالة 3 : تحديث نافذة المعلومات بناءً على رقم اللوحة ---
def update_info_window(plate_text, db_user, db_city):
    # تحديث نافذة TKinter لعرض معلومات السيارة بناءً على رقم اللوحة
    global _tk_root, _tk_title, _tk_frame
    if _tk_root is None: return
    _tk_title.config(text=f"🚗   {plate_text}")
    for widget in _tk_frame.winfo_children(): widget.destroy()
    city_code = ""
    for ch in plate_text:
        if ch.isdigit(): city_code += ch
        else: break
    city_name = db_city.get(city_code, "غير معروفة")
    fields = db_user.get(plate_text, None)
    # بناء قائمة الصفوف لعرض المعلومات بشكل مرتب وجميل في النافذة
    if fields:
        name    = fields[0] if len(fields) > 0 else ""
        age     = fields[1] if len(fields) > 1 else ""
        job     = fields[2] if len(fields) > 2 else ""
        college = fields[3] if len(fields) > 3 else ""
        dept    = fields[4] if len(fields) > 4 else ""
        rows = [(name, "الاسم"), (age, "العمر"), (job, "العنوان الوظيفي")]
        if college: rows.append((college, "الكلية"))
        if dept:    rows.append((dept,  "القسم"))
        rows.append((city_name, "المحافظة"))
    else:
        rows = [("غير مدرج", "الحالة")]
    for label_text, value_text in rows:
        row = tk.Frame(_tk_frame, bg="#1e1e2e")
        row.pack(fill="x", pady=5)
        # عرض كل معلومة في صف مستقل مع تنسيق جميل للنصوص (الاسم, العمر, الوظيفة, الكلية, القسم, المحافظة) وغيرها والمحاذاة إلى اليمين للعناوين والقيمة تكون بجانبها 
        tk.Label(row, text=value_text, font=("Arial", 12), bg="#1e1e2e", fg="#cdd6f4", anchor="e", justify="right").pack(side="right")
        # استخدام ":" كفاصل بين العنوان والقيمة
        tk.Label(row, text=f" {label_text} :", font=("Arial", 12, "bold"), bg="#1e1e2e", fg="#89b4fa", anchor="e").pack(side="right")
    _tk_root.update()

# --- الدالة 4 : تحميل الصورة وكشف اللوحة ---
def load_and_detect_plate(images, index, target_width, target_height, plate_cascade):
    # تحميل الصورة
    img = cv2.imread(images[index])
    if img is None:
        print(f"❌ تعذر فتح الصورة: {images[index]}")
        return None, None, None, None
    #    # 🔄 تغيير حجم الصورة لتصبح بنفس الأبعاد المحددة
    img_resized = cv2.resize(img, (target_width, target_height))
    # تحويل الصورة إلى تدرج رمادي (ضروري لكشف اللوحات)
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    # 🚗 كشف لوحات أرقام السيارات
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.07, minNeighbors=10, minSize=(35, 35))
    if len(plates) > 1:   plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    elif len(plates) == 0:
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=10, minSize=(35, 35))
        if len(plates) > 1: plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    return img_resized, gray, plates, img

# --- الدالة 5 : استخراج الرموز ---
def extract_symbols(img_resized, plates):
    symbol_boxes, plate_crop, numbers, letters = [], None, 0, 0
    if len(plates) >= 1:
        (x, y, w, h) = plates[0]
        plate_crop = img_resized[y:y + h, x:x + w]
        # --- 👇👇 ***استخراج الرموز داخل اللوحة*** 👇👇 ---
        gray_plate = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_plate, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # استخراج الكونتورز (كل كونتور = رمز)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) < 50: continue
            x2, y2, w2, h2 = cv2.boundingRect(c)
            if h2 > 48 or w2 > 45: continue
            if h2 < 35 and w2 < 16: continue
            symbol_boxes.append((x2, y2, w2, h2))
        letters = 1
        numbers = len(symbol_boxes) - 1
    return plate_crop, symbol_boxes, numbers, letters

# --- الدالة 6 : حفظ الرموز ---
def save_symbols(images, index, save_folder, plate_crop, symbol_boxes):
    filename     = os.path.splitext(os.path.basename(images[index]))[0]
    plate_folder = os.path.join(save_folder, filename)
    # ← امسح المجلد إذا موجود
    if os.path.exists(plate_folder):
        for f in os.listdir(plate_folder): os.remove(os.path.join(plate_folder, f))
    os.makedirs(plate_folder, exist_ok=True)
    symbol_boxes.sort(key=lambda b: b[0])
    for i, (sx, sy, sw, sh) in enumerate(symbol_boxes):
        symbol_crop = plate_crop[sy:sy+sh, sx:sx+sw]
        cv2.imwrite(os.path.join(plate_folder, f"symbol_{i+1}_area_{sw*sh}.png"), symbol_crop)
        cv2.rectangle(plate_crop, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)
    return filename, symbol_boxes

# --- الدالة 7 : العرض والتحكم ---
def display_and_control(img_resized, plates, numbers, letters, x, y, plate_crop, images, index, total, save_folder):
    # كتابة عدد الأرقام والأحرف فوق اللوحة
    cv2.putText(img_resized, f"Numbers: {numbers} | Letters: {letters}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
    cv2.imwrite(os.path.join(save_folder, os.path.basename(images[index])), plate_crop)
        # 🟩 رسم مربع حول كل لوحة
    for (x, y, w, h) in plates:
        cv2.rectangle(img_resized, (x, y), (x+w, y+h), (255, 0, 0), 3)
        cv2.putText(img_resized, "Plate", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    # نص يُظهر رقم الصورة وعدد اللوحات
    cv2.putText(img_resized, f"{index+1}/{total} | Plates: {len(plates)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    #عرض عنوان النافذة
    cv2.imshow("DataBase_Car_Photo", img_resized)
    while True:
        try: _tk_root.update()
        except: pass
        key = cv2.waitKeyEx(30)
        if key == 27:      return "exit",     index                  # ESC → خروج
        if key == 2555904: return "continue", (index + 1) % total   # → التالي
        if key == 2424832: return "continue", (index - 1) % total   # ← السابق

# ── تشغيل ──
def run_photo():
    global index
    db_user, db_city = load_databases(os.path.join(folder_path, "plate"))
    init_info_window()

    while True:
        img_resized, gray, plates, img = load_and_detect_plate(images, index, target_width, target_height, plate_cascade)
        if img_resized is None: break
        plate_crop, symbol_boxes, numbers, letters = extract_symbols(img_resized, plates)
        if len(plates) >= 1:
            (x, y, w, h) = plates[0]
            filename, symbol_boxes = save_symbols(images, index, save_folder, plate_crop, symbol_boxes)
            plate_text = predict_plate_from_symbols(model, os.path.join(save_folder, filename))
            print(f"🚗 Image: {os.path.basename(images[index])} | Plate: {plate_text}")
            update_info_window(plate_text, db_user, db_city)
            status, index = display_and_control(img_resized, plates, numbers, letters, x, y, plate_crop, images, index, total, save_folder)
            if status == "exit": break

    cv2.destroyAllWindows()
# --- تشغيل البرنامج ---
if __name__ == "__main__":    
    run_photo()