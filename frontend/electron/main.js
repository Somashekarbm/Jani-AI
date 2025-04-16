const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const isDev = process.env.NODE_ENV === 'development' || 
              !app.isPackaged;

let mainWindow;
let voiceCommandProcess;
let faceRecogProcess;

// Function to get the correct app path regardless of development or production
function getAppPath() {
  return isDev 
    ? path.join(__dirname, '../..') // In dev, we're in frontend/electron
    : path.join(process.resourcesPath); // In prod, use the resources path
}

// Function to log messages to a file
function logToFile(message) {
  const logPath = path.join(app.getPath('userData'), 'app.log');
  fs.appendFileSync(logPath, `${new Date().toISOString()}: ${message}\n`);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const startURL = isDev
    ? 'http://localhost:5173'
    : `file://${path.join(__dirname, '../dist/index.html')}`;

  mainWindow.loadURL(startURL);
  
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

function startSubprocess(scriptName, processName) {
  // Determine path based on environment
  const baseDir = isDev 
    ? path.join(__dirname, '../../backend') 
    : path.join(process.resourcesPath, 'backend');
    
  let batPath;
  
  if (scriptName === 'voice') {
    batPath = path.join(baseDir, 'fastapi_app/start_voice_recog.bat');
  } else if (scriptName === 'face') {
    batPath = path.join(baseDir, 'flask_app/start_face_recog.bat');
  }

  // Verify if the batch file exists
  if (!fs.existsSync(batPath)) {
    const errorMsg = `Error: ${processName} batch file not found at: ${batPath}`;
    logToFile(errorMsg);
    dialog.showErrorBox('Startup Error', errorMsg);
    return null;
  }

  // Log the start attempt
  logToFile(`Starting ${processName} from: ${batPath}`);
  
  const cwd = path.dirname(batPath);
  logToFile(`Working directory: ${cwd}`);
  
  try {
    // For Windows, we need to use cmd to run batch files
    const process = spawn('cmd.exe', ['/c', batPath], {
      cwd: cwd,
      detached: false,
      shell: true,
      stdio: ['ignore', 'pipe', 'pipe'], // Redirect stdout and stderr
      env: {
        ...process.env,
        // Add any environment variables needed by the Python processes
        PYTHONUNBUFFERED: '1' // Ensures Python output is not buffered
      }
    });

    // Log process ID
    logToFile(`${processName} started with PID: ${process.pid}`);
    
    // Handle process output for debugging
    process.stdout.on('data', (data) => {
      logToFile(`${processName} stdout: ${data.toString().trim()}`);
    });
    
    process.stderr.on('data', (data) => {
      logToFile(`${processName} stderr: ${data.toString().trim()}`);
    });
    
    // Handle process exit
    process.on('exit', (code) => {
      logToFile(`${processName} exited with code: ${code}`);
      if (code !== 0) {
        dialog.showErrorBox('Process Error', 
          `${processName} exited with code ${code}. Check app.log for details.`);
      }
    });
    
    // Handle process error
    process.on('error', (err) => {
      logToFile(`${processName} error: ${err.message}`);
      dialog.showErrorBox('Process Error', 
        `Failed to start ${processName}: ${err.message}`);
    });
    
    return process;
  } catch (error) {
    logToFile(`Exception when starting ${processName}: ${error.message}`);
    dialog.showErrorBox('Startup Error', 
      `Failed to start ${processName}: ${error.message}`);
    return null;
  }
}

app.whenReady().then(() => {
  // Log the app paths for debugging
  logToFile(`App path: ${app.getAppPath()}`);
  logToFile(`User data path: ${app.getPath('userData')}`);
  
  // Run VoiceCommand.py FastAPI
  voiceCommandProcess = startSubprocess('voice', 'Voice Command API');
  
  // Run the batch file to start Flask FaceRecognition
  faceRecogProcess = startSubprocess('face', 'Face Recognition API');
  
  // Create main window
  createWindow();
});

// Properly clean up processes when closing the app
app.on('window-all-closed', () => {
  logToFile('App closing - cleaning up processes');
  
  if (voiceCommandProcess && !voiceCommandProcess.killed) {
    logToFile(`Terminating voice command process (PID: ${voiceCommandProcess.pid})`);
    // Kill the process tree instead of just the parent process
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', voiceCommandProcess.pid, '/f', '/t']);
    } else {
      voiceCommandProcess.kill('SIGTERM');
    }
  }
  
  if (faceRecogProcess && !faceRecogProcess.killed) {
    logToFile(`Terminating face recognition process (PID: ${faceRecogProcess.pid})`);
    // Kill the process tree instead of just the parent process
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', faceRecogProcess.pid, '/f', '/t']);
    } else {
      faceRecogProcess.kill('SIGTERM');
    }
  }
  
  logToFile('App shutdown complete');
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});