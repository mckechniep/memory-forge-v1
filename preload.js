const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  processTranscript: (filePath, title) =>
    ipcRenderer.invoke("process-transcript", filePath, title),
  transcribeAudio: (filePath, title) =>
    ipcRenderer.invoke("transcribe-audio", filePath, title),
  selectFile: (fileTypes) => ipcRenderer.invoke("select-file", fileTypes),
});
