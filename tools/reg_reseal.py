#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path

PLACEHOLDER = "sha256:REPLACED_AT_RUNTIME"

def canon_bytes(obj: dict) -> bytes:
    o = dict(obj)
    o["contentHash"] = PLACEHOLDER
    s = json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main(rid: str):
    p = Path("data") / f"{rid}.jsonld"
    if not p.exists():
        print(f"FAIL: missing {p}")
        return 2

    obj = json.loads(p.read_text(encoding="utf-8"))
    h = sha256_hex(canon_bytes(obj))
    obj["contentHash"] = f"sha256:{h}"
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: resealed {rid} -> sha256:{h}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USAGE: python3 tools/reg_reseal.py <ID>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
