#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== BUILD api/v1 =="
python3 tools/build_api_v1.py

echo "== SMOKE TEST =="
bash tools/api_v1_smoketest.sh

echo "== COMMIT+PUSH (only if changed) =="
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes detected. Nothing to commit."
  exit 0
fi

git add \
  api/v1/index.json \
  api/v1/records.json \
  api/v1/manifest.json \
  api/v1/capabilities.json \
  api/v1/bundle/*.json

git commit -m "Release API v1 (rebuild index/records/bundles/manifest)"
git push
echo "OK: released"
