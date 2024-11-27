import cv2
import os

# Set the path to the desired folder on the Desktop
base_path = r"C:\Users\Somu\Desktop\J.A.R.V.I.S-master\Face-Recognition\samples"
if not os.path.exists(base_path):
    os.makedirs(base_path)

# Initialize the camera
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cam.isOpened():
    print("Error: Camera not accessible. Check your camera connection.")
    exit()

cam.set(3, 640)  # Set video FrameWidth
cam.set(4, 480)  # Set video FrameHeight

# Load the face detection model
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if detector.empty():
    print("Error: Unable to load Haar cascade. Check your OpenCV installation.")
    exit()

# User ID input
face_id = input("Enter a Numeric user ID here: ")
# Create a directory for the specific user inside the samples folder
user_folder = os.path.join(base_path, f"user_{face_id}")
if not os.path.exists(user_folder):
    os.makedirs(user_folder)

print("Taking samples, look at the camera .......")
count = 0
total_samples = 100  # Set the desired number of images to capture

while count < total_samples:  # Continue until 60 images are captured
    ret, img = cam.read()
    if not ret:
        print("Failed to grab frame, exiting...")
        break

    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(converted_image, 1.3, 5)

    for (x, y, w, h) in faces:
        # Draw rectangle around detected face
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Save the cropped face
        face_cropped = converted_image[y:y + h, x:x + w]
        if face_cropped.size > 0:  # Ensure the cropped face is not empty
            count += 1
            file_path = os.path.join(user_folder, f"face_{face_id}_{count}.jpg")
            cv2.imwrite(file_path, face_cropped)
            print(f"Saved: {file_path}")

        # Break the loop if enough images are captured
        if count >= total_samples:
            break

    # Display the video frame with rectangles
    cv2.imshow('image', img)

    # Exit on 'ESC' key
    if cv2.waitKey(1) & 0xFF == 27:
        print("ESC pressed, exiting...")
        break

print(f"{count} samples taken, now closing the program...")
cam.release()
cv2.destroyAllWindows()
