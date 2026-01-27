#!/usr/bin/env python3
import hashlib, json
from urllib.request import Request, urlopen

BASE="https://napier369.github.io/registry.parasks"

def get_text(url):
    req = Request(url, headers={"User-Agent":"registry.parasks probe"})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def dump_sorted(obj, mode):
    if mode == "sorted_min":
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if mode == "sorted_pretty":
        return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    raise ValueError(mode)

def main(rid):
    url = f"{BASE}/data/{rid}.jsonld"
    txt = get_text(url)
    obj = json.loads(txt)

    expected = obj.get("contentHash","").replace("sha256:","").strip()
    print(f"ID: {rid}")
    print(f"expected(contentHash): {expected}\n")

    # Candidate A: raw bytes as served
    print("A raw-served-bytes:     ", sha256_hex(txt.encode("utf-8")))

    # Candidate B: remove contentHash key, then minified sorted JSON
    o = dict(obj)
    o.pop("contentHash", None)
    print("B drop-key+sorted_min:  ", sha256_hex(dump_sorted(o,"sorted_min").encode("utf-8")))

    # Candidate C: set placeholder, then minified sorted JSON
    o = dict(obj)
    o["contentHash"] = "sha256:REPLACED_AT_RUNTIME"
    print("C placeholder+sorted_min:", sha256_hex(dump_sorted(o,"sorted_min").encode("utf-8")))

    # Candidate D: set placeholder, then pretty sorted JSON (common if you hashed a pretty file)
    o = dict(obj)
    o["contentHash"] = "sha256:REPLACED_AT_RUNTIME"
    print("D placeholder+sorted_pretty:", sha256_hex(dump_sorted(o,"sorted_pretty").encode("utf-8")))

    print("\nMATCH tells you the rule: whichever line equals expected.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("USAGE: python3 tools/hash_probe.py <ID>")
        raise SystemExit(2)
    main(sys.argv[1])
