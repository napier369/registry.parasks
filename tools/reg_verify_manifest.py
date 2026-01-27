#!/usr/bin/env python3
import json, hashlib, urllib.request

BASE = "https://napier369.github.io/registry.parasks"

def http_get_json(path: str):
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "registry.parasks verifier"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def canonical_bytes_placeholder_sorted_min(obj: dict) -> bytes:
    """
    HASH RULE (v1, sealed):
    - Ensure contentHash exists (placeholder allowed)
    - Deterministic JSON: sorted keys, minimal separators, UTF-8
    This matches the 'C placeholder+sorted_min' line from your hash_probe output.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    mani = http_get_json("/api/v1/manifest.json")
    recs = mani.get("records", {})
    ok = fail = 0

    for rid, meta in sorted(recs.items()):
        expected = meta["contentHash"].split("sha256:", 1)[-1].strip()
        data_path = meta["data"]
        data = http_get_json(data_path)

        # Compute using SAME rule as reseal: placeholder present, sorted_min
        actual = sha256_hex(canonical_bytes_placeholder_sorted_min(data))

        if actual == expected:
            print(f"OK  {rid} {actual}")
            ok += 1
        else:
            print(f"FAIL {rid}")
            print(f"  expected: {expected}")
            print(f"  actual:   {actual}")
            fail += 1

    print(f"\nSUMMARY: ok={ok} fail={fail}")
    return 0 if fail == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
