#!/usr/bin/env python3
import sys, json, hashlib, urllib.request

BASE = "https://napier369.github.io/registry.parasks"

def http_get_json(path: str) -> dict:
    url = BASE + path
    req = urllib.request.Request(url, headers={"User-Agent": "registry.parasks verifier"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def canon_sorted_min(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    if len(sys.argv) != 2:
        print("USAGE: verify_id_v1.py <ID>", file=sys.stderr)
        return 2
    rid = sys.argv[1].strip()

    bundle = http_get_json(f"/api/v1/bundle/{rid}.json")
    expected = bundle["contentHash"].split("sha256:", 1)[-1].strip()
    data = http_get_json(bundle["data"])

    # v1 sealed rule: data carries placeholder contentHash, hash canonical sorted_min
    actual = sha256_hex(canon_sorted_min(data))

    print(f"ID: {rid}")
    print(f"expected (bundle): {expected}")
    print(f"actual   (data):   {actual}")
    if actual == expected:
        print("OK: verified")
        return 0
    print("FAIL: mismatch")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
