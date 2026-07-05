#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
exec bash ./validate_task.sh "$@"
