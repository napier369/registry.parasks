#!/usr/bin/env python3
import json, os, re
from pathlib import Path

BASE = "https://napier369.github.io/registry.parasks"

data_dir = Path("data")
records = {}

pat = re.compile(r"^[A-Z]\d{6}\.jsonld$")

for p in sorted(data_dir.glob("*.jsonld")):
    if not pat.match(p.name):
        continue
    rid = p.stem
    records[rid] = f"/data/{p.name}"

out = {
    "apiVersion": "v1",
    "base": BASE,
    "latestAudit": "/audit/logs/index.json",
    "records": records
}

Path("api/v1").mkdir(parents=True, exist_ok=True)
Path("api/v1/index.json").write_text(json.dumps(out, indent=2, sort_keys=False) + "\n", encoding="utf-8")
print("OK: wrote api/v1/index.json with", len(records), "records")
