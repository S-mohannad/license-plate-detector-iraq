<div align="center">

# 🚗 License Plate Detector

### نظام كشف وتمييز لوحات السيارات العراقية باستخدام Deep Learning

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

[⬇️ تحميل البرنامج](#-تحميل-البرنامج-جاهز-للتشغيل) • [📖 طريقة العمل](#-طريقة-العمل) • [🛠️ البناء من المصدر](#️-البناء-من-المصدر)

</div>

---

## 📋 نظرة عامة

برنامج سطح مكتب لكشف لوحات السيارات العراقية وقراءة الأرقام والحروف عليها تلقائياً، باستخدام شبكة عصبية CNN مدرّبة خصيصاً على نمط اللوحات العراقية، مع واجهة رسومية بسيطة لا تتطلب أي خبرة تقنية من المستخدم.

---

## ✨ المميزات

- 📷 **كشف من كاميرا مباشرة** — معالجة لحظية للفيديو
- 🖼️ **كشف من صور بالتتابع** — معالجة دفعة من الصور تلقائياً
- 🗂️ **كشف من قاعدة بيانات** — فحص مجلد كامل من الصور دفعة واحدة
- 🧠 **نموذج CNN مدرّب** — دقة تقترب من 99% على بيانات الاختبار
- 🖥️ **واجهة رسومية بسيطة** — Tkinter، بدون أي تعقيد
- 📦 **EXE مستقل** — يعمل بدون تثبيت Python أو أي مكتبة

---

## ⬇️ تحميل البرنامج (جاهز للتشغيل)

> لا حاجة لتثبيت Python أو أي مكتبة — فقط حمّل وشغّل

1. حمّل الملف المضغوط من [الرابط هنا](#) *(ضع رابط Google Drive/OneDrive)*
2. فك الضغط في أي مكان على جهازك
3. شغّل `CarPlateDetector.exe`

**متطلبات النظام:** Windows 10/11 (64-bit) — لا حاجة لأي تثبيت إضافي

---

## 📖 طريقة العمل

```
   📷 إدخال الصورة/الفيديو
            │
            ▼
   🔍 كشف موقع اللوحة (Haar Cascade - OpenCV)
            │
            ▼
   ✂️ قص اللوحة وتقطيعها لرموز فردية
            │
            ▼
   🧠 تمييز كل رمز (CNN - TensorFlow/Keras)
            │
            ▼
   📋 عرض النتيجة النهائية للوحة
```

---

## 🗂️ هيكل المشروع

```
License-Plate-Detector/
│
├── License_Plate_Detector_Program.py   ← نقطة الدخول الرئيسية (الواجهة)
├── kerasss.py                          ← بناء وتدريب نموذج CNN
├── web_cam_video.py                    ← الكشف من كاميرا مباشرة
├── photo_detect.py                     ← الكشف من صور بالتتابع
├── db_photo.py                         ← الكشف من قاعدة بيانات صور
├── config.py                           ← إدارة المسارات الديناميكية
├── error_handler.py                    ← تسجيل الأخطاء (بدل Terminal)
├── nmozg.py                            ← تقييم أداء النموذج
│
├── build.spec                          ← إعدادات بناء EXE (PyInstaller)
├── car_icon.ico                        ← أيقونة البرنامج
│
└── DB_CAR/                             ← قاعدة بيانات الصور والنموذج المدرّب
    └── plate/
        ├── model.weights.h5
        └── (مجلدات الأحرف 0-9, A-Z)
```

---

## 🛠️ البناء من المصدر

### المتطلبات
```bash
pip install tensorflow opencv-python pyinstaller pillow numpy scikit-learn matplotlib
```

### تشغيل كسكربت Python
```bash
python License_Plate_Detector_Program.py
```

### بناء ملف EXE
```bash
pyinstaller build.spec
```

الناتج يكون في `dist/CarPlateDetector/`

> ⚠️ عملية البناء تستغرق 10-20 دقيقة بسبب حجم TensorFlow

---

## 🧠 النموذج (Model)

| المعيار | القيمة |
|---|---|
| النوع | CNN (Convolutional Neural Network) |
| الإطار | TensorFlow / Keras |
| الدقة النهائية | ~99% على بيانات التدريب |
| المخرجات | 36 فئة (أرقام 0-9 + حروف A-Z) |

---

## 🔒 ملاحظة أمنية

البرنامج يعمل بالكامل **محلياً (Offline)** — لا يتصل بالإنترنت ولا يرسل أي بيانات خارجية.
و ان جميع ملفات الداتا بيس هي تم انشائها من الذكاء الاصطناعي و لا وجود لها بتاتا بالواقع 
---

## 📄 التوثيق الكامل

للاطلاع على التفاصيل التقنية الكاملة لمراحل تطوير المشروع (من سكربت محلي إلى EXE قابل للتوزيع)، راجع: [`مشروع_كشف_لوحات_السيارات.md`](./مشروع_كشف_لوحات_السيارات.md)

---

## 👨‍💻 المطور

**S-mohannad** — [@S-mohannad](https://github.com/S-mohannad)

---

<div align="center">

صُنع بـ ❤️ لمشروع تخرج / دراسة

</div>
