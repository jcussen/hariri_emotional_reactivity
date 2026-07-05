#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ARGS=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    window|--window|--windowed)
      ARGS+=(--window)
      ;;
    fullscreen|--fullscreen)
      ;;
    --stim-dir|--participant-id|--session|--run|--seed)
      if [ "$#" -lt 2 ]; then
        echo "$1 requires a value." >&2
        exit 1
      fi
      ARGS+=("$1" "$2")
      shift
      ;;
    --validate-only)
      ARGS+=("$1")
      ;;
    --*)
      ARGS+=("$1")
      ;;
    *)
      ARGS+=("$1")
      ;;
  esac
  shift
done

bash ./run_with_env.sh "${ARGS[@]}"
