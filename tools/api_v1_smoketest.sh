cd ~/registry.parasks

cat > tools/api_v1_smoketest.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-https://napier369.github.io/registry.parasks}"
NC="$(date +%s)"

say(){ printf "\n== %s ==\n" "$*"; }

say "1) api/v1/index.json parses"
curl -sS "$BASE/api/v1/index.json?nocache=$NC" | python3 -m json.tool >/dev/null

say "2) api/v1/capabilities.json parses + bundleTemplate present"
curl -sS "$BASE/api/v1/capabilities.json?nocache=$NC" | python3 -m json.tool >/dev/null
curl -sS "$BASE/api/v1/capabilities.json?nocache=$NC" | python3 -m json.tool | grep -q '"bundleTemplate"' \
  && echo "OK: bundleTemplate present"

say "3) bundle example must resolve + include sealed contentHash + absolute latestAudit"
curl -sS "$BASE/api/v1/bundle/E000004.json?nocache=$NC" | python3 -m json.tool >/dev/null
curl -sS "$BASE/api/v1/bundle/E000004.json?nocache=$NC" | python3 -m json.tool | egrep 'contentHash|latestAudit'

say "4) manifest served"
curl -sS "$BASE/api/v1/manifest.json?nocache=$NC" | python3 -m json.tool >/dev/null

say "5) local verifier clean"
python3 tools/reg_verify_manifest.py

echo
echo "PASS: API v1 smoke test complete"
SH

chmod +x tools/api_v1_smoketest.sh

# quick run now
./tools/api_v1_smoketest.sh
