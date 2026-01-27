#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-https://napier369.github.io/registry.parasks}"
NC="$(date +%s)"

say() { echo ""; echo "== $* =="; }

say "1) api/v1/index.json parses"
curl -sS "$BASE/api/v1/index.json?nocache=$NC" | python3 -m json.tool >/dev/null

say "2) api/v1/capabilities.json parses + bundleTemplate present"
curl -sS "$BASE/api/v1/capabilities.json?nocache=$NC" | python3 -m json.tool >/dev/null
curl -sS "$BASE/api/v1/capabilities.json?nocache=$NC" | python3 -m json.tool | grep -q '"bundleTemplate"' \
  && echo "OK: bundleTemplate present" \
  || { echo "FAIL: bundleTemplate missing"; exit 1; }

say "3) bundle example must resolve + include sealed contentHash + absolute latestAudit"
curl -sS "$BASE/api/v1/bundle/E000004.json?nocache=$NC" | python3 -m json.tool >/dev/null
curl -sS "$BASE/api/v1/bundle/E000004.json?nocache=$NC" | python3 -m json.tool | egrep 'contentHash|latestAudit'

say "4) manifest served"
curl -sS "$BASE/api/v1/manifest.json?nocache=$NC" | python3 -m json.tool >/dev/null

say "5) local verifier clean"
python3 tools/reg_verify_manifest.py

say "6) latest-audit pointer must match audit index"
LA="$(curl -sS "$BASE/api/v1/latest-audit.json?nocache=$NC" | python3 -c 'import sys,json; print(json.load(sys.stdin)["latest"])')"
AI="$(curl -sS "$BASE/audit/logs/index.json?nocache=$NC" | python3 -c 'import sys,json; print(json.load(sys.stdin)["latest"])')"

echo "latest-audit.json.latest     = $LA"
echo "audit/logs/index.json.latest = $AI"

if [[ "$LA" != "$AI" ]]; then
  echo "FAIL: latest-audit pointer drift"
  exit 1
fi

echo "OK: latest-audit pointer matches audit index"
echo ""
echo "PASS: API v1 smoke test complete"
