import sys
import os
import subprocess
import json
from wcwidth import wcswidth

def run_ffprobe_json(file_path):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe error: {e.stderr.strip()}")

def parse_info(data):
    info = {}

    format_data = data.get("format", {})
    tags = format_data.get("tags", {})

    lyrics_keys = ["lyrics", "Lyrics", "unsyncedlyrics", "syncedlyrics", "LYRICS"]
    has_lyrics = any(key in tags for key in lyrics_keys)
    filtered_tags = {k: v for k, v in tags.items() if k not in lyrics_keys}

    filename = format_data.get("filename")
    info["filename"] = filename

    info["format_name"] = os.path.splitext(filename)[1].lstrip(".").lower()

    info["duration"] = format_data.get("duration")
    info["bit_rate"] = format_data.get("bit_rate")
    info["tags"] = filtered_tags
    info["has_lyrics"] = has_lyrics

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            info["codec_name"] = stream.get("codec_name")
            info["sample_rate"] = stream.get("sample_rate")
            info["channels"] = stream.get("channels")
            info["channel_layout"] = stream.get("channel_layout")
            info["bit_rate"] = stream.get("bit_rate", info.get("bit_rate"))
            break

    return info

def format_table(rows, headers):
    all_rows = [headers] + rows
    col_widths = [max(wcswidth(str(cell)) for cell in col) for col in zip(*all_rows)]

    def format_row(row):
        return "| " + " | ".join(
            f"{str(cell)}{' ' * (col_widths[i] - wcswidth(str(cell)))}"
            for i, cell in enumerate(row)
        ) + " |"

    sep = "+-" + "-+-".join("-" * width for width in col_widths) + "-+"

    table = [sep, format_row(headers), sep]
    for row in rows:
        table.append(format_row(row))
    table.append(sep)
    return "\n".join(table)

def print_info(info):
    tags = info.get("tags", {})

    def get_tag(*keys):
        for key in keys:
            if key in tags:
                return tags[key]
        return ""

    def format_duration(seconds):
        try:
            seconds = float(seconds)
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}.{secs:02d}"
        except:
            return ""

    audio_data = [
        ["Title", get_tag("title", "TITLE")],
        ["Artist", get_tag("artist", "ARTIST")],
        ["Album", get_tag("album", "ALBUM")],
        ["Album Artist", get_tag("album_artist", "ALBUM_ARTIST")],
        ["Genre", get_tag("genre", "GENRE")],
        ["Composer", get_tag("composer", "COMPOSER")],
        ["Year/Date", get_tag("date", "year", "DATE", "YEAR")],
        ["Duration", format_duration(info.get("duration"))],
        ["Bitrate", f"{int(info.get('bit_rate')) // 1000} kbps" if info.get("bit_rate") else ""],
        ["Sample Rate", f"{info.get('sample_rate', '')} Hz"],
        ["Channels", f"{info.get('channels', '')} ({info.get('channel_layout', '')})"],
        ["Disc Number", get_tag("disc", "disc_number", "DISCNUMBER")],
        ["Track Number", get_tag("track", "track_number", "TRACKNUMBER")],
        ["Format", info.get("format_name", "")],
        ["File Name", os.path.basename(info.get("filename", ""))],
        ["File Path", info.get("filename", "")],
        ["Contain Lyrics", "Yes" if info.get("has_lyrics") else "No"]
    ]

    print("\nTrack Info:")
    print(format_table(audio_data, headers=["Field", "Value"]))

    return dict(audio_data)  # for JSON export

def save_json(formatted_info, output_path):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted_info, f, indent=2, ensure_ascii=False)
        print(f"\nData saved to file: {output_path}")
    except Exception as e:
        print(f"Failed to save JSON: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check.py <file> [--json output.json]")
        sys.exit(1)

    file_path = sys.argv[1]
    json_output = None

    if "--json" in sys.argv:
        idx = sys.argv.index("--json")
        if len(sys.argv) > idx + 1:
            json_output = sys.argv[idx + 1]

    if not os.path.isfile(file_path):
        print("File not found.")
        sys.exit(1)

    data = run_ffprobe_json(file_path)

    if data is None:
        print("ffprobe is not available. Please install it first.")
        sys.exit(1)

    info = parse_info(data)
    formatted_info = print_info(info)

    if json_output:
        save_json(formatted_info, json_output)