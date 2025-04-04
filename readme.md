# JANI AI - A Virtual Companion - Just in Time Assistant for Necessary Insights

JANI AI is an AI-powered voice/text assistant with features like OCR, face recognition, conversational AI with memory, app automation, search functionalities, music & mood-based recommendations, screenshot capture, note-taking, news updates, document summarization, email & chat automation, AI-powered coding assistance, voice-based file search.

## Features
- Voice and text-based interaction
- Conversational AI with memory
- App automation
- AI-powered coding assistance
- News updates and document summarization
- Screenshot capture and note-taking
- Face recognition 


## Tech Stack
- **Backend**: FastAPI, Flask (for Face Recognition), Python, Open-source LLMs
- **Frontend**: React (Vite), Tailwind CSS
- **Database**: SQLite / PostgreSQL (Configurable)
- **LLM Integration**: Hugging Face models
- **Deployment**: NGROK for Colab, Uvicorn for local server

## Setup

### Prerequisites
- Python 3.8+
- Node.js & npm (for frontend)
- Virtual environment (optional but recommended)
- NGROK (if running backend on Colab)

### Backend Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/jani-ai.git
   cd jani-ai
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
5. If running on Google Colab, use NGROK to expose the local server:
   ```sh
   !ngrok authtoken YOUR_NGROK_AUTH_TOKEN
   !ngrok http 8000
   ```

### Face Recognition Server (Flask)
1. Navigate to the backend directory (if applicable):
   ```sh
   cd backend
   ```
2. Create a virtual environment using Python 3.10:
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install necessary packages:
   ```sh
   pip install cmake face_recognition
   pip install -r requirements.txt  # if additional dependencies are listed
   ```
4. Download and install the `dlib` package available in the repo if necessary and there might an error with this package as of date.
5. Run the Flask server:
   ```sh
   python FaceRecognition.py
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm run dev
   ```

## API Endpoints
### 1. General Chat
- **Endpoint**: `POST /general_chat/`
- **Description**: Handles general chat queries using LLMs.
- **Request Body**:
  ```json
  {
    "query": "What is AI?"
  }
  ```
- **Response**:
  ```json
  {
    "response": "AI stands for Artificial Intelligence."
  }
  ```

### 2. Ask AI
- **Endpoint**: `POST /ask/`
- **Description**: Provides AI-powered responses based on contextual memory.
- **Request Body**:
  ```json
  {
    "query": "Summarize this article"
  }
  ```
- **Response**:
  ```json
  {
    "summary": "This article discusses..."
  }
  ```

### 3. Face Authentication
- **Using the Flask backend**: `POST /authenticate_user` and `POST /register_user`
- return response of face recognition success or failure to the frontend for display


### 4. Voice Command Processing
- **Endpoint**: `POST /voice_command/`
- **Description**: Processes voice commands such as opening apps, taking notes, setting reminders, and searching Wikipedia.
- **Request Body**:
  ```json
  {
    "command": "search google for AI advancements"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "message": "Searching Google for AI advancements",
    "action": "google_search"
  }
  ```

## Deployment
- For local deployment, run `uvicorn main:app --host 0.0.0.0 --port 8000`
- Use NGROK for exposing the backend if running on Google Colab
- Frontend can be deployed using Vercel or Netlify

## Contribution
Feel free to contribute by creating a pull request or reporting issues.


