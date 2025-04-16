// chatbot.jsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./Chatbot.css";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("ask"); // "ask" for fine-tuned, "general_chat" for general
  const [conversations, setConversations] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const API_BASE_URL = "https://5df9-34-69-196-141.ngrok-free.app";  //remove '/' after the url everytime to run the chat API endpoint 
  const LOCAL_VOICE_API = "http://127.0.0.1:8010";

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('jani_conversations');
    if (savedConversations) {
      try {
        setConversations(JSON.parse(savedConversations));
      } catch (e) {
        console.error("Error parsing saved conversations:", e);
      }
    }
  }, []);

  // Scroll to bottom of conversation whenever new messages are added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversations]);

  // Focus input field when component loads
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const saveConversation = (newConversation) => {
    const updatedConversations = [...conversations, newConversation];
    setConversations(updatedConversations);
    
    // Save to localStorage (acting as our simple "database")
    localStorage.setItem('jani_conversations', JSON.stringify(updatedConversations));
    
    // In a real app, you would also save to a database here
    // Example: axios.post(`${API_BASE_URL}/save_conversation`, { conversation: newConversation });
  };

  const clearConversations = () => {
    setConversations([]);
    localStorage.removeItem('jani_conversations');
    // Also delete from database in a real app
    // Example: axios.delete(`${API_BASE_URL}/clear_conversations`);
  };

  const handleSend = async () => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const endpoint = mode === "ask" ? "/ask" : "/general_chat";
      const res = await axios.post(`${API_BASE_URL}${endpoint}`, { query });


        if (res.data.action === "exit_assistant") {
          alert("Thanks for using my services! The assistant will now close.");
          setTimeout(() => {
              window.close();
          }, 1000);
          return;
      }
    
      const newResponse = { 
        input: query, 
        output: res.data.response || "No response received.",
        timestamp: new Date().toISOString(),
        mode
      };
      
      setResponse(newResponse);
      saveConversation(newResponse);
    } catch (error) {
      console.error("Error fetching response:", error);
      const errorResponse = { 
        input: query, 
        output: "Error: Unable to fetch response.",
        timestamp: new Date().toISOString(),
        mode,
        error: true
      };
      
      setResponse(errorResponse);
      saveConversation(errorResponse);
    } finally {
      setLoading(false);
      setQuery("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
            utterance.rate = 1;
            utterance.pitch = 1;
            
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {
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
        setLoading(true);
        
        // Show user feedback that we're listening
        setQuery("Listening...");
        
        // Call the FastAPI endpoint to record and recognize speech
        const recordingResponse = await axios.post(`${LOCAL_VOICE_API}/record_voice`);
        
        if (recordingResponse.data.status === "success") {
          const voiceCommand = recordingResponse.data.text;
          setQuery(voiceCommand);
          
          // Process the recognized command
          const res = await axios.post(`${LOCAL_VOICE_API}/voice_command`, 
              { command: voiceCommand },
              {
                  headers: {
                      'Content-Type': 'application/json'
                  }
              }
          );
    
          if (res.data.action === "exit_assistant") {
            alert("Thanks for using my services! The assistant will now close.");
            setTimeout(() => {
                window.close();
            }, 1000);
            return;
          }
          
          let newResponse;
          
          if (res.data.status === 'success') {
              newResponse = {
                  input: voiceCommand,
                  output: res.data.message || "Command executed successfully",
                  action: res.data.action,
                  timestamp: new Date().toISOString(),
                  mode: "voice",
                  voiceCommand: true
              };
              setResponse(newResponse);
              speakResponse(newResponse.output);
          } else {
              newResponse = {
                  input: voiceCommand,
                  output: res.data.message || "Command processing failed",
                  action: "error",
                  timestamp: new Date().toISOString(),
                  mode: "voice",
                  voiceCommand: true,
                  error: true
              };
              setResponse(newResponse);
              speakResponse(newResponse.output);
          }
          
          saveConversation(newResponse);
        } else {
          // Handle recording error
          const errorResponse = {
              input: "Voice Recognition Error",
              output: recordingResponse.data.message || "An error occurred during voice recognition",
              action: "recognition_error",
              timestamp: new Date().toISOString(),
              mode: "voice",
              voiceCommand: true,
              error: true
          };
          
          setResponse(errorResponse);
          saveConversation(errorResponse);
          speakResponse(errorResponse.output);
        }
      } catch (error) {
        console.error("Error initializing voice recognition:", error);
        const errorResponse = {
            input: "Voice Recognition Error",
            output: "Network or server error occurred",
            action: "network_error",
            timestamp: new Date().toISOString(),
            mode: "voice",
            voiceCommand: true,
            error: true
        };
        
        setResponse(errorResponse);
        saveConversation(errorResponse);
        speakResponse(errorResponse.output);
      } finally {
        setLoading(false);
      }
    };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  };

  return (
    <div className={`app-container ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      {/* Sidebar toggle button - moved outside the sidebar */}
      <button 
        className="sidebar-toggle-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? '◀' : '▶'}
      </button>
      
      {/* Sidebar for conversation history */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h3>Conversation History</h3>
          <div className="sidebar-actions">
            <button className="clear-btn" onClick={clearConversations}>Clear All</button>
          </div>
        </div>
        
        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div className="no-conversations">No conversations yet</div>
          ) : (
            conversations.map((item, index) => (
              <div 
                key={index} 
                className={`conversation-item ${item.error ? 'error' : ''} ${item.voiceCommand ? 'voice' : item.mode}`}
              >
                <div className="conversation-timestamp">{formatTimestamp(item.timestamp)}</div>
                <div className="conversation-input">{item.input}</div>
                <div className="conversation-output">{item.output}</div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Main chat interface */}
      <div className="main-content">
        <div className="chat-container">
          <div className="header">
            <h1>JANI AI Assistant</h1>
            <h3>Helps you Navigate through your System!</h3>
          </div>

          <div className="chat-box">
            {response && (
              <div className={`response-box ${response.error ? 'error' : ''}`}>
                <div className="response-input">
                  <span className="label">Input:</span> {response.input}
                </div>
                <div className="response-output">
                  <span className="label">Output:</span> {response.output}
                </div>
              </div>
            )}
          </div>

          <div className="input-area">
            <textarea
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              rows={3}
            />

            <div className="controls">
              <div className="mode-toggle">
                <button 
                  onClick={() => setMode("ask")} 
                  className={`mode-btn ${mode === "ask" ? "active" : ""}`}
                >
                  Learn About Jani?
                </button>

                <button 
                  onClick={() => setMode("general_chat")} 
                  className={`mode-btn ${mode === "general_chat" ? "active" : ""}`}
                >
                  Open Chat
                </button>
              </div>

              <div className="action-btns">
                <button 
                  className="send-btn" 
                  onClick={handleSend} 
                  disabled={loading}
                >
                  {loading ? "Thinking..." : "Ask AI"}
                </button>

                <button 
                  className="voice-btn" 
                  onClick={handleVoiceCommand} 
                  disabled={loading}
                >
                  🎙 Speak to JANI
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;