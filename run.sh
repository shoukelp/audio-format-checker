#!/bin/bash

SCRIPT_DIR="./script"
RESULT_DIR="./result"
PY_SCRIPT="$SCRIPT_DIR/check.py"
SETUP_SCRIPT="$SCRIPT_DIR/setup.py"

# Run setup mode
if [[ "$1" == "setup" ]]; then
  python3 "$SETUP_SCRIPT"
  exit 0
fi

# Require at least one argument
if [[ $# -lt 1 ]]; then
  echo "Usage: ./run.sh <audiofile> [--json output.json]"
  echo "       ./run.sh setup  # to run setup"
  exit 1
fi

AUDIO_FILE="$1"
shift

SAVE_JSON=false
JSON_OUTPUT=""

# Check for --json flag
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

# Execute script
if $SAVE_JSON; then
  mkdir -p "$RESULT_DIR"
  python3 "$PY_SCRIPT" "$AUDIO_FILE" --json "$JSON_OUTPUT"
else
  python3 "$PY_SCRIPT" "$AUDIO_FILE"
fi