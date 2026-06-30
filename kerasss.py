import os
import cv2
import numpy as np
from config import PLATE_PATH, MODEL_PATH
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from keras.callbacks import EarlyStopping
from keras.utils import to_categorical
# ===== الكلاسات =====
classes = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','J','K','L','M','Q','N','R','S','Z']
class_to_index = {name: idx for idx, name in enumerate(classes)}
index_to_class = {idx: name for idx, name in enumerate(classes)}
# ================= تحميل البيانات =================
def load_data(dataset_path):
    images, labels = [], []

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

    x = np.array(images).reshape(-1, 28, 28, 1)
    y = np.array(labels)
    y_cat = to_categorical(y, len(classes))
    return train_test_split(x, y_cat, y, test_size=0.2, random_state=42)
# ================= بناء الموديل =================
def build_model():
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
    return model
# ================= تدريب سريع =================
def train_model(model, dataset_path):
    x_train, x_test, y_train_cat, y_test_cat, _, _ = load_data(dataset_path)
    early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)
    model.fit(x_train,y_train_cat,validation_data=(x_test, y_test_cat),epochs=30,batch_size=16,callbacks=[early_stop],verbose=1)
    return model
# ================= قراءة لوحة من الرموز =================
def predict_plate_from_symbols(model, symbols_folder):
    files = sorted(os.listdir(symbols_folder))
    plate_text = ""

    for file in files:
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        path = os.path.join(symbols_folder, file)

        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue

        img = cv2.resize(img, (28, 28))
        img = img.astype("float32") / 255.0
        img = img.reshape(1, 28, 28, 1)

        pred_idx = np.argmax(model.predict(img, verbose=0))
        pred_char = index_to_class[pred_idx]
        plate_text += pred_char
    return plate_text
# ================= تحميل موديل جاهز او تدريبه =================
def get_trained_model(dataset_path, model_path=MODEL_PATH):
    model = build_model()

    if os.path.exists(model_path):
        print("📦 Loading pre-trained model...")
        model.load_weights(model_path)
    else:
        print("🧠 Training the model...")
        model = train_model(model, dataset_path)
        model.save_weights(model_path)
        print("✅ the model has been trained and saved.")

    return model
if __name__ == "__main__":
    model = get_trained_model(PLATE_PATH)
    print("✅ Model is ready for use")