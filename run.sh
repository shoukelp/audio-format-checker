#!/bin/bash

SCRIPT_DIR="./script"
RESULT_DIR="./result"
PY_SCRIPT="$SCRIPT_DIR/check.py"
LYRICS_SCRIPT="$SCRIPT_DIR/lyrics.py"
SETUP_SCRIPT="$SCRIPT_DIR/setup.py"

# Run setup mode
if [[ "$1" == "setup" ]]; then
  python3 "$SETUP_SCRIPT"
  exit 0
fi

if [[ "$1" == "lrc" ]]; then
  if [[ -z "$2" ]]; then
    echo "Usage: ./run.sh lrc <audiofile>"
    exit 1
  fi

  AUDIO_FILE="$2"
  if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "File not found: $AUDIO_FILE"
    exit 1
  fi

  mkdir -p "$RESULT_DIR"
  python3 "$LYRICS_SCRIPT" "$AUDIO_FILE"
  exit 0
fi


if [[ $# -lt 1 ]]; then
  echo "Usage: ./run.sh <audiofile> [--json output.json]"
  echo "       ./run.sh lrc <audiofile>"
  echo "       ./run.sh setup"
  exit 1
fi

AUDIO_FILE="$1"
shift

SAVE_JSON=false
JSON_OUTPUT=""

if [[ "$1" == "--json" ]]; then
  SAVE_JSON=true
  shift

  base_name=$(basename "$AUDIO_FILE")
  base_name_no_ext="${base_name%.*}"

  if [[ -n "$1" && "$1" != --* ]]; then
    JSON_OUTPUT="$RESULT_DIR/$1"
    shift
  else
    JSON_OUTPUT="$RESULT_DIR/${base_name_no_ext}.json"
  fi
fi

if $SAVE_JSON; then
  mkdir -p "$RESULT_DIR"
  python3 "$PY_SCRIPT" "$AUDIO_FILE" --json "$JSON_OUTPUT"
else
  python3 "$PY_SCRIPT" "$AUDIO_FILE"
fi