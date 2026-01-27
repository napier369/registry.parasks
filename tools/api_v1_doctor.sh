#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-https://napier369.github.io/registry.parasks}"
RAW="${RAW:-https://raw.githubusercontent.com/napier369/registry.parasks/main}"
NC="${NC:-$(date +%s)}"

echo "== API v1 DOCTOR =="

raw_la="$(curl -fsS "$RAW/api/v1/latest-audit.json" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["latest"])')"

pages_la="$(curl -fsS -H "Cache-Control: no-cache" -H "Pragma: no-cache" \
  "$BASE/api/v1/latest-audit.json?nocache=$NC" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["latest"])')"

audit_idx="$(curl -fsS "$BASE/audit/logs/index.json?nocache=$NC" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["latest"])')"

echo "RAW   latest-audit.json.latest = $raw_la"
echo "PAGES latest-audit.json.latest = $pages_la"
echo "AUDIT audit/logs/index.json    = $audit_idx"

if [[ "$raw_la" != "$audit_idx" ]]; then
  echo "FAIL: RAW pointer != audit index (repo build/push issue)"
  exit 2
fi

if [[ "$pages_la" != "$audit_idx" ]]; then
  echo "WARN: Pages cache lag (expected sometimes). RAW is authoritative."
  exit 0
fi

echo "PASS: RAW + Pages both match audit index"
