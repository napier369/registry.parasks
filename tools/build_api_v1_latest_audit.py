#!/usr/bin/env python3
import json
from datetime import datetime, timezone

BASE = "https://napier369.github.io/registry.parasks"

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def write(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    idx = load("audit/logs/index.json")
    latest = idx.get("latest")
    if not latest:
        raise SystemExit("FAIL: audit/logs/index.json has no 'latest'")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

    write("api/v1/latest-audit.json", {
        "apiVersion": "v1",
        "base": BASE,
        "generatedAt": now,
        "pointer": "/audit/logs/index.json",
        "latest": latest
    })

    print(f"OK: wrote api/v1/latest-audit.json latest={latest}")

if __name__ == "__main__":
    raise SystemExit(main())
