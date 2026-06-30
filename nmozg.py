import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from keras.callbacks import EarlyStopping
from keras.utils import to_categorical

# ================= تحميل الصور =================
from config import PLATE_PATH
dataset_path = PLATE_PATH

images = []
labels = []
# الكلاسات المسموحة
classes = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','J','K','L','M','N','Q','R','S','Z']

# تحويل الاسم إلى رقم index
class_to_index = {name: idx for idx, name in enumerate(classes)}
index_to_class = {idx: name for idx, name in enumerate(classes)}

for folder_name in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, folder_name)

    if not os.path.isdir(folder_path):
        continue

    if folder_name not in class_to_index:
        continue

    label = class_to_index[folder_name]

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        img = cv2.resize(img, (28, 28))
        img = img.astype("float32") / 255.0

        images.append(img)
        labels.append(label)
# ================= تحويل البيانات =================
x = np.array(images)
y = np.array(labels)

x = x.reshape(-1, 28, 28, 1)
y_cat = to_categorical(y, len(classes))
# ================= تقسيم Train / Test =================
x_train, x_test, y_train_cat, y_test_cat, y_train, y_test = train_test_split(x, y_cat, y, test_size=0.2, random_state=42)
# ================= بناء النموذج =================
model = Sequential([Input(shape=(28, 28, 1)),

    Conv2D(32, (3, 3), activation="relu"),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D((2, 2)),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.3),

    Dense(len(classes), activation="softmax")
])
model.compile(optimizer="adam",loss="categorical_crossentropy",metrics=["accuracy"])

# ================= التدريب =================
early_stop = EarlyStopping(monitor="val_loss",patience=5,restore_best_weights=True)
history = model.fit(x_train,y_train_cat,validation_data=(x_test, y_test_cat),epochs=30,batch_size=16,callbacks=[early_stop])

# ================= تقييم النموذج =================
loss, acc = model.evaluate(x_test, y_test_cat)
print("\nTest Accuracy:", acc)

# ================= رسم Accuracy و Loss =================
fig_history, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(history.history["accuracy"], label="Train Accuracy")
ax1.plot(history.history["val_accuracy"], label="Validation Accuracy")
ax1.set_title("Model Accuracy")
ax1.legend()
ax1.grid(True)

ax2.plot(history.history["loss"], label="Train Loss")
ax2.plot(history.history["val_loss"], label="Validation Loss")
ax2.set_title("Model Loss")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# ================= Confusion Matrix =================
y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)

cm = confusion_matrix(y_test, y_pred)

fig_cm, ax_cm = plt.subplots(figsize=(8, 8))
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(ax=ax_cm)

plt.title("Confusion Matrix")
plt.show()

# ================= واجهة عرض الصور =================
root = tk.Tk()
root.title("Digit Viewer")

fig, ax = plt.subplots(figsize=(5, 5))

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()

index = 0
total_images = len(x_test)

def show_image():
    global index

    ax.clear()

    img = x_test[index].reshape(28, 28)
    pred_idx = np.argmax(model.predict(x_test[index:index+1], verbose=0))
    pred = index_to_class[pred_idx]
    actual: str = index_to_class[y_test[index]]

    ax.imshow(img, cmap="gray")
    ax.set_title(f"Image {index+1}/{total_images}\n"f"Actual: {actual} | Predicted: {pred}")
    ax.axis("off")

    print(f"Image {index+1}/{total_images}")
    print("Actual:", y_test[index])
    print("Predicted:", pred)
    print("-" * 30)

    canvas.draw()

def next_image(event=None):
    global index
    index = (index + 1) % total_images
    show_image()

def prev_image(event=None):
    global index
    index = (index - 1) % total_images
    show_image()

root.bind("<Return>", next_image)
root.bind("<space>", prev_image)

show_image()
root.mainloop()