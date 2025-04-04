// import React, { useState, useEffect, useRef } from "react";
// import axios from "axios";
// import "./Chatbot.css";

// const Chatbot = () => {
//   const [query, setQuery] = useState("");
//   const [response, setResponse] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [mode, setMode] = useState("ask"); // "ask" for fine-tuned, "general_chat" for general
//   const [conversations, setConversations] = useState([]);
//   const [sidebarOpen, setSidebarOpen] = useState(true);
//   const [wakeWordEnabled, setWakeWordEnabled] = useState(false);
//   const [wakeWordStatus, setWakeWordStatus] = useState("Disabled");
  
//   const messagesEndRef = useRef(null);
//   const inputRef = useRef(null);
//   const recognitionRef = useRef(null);

//   const API_BASE_URL = "https://d616-34-106-118-230.ngrok-free.app";
//   const LOCAL_VOICE_API = "http://127.0.0.1:8001";

//   // Load conversation history from localStorage on component mount
//   useEffect(() => {
//     const savedConversations = localStorage.getItem('jani_conversations');
//     if (savedConversations) {
//       try {
//         setConversations(JSON.parse(savedConversations));
//       } catch (e) {
//         console.error("Error parsing saved conversations:", e);
//       }
//     }
//   }, []);

//   // Scroll to bottom of conversation whenever new messages are added
//   useEffect(() => {
//     if (messagesEndRef.current) {
//       messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
//     }
//   }, [conversations]);

//   // Focus input field when component loads
//   useEffect(() => {
//     if (inputRef.current) {
//       inputRef.current.focus();
//     }
//   }, []);

//   // Clean up recognition when component unmounts
//   useEffect(() => {
//     return () => {
//       if (recognitionRef.current) {
//         recognitionRef.current.abort();
//       }
//     };
//   }, []);

//   // Effect to manage wake word detection
//   useEffect(() => {
//     if (wakeWordEnabled) {
//       startWakeWordDetection();
//     } else {
//       stopWakeWordDetection();
//     }
//   }, [wakeWordEnabled]);

//   const saveConversation = (newConversation) => {
//     const updatedConversations = [...conversations, newConversation];
//     setConversations(updatedConversations);
    
//     // Save to localStorage (acting as our simple "database")
//     localStorage.setItem('jani_conversations', JSON.stringify(updatedConversations));
//   };

//   const clearConversations = () => {
//     setConversations([]);
//     localStorage.removeItem('jani_conversations');
//   };

//   const handleSend = async () => {
//     if (!query.trim()) return;
//     setLoading(true);

//     try {
//       const endpoint = mode === "ask" ? "/ask" : "/general_chat";
//       const res = await axios.post(`${API_BASE_URL}${endpoint}`, { query });

//       const newResponse = { 
//         input: query, 
//         output: res.data.response || "No response received.",
//         timestamp: new Date().toISOString(),
//         mode
//       };
      
//       setResponse(newResponse);
//       saveConversation(newResponse);
//     } catch (error) {
//       console.error("Error fetching response:", error);
//       const errorResponse = { 
//         input: query, 
//         output: "Error: Unable to fetch response.",
//         timestamp: new Date().toISOString(),
//         mode,
//         error: true
//       };
      
//       setResponse(errorResponse);
//       saveConversation(errorResponse);
//     } finally {
//       setLoading(false);
//       setQuery("");
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSend();
//     }
//   };

//   const startWakeWordDetection = () => {
//     if (!window.webkitSpeechRecognition) {
//       alert("Voice recognition is not supported in this browser.");
//       setWakeWordEnabled(false);
//       return;
//     }

//     try {
//       // Create a new recognition instance if one doesn't exist
//       if (!recognitionRef.current) {
//         recognitionRef.current = new window.webkitSpeechRecognition();
//         recognitionRef.current.continuous = true;
//         recognitionRef.current.interimResults = true;
//         recognitionRef.current.lang = "en-IN";
//       }

//       // Set up event handlers
//       recognitionRef.current.onresult = handleRecognitionResult;
//       recognitionRef.current.onerror = handleRecognitionError;
//       recognitionRef.current.onend = handleRecognitionEnd;
      
//       // Start recognition
//       recognitionRef.current.start();
//       setWakeWordStatus("Listening for 'Hey Jani'");
//       console.log("Wake word detection started");
//     } catch (error) {
//       console.error("Error starting wake word detection:", error);
//       setWakeWordEnabled(false);
//       setWakeWordStatus("Failed to start");
//     }
//   };

//   const stopWakeWordDetection = () => {
//     if (recognitionRef.current) {
//       try {
//         recognitionRef.current.stop();
//         setWakeWordStatus("Disabled");
//         console.log("Wake word detection stopped");
//       } catch (error) {
//         console.error("Error stopping wake word detection:", error);
//       }
//     }
//   };

//   const handleRecognitionResult = (event) => {
//     // Get the transcript of what was heard
//     const transcript = Array.from(event.results)
//       .map(result => result[0].transcript.toLowerCase())
//       .join(' ');
    
