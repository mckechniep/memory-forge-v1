import sys
import re
import json
import os
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Exit if API key is not set
if not openai.api_key:
    print("OPENAI_API_KEY not set. Please export it.")
    sys.exit(1)

# --- Tagging Logic for RAG ---
# This function analyzes text and suggests relevant tags based on keyword matching
# Input: text (string) to analyze, top_n (int) number of tags to return
# Output: list of the most relevant tags (strings)
def suggest_tags(text, top_n=5):
    # Dictionary mapping tag categories to related keywords
    keywords = {
        # Each category contains a list of keywords that indicate that topic
        "meta": ["llm", "digital twin", "ai", "model", "neural", "trained", "memory bank", "what i am", "avatar", "self aware", "parameters", "fine-tuned", "rag"],
        "childhood": ["childhood", "child", "childish", "formative", "formative years", "growing up", "grew up", "little", "little one", "raised", "kid", "daycare", "preschool", "preschooler", "toddler", "kindergarten", "kindergartener", "pre-kindergarten", "born", "newborn", "birth", "baby", "infant", "infancy", "infantile", "elementary school", "primary school", "lower school", "grade school", "recess", "k1", "k-one", "k2", "k-two", "first grade", "second grade", "third grade", "fourth grade", "fifth grade", "sixth grade", "seventh grade", "eighth grade", "arts and crafts", "babysitter", "babysitting", "nanny"],
        "adolescence": ["adolescence", "adolescent", "teenage", "teens", "teen", "teenager", "youngster", "youth", "younger", "grasshopper", "padawan", "highschool", "secondary school", "asl", "american school in london", "ninth grade", "tenth grade", "eleventh grade", "twelfth grade", "the arcade", "the shop"],
        "adulthood": ["adulthood", "adult", "twenties", "thirties", "young man", "grownup"],
        "family": ["parents", "relatives", "blood", "mom", "dad", "sibling", "family", "brother", "sister", "alec", "caleb", "kyle", "deirdre", "dee", "colin", "clan", "meaul", "aunt", "aunts", "uncle", "uncles", "cousin", "cousins", "ancestry", "ancestor", "ancestors", "lineage"],
        "identiy": ["identity", "self", "me", "i am", "alias", "nickname", "myself", "how i describe", "personality", "who i am", "ego", "inner self", "core self"],
        "emotion": ["happy", "joy", "excited", "hype", "sad", "angry", "mad", "frustrated", "scared", "fear", "anxious", "nervous", "guilt", "ashamed", "proud", "regret", "love", "heartbroken", "lonely", "euphoria", "nostalgic", "grief", "panic", "relief", "emotional", "overwhelmed", "meltdown", "breakdown", "tears", "cry", "laughed"],
        "memory": ["remember", "i remember", "flashback", "memory", "memories", "can still see", "can't forget", "etched", "stuck with me", "won't ever forget", "came back to me", "triggered", "recall", "thought about", "vivid", "nostalgia", "felt like yesterday"],
        "belief": ["belief", "believe", "i think", "i know", "knowledge", "core beliefs", "ideology"],
        "relationships": ["relationship", "friend", "best friend", "girlfriend", "boyfriend", "partner", "ex", "romance", "fling", "situationship", "crush", "intimacy", "love", "chemistry", "connection", "bond", "jealousy", "trust", "breakup", "falling in love", "heart", "together", "apart", "attraction"],
        "reflection": ["looking back", "in hindsight", "i realized", "i've been thinking", "it hit me", "i used to think", "it occurred to me", "i learned", "i noticed", "what i saw", "looking inward", "self-awareness", "reflection", "reflect", "reflecting", "growth", "change in me", "insight", "clarity"],
        "humor": ["funny", "hilarious", "lol", "joke", "banter", "roasted", "laughed", "clown", "absurd", "ridiculous", "sarcastic", "dark humor", "meme", "ironic", "prank", "goofy", "got jokes", "stupid funny", "dry humor", "one-liner"],
        "dream": ["dream", "dreamed", "nightmare", "lucid", "surreal", "vision", "dreamlike", "woke up", "sleep", "asleep", "subconscious", "fantasy", "symbolic", "unreal", "hallucinated", "imagination", "otherworldly", "trippy"],
        "goal": ["goal", "ambition", "i want to", "i hope", "i'm working on", "bucket list", "objective", "vision", "future", "i'm aiming for", "my dream", "milestone", "target", "next step", "plan", "roadmap"],
        "inspiration": ["inspired", "inspiration", "role model", "hero", "idol", "motivation", "spark", "ignite", "reminded me", "what pushes me", "light a fire", "fuel", "admire", "who i look up to", "legend", "powerful"],
        "education": ["school", "education", "class", "learning", "teacher", "preschool", "middleschool", "highschool", "college", "uni", "university", "immersion"],      
        "military": ["army", "infantry", "unit", "fireteam", "mission", "combat", "deployed", "deployment", "tour", "platoon", "base", "ops", "squad", "war", "PT", "sergeant", "rank", "training", "enlisted", "oath", "south sudan", "somalia", "afghanistan", "marine", "air force", "military"],
        "career": ["career", "job", "work", "boss", "co-worker", "hired", "fired", "promotion", "quit", "resume", "interview", "position", "title", "grind", "corporate", "nine to five", "dream job", "intern", "freelance", "ambition", "hustle", "project", "team", "startup", "clients"],
        "mental_health": ["burnout", "anxiety", "depression", "mental health", "breakdown", "healing", "therapy", "struggling", "stressed", "panic", "coping", "trauma", "triggered", "overwhelmed", "isolation", "sleep disorder", "self-care", "resilience", "inner work", "mindset", "addiction", "ADHD"],
        "biography": ["born", "raised", "childhood", "background", "life"],
        "life_event": ["born", "moved", "lived", "raised", "birthday", "war", "graduated", "started", "ended", "quit", "got hired", "fired", "broke up", "divorced", "married", "death", "joined", "enlisted", "deployed", "return", "trip", "transition", "turning point", "milestone", "incarcerated", "sentenced", "rehab", "came home"],
        "location": ["london", "england", "america", "summit", "uk", "new jersey", "new york city", "arizona", "spain"],
        "grateful": ["grateful", "thankful", "fortunate", "blessed"],
        "privileged": ["privileged", "wealth", "affluent", "elite", "rich", "upperclass", "wealthy"],
        "travel": ["travel", "trip", "vacation", "visit", "explore", "travelling"],
        "god": ["god", "gods", "creation", "creator", "higher power", "universal spirit", "omnipotent", "deity", "religion", "religious", "faith", "catholic", "catholicism", "spirit", "spiritual", "spirituality", "white light", "alcoholics anonymous", "twelve step", "lord", "holy spirit", "jesus", "king of kings", "pray", "prayer", "praying", "amen", "worship", "eternal", "heaven", "supreme being"],
        "society": ["society", "societies", "societal", "social", "sociology", "democracy", "democratic", "western", "civilized society", "egalitarianism", "politics", "political", "military", "political power",  "elites", "capitalism", "collective", "law", "institutions", "government", "citizen", "economy", "americans", "people", "other people", "individual", "individualism", "norms"],
        "culture": ["culture", "cultural", "multicultural", "multiculturalism", "globalism", "upbringing", "race", "racial", "community", "region", "traditions", "traditional", "religion", "beliefs", "background", "religion", "history", "values", "country", "nationality", "celtic", "irish", "scottish", "ethnicity", "ethnic", "identity", "ritual", "music", "art", "heritage", "roots"],
        "question": ["what do i think", "what if", "how come", "?"]
    }
    
    # Clean the text by removing non-alphabetic characters and converting to lowercase
    cleaned = re.sub(r"[^a-zA-Z\s]", "", text.lower())
    words = cleaned.split()
    
    # Calculate scores for each tag by counting keyword occurrences
    scores = {
        tag: sum(word in words for word in kwds)
        for tag, kwds in keywords.items()
    }
    
    # Return the top N tags with scores > 0, sorted by score (highest first)
    return sorted([k for k, v in scores.items() if v > 0], key=lambda k: -scores[k])[:top_n]

