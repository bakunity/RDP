#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
find "$ROOT/scripts" -type f -name '*.sh' -print0 | xargs -0 -n1 bash -n
python3 -m compileall -q "$ROOT/server/hermes_rdp"
PYTHONPATH="$ROOT/server" python3 -m unittest discover -s "$ROOT/tests" -v
