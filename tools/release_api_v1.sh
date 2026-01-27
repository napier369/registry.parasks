#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== BUILD api/v1 =="
python3 tools/build_api_v1.py
# Update API pointer so it always matches audit/logs/index.json (avoid cache/lag confusion)
python3 - <<'PY'
import json
idx=json.load(open("audit/logs/index.json","r",encoding="utf-8"))
out={
  "apiVersion":"v1",
  "base":"https://napier369.github.io/registry.parasks",
  "pointer":"/audit/logs/index.json",
  "latest":idx["latest"],
}
with open("api/v1/latest-audit.json","w",encoding="utf-8") as f:
  json.dump(out,f,indent=2,ensure_ascii=False); f.write("\n")
print("OK: wrote api/v1/latest-audit.json ->", out["latest"])
PY

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
