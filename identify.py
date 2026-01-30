import cv2
import os
import numpy as np
import tkinter as tk
import tkinter.font as font

# -------------------------
# GLOBALS
# -------------------------
DATASET_DIR = "persons"
CASCADE_PATH = "haarcascade_frontalface_default.xml"
MODEL_PATH = "model.yml"

# ensure dataset directory exists
os.makedirs(DATASET_DIR, exist_ok=True)

# global flag to stop identify loop
stop_identify = False


# -------------------------
# COLLECT DATA
# -------------------------
def collect_data():
    name = input("Enter name of person: ").strip()
    while name == "":
        name = input("Name cannot be empty. Enter name: ").strip()

    ids = input("Enter ID (numeric): ").strip()
    while not ids.isdigit():
        ids = input("Invalid ID. Enter numeric ID: ").strip()
    ids = int(ids)

    cap = cv2.VideoCapture(0)
    cascade = cv2.CascadeClassifier(CASCADE_PATH)

    count = 1
    print("[INFO] Collecting samples. Press ESC to stop early...")

    while True:
        ret, frm = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.3, 5)

        for x, y, w, h in faces:
            roi = gray[y:y + h, x:x + w]

            filename = f"{name}-{count}-{ids}.jpg"
            cv2.imwrite(os.path.join(DATASET_DIR, filename), roi)

            cv2.rectangle(frm, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frm, f"Samples: {count}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            count += 1

        cv2.imshow("Collecting Data", frm)

        if cv2.waitKey(1) == 27 or count > 300:
            break

    cap.release()
    cv2.destroyAllWindows()

    print("[INFO] Training model...")
    train()


# -------------------------
# TRAIN MODEL
# -------------------------
def train():
    recog = cv2.face.LBPHFaceRecognizer_create()

    image_paths = [
        os.path.join(DATASET_DIR, f)
        for f in os.listdir(DATASET_DIR)
        if f.lower().endswith((".jpg", ".png"))
    ]

    if not image_paths:
        print("[ERROR] No images found in persons folder.")
        return

    faces = []
    ids = []

    for path in image_paths:
        filename = os.path.basename(path)
        try:
            name, count, person_id = filename.split('-')
            person_id = int(person_id.split(".")[0])
        except:
            print(f"[WARNING] Skipping bad filename: {filename}")
            continue

        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        faces.append(image)
        ids.append(person_id)

    recog.train(faces, np.array(ids))
    recog.save(MODEL_PATH)

    print("[INFO] Training completed. Model saved.")


# -------------------------
# IDENTIFY
# -------------------------
def identify():
    global stop_identify
    stop_identify = False

    if not os.path.exists(MODEL_PATH):
        print("[ERROR] No trained model found. Add member first.")
        return

    recog = cv2.face.LBPHFaceRecognizer_create()
    recog.read(MODEL_PATH)

    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    cap = cv2.VideoCapture(0)

    # load name->id mapping
    labelslist = {}
    for f in os.listdir(DATASET_DIR):
        if f.lower().endswith((".jpg", ".png")):
            try:
                name, _, pid = f.split('-')
                labelslist[int(pid.split('.')[0])] = name
            except:
                continue

    print("[INFO] Starting identification...")

    while not stop_identify:
        ret, frm = cap.read()
        if not ret:
            print("[ERROR] Cannot read camera frame.")
            break

        gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.3, 5)

        for x, y, w, h in faces:
            roi = gray[y:y+h, x:x+w]
            label, confidence = recog.predict(roi)

            if confidence < 100:
                name = labelslist.get(label, "Unknown")
                text = f"{name} ({int(confidence)})"
            else:
                text = "Unknown"

            cv2.rectangle(frm, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frm, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Identify", frm)

        if cv2.waitKey(1) == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    stop_identify = False


# -------------------------
# MAIN TKINTER WINDOW
# -------------------------
def maincall():
    global stop_identify

    root = tk.Tk()
    root.geometry("480x100")
    root.title("Identify System")

    label_font = font.Font(size=35, weight='bold')
    btn_font = font.Font(size=25)

    label = tk.Label(root, text="Select below buttons", font=label_font)
    label.grid(row=0, columnspan=2)

    btn1 = tk.Button(root, text="Add Member", command=collect_data,
                     height=2, width=20, font=btn_font)
    btn1.grid(row=1, column=0, padx=5, pady=10)

    btn2 = tk.Button(root, text="Start Identify", command=identify,
                     height=2, width=20, font=btn_font)
    btn2.grid(row=1, column=1, padx=5, pady=10)

    # FIX: Make X button stop the identify loop
    def on_close():
        global stop_identify
        stop_identify = True
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
