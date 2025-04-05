const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");

/**
 * Main.js - Entry point for the Electron application
 * 
 * This file sets up the desktop application window, handles file selection,
 * and manages communication between the UI and Python backend scripts.
 */

// Store default directories
let defaultOpenDirectory = app.getPath("documents");
let defaultSaveDirectory = app.getPath("documents");

// Load saved directories if they exist
const userDataPath = app.getPath("userData");
const dirConfigPath = path.join(userDataPath, "directory-config.json");

try {
  if (fs.existsSync(dirConfigPath)) {
    const dirConfig = JSON.parse(fs.readFileSync(dirConfigPath, 'utf8'));
    if (dirConfig.openDirectory && fs.existsSync(dirConfig.openDirectory)) {
      defaultOpenDirectory = dirConfig.openDirectory;
    }
    if (dirConfig.saveDirectory && fs.existsSync(dirConfig.saveDirectory)) {
      defaultSaveDirectory = dirConfig.saveDirectory;
    }
  }
} catch (error) {
  console.error("Error loading directory config:", error);
}

// Function to save directory preferences
function saveDirectoryPreferences() {
  try {
    const dirConfig = {
      openDirectory: defaultOpenDirectory,
      saveDirectory: defaultSaveDirectory
    };
    fs.writeFileSync(dirConfigPath, JSON.stringify(dirConfig, null, 2));
  } catch (error) {
    console.error("Error saving directory config:", error);
  }
}

/**
 * Creates the main application window.
 * 
 * This function:
 * - Sets the window size (1000x800 pixels)
 * - Configures security settings (contextIsolation, nodeIntegration)
 * - Loads the main HTML file (index.html) that contains the user interface
 */
function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"), // uses a "preload" script which helps set up communication between the web page and the application's backend.
      contextIsolation: true, // contextIsolation and nodeIntegration are security settings
      nodeIntegration: false,
    },
  });

  win.loadFile("index.html"); // loads an "index.html" file into the window, this means the visual content and structure of the application will be defined by this HTML file, 
}

/**
 * Application startup logic
 * 
 * When the app is ready:
 * - Creates the main window
 * - Sets up an event handler to recreate the window on macOS when the app icon is clicked
 *   (macOS apps typically stay running even when all windows are closed)
 */
app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

/**
 * Application shutdown logic
 * 
 * When all windows are closed:
 * - Quit the app completely on Windows and Linux
 * - On macOS (darwin), the app stays running unless the user explicitly quits
 */
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

/**
 * File selection dialog handler
 * 
 * Inputs: None directly (triggered by a request from the renderer process)
 * Outputs: Returns the selected file path or null if canceled
 * 
 * Opens a file dialog allowing users to select text files (.txt) or 
 * audio files (.mp3, .wav, .ogg, .m4a)
 */
ipcMain.handle('dialog:openFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    defaultPath: defaultOpenDirectory,
    properties: ['openFile'],
    filters: [
      { name: 'All Supported Files', extensions: ['txt', 'mp3', 'wav', 'ogg', 'm4a'] },
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'Audio Files', extensions: ['mp3', 'wav', 'ogg', 'm4a'] }
    ]
  });
  
  if (canceled || filePaths.length === 0) {
    return null;
  } else {
    // Update the default directory to the directory of the selected file
    defaultOpenDirectory = path.dirname(filePaths[0]);
    saveDirectoryPreferences();
    return filePaths[0];
  }
});

/**
 * Set default directories handler
 */
ipcMain.handle('settings:setDefaultDirectories', async () => {
  // Open directory selection for input files
  const openResult = await dialog.showOpenDialog({
    defaultPath: defaultOpenDirectory,
    properties: ['openDirectory'],
    title: 'Select Default Directory for Opening Files'
  });
  
  if (!openResult.canceled && openResult.filePaths.length > 0) {
    defaultOpenDirectory = openResult.filePaths[0];
  }
  
  // Open directory selection for output files
  const saveResult = await dialog.showOpenDialog({
    defaultPath: defaultSaveDirectory,
    properties: ['openDirectory'],
    title: 'Select Default Directory for Saving Files'
  });
  
  if (!saveResult.canceled && saveResult.filePaths.length > 0) {
    defaultSaveDirectory = saveResult.filePaths[0];
  }
  
  saveDirectoryPreferences();
  return {
    openDirectory: defaultOpenDirectory,
    saveDirectory: defaultSaveDirectory
  };
});

/**
 * Get current default directories
 */
ipcMain.handle('settings:getDefaultDirectories', async () => {
  return {
    openDirectory: defaultOpenDirectory,
    saveDirectory: defaultSaveDirectory
  };
});

