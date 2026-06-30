import os
import tkinter as tk
import cv2
from config import DB_CAR_PATH
import web_cam_video
import db_photo
import photo_detect

BG,BTN_BG,BTN_HV,TEXT,MUTED = "#1c2a4a","#2a3f6f","#3a5490","#ffffff","#8aaad4"

def go_back(module):
    cv2.destroyAllWindows()
    try:
        if module._tk_root.winfo_exists(): module._tk_root.destroy()
    except: pass
    try: root.deiconify()
    except: pass

def launch(fn, module):
    # ── إعادة فتح الكاميرا إذا أُغلقت ──
    if hasattr(module, "cap") and not module.cap.isOpened():
        module.cap = cv2.VideoCapture(0)

    # ── patch exit_program (كاميرا) ──
    if hasattr(module, "exit_program"):
        module.exit_program = lambda: go_back(module)

    # ── patch close_all (ليست بوكس) ──
    if hasattr(module, "close_all"):
        module.close_all = lambda: go_back(module)

    # ── أضف زر الرجوع مرة واحدة فقط ──
    if not getattr(module, "_back_added", False):
        orig = module.init_info_window
        def patched(orig=orig, module=module):
            orig()
            tk.Button(module._tk_root, text="◀  رجوع للرئيسية",
                      font=("Consolas",10,"bold"), bg="#0d1f3c", fg="#00d4ff",
                      relief="flat", cursor="hand2", pady=7,
                      command=lambda: go_back(module)).pack(side="top", fill="x")
        module.init_info_window = patched
        module._back_added = True

    root.withdraw()
    fn()
    try: root.deiconify()
    except: pass

root = tk.Tk()
root.title("🚗 Car Plate Detection")
root.configure(bg=BG)
root.geometry("860x500")
root.resizable(False, False)

h = tk.Frame(root, bg=BG); h.pack(fill="x", padx=50, pady=(35,0))
tk.Label(h, text="🚗", font=("Segoe UI Emoji",36), bg=BG, fg="#00d4ff").pack(side="left")
tf = tk.Frame(h, bg=BG); tf.pack(side="left", padx=16)
tk.Label(tf, text="Car Plate Detection", font=("Consolas",26,"bold"), bg=BG, fg=TEXT).pack(anchor="w")
tk.Label(tf, text="اختر وضع التشغيل",   font=("Arial",13),           bg=BG, fg=MUTED).pack(anchor="w")
tk.Frame(root, height=2, bg="#00d4ff").pack(fill="x", padx=50, pady=20)

def make_btn(parent, text, sub, color, cmd):
    f = tk.Frame(parent, bg=BTN_BG, cursor="hand2")
    f.pack(side="left", padx=12, pady=8, fill="both", expand=True)
    i = tk.Frame(f, bg=BTN_BG, padx=20, pady=20); i.pack(fill="both", expand=True)
    tk.Frame(i, height=4, bg=color).pack(fill="x", pady=(0,12))
    tk.Label(i, text=text, font=("Consolas",15,"bold"), bg=BTN_BG, fg=TEXT).pack(anchor="w")
    tk.Label(i, text=sub,  font=("Arial",10),           bg=BTN_BG, fg=MUTED, wraplength=180).pack(anchor="w", pady=(5,12))
    tk.Button(i, text="▶  تشغيل", font=("Consolas",11,"bold"), bg=color, fg="#0d1b35",
              relief="flat", command=cmd, padx=14, pady=6, cursor="hand2").pack(anchor="w")
    f.bind("<Enter>", lambda e: [f.config(bg=BTN_HV), i.config(bg=BTN_HV)])
    f.bind("<Leave>", lambda e: [f.config(bg=BTN_BG), i.config(bg=BTN_BG)])

row = tk.Frame(root, bg=BG); row.pack(fill="both", expand=True, padx=50)
make_btn(row,"Webcam Video","كشف من كاميرا\nمباشرة", "#00d4ff",lambda: launch(web_cam_video.run_detector, web_cam_video))
make_btn(row,"Photo Detect","كشف من صور\nبالتتابع",  "#a855f7",lambda: launch(photo_detect.run,     photo_detect))
make_btn(row,"DB Photo",    "قاعدة بيانات\nالصور",   "#ff6b35",lambda: launch(db_photo.run_photo,               db_photo))

tk.Frame(root, height=1, bg=MUTED).pack(fill="x", padx=50, pady=(16,0))
bot = tk.Frame(root, bg=BG); bot.pack(fill="x", padx=50, pady=10)
ex = tk.Button(bot, text="✕  خروج", font=("Consolas",11,"bold"), bg=BG, fg=MUTED,
               relief="flat", command=root.destroy, padx=16, pady=7, cursor="hand2",
               bd=1, highlightthickness=1, highlightbackground=MUTED)
ex.pack(side="left")
ex.bind("<Enter>", lambda e: ex.config(bg="#cc3333", fg=TEXT, highlightbackground="#cc3333"))
ex.bind("<Leave>", lambda e: ex.config(bg=BG,       fg=MUTED, highlightbackground=MUTED))
tk.Label(bot, text="v1.0  |  " + DB_CAR_PATH, font=("Consolas",9), bg=BG, fg=MUTED).pack(side="right")

root.mainloop()