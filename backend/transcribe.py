import sys
import os
import tempfile
import whisper
from process import process

if len(sys.argv) < 4:
    print("Usage: python transcribe.py <mp3_path> <title> <output_path>")
    sys.exit(1)

mp3_path = sys.argv[1]
title = sys.argv[2]
output_path = sys.argv[3]  # <- typo was here (sys.arv)

# Load Whisper model
model = whisper.load_model("small")

# Transcribe audio
print("Transcribing with Whisper...")
result = model.transcribe(mp3_path)

# Save to temporary .txt
with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
    tmp.write(result["text"])
    txt_path = tmp.name

# Process into JSONL memory chunk
final_output = process(txt_path, title, output_path)
print("Done!")
print(final_output)
