#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_PREFIX="$PWD/.conda_env"

find_conda() {
  if command -v conda >/dev/null 2>&1; then
    command -v conda
    return 0
  fi

  local candidates=(
    "/opt/homebrew/Caskroom/miniconda/base/bin/conda"
    "$HOME/miniconda3/bin/conda"
    "$HOME/anaconda3/bin/conda"
  )

  if [ -n "${USERPROFILE:-}" ]; then
    if command -v cygpath >/dev/null 2>&1; then
      candidates+=(
        "$(cygpath -u "$USERPROFILE/miniconda3/Scripts/conda.exe")"
        "$(cygpath -u "$USERPROFILE/anaconda3/Scripts/conda.exe")"
      )
    else
      candidates+=(
        "$USERPROFILE/miniconda3/Scripts/conda.exe"
        "$USERPROFILE/anaconda3/Scripts/conda.exe"
      )
    fi
  fi

  local candidate
  for candidate in "${candidates[@]}"; do
    if [ -x "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

CONDA_EXE="$(find_conda)" || {
  echo "Could not find conda. Install Miniconda or add conda to PATH first."
  exit 1
}

if [ -x "$ENV_PREFIX/bin/python" ] || [ -x "$ENV_PREFIX/Scripts/python.exe" ]; then
  echo "Updating existing environment at $ENV_PREFIX..."
  "$CONDA_EXE" env update -p "$ENV_PREFIX" -f environment.yml --prune
else
  echo "Creating environment at $ENV_PREFIX..."
  "$CONDA_EXE" env create -p "$ENV_PREFIX" -f environment.yml
fi

echo
echo "Environment is ready."
echo "Windowed test run:"
echo "  bash run_task.sh window"
echo "Fullscreen run:"
echo "  bash run_task.sh"
