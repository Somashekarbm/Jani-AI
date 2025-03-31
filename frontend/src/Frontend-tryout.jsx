import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("ask"); // "ask" for fine-tuned, "general_chat" for general

  const API_BASE_URL = "https://0e08-34-19-73-88.ngrok-free.app"; // Change to your actual API URL
  const LOCAL_VOICE_API = "http://127.0.0.1:8000"; // Local API for voice commands

  const handleSend = async () => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const endpoint = mode === "ask" ? "/ask" : "/general_chat";
      const res = await axios.post(`${API_BASE_URL}${endpoint}`, { query });

      setResponse({ input: query, output: res.data.response || "No response received." });
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponse({ input: query, output: "Error: Unable to fetch response." });
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  const handleVoiceCommand = async () => {
    if (!window.webkitSpeechRecognition) {
        alert("Voice recognition is not supported in this browser.");
        return;
    }

    // Add text-to-speech function
    const speakResponse = (text) => {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            // Optional: Customize voice, rate, pitch
            utterance.rate = 1; // Speed of speech
            utterance.pitch = 1; // Pitch of speech
            
            // You can choose a specific voice if needed
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {
                // Try to find an Indian English voice
                const indianVoice = voices.find(voice => 
                    voice.lang.includes('en-IN') || voice.lang.includes('en-GB')
                );
                if (indianVoice) {
                    utterance.voice = indianVoice;
                }
            }

            window.speechSynthesis.speak(utterance);
        } else {
            console.warn("Text-to-speech not supported");
        }
    };

    try {
        const recognition = new window.webkitSpeechRecognition();
        recognition.lang = "en-IN";
        recognition.start();

        recognition.onresult = async (event) => {
            const voiceCommand = event.results[0][0].transcript;
            setQuery(voiceCommand);
            setLoading(true);

            try {
                const res = await axios.post(`${LOCAL_VOICE_API}/voice_command`, 
                    { command: voiceCommand },
                    {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    }
                );

                // Handle different response statuses
                if (res.data.status === 'success') {
                    const responseData = {
                        input: voiceCommand,
                        output: res.data.message || "Command executed successfully",
                        action: res.data.action
                    };
                    setResponse(responseData);

                    // Speak the response
                    speakResponse(responseData.output);
                } else {
                    const errorResponse = {
                        input: voiceCommand,
                        output: res.data.message || "Command processing failed",
                        action: "error"
                    };
                    setResponse(errorResponse);

                    // Speak the error message
                    speakResponse(errorResponse.output);
                }
            } catch (error) {
                console.error("Error processing voice command:", error);
                
                const errorResponse = {
                    input: voiceCommand,
                    output: "Network or server error occurred",
                    action: "network_error"
                };
                setResponse(errorResponse);

                // Speak the error message
                speakResponse(errorResponse.output);
            } finally {
                setLoading(false);
            }
        };

        recognition.onerror = (event) => {
            console.error("Voice recognition error:", event);
            const errorResponse = {
                input: "Voice Recognition Error",
                output: "An error occurred during voice recognition",
                action: "recognition_error"
            };
            setResponse(errorResponse);

            // Speak the error message
            speakResponse(errorResponse.output);
        };
    } catch (error) {
        console.error("Error initializing voice recognition:", error);
    }
};

  return (
    <div className="chat-container">
      <h2>JANI AI Assistant</h2>

      <h3>Helps you Navigate through your System!</h3>

      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask me anything..."
      />

      <div className="button-group">
        <button onClick={() => setMode("ask")} className={mode === "ask" ? "active" : ""}>
          Fine-Tuned Chat
        </button>

        <button onClick={() => setMode("general_chat")} className={mode === "general_chat" ? "active" : ""}>
           Open Chat
        </button>
      </div>

      <button onClick={handleSend} disabled={loading}>
        {loading ? "Thinking..." : "Ask AI"}
      </button>

      <button onClick={handleVoiceCommand} disabled={loading}>
        🎙 Speak to JANI
      </button>

      {response && (
        <div className="response-box">
          <p><strong>Input:</strong> {response.input}</p>
          <p><strong>Output:</strong> {response.output}</p>
        </div>
      )}
    </div>
  );
};

export default Chatbot;





