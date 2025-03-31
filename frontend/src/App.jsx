import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import styles from "./faceAuth.module.css";
import Chatbot from "./chatbot";

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [authStatus, setAuthStatus] = useState("");

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);


  const FACE_AUTH_API = "http://127.0.0.1:8000"; // Update this to your face auth API endpoint

  useEffect(() => {
    return () => {
      // Clean up video stream when component unmounts
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    setIsCapturing(true);
    setAuthStatus("Starting camera...");
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "user" } 
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setAuthStatus("Camera active. Please look directly at the camera.");
    } catch (err) {
      console.error("Error accessing camera:", err);
      setAuthStatus("Error: Unable to access camera. Please check permissions.");
      setIsCapturing(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCapturing(false);
  };

  // This is a modification for the captureImage function in your App.jsx file

  // Replace the captureImage function in your App.jsx file
const captureImage = () => {
  if (!videoRef.current || !canvasRef.current) return null;
  
  const canvas = canvasRef.current;
  const video = videoRef.current;
  const context = canvas.getContext("2d");
  
  // Set canvas dimensions
  canvas.width = 320;  // Keep the size moderate
  canvas.height = 240; // Keep the size moderate
  
  // Draw the video frame to the canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  // Get JPEG image data (important to use JPEG format)
  const imageData = canvas.toDataURL("image/jpeg", 0.8);
  
  console.log(`Captured image data length: ${imageData.length}`);
  
  return imageData;
};

// Also update the registerFace function for better debugging
const registerFace = async () => {
  setAuthStatus("Registering face...");
  
  try {
    const imageData = captureImage();
    if (!imageData) {
      setAuthStatus("Error: Could not capture image");
      return;
    }
    
    console.log("Image data length:", imageData.length);
    console.log("Image data starts with:", imageData.substring(0, 50));
    
    // Verify image is properly formatted
    if (!imageData.startsWith("data:image/jpeg;base64,")) {
      setAuthStatus("Error: Invalid image format. Expected JPEG format.");
      return;
    }
    
    console.log("Sending registration request...");
    
    const response = await axios.post(`${FACE_AUTH_API}/register`, {
      image: imageData
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log("Registration response:", response);
    
    if (response.data.message) {
      setAuthStatus("Registration successful! You can now authenticate.");
    } else {
      setAuthStatus("Registration failed. Please try again.");
    }
  } catch (error) {
    console.error("Registration error:", error);
    if (error.response) {
      console.error("Error data:", error.response.data);
      console.error("Error status:", error.response.status);
      setAuthStatus(`Error during registration: ${error.response.data.error || 'Unknown error'}`);
    } else if (error.request) {
      console.error("No response received:", error.request);
      setAuthStatus("Error: Server did not respond. Check if the server is running.");
    } else {
      console.error("Error message:", error.message);
      setAuthStatus(`Error during registration: ${error.message}`);
    }
  }
};

// Similarly update the authenticateFace function
const authenticateFace = async () => {
  setAuthStatus("Authenticating...");
  
  try {
    const imageData = captureImage();
    if (!imageData) {
      setAuthStatus("Error: Could not capture image");
      return;
    }
    
    console.log("Auth image data length:", imageData.length);
    
    const response = await axios.post(`${FACE_AUTH_API}/authenticate`, {
      image: imageData
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.data.authenticated) {
      setAuthStatus("Authentication successful!");
      stopCamera();
      setIsAuthenticated(true);
    } else {
      setAuthStatus("Authentication failed. Please try again.");
    }
  } catch (error) {
    console.error("Authentication error:", error);
    if (error.response) {
      setAuthStatus(`Error: ${error.response.data.error || "Authentication failed"}`);
    } else {
      setAuthStatus("Error during authentication. Please try again.");
    }
  }
};


  // Render authentication page
  if (!isAuthenticated) {
    return (
      <div className={styles["auth-container"]}>
        <div className={styles["auth-card"]}>
          <h1>JANI - Your Personal Assistant</h1>
          <p>Please authenticate yourself to continue</p>
          
          <div className={styles["video-container"]}>
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className={isCapturing ? styles["video-visible"] : styles["video-hidden"]}
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </div>
          
          <div className={styles["auth-status"]}>{authStatus}</div>
          
          <div className={styles["auth-buttons"]}>
          {!isCapturing ? (
            <>
              <button onClick={startCamera} className={styles["auth-button"]}>
                Start Face Authentication
              </button>
              <button onClick={startCamera} className={`${styles["auth-button"]} ${styles["register-button"]}`}>
                Register New Face
              </button>
            </>
          ) : (
            <div className={styles["capture-buttons"]}>
              <button onClick={authenticateFace} className={styles["verify-button"]}>
                Verify Identity
              </button>
              <button onClick={registerFace} className={styles["register-button"]}>
                Register Face
              </button>
              <button onClick={stopCamera} className={styles["cancel-button"]}>
                Cancel
              </button>
            </div>
          )}
        </div>
        </div>
      </div>
    );
  }
  else{
    return <Chatbot/>
  }
};
//   // Render chatbot interface after authentication
//   return (  
//     <div className="chat-container">
//       <h2>JANI AI Assistant</h2>

//       <h3>Helps you Navigate through your System!</h3>

//       <textarea
//         value={query}
//         onChange={(e) => setQuery(e.target.value)}
//         placeholder="Ask me anything..."
//       />

//       <div className="button-group">
//         <button onClick={() => setMode("ask")} className={mode === "ask" ? "active" : ""}>
//           Fine-Tuned Chat
//         </button>

//         <button onClick={() => setMode("general_chat")} className={mode === "general_chat" ? "active" : ""}>
//            Open Chat
//         </button>
//       </div>

//       <button onClick={handleSend} disabled={loading}>
//         {loading ? "Thinking..." : "Ask AI"}
//       </button>

//       <button onClick={handleVoiceCommand} disabled={loading}>
//         🎙 Speak to JANI
//       </button>

//       {response && (
//         <div className="response-box">
//           <p><strong>Input:</strong> {response.input}</p>
//           <p><strong>Output:</strong> {response.output}</p>
//         </div>
//       )}
//     </div>
//   );
// };

export default App;