//     console.log("Heard:", transcript);
    
//     // Check if the wake word is in the transcript
//     if (transcript.includes("hey jani") || 
//         transcript.includes("hey johnny") || 
//         transcript.includes("hey jenny") || 
//         transcript.includes("hey jaani")) {
      
//       // Temporarily pause listening to avoid duplicate triggers
//       if (recognitionRef.current) {
//         recognitionRef.current.stop();
//       }
      
//       // Visual feedback
//       setWakeWordStatus("Wake word detected! Processing command...");
      
//       // Extract the command that comes after the wake word
//       let command = transcript;
      
//       // Use regex to find and remove the wake word pattern
//       const wakeWordPattern = /(hey jani|hey johnny|hey jenny|hey jaani)/i;
//       const match = transcript.match(wakeWordPattern);
      
//       if (match) {
//         // Extract only what comes after the wake word
//         const wakeWordIndex = transcript.indexOf(match[0]);
//         if (wakeWordIndex !== -1) {
//           command = transcript.substring(wakeWordIndex + match[0].length).trim();
//         }
//       }
      
//       // If there's a command after the wake word, process it
//       if (command && command !== transcript) {
//         console.log("Command extracted:", command);
//         processVoiceCommand(command);
//       } else {
//         // If there's no clear command after "Hey Jani", wait for the next input
//         console.log("No command after wake word, activating voice input");
//         setTimeout(() => {
//           handleVoiceCommand();
//         }, 500);
//       }
//     }
//   };

//   const handleRecognitionError = (event) => {
//     console.error("Recognition error:", event.error);
    
//     // Handle various error types
//     if (event.error === 'no-speech') {
//       setWakeWordStatus("No speech detected. Still listening...");
//     } else if (event.error === 'audio-capture') {
//       setWakeWordStatus("Microphone issue. Please check your device.");
//       setWakeWordEnabled(false);
//     } else if (event.error === 'not-allowed') {
//       setWakeWordStatus("Microphone access denied. Please enable permissions.");
//       setWakeWordEnabled(false);
//     } else {
//       setWakeWordStatus(`Error: ${event.error}`);
//     }
//   };

//   const handleRecognitionEnd = () => {
//     console.log("Recognition ended");
    
//     // Restart recognition if it's still enabled
//     if (wakeWordEnabled && recognitionRef.current) {
//       try {
//         recognitionRef.current.start();
//         console.log("Restarting recognition");
//       } catch (error) {
//         console.error("Error restarting recognition:", error);
//         // If we can't restart immediately, try again after a short delay
//         setTimeout(() => {
//           if (wakeWordEnabled) {
//             startWakeWordDetection();
//           }
//         }, 300);
//       }
//     }
//   };

//   const speakResponse = (text) => {
//     if ('speechSynthesis' in window) {
//       const utterance = new SpeechSynthesisUtterance(text);
//       utterance.rate = 1;
//       utterance.pitch = 1;
      
//       const voices = window.speechSynthesis.getVoices();
//       if (voices.length > 0) {
//         const indianVoice = voices.find(voice => 
//           voice.lang.includes('en-IN') || voice.lang.includes('en-GB')
//         );
//         if (indianVoice) {
//           utterance.voice = indianVoice;
//         }
//       }

//       window.speechSynthesis.speak(utterance);
//     } else {
//       console.warn("Text-to-speech not supported");
//     }
//   };

//   const processVoiceCommand = async (command) => {
//     setQuery(command);
//     setLoading(true);

//     try {
//       const res = await axios.post(`${LOCAL_VOICE_API}/voice_command`, 
//         { command },
//         {
//           headers: {'Content-Type': 'application/json'}
//         }
//       );

//       let newResponse;
      
//       if (res.data.status === 'success') {
//         newResponse = {
//           input: command,
//           output: res.data.message || "Command executed successfully",
//           action: res.data.action,
//           timestamp: new Date().toISOString(),
//           mode: "voice",
//           voiceCommand: true
//         };
//         setResponse(newResponse);
//         speakResponse(newResponse.output);
//       } else {
//         newResponse = {
//           input: command,
//           output: res.data.message || "Command processing failed",
//           action: "error",
//           timestamp: new Date().toISOString(),
//           mode: "voice",
//           voiceCommand: true,
//           error: true
//         };
//         setResponse(newResponse);
//         speakResponse(newResponse.output);
//       }
      
//       saveConversation(newResponse);
//     } catch (error) {
//       console.error("Error processing voice command:", error);
      
//       const errorResponse = {
//         input: command,
//         output: "Network or server error occurred",
//         action: "network_error",
//         timestamp: new Date().toISOString(),
//         mode: "voice",
//         voiceCommand: true,
//         error: true
//       };
      
//       setResponse(errorResponse);
//       saveConversation(errorResponse);
//       speakResponse(errorResponse.output);
//     } finally {
//       setLoading(false);
      
//       // Resume wake word detection after a short delay
//       setTimeout(() => {
//         if (wakeWordEnabled) {
//           setWakeWordStatus("Listening for 'Hey Jani'");
//           if (!recognitionRef.current) {
//             startWakeWordDetection();
//           }
//         }
//       }, 2000);
//     }
//   };

