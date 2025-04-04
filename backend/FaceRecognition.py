#FaceRecognition.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import os
import face_recognition
import pickle
import re
import io
from PIL import Image

app = Flask(__name__)
CORS(app)

# Path to save face encodings
FACE_ENCODINGS_PATH = "face_encodings.pkl"

# Load existing face encodings if available
def load_face_encodings():
    if os.path.exists(FACE_ENCODINGS_PATH):
        with open(FACE_ENCODINGS_PATH, "rb") as f:
            return pickle.load(f)
    return {}

# Save face encodings
def save_face_encodings(encodings):
    with open(FACE_ENCODINGS_PATH, "wb") as f:
        pickle.dump(encodings, f)

# New, completely rewritten base64 to image conversion function
def base64_to_image(base64_string):
    try:
        # Clean up the base64 string
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        # Remove any whitespace
        base64_string = re.sub(r'\s', '', base64_string)
        
        # Decode base64 to binary
        img_data = base64.b64decode(base64_string)
        
        # Convert to a numpy array using PIL
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Make sure it's in RGB mode
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL image to numpy array
        image_array = np.array(pil_image)
        
        # Ensure the image has the right data type
        if image_array.dtype != np.uint8:
            image_array = image_array.astype(np.uint8)
        
        # Check the image shape to ensure it's valid
        if len(image_array.shape) != 3 or image_array.shape[2] != 3:
            raise ValueError(f"Invalid image shape: {image_array.shape}")
        
        print(f"Converted image: shape={image_array.shape}, dtype={image_array.dtype}")
        
        return image_array
    
    except Exception as e:
        print(f"Error in base64_to_image: {str(e)}")
        raise

@app.route("/authenticate", methods=["POST"])
def authenticate():
    try:
        data = request.json
        image_data = data.get("image")
        
        if not image_data:
            return jsonify({"error": "No image provided", "authenticated": False}), 400
        
        # Debug image data
        print(f"Auth image data length: {len(image_data)}")
        
        # Convert base64 image to numpy array format
        img = base64_to_image(image_data)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(img)
        
        if not face_locations:
            return jsonify({"error": "No face detected", "authenticated": False}), 400
        
        face_encodings = face_recognition.face_encodings(img, face_locations)
        
        # Load existing face encodings
        known_face_encodings = load_face_encodings()
        
        # If there are no registered users, register this face
        if "authorized_user" not in known_face_encodings:
            known_face_encodings["authorized_user"] = face_encodings[0]
            save_face_encodings(known_face_encodings)
            return jsonify({
                "message": "Face registered successfully",
                "authenticated": True
            })
        
        # Compare face with registered face
        matches = face_recognition.compare_faces(
            [known_face_encodings["authorized_user"]], 
            face_encodings[0],
            tolerance=0.5
        )
        
        if matches[0]:
            return jsonify({
                "message": "Authentication successful",
                "authenticated": True
            })
        else:
            return jsonify({
                "message": "Authentication failed",
                "authenticated": False
            })
            
    except Exception as e:
        print(f"Error in authenticate: {str(e)}")
        return jsonify({"error": str(e), "authenticated": False}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        image_data = data.get("image")
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        # Debug image data
        print(f"Register image data length: {len(image_data)}")
        print(f"Image data type: {type(image_data)}")
        print(f"Image data starts with: {image_data[:50]}")
        
        try:
            # Convert base64 image to numpy array format
            img = base64_to_image(image_data)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(img)
            
            if not face_locations:
                return jsonify({"error": "No face detected in the image"}), 400
            
            face_encodings = face_recognition.face_encodings(img, face_locations)
            
            # Load existing face encodings
            known_face_encodings = load_face_encodings()
            
            # Register or update the face
            known_face_encodings["authorized_user"] = face_encodings[0]
            save_face_encodings(known_face_encodings)
            
            return jsonify({
                "message": "Face registered successfully"
            })
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({"error": f"Image processing failed: {str(e)}"}), 500
            
    except Exception as e:
        print(f"Error in /register: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)