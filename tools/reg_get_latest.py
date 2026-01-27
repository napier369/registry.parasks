#!/usr/bin/env python3
import json, urllib.request

BASE = "https://napier369.github.io/registry.parasks"

def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "registry.parasks client"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

idx = get_json(f"{BASE}/audit/logs/index.json")
latest_path = idx["latest"]
latest = get_json(f"{BASE}/{latest_path}")

print("latestSeq:", idx["latestSeq"])
print("latestAudit:", latest_path)
print("event:", latest.get("event"))
print("targets:", latest.get("targets") or latest.get("adds") or [])
