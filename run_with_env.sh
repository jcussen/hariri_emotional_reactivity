#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PREFIX="$SCRIPT_DIR/.conda_env"
PSYCHOPY_HOME="$SCRIPT_DIR/.home"

if [ -x "$ENV_PREFIX/bin/python" ]; then
  PYTHON="$ENV_PREFIX/bin/python"
elif [ -x "$ENV_PREFIX/Scripts/python.exe" ]; then
  PYTHON="$ENV_PREFIX/Scripts/python.exe"
else
  echo "Missing environment at $ENV_PREFIX"
  echo "Create it with:"
  echo "  cd \"$SCRIPT_DIR\""
  echo "  bash setup_env.sh"
  exit 1
fi

mkdir -p "$PSYCHOPY_HOME"
export HOME="$PSYCHOPY_HOME"

if [ "${1:-}" = "window" ]; then
  shift
  exec "$PYTHON" "$SCRIPT_DIR/run_task.py" --window "$@"
fi

exec "$PYTHON" "$SCRIPT_DIR/run_task.py" "$@"
