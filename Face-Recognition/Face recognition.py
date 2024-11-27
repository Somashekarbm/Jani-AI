import cv2
import os

# Paths for cascade and trained models
cascadePath = r"C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\haarcascade_frontalface_default.xml"
trainer_path = r'C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\trainer'

faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX

# Load all recognizer models
recognizers = []
names = ['unknown','soma','anjan']  # Placeholder for ID to name mapping
for trainer_file in os.listdir(trainer_path):
    if trainer_file.endswith('.yml'):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(os.path.join(trainer_path, trainer_file))
        recognizers.append(recognizer)
        face_id = int(trainer_file.split("_")[1].split(".")[0])
        names.append(f'user_{face_id}')

# Initialize camera
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, 640)
cam.set(4, 480)

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        matched_name = "unknown"
        best_accuracy = 100  # Start with worst accuracy

        for recognizer, name in zip(recognizers, names[1:]):
            face_id, accuracy = recognizer.predict(gray[y:y + h, x:x + w])
            if accuracy < best_accuracy:
                best_accuracy = accuracy
                matched_name = name if accuracy < 100 else "unknown"

        cv2.putText(img, matched_name, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, f"{round(100 - best_accuracy)}%", (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

    cv2.imshow('camera', img)
    k = cv2.waitKey(10) & 0xff
    if k == 27:
        break

print("Exiting...")
cam.release()
cv2.destroyAllWindows()
