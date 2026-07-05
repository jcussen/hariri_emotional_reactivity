#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEFAULT_STIM_DIR="$PWD/resources/NimStim_ER"

if [ ! -d "$DEFAULT_STIM_DIR" ]; then
  echo "NimStim_ER was not found at resources/NimStim_ER." >&2
  echo "Move the private NimStim_ER folder into the repo's resources folder first." >&2
  exit 1
fi

bash ./run_with_env.sh \
  --validate-only \
  --seed 1234 \
  --stim-dir "$DEFAULT_STIM_DIR"
