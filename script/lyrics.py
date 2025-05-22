import sys
import os
import subprocess
import json
import requests
from bs4 import BeautifulSoup

def run_ffprobe_json(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"ffprobe error: {e}")
        return None

def extract_lyrics_from_metadata(tags):
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

def search_lyrics_sources(title, artist):
    results = []

    try:
        res = requests.get(f"https://api.lyrics.ovh/v1/{artist}/{title}")
        if res.status_code == 200:
            lyrics = res.json().get("lyrics", "")
            if lyrics:
                results.append({"source": "lyrics.ovh", "lyrics": lyrics})
    except Exception as e:
        print("[lyrics.ovh] Error:", e)

    try:
        query = f"{artist} {title}".replace(" ", "+")
        search_url = f"https://www.lyricsfreak.com/search.php?a=search&q={query}"
        r = requests.get(search_url)
        soup = BeautifulSoup(r.text, "html.parser")
        link = soup.select_one(".lf-list__cell.lf-list__cell_song a")
        if link:
            href = link["href"]
            lyrics_url = "https://www.lyricsfreak.com" + href
            lyrics_page = requests.get(lyrics_url)
            lyrics_soup = BeautifulSoup(lyrics_page.text, "html.parser")
            lyrics = lyrics_soup.select_one(".lyrictxt").get_text("\n", strip=True)
            if lyrics:
                results.append({"source": "LyricsFreak", "lyrics": lyrics})
    except Exception as e:
        print("[LyricsFreak] Error:", e)

    return results

def embed_lyrics_to_metadata(audio_file, lyrics_text):
    try:
        # Membuat file output sementara
        temp_file = "temp_with_lyrics.m4a"
        result = subprocess.run([
            "ffmpeg", "-i", audio_file, "-metadata", f"lyrics={lyrics_text}",
            "-c", "copy", temp_file, "-y"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("Failed to embed lyrics:", result.stderr)
        else:
            os.replace(temp_file, audio_file)
            print("Lyrics embedded successfully into the audio file.")
    except Exception as e:
        print("Failed to embed lyrics:", e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lyrics.py <audiofile> [--import]")
        sys.exit(1)

    audio_file = sys.argv[1]
    import_mode = "--import" in sys.argv

    if not os.path.isfile(audio_file):
        print("File not found.")
        sys.exit(1)

    data = run_ffprobe_json(audio_file)
    if not data:
        sys.exit(1)

    tags = data.get("format", {}).get("tags", {})
    title = tags.get("title", "")
    artist = tags.get("artist", "")

    if not import_mode:
        lyrics_text = extract_lyrics_from_metadata(tags)
        if lyrics_text:
            save_lyrics_to_file(audio_file, lyrics_text)
        else:
            print("No lyrics found in metadata.")
    else:
        print("Import mode enabled. Requires internet connection.")
        results = search_lyrics_sources(title, artist)

        if not results:
            print("No lyrics found online.")
            sys.exit(1)

        for i, item in enumerate(results):
            print(f"\n[{i + 1}] Source: {item['source']}\n{'-' * 40}\n{item['lyrics'][:200]}...\n")

        try:
            choice = int(input(f"Select lyrics to embed (1-{len(results)}): "))
            if 1 <= choice <= len(results):
                selected_lyrics = results[choice - 1]["lyrics"]
                embed_lyrics_to_metadata(audio_file, selected_lyrics)
                save_lyrics_to_file(audio_file, selected_lyrics)
            else:
                print("Invalid choice.")
        except Exception as e:
            print("Input error:", e)