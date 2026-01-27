#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone

BASE = "https://napier369.github.io/registry.parasks"
OUT_DIR = "api/v1/bundle"
MANIFEST_PATH = "api/v1/manifest.json"
LATEST_AUDIT_PATH = "api/v1/latest-audit.json"

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main() -> int:
    if not os.path.isfile(MANIFEST_PATH):
        raise SystemExit(f"FAIL: missing {MANIFEST_PATH}. Run your manifest generator first.")

    manifest = load_json(MANIFEST_PATH)
    latest_audit = load_json(LATEST_AUDIT_PATH) if os.path.isfile(LATEST_AUDIT_PATH) else None

    records = manifest.get("records", {})
    if not isinstance(records, dict) or not records:
        raise SystemExit("FAIL: manifest.records missing/empty")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    count = 0
    for rid, meta in sorted(records.items()):
        # meta: { data: "/data/ID.jsonld", contentHash: "sha256:..." }
        data_path = meta.get("data")
        content_hash = meta.get("contentHash")

        bundle = {
            "apiVersion": "v1",
            "base": BASE,
            "generatedAt": generated_at,
            "id": rid,
            "resolver": f"/id/{rid}/",
            "page": f"/page/{rid}/",
            "data": data_path,
            "contentHash": content_hash,
            "latestAuditPointer": "/audit/logs/index.json",
        }

        # convenience: include latest audit file if we have it
        if latest_audit and isinstance(latest_audit, dict):
            bundle["latestAudit"] = latest_audit.get("latest")

        out_path = os.path.join(OUT_DIR, f"{rid}.json")
        write_json(out_path, bundle)
        count += 1

    print(f"OK: wrote {count} bundles into {OUT_DIR}/")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
