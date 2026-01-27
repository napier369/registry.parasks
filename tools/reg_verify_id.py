#!/usr/bin/env python3
import hashlib, json, sys, urllib.request

BASE = "https://napier369.github.io/registry.parasks"

def get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "registry.parasks verifier"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")

def canonical_json_bytes(obj: dict) -> bytes:
    # Canonical JSON: sorted keys, stable separators, UTF-8
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) != 2:
        print("USAGE: python3 tools/reg_verify_id.py E000004", file=sys.stderr)
        return 2

    rid = sys.argv[1].strip().upper()
    url = f"{BASE}/data/{rid}.jsonld"
    obj = json.loads(get_text(url))

    ch = obj.get("contentHash", "")
    if not ch.startswith("sha256:"):
        raise SystemExit(f"FAIL: contentHash missing/invalid in {rid}")

    expected = ch.split("sha256:", 1)[1].strip()

    # Hash canonical form with contentHash neutralized (so record can contain its own hash)
    obj2 = dict(obj)
    obj2["contentHash"] = "sha256:"
    actual = sha256_hex(canonical_json_bytes(obj2))

    print("ID:", rid)
    print("expected:", expected)
    print("actual:  ", actual)
    print("OK" if expected == actual else "FAIL")

if __name__ == "__main__":
    raise SystemExit(main())
