import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import './output.css'
// import App from './App.jsx'
// import Chatbot from './chatbot'
import Chatbot2 from './Frontend-tryout'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Chatbot2 />
  </StrictMode>,
)
