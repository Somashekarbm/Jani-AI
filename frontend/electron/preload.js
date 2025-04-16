const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // For future IPC communication between main and renderer processes
    send: (channel, data) => {
      // List allowed channels to send messages to
      const validChannels = ['toMain'];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    receive: (channel, func) => {
      // List allowed channels to receive messages from
      const validChannels = ['fromMain'];
      if (validChannels.includes(channel)) {
        // Remove the event to avoid memory leaks
        ipcRenderer.removeAllListeners(channel);
        // Add a new listener
        ipcRenderer.on(channel, (event, ...args) => func(...args));
      }
    }
  }
);