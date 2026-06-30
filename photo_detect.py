import cv2
import os
import tkinter as tk
from kerasss import get_trained_model, predict_plate_from_symbols

from config import DB_CAR_PATH, PLATE_PATH
folder_path = DB_CAR_PATH
supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
save_folder       = os.path.join(folder_path, "plate")
os.makedirs(save_folder, exist_ok=True)

model = get_trained_model(PLATE_PATH)
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_russian_plate_number.xml")
images        = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(supported_formats)]

if not images: print("⚠️ لا توجد صور في المجلد المحدد."); exit()

img0          = cv2.imread(images[0])
target_width  = int(img0.shape[1] * 78.8 / 69.5)
target_height = int(img0.shape[0] * 78.8 / 98)
total         = len(images)

_tk_root = _tk_title = _tk_frame = None
db_user  = db_city = {}

def load_databases(base_folder):
    db_user, db_city = {}, {}
    for fname, db in [("DB_USER.txt", db_user), ("DB_CITY.txt", db_city)]:
        fpath = os.path.join(base_folder, fname)
        if not os.path.exists(fpath): continue
        with open(fpath, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or ";" not in line: continue
                k, v = line.split(";", 1)
                db[k.strip()] = [x.strip() for x in v.split(",")] if "USER" in fname else v.strip()
    return db_user, db_city

def close_all():
    cv2.destroyAllWindows()
    try: _tk_root.destroy()
    except: pass

def init_info_window():
    global _tk_root, _tk_title, _tk_frame
    _tk_root = tk.Toplevel()                          # ← Toplevel بدل Tk
    _tk_root.title("معلومات السيارة")
    _tk_root.configure(bg="#1e1e2e")
    _tk_root.geometry("800x460")
    _tk_root.resizable(False, False)
    _tk_root.protocol("WM_DELETE_WINDOW", close_all)
    _tk_root.bind("<Escape>", lambda e: close_all())

    left = tk.Frame(_tk_root, bg="#181825", width=260)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)
    tk.Label(left, text="📁 الصور", font=("Arial",13,"bold"), bg="#181825", fg="#89b4fa").pack(pady=8)
    tk.Frame(left, height=1, bg="#313244").pack(fill="x", padx=10)

    search_var = tk.StringVar()
    tk.Entry(left, textvariable=search_var, bg="#313244", fg="#cdd6f4",
             insertbackground="#cdd6f4", font=("Arial",10), relief="flat", bd=6).pack(fill="x", padx=10, pady=6)

    lb_frame = tk.Frame(left, bg="#181825")
    lb_frame.pack(fill="both", expand=True, padx=6)
    sb = tk.Scrollbar(lb_frame); sb.pack(side="right", fill="y")

    lb = tk.Listbox(lb_frame, bg="#181825", fg="#cdd6f4", font=("Arial",10),
                    selectbackground="#89b4fa", selectforeground="#1e1e2e",
                    relief="flat", bd=0, highlightthickness=0, yscrollcommand=sb.set, activestyle="none")
    lb.pack(side="left", fill="both", expand=True)
    sb.config(command=lb.yview)
    for img_path in images: lb.insert(tk.END, os.path.basename(img_path))
    tk.Label(left, text=f"إجمالي: {total} صورة", font=("Arial",9), bg="#181825", fg="#6c7086").pack(pady=4)

    right = tk.Frame(_tk_root, bg="#1e1e2e")
    right.pack(side="left", fill="both", expand=True)
    global _tk_title, _tk_frame
    _tk_title = tk.Label(right, text="في انتظار الكشف...", font=("Arial",18,"bold"), bg="#1e1e2e", fg="#cdd6f4", anchor="center")
    _tk_title.pack(pady=14, fill="x")
    tk.Frame(right, height=2, bg="#89b4fa").pack(fill="x", padx=20)
    _tk_frame = tk.Frame(right, bg="#1e1e2e")
    _tk_frame.pack(fill="both", expand=True, padx=24, pady=12)

    def on_search(*args):
        q = search_var.get().lower()
        lb.delete(0, tk.END)
        for img_path in images:
            if q in os.path.basename(img_path).lower(): lb.insert(tk.END, os.path.basename(img_path))

    search_var.trace("w", on_search)
    lb.bind("<<ListboxSelect>>", lambda e: on_select(lb))
    _tk_root.update()

