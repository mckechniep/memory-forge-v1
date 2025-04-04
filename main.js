const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  win.loadFile("index.html");
}

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

// 📁 Handle .txt file
ipcMain.handle("process-transcript", async (event, filePath, title) => {
  const saveDialog = await dialog.showSaveDialog({
    title: "Save Memory Chunk",
    defaultPath: `${title.replace(/\s+/g, "_").toLowerCase()}.jsonl`,
    filters: [{ name: "JSONL", extensions: ["jsonl"] }],
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return "❌ Save canceled.";
  }

  return runPython("process.py", [filePath, title, saveDialog.filePath]);
});

// 🎧 Handle .mp3 audio
ipcMain.handle("transcribe-audio", async (event, filePath, title) => {
  const saveDialog = await dialog.showSaveDialog({
    title: "Save Memory Chunk",
    defaultPath: `${title.replace(/\s+/g, "_").toLowerCase()}.jsonl`,
    filters: [{ name: "JSONL", extensions: ["jsonl"] }],
  });

  if (saveDialog.canceled || !saveDialog.filePath) {
    return "Save canceled.";
  }

  return runPython("transcribe.py", [filePath, title, saveDialog.filePath]);
});

// 🔁 Shared subprocess logic
function runPython(scriptName, args) {
  return new Promise((resolve, reject) => {
    // Normalize paths for cross-platform compatibility
    const normalizedArgs = args.map((arg) => {
      // Only normalize strings that look like paths
      if (
        typeof arg === "string" &&
        (arg.includes("/") || arg.includes("\\"))
      ) {
        return path.normalize(arg);
      }
      return arg;
    });

    const venvPython = path.join(
      __dirname,
      "backend",
      "venv",
      "Scripts",
      "python.exe"
    );
    const scriptPath = path.join(__dirname, "backend", scriptName);

    const subprocess = spawn(venvPython, [scriptPath, ...normalizedArgs], {
      cwd: path.join(__dirname, "backend"),
    });

    let output = "";
    let errorOutput = "";

    subprocess.stdout.on("data", (data) => (output += data.toString()));
    subprocess.stderr.on("data", (data) => (errorOutput += data.toString()));

    subprocess.on("close", (code) => {
      if (code === 0) resolve(output);
      else reject(errorOutput || `Script exited with code ${code}`);
    });
  });
}

ipcMain.handle("select-file", async (event, fileTypes) => {
  const result = await dialog.showOpenDialog({
    properties: ["openFile"],
    filters: fileTypes || [
      { name: "All Files", extensions: ["*"] },
      { name: "Text", extensions: ["txt"] },
      { name: "Audio", extensions: ["mp3"] },
    ],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return result.filePaths[0];
});
