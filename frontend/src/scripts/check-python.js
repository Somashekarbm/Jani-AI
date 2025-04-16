const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('Checking Python environment...');

try {
  // Check if Python is installed
  const pythonVersion = execSync('python --version', { encoding: 'utf8' });
  console.log(`Found Python: ${pythonVersion.trim()}`);
  
  // Install required packages
  const requirementsPath = path.join(__dirname, '../api/requirements.txt');
  
  if (fs.existsSync(requirementsPath)) {
    console.log('Installing required Python packages...');
    const pip = spawn('pip', ['install', '-r', requirementsPath], { stdio: 'inherit' });
    
    pip.on('close', (code) => {
      if (code === 0) {
        console.log('Python packages installed successfully');
      } else {
        console.error(`Failed to install Python packages (exit code: ${code})`);
      }
    });
  } else {
    console.log('No requirements.txt found at', requirementsPath);
  }
} catch (error) {
  console.error('Python not found or error checking environment:', error.message);
  console.log('Please install Python and run "npm run setup-python" again');
}