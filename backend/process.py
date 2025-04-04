import sys
import re
import json
import os
from pathlib import Path
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("OPENAI_API_KEY not set. Please export it. Please review README or launch instructions for details on how to do this.")
    sys.exit(1)


# --- Tagging Logic ---
def suggest_tags(text, top_n=5):
    keywords = {
        "memory": ["remember", "memory", "nostalgia"],
        "adolescence": ["school", "teen", "highschool"],
        "reflection": ["realized", "insight", "reflection"],
        "humor": ["funny", "joke", "laughed"],
        "emotion": ["angry", "sad", "joy", "panic", "happy"],
    }
    cleaned = re.sub(r"[^a-zA-Z\s]", "", text.lower())
    words = cleaned.split()
    scores = {
        tag: sum(word in words for word in kwds)
        for tag, kwds in keywords.items()
    }
    return sorted([k for k, v in scores.items() if v > 0], key=lambda k: -scores[k])[:top_n]

# --- OpenAI Punctuation ---
def punctuate(text):
    client = openai.OpenAI()
    prompt = (
        "Take this raw transcript and format it into clean, properly punctuated text. "
        "Keep the tone natural and preserve slang or profanity:\n\n"
        + text + "\n\nFormatted version:"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

# --- Clean Whisper transcript ---
def clean_transcript(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    content = [re.sub(r"\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]", "", line).strip() for line in lines]
    return " ".join(line for line in content if line)

# --- Main processing ---
def process(txt_path, title, output_path="rag_memory_chunks.jsonl"):
    raw = clean_transcript(txt_path)
    formatted = punctuate(raw)
    tags = suggest_tags(formatted)
    chunk = {"title": title, "content": formatted, "tags": tags}

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return formatted


# 👇 Near bottom
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process.py <path> <title> [output_path]")
        sys.exit(1)

    txt_path = sys.argv[1]
    memory_title = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "rag_memory_chunks.jsonl"

    output = process(txt_path, memory_title, output_path)
    print(output)