def update_info_window(plate_text, db_user, db_city):
    global _tk_root, _tk_title, _tk_frame
    if _tk_root is None: return
    _tk_title.config(text=f"🚗   {plate_text}")
    for widget in _tk_frame.winfo_children(): widget.destroy()
    city_code = "".join(c for c in plate_text if c.isdigit())[:2]
    city_name = db_city.get(city_code, "غير معروفة")
    fields    = db_user.get(plate_text, None)
    if fields:
        rows = [(fields[0] if len(fields)>0 else "", "الاسم"),
                (fields[1] if len(fields)>1 else "", "العمر"),
                (fields[2] if len(fields)>2 else "", "العنوان الوظيفي")]
        if len(fields) > 3: rows.append((fields[3], "الكلية"))
        if len(fields) > 4: rows.append((fields[4], "القسم"))
        rows.append((city_name, "المحافظة"))
    else:
        rows = [("غير مدرج", "الحالة")]
    for label_text, value_text in rows:
        row = tk.Frame(_tk_frame, bg="#1e1e2e")
        row.pack(fill="x", pady=5)
        tk.Label(row, text=value_text, font=("Arial",12), bg="#1e1e2e", fg="#cdd6f4", anchor="e", justify="right").pack(side="right")
        tk.Label(row, text=f" {label_text} :", font=("Arial",12,"bold"), bg="#1e1e2e", fg="#89b4fa", anchor="e").pack(side="right")
    _tk_root.update()

def load_and_detect_plate(img_path):
    img = cv2.imread(img_path)
    if img is None: return None, None, None, None
    img_resized = cv2.resize(img, (target_width, target_height))
    gray        = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    plates      = plate_cascade.detectMultiScale(gray, scaleFactor=1.07, minNeighbors=10, minSize=(35,35))
    if len(plates) > 1:   plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    elif len(plates) == 0:
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=10, minSize=(35,35))
        if len(plates) > 1: plates = sorted(plates, key=lambda x: x[2]*x[3], reverse=True)[:1]
    return img_resized, gray, plates, img

def extract_symbols(img_resized, plates):
    symbol_boxes, plate_crop, numbers, letters = [], None, 0, 0
    if len(plates) >= 1:
        (x, y, w, h) = plates[0]
        plate_crop  = img_resized[y:y+h, x:x+w]
        _, thresh   = cv2.threshold(cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) < 50: continue
            x2,y2,w2,h2 = cv2.boundingRect(c)
            if h2>48 or w2>45 or (h2<35 and w2<16): continue
            symbol_boxes.append((x2, y2, w2, h2))
        symbol_boxes.sort(key=lambda b: b[0])
        clean = []
        for b in symbol_boxes:
            if not any(abs((b[0]+b[2]//2) - (k[0]+k[2]//2)) < 10 for k in clean):
                clean.append(b)
        symbol_boxes = clean
        letters = 1; numbers = len(symbol_boxes) - 1
    return plate_crop, symbol_boxes, numbers, letters

def save_symbols(img_path, save_folder, plate_crop, symbol_boxes):
    filename     = os.path.splitext(os.path.basename(img_path))[0]
    plate_folder = os.path.join(save_folder, filename)
    if os.path.exists(plate_folder):
        for f in os.listdir(plate_folder): os.remove(os.path.join(plate_folder, f))
    os.makedirs(plate_folder, exist_ok=True)
    symbol_boxes.sort(key=lambda b: b[0])
    for i, (sx,sy,sw,sh) in enumerate(symbol_boxes):
        cv2.imwrite(os.path.join(plate_folder, f"symbol_{i+1}_area_{sw*sh}.png"), plate_crop[sy:sy+sh, sx:sx+sw])
        cv2.rectangle(plate_crop, (sx,sy), (sx+sw,sy+sh), (0,255,0), 2)
    return filename, symbol_boxes

def display_image(img_resized, plates, numbers, letters, x, y, img_path, index):
    cv2.putText(img_resized, f"Numbers: {numbers} | Letters: {letters}", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
    for (x,y,w,h) in plates:
        cv2.rectangle(img_resized, (x,y), (x+w,y+h), (255,0,0), 3)
        cv2.putText(img_resized, "Plate", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
    cv2.putText(img_resized, f"{index+1}/{total} | Plates: {len(plates)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    cv2.imshow("Car_License_Plate_Detector", img_resized)
    cv2.waitKey(1)

def on_select(lb):
    sel = lb.curselection()
    if not sel: return
    img_name = lb.get(sel[0])
    img_path = os.path.join(folder_path, img_name)
    index    = [os.path.basename(p) for p in images].index(img_name)
    img_resized, gray, plates, img = load_and_detect_plate(img_path)
    if img_resized is None: return
    plate_crop, symbol_boxes, numbers, letters = extract_symbols(img_resized, plates)
    if len(plates) >= 1:
        (x, y, w, h) = plates[0]
        filename, symbol_boxes = save_symbols(img_path, save_folder, plate_crop, symbol_boxes)
        plate_text = predict_plate_from_symbols(model, os.path.join(save_folder, filename))
        print(f"🚗 Image: {img_name} | Plate: {plate_text}")
        update_info_window(plate_text, db_user, db_city)
        display_image(img_resized, plates, numbers, letters, x, y, img_path, index)

def run():
    global db_user, db_city
    db_user, db_city = load_databases(save_folder)
    init_info_window()
    _tk_root.wait_window()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    _root = tk.Tk(); _root.withdraw()
    run()