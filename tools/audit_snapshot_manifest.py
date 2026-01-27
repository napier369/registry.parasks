#!/usr/bin/env python3
import json, os, re, hashlib, subprocess
from datetime import datetime, timezone

IDX = "audit/logs/index.json"
MANI = "api/v1/manifest.json"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def next_seq(latest_path: str | None) -> str:
    if not latest_path:
        return "000001"
    m = re.search(r"/(\d{6})\.json$", latest_path)
    if not m:
        return "000001"
    n = int(m.group(1)) + 1
    return f"{n:06d}"

def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNKNOWN"

def main():
    os.makedirs("audit/logs", exist_ok=True)

    if not os.path.isfile(MANI):
        raise SystemExit(f"FAIL: missing {MANI} (run build/release first)")

    idx = {"latest": None, "logs": []}
    if os.path.isfile(IDX):
        with open(IDX, "r", encoding="utf-8") as f:
            idx = json.load(f)

    seq = next_seq(idx.get("latest"))
    out = f"audit/logs/{seq}.json"

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    entry = {
        "seq": seq,
        "time": now,
        "gitCommit": git_head(),
        "apiVersion": "v1",
        "manifest": f"/{MANI}",
        "manifestSha256": f"sha256:{sha256_file(MANI)}"
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
        f.write("\n")

    latest = f"/audit/logs/{seq}.json"
    logs = idx.get("logs", [])
    logs.append(latest)

    idx2 = {
        "latest": latest,
        "logs": logs
    }
    with open(IDX, "w", encoding="utf-8") as f:
        json.dump(idx2, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"OK: wrote {out}")
    print(f"OK: updated {IDX} latest={latest}")

if __name__ == "__main__":
    raise SystemExit(main())
