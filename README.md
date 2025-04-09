# 🧠 Memory Forge

**Memory Forge** is a desktop application that converts raw `.txt` or `.mp3` files into structured memory chunks for use in Retrieval-Augmented Generation (RAG) or Supervised Fine-Tuning (SFT) workflows.

Built with Electron + Python + Whisper + OpenAI.

---

##  Features

-  Process `.txt` and transcribe `.mp3`, `.wav`, `.ogg`, `.m4a` audio files
-  Automatically punctuates and formats transcripts with OpenAI
-  Outputs:
  - **RAG Memory**: title, content, and auto-tagged topics
  - **SFT Data**: instruction-response pairs
-  Save output as `.jsonl`
-  Customize default open/save directories
-  Works entirely offline for Whisper (OpenAI required for punctuation only)

---

##  Requirements

- Python 3.10+
- Node.js (latest LTS)
- ffmpeg installed and in your PATH
- OpenAI API key

---

##  Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/memory-forge.git
cd memory-forge
```

2. **Run setup.bat** (Windows only)

```bash
./setup.bat
```

This will:
- Install frontend dependencies
- Create a Python virtual environment
- Install backend dependencies from `requirements.txt`

3. **Run the app**

```bash
npm start
```

---

##  Usage

1. Launch Memory Forge
2. Choose your mode: `RAG Memory` or `SFT Data`
3. Enter a title (RAG) or instruction (SFT)
4. Click `Select .txt or .mp3 File`
5. Choose a file to process
6. Preview formatted output
7. Choose where to save the `.jsonl` output

---

##  Output Formats

### RAG Memory
```json
{
  "title": "Defying Authority and Skipping School",
  "content": "So one time in high school I totally ditched class...",
  "tags": ["adolescence", "humor", "memory"]
}
```

### SFT Data
```json
{
  "instruction": "What did the speaker say about the political system?",
  "response": "They said it was totally corrupt and influenced by money..."
}
```

---

##  Environment Variables

Create a `.env` file in `/backend` with:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

---

##  Packaging (Windows)

To create a `.zip` or `.exe`:
```bash
npm run make
```
- Outputs to `/out/make`
- Uses `electron-forge`

---

##  Credits

- Built by Peter McKechnie
- Speech-to-text via [`openai-whisper`](https://github.com/openai/whisper)
- Punctuation via OpenAI GPT-3.5
- UI via Electron

---

## 🧪 License

MIT

