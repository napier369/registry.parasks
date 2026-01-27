#!/usr/bin/env python3
import json, hashlib, urllib.request, urllib.error, time, random

BASE = "https://napier369.github.io/registry.parasks"

def http_get_json(path: str, retries: int = 6, base_sleep: float = 0.6):
    url = BASE + path
    last_err = None
    for attempt in range(retries):
        try:
            # Always add a nocache param to reduce stale/cdn weirdness
            sep = "&" if "?" in url else "?"
            u = f"{url}{sep}nocache={int(time.time())}"
            req = urllib.request.Request(u, headers={"User-Agent": "registry.parasks verifier"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            # Retry on transient server errors + rate limits
            if e.code in (429, 500, 502, 503, 504):
                sleep = base_sleep * (2 ** attempt) + random.random() * 0.25
                time.sleep(sleep)
                continue
            raise
        except Exception as e:
            last_err = e
            sleep = base_sleep * (2 ** attempt) + random.random() * 0.25
            time.sleep(sleep)
            continue
    raise last_err

def canonical_bytes_placeholder_sorted_min(obj: dict) -> bytes:
    # v1 hash rule: placeholder contentHash allowed; sorted keys; minimal separators; UTF-8
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
        try:
            data = http_get_json(data_path)
            actual = sha256_hex(canonical_bytes_placeholder_sorted_min(data))
            if actual == expected:
                print(f"OK  {rid} {actual}")
                ok += 1
            else:
                print(f"FAIL {rid}")
                print(f"  expected: {expected}")
                print(f"  actual:   {actual}")
                fail += 1
        except Exception as e:
            print(f"FAIL {rid}")
            print(f"  expected: {expected}")
            print(f"  error:    {type(e).__name__}: {e}")
            fail += 1

    print(f"\nSUMMARY: ok={ok} fail={fail}")
    return 0 if fail == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