/**
 * Text file processing handler
 * 
 * Inputs:
 * - filePath: Path to the text file to process
 * - title: Title for the memory chunk
 * - instruction: Processing instruction
 * - mode: Processing mode (e.g., "rag")
 * 
 * Outputs: Result message from the Python script or error message
 * 
 * This handler:
 * 1. Opens a save dialog to get the output file location
 * 2. Calls the Python script (process.py) to process the text file
 * 3. Returns the result or error message
 */
ipcMain.handle("process-transcript", async (event, filePath, title, instruction, mode) => {
  const defaultFileName = `${(mode === "rag" ? title : instruction).replace(/\s+/g, "_").toLowerCase()}.jsonl`;
  const defaultSavePath = path.join(defaultSaveDirectory, defaultFileName);
  
  const saveDialog = await dialog.showSaveDialog({
    title: "Save Memory Chunk",
    defaultPath: defaultSavePath,
    filters: [{ name: "JSONL", extensions: ["jsonl"] }],
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return "Save canceled.";
  }

  // Update the default save directory
  defaultSaveDirectory = path.dirname(saveDialog.filePath);
  saveDirectoryPreferences();

  return runPython("process.py", [filePath, title, instruction, mode, saveDialog.filePath]);
});

/**
 * Audio file transcription handler
 * 
 * Inputs:
 * - filePath: Path to the audio file to transcribe
 * - title: Title for the transcription
 * - instruction: Processing instruction
 * - mode: Processing mode
 * 
 * Outputs: Result message from the Python script or error message
 * 
 * This handler:
 * 1. Logs the received parameters
 * 2. Validates the file path
 * 3. Opens a save dialog to get the output file location
 * 4. Calls the Python script (transcribe.py) to transcribe the audio
 * 5. Returns the result or error message
 */
ipcMain.handle("transcribe-audio", async (event, filePath, title, instruction, mode) => {
  console.log("Received file path:", filePath);
  console.log("Title:", title);
  console.log("Instruction:", instruction);
  console.log("Mode:", mode);
  
  if (!filePath || filePath === "undefined") {
    return "Error: No valid file path provided";
  }

  const defaultFileName = `${(title || instruction).replace(/\s+/g, "_").toLowerCase()}.jsonl`;
  const defaultSavePath = path.join(defaultSaveDirectory, defaultFileName);

  const saveDialog = await dialog.showSaveDialog({
    title: "Save Memory Chunk",
    defaultPath: defaultSavePath,
    filters: [{ name: "JSONL", extensions: ["jsonl"] }],
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return "Save canceled.";
  }

  // Update the default save directory
  defaultSaveDirectory = path.dirname(saveDialog.filePath);
  saveDirectoryPreferences();

  return runPython("transcribe.py", [
    filePath,
    title || "",
    instruction || "",
    mode,
    saveDialog.filePath,
  ]);
});

/**
 * Python script execution function
 * 
 * Inputs:
 * - scriptName: Name of the Python script to run
 * - args: Array of arguments to pass to the script
 * 
 * Outputs: Promise that resolves with the script's output or rejects with an error
 * 
 * This function:
 * 1. Normalizes file paths to avoid issues on different operating systems
 * 2. Spawns a Python process from the virtual environment
 * 3. Captures stdout and stderr from the process
 * 4. Returns a promise that resolves with the output when the process completes
 */
function runPython(scriptName, args) {
  return new Promise((resolve, reject) => {
    const path = require("path");
    const { spawn } = require("child_process");

    // Normalize arguments to avoid path issues (especially on Windows)
    const normalizedArgs = args.map(arg =>
      typeof arg === "string" && (arg.includes("/") || arg.includes("\\"))
        ? path.normalize(arg)
        : arg
    );

      const venvPython = process.platform === "win32" 
        ? path.join(__dirname, "backend", "venv", "Scripts", "python.exe")
        : path.join(__dirname, "backend", "venv", "bin", "python");
    const scriptPath = path.join(__dirname, "backend", scriptName);

    const subprocess = spawn(venvPython, [scriptPath, ...normalizedArgs], {
      cwd: path.join(__dirname, "backend"),
    });

    let output = "";
    let errorOutput = "";

    subprocess.stdout.on("data", data => (output += data.toString()));
    subprocess.stderr.on("data", data => (errorOutput += data.toString()));

    subprocess.on("close", code => {
      if (code === 0) resolve(output.trim());
      else reject(errorOutput || `Script exited with code ${code}`);
    });
  });
}