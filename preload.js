const { contextBridge, ipcRenderer } = require("electron");

// Expose specific functions from the main process to the renderer process
// This creates a safe bridge for communication between processes
contextBridge.exposeInMainWorld("electronAPI", {
  // Function to process a transcript file
  // Inputs: filePath (string), title (string), instruction (string), mode (string)
  // Output: Returns the result from the main process after processing the transcript
  processTranscript: (filePath, title, instruction, mode) =>
    ipcRenderer.invoke("process-transcript", filePath, title, instruction, mode),
  
  // Function to open a file selection dialog
  // Inputs: None
  // Output: Returns the selected file path from the main process
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  
  // Function to open a file selection dialog specifically for audio files
  // Inputs: None
  // Output: Returns the selected audio file path from the main process
  selectAudioFile: () => ipcRenderer.invoke('dialog:openAudioFile'),
  
  // Function to transcribe an audio file
  // Inputs: filePath (string), title (string), instruction (string), mode (string)
  // Output: Returns the transcription result from the main process
  transcribeAudio: (filePath, title, instruction, mode) => 
    ipcRenderer.invoke('transcribe-audio', filePath, title, instruction, mode),
    
  // Function to set default directories for file operations
  // Inputs: None
  // Output: Returns the updated directory settings
  setDefaultDirectories: () => ipcRenderer.invoke('settings:setDefaultDirectories'),
  
  // Function to get current default directories
  // Inputs: None
  // Output: Returns the current directory settings
  getDefaultDirectories: () => ipcRenderer.invoke('settings:getDefaultDirectories')
});
