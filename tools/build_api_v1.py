#!/usr/bin/env python3
import json, glob, os, hashlib
from datetime import datetime, timezone

BASE = "https://napier369.github.io/registry.parasks"
PLACEHOLDER = "sha256:REPLACED_AT_RUNTIME"

def canonical_placeholder_sorted_min(obj: dict) -> bytes:
    # v1 sealed hash rule: placeholder allowed, sorted keys, min separators, utf-8
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, obj: dict):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def ensure_leading_slash(p: str) -> str:
    if not p:
        return p
    return p if p.startswith("/") else ("/" + p)

def main():
    # Collect IDs from /data/*.jsonld
    ids = sorted([os.path.splitext(os.path.basename(p))[0] for p in glob.glob("data/*.jsonld")])

    # Audit pointer/index (latest may be stored as relative; normalize for API)
    audit_idx = load_json("audit/logs/index.json")
    latest_audit = ensure_leading_slash(audit_idx.get("latest", ""))

    # Timestamp for generated files
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # 1) records.json (list form)
    records_list = []
    for rid in ids:
        records_list.append({
            "id": rid,
            "data": f"/data/{rid}.jsonld",
            "page": f"/page/{rid}/",
            "resolver": f"/id/{rid}/"
        })
    write_json("api/v1/records.json", {
        "apiVersion": "v1",
        "base": BASE,
        "records": records_list
    })

    # 2) index.json (map form + pointers)
    write_json("api/v1/index.json", {
        "apiVersion": "v1",
        "base": BASE,
        "latestAudit": "/audit/logs/index.json",
        "wikiIndex": "/api/v1/wiki.json",
        "records": { rid: f"/data/{rid}.jsonld" for rid in ids }
    })

    # 3) manifest (sealed hashes of canonical bytes, using placeholder rule)
    manifest_recs = {}
    for rid in ids:
        obj = load_json(f"data/{rid}.jsonld")
        # enforce placeholder presence to match v1 rule
        obj["contentHash"] = PLACEHOLDER
        sealed = sha256_hex(canonical_placeholder_sorted_min(obj))
        manifest_recs[rid] = {
            "data": f"/data/{rid}.jsonld",
            "contentHash": f"sha256:{sealed}"
        }
    write_json("api/v1/manifest.json", {
        "apiVersion": "v1",
        "base": BASE,
        "latestAudit": "/audit/logs/index.json",
        "records": manifest_recs
    })

    # 4) bundles (MUST use sealed hash from manifest; NEVER use placeholder from /data)
    for rid in ids:
        sealed_ch = manifest_recs[rid]["contentHash"]
        write_json(f"api/v1/bundle/{rid}.json", {
            "apiVersion": "v1",
            "base": BASE,
            "id": rid,
            "resolver": f"/id/{rid}/",
            "page": f"/page/{rid}/",
            "data": f"/data/{rid}.jsonld",
            "contentHash": sealed_ch,
            "latestAuditPointer": "/audit/logs/index.json",
            "latestAudit": latest_audit
        })

    print(f"OK: built api/v1 (ids={len(ids)})")

if __name__ == "__main__":
    raise SystemExit(main())
