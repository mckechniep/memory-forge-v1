Perfect. Here's a breakdown of how your current setup works and how the files interact:

* * *

### 🧠 Memory Forge Architecture (High-Level Flow)

Your Electron-based desktop app allows users to:

1. Select a `.txt` or `.mp3` file.

2. Input a memory title.

3. Automatically:
   
   * Clean and punctuate text (using OpenAI).
   
   * Transcribe audio if `.mp3` (using Whisper).
   
   * Suggest tags.
   
   * Save output as a `.jsonl` memory chunk.

* * *

### 📂 File-by-File Breakdown

* * *

#### `index.html`

* **Frontend UI** (styled form and script).

* Contains:
  
  * Text input for memory title.
  
  * A hidden file input (`<input type="file" id="file">`).
  
  * A visible button (`Select .txt or .mp3 File`) that triggers `fileInput.click()`.
  
  * Logic to:
    
    * Determine file extension.
    
    * Call `window.api.processTranscript()` or `transcribeAudio()` depending on type.
    
    * Display formatted memory preview in a textarea.

* * *

#### `preload.js`

* **Secure bridge** between frontend and Electron backend using `contextBridge`.

* Exposes:
  
      window.api.processTranscript(filePath, title);
      window.api.transcribeAudio(filePath, title);
  
  

These map to Electron `ipcMain.handle` events in `main.js`.

* * *

#### `main.js`

* **Main Electron Process**.

* Opens the app window.

* Handles IPC calls from frontend:
  
  * `"process-transcript"`: calls `process.py` via Python subprocess.
  
  * `"transcribe-audio"`: calls `transcribe.py`, then runs `process.py`.

* Uses:
  
  * `dialog.showSaveDialog()` to let users pick where `.jsonl` gets saved.
  
  * A `runPython()` helper to spawn Python scripts with arguments.
  
  * All Python subprocesses run using the virtual environment interpreter.

* * *

#### `backend/process.py`

* **Text processing + tagging**.

* Responsibilities:
  
  * Clean transcripts.
  
  * Format/punctuate text via OpenAI GPT.
  
  * Auto-tag content with simple keyword logic.
  
  * Write `.jsonl` memory chunk to specified `output_path`.

* Can be run standalone: `python process.py transcript.txt "Title" [optional_output_path]`.

* * *

#### `backend/transcribe.py`

* **Audio transcription using Whisper**.

* Responsibilities:
  
  * Transcribe `.mp3` using `whisper`.
  
  * Write raw transcription to temporary `.txt` file.
  
  * Call `process()` function from `process.py`.
  
  * Output the formatted memory and write `.jsonl` to provided path.

* Requires 3 args: mp3 path, title, output path.
  
  * Example: `python transcribe.py audio.mp3 "Title" path/to/output.jsonl`

* * *

### ✅ Summary of Flow (for `.mp3`)

1. User selects `.mp3` file in UI.

2. `index.html` calls `window.api.transcribeAudio(filePath, title)`.

3. `main.js` prompts user for output `.jsonl` location.

4. `main.js` spawns `backend/transcribe.py` with:
   
   * `filePath`, `title`, and `outputPath`.

5. `transcribe.py`:
   
   * Runs Whisper, creates `.txt` temp file.
   
   * Calls `process()` from `process.py` using temp `.txt`.
   
   * Writes memory chunk to `.jsonl`.

6. Output is returned to frontend and shown in the textarea.

* * *

### 🎯 You’re super close.

You’ve:

* Modularized Python logic cleanly.

* Handled both audio and text input.

* Given users flexibility to pick where memory chunks are saved.

Let me know if you want to:

* Add metadata like timestamps or UUIDs.

* Let users pick tags.

* Combine multiple `.jsonl` chunks into one.

* Package it for distribution via `.exe`.

Want help tightening any part next?
