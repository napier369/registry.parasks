#!/usr/bin/env python3
import hashlib, json, re, sys
from pathlib import Path

RID_RE = re.compile(r"^[A-Z]\d{6}$")

def canon_bytes(obj: dict) -> bytes:
    import json as _json
    s = _json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return s.encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def fail(msg: str):
    print("FAIL:", msg)
    raise SystemExit(2)

def main():
    if len(sys.argv) != 2 or not RID_RE.match(sys.argv[1].upper()):
        fail("USAGE: python3 tools/issue_check.py E000004")

    rid = sys.argv[1].upper()

    data_path = Path("data") / f"{rid}.jsonld"
    if not data_path.exists():
        fail(f"missing {data_path}")

    obj = json.loads(data_path.read_text(encoding="utf-8"))
    ch = obj.get("contentHash", "")
    if not ch.startswith("sha256:"):
        fail("contentHash missing/invalid")

    expected = ch.split("sha256:", 1)[1].strip()
    obj2 = dict(obj)
    obj2["contentHash"] = "sha256:"
    actual = sha256_hex(canon_bytes(obj2))
    if actual != expected:
        fail(f"contentHash mismatch expected={expected} actual={actual}")

    page_path = Path("page") / rid / "index.html"
    id_path = Path("id") / rid / "index.html"
    if not page_path.exists():
        fail(f"missing {page_path}")
    if not id_path.exists():
        fail(f"missing {id_path}")

    audit_idx = Path("audit/logs/index.json")
    if not audit_idx.exists():
        fail("missing audit/logs/index.json")

    print("OK:", rid)
    print(" - data:", data_path)
    print(" - page:", page_path)
    print(" - id:  ", id_path)
    print(" - hash:", expected)

if __name__ == "__main__":
    main()
