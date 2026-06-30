import cv2
import os
import tkinter as tk
import numpy as np
from kerasss import get_trained_model

classes = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','J','K','L','M','Q','N','R','S','Z']
index_to_class = {i: c for i, c in enumerate(classes)}

from config import PLATE_PATH
save_folder = PLATE_PATH
os.makedirs(save_folder, exist_ok=True)
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")
prev_plate, alpha, frame_count = None, 0.9, 0
_tk_root = _tk_title = _tk_frame = None
capture_flag = False
last_plate_crop, last_boxes_rel, last_frame = None, [], None

model = get_trained_model(PLATE_PATH)
cap = cv2.VideoCapture(0)
def load_databases():
    db_user, db_city = {}, {}
    for fname, db in [("DB_USER.txt", db_user), ("DB_CITY.txt", db_city)]:
        fpath = os.path.join(save_folder, fname)
        if not os.path.exists(fpath): continue
        with open(fpath, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or ";" not in line: continue
                k, v = line.split(";", 1)
                db[k.strip()] = [x.strip() for x in v.split(",")] if fname == "DB_USER.txt" else v.strip()
    return db_user, db_city

def exit_program():
    cap.release()
    cv2.destroyAllWindows()
    try:
        if _tk_root is not None:
            _tk_root.destroy()
    except:
        pass
    return

def on_space(event=None):
    global capture_flag
    capture_flag = True

def init_info_window():
    global _tk_root, _tk_title, _tk_frame
    _tk_root = tk.Tk()
    _tk_root.title("معلومات السيارة")
    _tk_root.configure(bg="#1e1e2e")
    _tk_root.geometry("460x400")
    _tk_root.resizable(False, False)
    _tk_root.protocol("WM_DELETE_WINDOW", lambda: None)
    _tk_root.bind("<Escape>", lambda e: exit_program())
    _tk_root.bind("<space>", on_space)
    _tk_title = tk.Label(_tk_root, text="في انتظار الكشف...", font=("Arial", 20, "bold"), bg="#1e1e2e", fg="#cdd6f4")
    _tk_title.pack(pady=14, fill="x")
    tk.Frame(_tk_root, height=2, bg="#89b4fa").pack(fill="x", padx=20)
    _tk_frame = tk.Frame(_tk_root, bg="#1e1e2e")
    _tk_frame.pack(fill="both", expand=True, padx=24, pady=12)
    _tk_root.update()

def update_info_window(plate_text):
    if _tk_root is None: return
    _tk_title.config(text=f"🚗   {plate_text}")
    for w in _tk_frame.winfo_children(): w.destroy()
    city_code = "".join(c for c in plate_text if c.isdigit())[:2]
    city_name = db_city.get(city_code, "غير معروفة")
    fields = db_user.get(plate_text)
    if fields:
        rows = [(fields[0],"الاسم"  if len(fields)>0 else ""),
                (fields[1],"العمر" if len(fields)>1 else ""),
                (fields[2],"العنوان الوظيفي" if len(fields)>2 else "")]
        if len(fields) > 3: rows.append((fields[3],"الكلية"))
        if len(fields) > 4: rows.append((fields[4],"القسم"))
        rows.append((city_name,"المحافظة"))
    else:
        rows = [("غير مدرج", "الحالة")]
    for lbl, val in rows:
        row = tk.Frame(_tk_frame, bg="#1e1e2e")
        row.pack(fill="x", pady=5)
        tk.Label(row, text=val, font=("Arial",12), bg="#1e1e2e", fg="#cdd6f4", anchor="e").pack(side="right")
        tk.Label(row, text=f" {lbl} -:", font=("Arial",12,"bold"), bg="#1e1e2e", fg="#89b4fa").pack(side="right")
    _tk_root.update()

def detect_plate(frame):
    img = cv2.resize(frame, (900, 600))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, 1.07, 10, minSize=(35,35))
    if len(plates) > 1:  plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    elif len(plates)==0:
        plates = plate_cascade.detectMultiScale(gray, 1.01, 10, minSize=(35,35))
        if len(plates) > 1: plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    return img, plates

