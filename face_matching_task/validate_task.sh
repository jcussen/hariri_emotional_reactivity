#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEFAULT_STIM_DIR="/Users/joecussen/Documents/Jobs/unimelb/projects/breathwork/resources/faces/NimStim_ER"

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

STIM_DIR="$(resolve_stim_dir "${1:-}")"

if [ -n "$STIM_DIR" ]; then
  bash ./run_with_env.sh \
    --validate-only \
    --seed 1234 \
    --stim-dir "$STIM_DIR"
else
  bash ./run_with_env.sh \
    --validate-only \
    --seed 1234
fi
