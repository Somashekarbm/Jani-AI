const fs = require('fs');
const path = require('path');

// Get the backend path relative to the frontend directory
const backendDir = path.join(__dirname, '../../backend');

// Create voice recognition batch file
const voiceTemplate = fs.readFileSync(
  path.join(backendDir, 'fastapi_app/start_voice_recog.bat.template'), 
  'utf8'
);
fs.writeFileSync(
  path.join(backendDir, 'fastapi_app/start_voice_recog.bat'),
  voiceTemplate
);

// Create face recognition batch file
const faceTemplate = fs.readFileSync(
  path.join(backendDir, 'flask_app/start_face_recog.bat.template'), 
  'utf8'
);
fs.writeFileSync(
  path.join(backendDir, 'flask_app/start_face_recog.bat'),
  faceTemplate
);

console.log('Batch files created successfully');