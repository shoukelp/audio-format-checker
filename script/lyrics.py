import sys
import os
import subprocess
import json

def run_ffprobe_json(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"ffprobe error: {e}")
        return None

def extract_lyrics(tags):
    lyrics_keys = ["lyrics", "Lyrics", "unsyncedlyrics", "syncedlyrics", "LYRICS"]
    for key in lyrics_keys:
        if key in tags:
            return tags[key]
    return None

def save_lyrics_to_file(audio_file, lyrics_text):
    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    result_dir = "./result"
    os.makedirs(result_dir, exist_ok=True)
    lrc_path = os.path.join(result_dir, base_name + ".lrc")

    try:
        with open(lrc_path, "w", encoding="utf-8") as f:
            f.write(lyrics_text)
        print(f"Lyrics saved to {lrc_path}")
    except Exception as e:
        print(f"Failed to save lyrics: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lyrics.py <audiofile>")
        sys.exit(1)

    audio_file = sys.argv[1]

    if not os.path.isfile(audio_file):
        print("File not found.")
        sys.exit(1)

    data = run_ffprobe_json(audio_file)
    if not data:
        sys.exit(1)

    tags = data.get("format", {}).get("tags", {})
    lyrics_text = extract_lyrics(tags)

    if lyrics_text:
        save_lyrics_to_file(audio_file, lyrics_text)
    else:
        print("No lyrics found in file.")