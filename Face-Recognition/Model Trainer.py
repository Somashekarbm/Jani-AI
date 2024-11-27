import cv2
import numpy as np
from PIL import Image
import os

# Paths for samples and trainer
samples_path = r'C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\samples'
trainer_path = r'C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\trainer'

# Initialize recognizer and detector
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def Images_And_Labels(user_folder):
    imagePaths = [os.path.join(user_folder, f) for f in os.listdir(user_folder)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')
        
        # Extract the face ID from the filename
        id = int(os.path.split(imagePath)[-1].split("_")[1])
        faces = detector.detectMultiScale(img_arr)

        for (x, y, w, h) in faces:
            faceSamples.append(img_arr[y:y + h, x:x + w])
            ids.append(id)

    return faceSamples, ids

print("Training faces. This may take a few seconds. Please wait...")

# Loop through each user folder and train separately
for user_folder in os.listdir(samples_path):
    user_folder_path = os.path.join(samples_path, user_folder)
    if os.path.isdir(user_folder_path):
        face_id = int(user_folder.split("_")[1])  # Get ID from folder name
        faces, ids = Images_And_Labels(user_folder_path)

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(ids))

        # Save each user's trained model separately in the trainer folder
        recognizer.write(os.path.join(trainer_path, f"trainer_{face_id}.yml"))
        print(f"Model trained and saved for user ID {face_id}.")

print("All models trained and saved.")
