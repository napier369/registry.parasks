#!/usr/bin/env python3
import json, urllib.request

API = "https://napier369.github.io/registry.parasks/api/v1/index.json"

def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "registry.parasks api client"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

idx = get_json(API)
base = idx["base"].rstrip("/")
print("apiVersion:", idx.get("apiVersion"))
print("latestAudit:", base + idx["latestAudit"])
print("records:")
for k, v in sorted(idx["records"].items()):
    print("  ", k, "->", base + v)