//   const handleVoiceCommand = async () => {
//     if (!window.webkitSpeechRecognition) {
//       alert("Voice recognition is not supported in this browser.");
//       return;
//     }

//     try {
//       const recognition = new window.webkitSpeechRecognition();
//       recognition.lang = "en-IN";
//       recognition.start();

//       recognition.onresult = async (event) => {
//         const voiceCommand = event.results[0][0].transcript;
//         processVoiceCommand(voiceCommand);
//       };

//       recognition.onerror = (event) => {
//         console.error("Voice recognition error:", event);
//         const errorResponse = {
//           input: "Voice Recognition Error",
//           output: "An error occurred during voice recognition",
//           action: "recognition_error",
//           timestamp: new Date().toISOString(),
//           mode: "voice",
//           voiceCommand: true,
//           error: true
//         };
        
//         setResponse(errorResponse);
//         saveConversation(errorResponse);
//         speakResponse(errorResponse.output);
//       };
//     } catch (error) {
//       console.error("Error initializing voice recognition:", error);
//     }
//   };

//   const toggleWakeWordDetection = () => {
//     setWakeWordEnabled(!wakeWordEnabled);
//   };

//   const formatTimestamp = (timestamp) => {
//     const date = new Date(timestamp);
//     return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
//   };

//   return (
//     <div className={`app-container ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
//       {/* Sidebar toggle button - moved outside the sidebar */}
//       <button 
//         className="sidebar-toggle-btn"
//         onClick={() => setSidebarOpen(!sidebarOpen)}
//       >
//         {sidebarOpen ? '◀' : '▶'}
//       </button>
      
//       {/* Wake word status indicator */}
//       <div className={`wake-word-status ${wakeWordEnabled ? 'active' : 'inactive'}`}>
//         {wakeWordStatus}
//       </div>
      
//       {/* Sidebar for conversation history */}
//       <div className="sidebar">
//         <div className="sidebar-header">
//           <h3>Conversation History</h3>
//           <div className="sidebar-actions">
//             <button className="clear-btn" onClick={clearConversations}>Clear All</button>
//           </div>
//         </div>
        
//         <div className="conversation-list">
//           {conversations.length === 0 ? (
//             <div className="no-conversations">No conversations yet</div>
//           ) : (
//             conversations.map((item, index) => (
//               <div 
//                 key={index} 
//                 className={`conversation-item ${item.error ? 'error' : ''} ${item.voiceCommand ? 'voice' : item.mode}`}
//               >
//                 <div className="conversation-timestamp">{formatTimestamp(item.timestamp)}</div>
//                 <div className="conversation-input">{item.input}</div>
//                 <div className="conversation-output">{item.output}</div>
//               </div>
//             ))
//           )}
//           <div ref={messagesEndRef} />
//         </div>
//       </div>

//       {/* Main chat interface */}
//       <div className="main-content">
//         <div className="chat-container">
//           <div className="header">
//             <h1>JANI AI Assistant</h1>
//             <h3>Helps you Navigate through your System!</h3>
//           </div>

//           <div className="chat-box">
//             {response && (
//               <div className={`response-box ${response.error ? 'error' : ''}`}>
//                 <div className="response-input">
//                   <span className="label">Input:</span> {response.input}
//                 </div>
//                 <div className="response-output">
//                   <span className="label">Output:</span> {response.output}
//                 </div>
//               </div>
//             )}
//           </div>

//           <div className="input-area">
//             <textarea
//               ref={inputRef}
//               value={query}
//               onChange={(e) => setQuery(e.target.value)}
//               onKeyPress={handleKeyPress}
//               placeholder="Ask me anything..."
//               rows={3}
//             />

//             <div className="controls">
//               <div className="mode-toggle">
//                 <button 
//                   onClick={() => setMode("ask")} 
//                   className={`mode-btn ${mode === "ask" ? "active" : ""}`}
//                 >
//                   Learn About Jani?
//                 </button>

//                 <button 
//                   onClick={() => setMode("general_chat")} 
//                   className={`mode-btn ${mode === "general_chat" ? "active" : ""}`}
//                 >
//                   Open Chat
//                 </button>
//               </div>

//               <div className="action-btns">
//                 <button 
//                   className="send-btn" 
//                   onClick={handleSend} 
//                   disabled={loading}
//                 >
//                   {loading ? "Thinking..." : "Ask AI"}
//                 </button>

//                 <button 
//                   className="voice-btn" 
//                   onClick={handleVoiceCommand} 
//                   disabled={loading}
//                 >
//                   🎙 Speak to JANI
//                 </button>
                
//                 <button 
//                   className={`wake-word-btn ${wakeWordEnabled ? 'active' : ''}`} 
//                   onClick={toggleWakeWordDetection}
//                   disabled={loading}
//                 >
//                   {wakeWordEnabled ? "Disable 'Hey Jani'" : "Enable 'Hey Jani'"}
//                 </button>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Chatbot;