def extract_symbols(img, plates):
    if len(plates) < 1: return None, [], []
    x, y, w, h = plates[0]
    crop = img[y:y+h, x:x+w]
    _, thresh = cv2.threshold(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes_rel, boxes_abs = [], []
    for c in contours:
        if cv2.contourArea(c) < 50: continue
        x2,y2,w2,h2 = cv2.boundingRect(c)
        if h2>48 or w2>45 or (h2<35 and w2<16): continue
        boxes_rel.append((x2, y2, w2, h2))
        boxes_abs.append((x+x2, y+y2, w2, h2))
    return crop, boxes_rel, boxes_abs

def predict_from_boxes(plate_crop, boxes_rel, frame_img):
    if plate_crop is None or len(boxes_rel) == 0: return None
    folder_name = f"frame_{frame_count}"
    folder      = os.path.join(save_folder, folder_name)
    os.makedirs(folder, exist_ok=True)
    # ── حفظ الفريم الكامل + اللوحة ──
    cv2.imwrite(os.path.join(folder, "full_frame.png"), frame_img)
    cv2.imwrite(os.path.join(folder, "plate.png"),      plate_crop)
    plate_text = ""
    for i, (sx, sy, sw, sh) in enumerate(sorted(boxes_rel, key=lambda b: b[0])):
        sym = plate_crop[sy:sy+sh, sx:sx+sw]
        if sym is None or sym.size == 0: continue
        cv2.imwrite(os.path.join(folder, f"symbol_{i+1}_area_{sw*sh}.png"), sym)
        gray_sym = cv2.cvtColor(sym, cv2.COLOR_BGR2GRAY) if len(sym.shape)==3 else sym
        resized  = cv2.resize(gray_sym, (28,28)).astype("float32") / 255.0
        pred     = np.argmax(model.predict(resized.reshape(1,28,28,1), verbose=0))
        plate_text += index_to_class[pred]
    return plate_text if plate_text else "UNKNOWN", folder_name

def do_capture():
    global last_plate_crop, last_boxes_rel, last_frame
    crop, boxes, frame_img = last_plate_crop, last_boxes_rel, last_frame
    if crop is not None and len(boxes) > 0 and frame_img is not None:
        result = predict_from_boxes(crop, boxes, frame_img)
        if result:
            plate_text, folder_name = result
            print(f"📸 اسم الصورة : {folder_name}")
            print(f"🔢 الرقم      : {plate_text}")
            update_info_window(plate_text)
    else:
        print("❌ لا توجد لوحة — وجّه الكاميرا على لوحة أولاً")

def run_detector():
    global db_user, db_city, prev_plate, frame_count, capture_flag
    global last_plate_crop, last_boxes_rel, last_frame
    db_user, db_city = load_databases()
    init_info_window()
    while True:
        ret, frame = cap.read()
        if not ret: break

        img, plates = detect_plate(frame)

        if len(plates) >= 1:
            x, y, w, h = plates[0]
            if prev_plate is None: prev_plate = (x,y,w,h)
            else:
                px,py,pw,ph = prev_plate
                prev_plate = (int(alpha*px+(1-alpha)*x), int(alpha*py+(1-alpha)*y),
                            int(alpha*pw+(1-alpha)*w), int(alpha*ph+(1-alpha)*h))
            plates = [prev_plate]

        plate_crop, boxes_rel, boxes_abs = extract_symbols(img, plates)

        # ── تحديث آخر فريم + لوحة مكتشفة ──
        if plate_crop is not None and len(boxes_rel) > 0:
            last_plate_crop = plate_crop.copy()
            last_boxes_rel  = boxes_rel.copy()
            last_frame      = img.copy()

        for (x,y,w,h) in plates:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
            cv2.putText(img,f"Plate | Symbols: {len(boxes_rel)}",(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
        for (sx,sy,sw,sh) in boxes_abs:
            cv2.rectangle(img,(sx,sy),(sx+sw,sy+sh),(0,255,0),2)
        cv2.imshow("Webcam-Detector Camera", img)

        try: _tk_root.update()
        except: pass

        # ── ESC من نافذة الكاميرا ──
        if cv2.getWindowProperty("Webcam-Detector Camera", cv2.WND_PROP_VISIBLE) < 1:
            break

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == 32 or capture_flag:
            capture_flag = False
            do_capture()

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
# ── تشغيل مباشر ──
if __name__ == "__main__":
    run_detector()