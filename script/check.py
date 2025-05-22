import sys
import os
import subprocess
import json

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
    info["filename"] = format_data.get("filename")
    info["format_name"] = format_data.get("format_name")
    info["duration"] = format_data.get("duration")
    info["bit_rate"] = format_data.get("bit_rate")
    info["tags"] = format_data.get("tags", {})

    tags = info["tags"]
    lyrics_keys = ["lyrics", "Lyrics", "unsyncedlyrics", "syncedlyrics", "LYRICS"]
    info["has_lyrics"] = any(key in tags for key in lyrics_keys)

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            info["codec_name"] = stream.get("codec_name")
            info["sample_rate"] = stream.get("sample_rate")
            info["channels"] = stream.get("channels")
            info["channel_layout"] = stream.get("channel_layout")
            info["bit_rate"] = stream.get("bit_rate", info.get("bit_rate"))
            break

    return info

def print_info(info):
    print("Audio Information:")
    print(f"- File        : {info.get('filename')}")
    print(f"- Format      : {info.get('format_name')}")
    print(f"- Codec       : {info.get('codec_name')}")
    print(f"- Duration    : {info.get('duration')} seconds")
    print(f"- Bitrate     : {info.get('bit_rate')} bps")
    print(f"- Sample Rate : {info.get('sample_rate')} Hz")
    print(f"- Channels    : {info.get('channels')} ({info.get('channel_layout')})")
    print(f"- Contains Lyrics : {'Yes' if info.get('has_lyrics') else 'No'}")

    if info.get("tags"):
        print("\nMetadata:")
        for key, value in info["tags"].items():
            print(f"  {key}: {value}")

def save_json(info, output_path):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
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
    print_info(info)

    if json_output:
        save_json(info, json_output)