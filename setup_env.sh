#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_PREFIX="$PWD/.conda_env"
PSYCHOPY_VERSION="2023.2.3"

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

if [ -x "$ENV_PREFIX/bin/python" ]; then
  PYTHON="$ENV_PREFIX/bin/python"
elif [ -x "$ENV_PREFIX/Scripts/python.exe" ]; then
  PYTHON="$ENV_PREFIX/Scripts/python.exe"
else
  echo "Could not find Python in $ENV_PREFIX after setup."
  exit 1
fi

OLD_PYOBJC_PACKAGES="$("$PYTHON" -m pip freeze | awk -F== 'tolower($1) ~ /^pyobjc/ && $2 != "7.3" {print $1}')"
if [ -n "$OLD_PYOBJC_PACKAGES" ]; then
  # Downgrading an existing PsychoPy 2026 environment can leave newer pyobjc
  # framework wheels behind. Remove only those stale pyobjc wheels.
  "$PYTHON" -m pip uninstall -y $OLD_PYOBJC_PACKAGES
fi

echo "Installing PsychoPy $PSYCHOPY_VERSION..."
"$PYTHON" -m pip install --no-deps "psychopy==$PSYCHOPY_VERSION"

PSYCHOPY_HOME="$PWD/.home"
mkdir -p "$PSYCHOPY_HOME"
INSTALLED_PSYCHOPY_VERSION="$(HOME="$PSYCHOPY_HOME" "$PYTHON" -c 'import psychopy; print(psychopy.__version__)')"
if [ "$INSTALLED_PSYCHOPY_VERSION" != "$PSYCHOPY_VERSION" ]; then
  echo "Expected PsychoPy $PSYCHOPY_VERSION but found $INSTALLED_PSYCHOPY_VERSION." >&2
  exit 1
fi
INSTALLED_NUMPY_VERSION="$("$PYTHON" -c 'import numpy; print(numpy.__version__)')"
NUMPY_MAJOR="${INSTALLED_NUMPY_VERSION%%.*}"
if [ "$NUMPY_MAJOR" -ge 2 ]; then
  echo "Expected NumPy < 2.0 for PsychoPy $PSYCHOPY_VERSION but found $INSTALLED_NUMPY_VERSION." >&2
  exit 1
fi

echo
echo "Environment is ready with PsychoPy $INSTALLED_PSYCHOPY_VERSION and NumPy $INSTALLED_NUMPY_VERSION."
echo "Windowed test run:"
echo "  bash run_task.sh window"
echo "Fullscreen run:"
echo "  bash run_task.sh"
