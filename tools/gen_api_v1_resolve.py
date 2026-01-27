#!/usr/bin/env python3
import json, os, glob

BASE = "https://napier369.github.io/registry.parasks"

def main():
    os.makedirs("api/v1/resolve", exist_ok=True)
    ids = sorted([os.path.splitext(os.path.basename(p))[0] for p in glob.glob("data/*.jsonld")])

    for rid in ids:
        out = f"api/v1/resolve/{rid}.json"
        obj = {
            "apiVersion": "v1",
            "base": BASE,
            "id": rid,
            "resolver": f"/id/{rid}/",
            "page": f"/page/{rid}/",
            "data": f"/data/{rid}.jsonld",
        }
        with open(out, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")

    print(f"OK: wrote {len(ids)} resolve files into api/v1/resolve/")

if __name__ == "__main__":
    main()