# --- OpenAI Punctuation ---
# This function uses OpenAI to properly format and punctuate raw text
# Input: text (string) to format
# Output: formatted text with proper punctuation
def punctuate(text):
    client = openai.OpenAI()
    # Create a prompt asking the model to format the text
    prompt = (
        "Take this raw transcript and format it into organized, properly punctuated text. "
        "Keep the tone as is, preserve slang and profanity:\n\n"
        + text + "\n\nFormatted version:"
    )
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    # Return the formatted text
    return response.choices[0].message.content.strip()

# --- Clean Whisper transcript ---
# This function cleans a transcript file by removing timestamps and joining lines
# Input: path (string) to the transcript file
# Output: cleaned text as a single string
def clean_transcript(path):
    # Read all lines from the file
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    # Remove timestamp markers using regex and strip whitespace
    content = [re.sub(r"\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]", "", line).strip() for line in lines]
    # Join non-empty lines into a single string
    return " ".join(line for line in content if line)

# --- Main processing ---
# This function processes a transcript file into either a RAG memory chunk or SFT training example
# Inputs: 
#   txt_path (string): path to transcript file
#   title (string): title for the memory chunk
#   instruction (string): instruction for SFT mode
#   mode (string): "sft" or "rag"
#   output_path (string): path to save the output JSONL
# Output: formatted text content
def process(txt_path, title, instruction, mode, output_path="rag_memory_chunks.jsonl"):
    # Clean the transcript
    raw = clean_transcript(txt_path)
    # Format with proper punctuation
    formatted = punctuate(raw)

    # Create different output formats based on mode
    if mode == "sft":
        # For Supervised Fine-Tuning, create instruction-response pair
        chunk = {
            "instruction": instruction,
            "response": formatted
        }
    else:  # rag mode (default)
        # For RAG, include content with tags
        tags = suggest_tags(formatted)
        chunk = {
            "title": title,
            "content": formatted,
            "tags": tags
        }

    # Append the chunk to the output file
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return formatted

# --- CLI usage ---
# This section runs when the script is executed directly (not imported)
if __name__ == "__main__":
    # Check if enough command-line arguments are provided
    if len(sys.argv) < 5:
        print("Usage: python process.py <txt_path> <title> <instruction> <mode> [output_path]")
        sys.exit(1)

    # Parse command-line arguments
    txt_path = sys.argv[1]
    title = sys.argv[2]
    instruction = sys.argv[3]
    mode = sys.argv[4]
    output_path = sys.argv[5] if len(sys.argv) > 5 else "rag_memory_chunks.jsonl"

    # Process the transcript and print the result
    output = process(txt_path, title, instruction, mode, output_path)
    print(output)
