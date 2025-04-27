import sys
import os
import tempfile
import whisper
from process import process
import traceback

# This script transcribes an MP3 audio file to text and processes it according to specified parameters.
# It requires 5 command-line arguments to run properly.
def main():
    try:
        # Print arguments for debugging
        print(f"Received {len(sys.argv)} arguments:")
        for i, arg in enumerate(sys.argv):
            print(f"  Arg {i}: {arg}")
            
        # Check if the correct number of command-line arguments is provided
        if len(sys.argv) < 6:
            print("Usage: python transcribe.py <mp3_path> <title> <instruction> <mode> <output_path>")
            sys.exit(1)

        # Extract command-line arguments
        mp3_path = sys.argv[1]
        title = sys.argv[2]
        instruction = sys.argv[3]
        mode = sys.argv[4]
        output_path = sys.argv[5]
        
        # Validate paths
        if not os.path.exists(mp3_path):
            print(f"Error: MP3 file not found: {mp3_path}")
            sys.exit(1)
            
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            print(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)

        # Initialize the Whisper speech recognition model
        print("Transcribing with Whisper...")
        model = whisper.load_model("tiny")

        # Perform the actual transcription of the audio file
        result = model.transcribe(mp3_path)

        # Save the transcribed text to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp.write(result["text"])
            txt_path = tmp.name

        # Process the transcription according to the specified mode
        final_output = process(txt_path, title, instruction, mode, output_path)

        # Indicate completion and show the result
        print("Done!")
        print(final_output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()