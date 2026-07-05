#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEFAULT_STIM_DIR="/Users/joecussen/Documents/Jobs/unimelb/projects/breathwork/resources/faces/NimStim_ER"

prompt_default() {
  local label="$1"
  local default="$2"
  local value
  read -r -p "$label [$default]: " value
  printf '%s\n' "${value:-$default}"
}

prompt_required() {
  local label="$1"
  local value
  read -r -p "$label: " value
  if [ -z "$value" ]; then
    echo "$label is required." >&2
    exit 1
  fi
  printf '%s\n' "$value"
}

resolve_stim_dir() {
  local stim_dir="${1:-${FACE_STIM_DIR:-}}"
  if [ -n "$stim_dir" ]; then
    printf '%s\n' "$stim_dir"
    return 0
  fi

  if [ -d "$DEFAULT_STIM_DIR" ]; then
    return 0
  fi

  echo "NimStim directory was not found at the macOS default path." >&2
  echo "For Windows Git Bash, use a path like /c/Users/you/path/to/NimStim_ER." >&2
  stim_dir="$(prompt_required "NimStim_ER directory")"
  printf '%s\n' "$stim_dir"
}

WINDOW_FLAG=""
PARTICIPANT_ID=""
SESSION=""
RUN_LABEL=""
STIM_DIR="${FACE_STIM_DIR:-}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    window|--window|--windowed)
      WINDOW_FLAG="--window"
      ;;
    fullscreen|--fullscreen)
      ;;
    *)
      if [ -z "$PARTICIPANT_ID" ]; then
        PARTICIPANT_ID="$1"
      elif [ -z "$SESSION" ]; then
        SESSION="$1"
      elif [ -z "$RUN_LABEL" ]; then
        RUN_LABEL="$1"
      elif [ -z "$STIM_DIR" ]; then
        STIM_DIR="$1"
      else
        echo "Unexpected extra argument: $1" >&2
        exit 1
      fi
      ;;
  esac
  shift
done

if [ -z "$PARTICIPANT_ID" ]; then
  PARTICIPANT_ID="$(prompt_default "Participant ID" "TEST01")"
fi
if [ -z "$SESSION" ]; then
  SESSION="$(prompt_default "Session" "01")"
fi
if [ -z "$RUN_LABEL" ]; then
  RUN_LABEL="$(prompt_default "Run" "01")"
fi

STIM_DIR="$(resolve_stim_dir "$STIM_DIR")"

if [ -n "$STIM_DIR" ]; then
  if [ -n "$WINDOW_FLAG" ]; then
    bash ./run_with_env.sh \
      --participant-id "$PARTICIPANT_ID" \
      --session "$SESSION" \
      --run "$RUN_LABEL" \
      --stim-dir "$STIM_DIR" \
      "$WINDOW_FLAG"
  else
    bash ./run_with_env.sh \
      --participant-id "$PARTICIPANT_ID" \
      --session "$SESSION" \
      --run "$RUN_LABEL" \
      --stim-dir "$STIM_DIR"
  fi
else
  if [ -n "$WINDOW_FLAG" ]; then
    bash ./run_with_env.sh \
      --participant-id "$PARTICIPANT_ID" \
      --session "$SESSION" \
      --run "$RUN_LABEL" \
      "$WINDOW_FLAG"
  else
    bash ./run_with_env.sh \
      --participant-id "$PARTICIPANT_ID" \
      --session "$SESSION" \
      --run "$RUN_LABEL"
  fi
fi
