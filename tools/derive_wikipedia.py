#!/usr/bin/env python3
"""
Derive structured signals from Wikipedia (API only) and emit:
- raw JSON response (for provenance)
- derived tags + categories
- registry JSON-LD record (no copied prose)

Usage:
  python3 tools/derive_wikipedia.py "Albert Einstein" E000003
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_PAGE_BASE = "https://en.wikipedia.org/wiki/"

def http_get_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "registry.parasks derivation bot (contact: local) Python urllib",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")
    return json.loads(data)

def slugify(title: str) -> str:
    # For filenames/paths only (not identifiers)
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "page"

def derive_tags(title: str, categories: list[str]) -> list[str]:
    tags: set[str] = set()

    # Title keywords
    for tok in re.findall(r"[A-Za-z0-9]+", title.lower()):
        if len(tok) >= 3:
            tags.add(tok)

    # Category keywords (strip "Category:" and simplify)
    for c in categories:
        c = c.replace("Category:", "").lower()
        c = re.sub(r"[^a-z0-9 ]+", " ", c)
        for tok in c.split():
            if len(tok) >= 4 and tok not in {"from", "with", "that", "this", "their"}:
                tags.add(tok)

    # Small normalisations
    if "einstein" in tags:
        tags.add("relativity")
        tags.add("physics")

    return sorted(tags)

def main() -> int:
    if len(sys.argv) < 3:
        print('USAGE: python3 tools/derive_wikipedia.py "Albert Einstein" E000003', file=sys.stderr)
        return 2

    title = sys.argv[1]
    out_id = sys.argv[2].strip().upper()

    # Timestamp for provenance
    retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    # Query: page info + revision id + categories
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "titles": title,
        "prop": "info|categories|pageprops",
        "cllimit": "500",
        "inprop": "url",
        # pageprops often contains wikibase_item (QID) when present
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    raw = http_get_json(url)

    pages = raw.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise SystemExit(f"FAIL: page not found: {title}")

    page = pages[0]
    resolved_title = page.get("title", title)
    pageid = page.get("pageid")
    fullurl = page.get("fullurl") or (WIKI_PAGE_BASE + urllib.parse.quote(resolved_title.replace(" ", "_")))
    qid = (page.get("pageprops") or {}).get("wikibase_item")

    categories = [c.get("title") for c in page.get("categories", []) if c.get("title")]
    tags = derive_tags(resolved_title, categories)

    # Outputs
    slug = slugify(resolved_title)
    raw_dir = Path("sources/raw/wikipedia") / slug
    raw_dir.mkdir(parents=True, exist_ok=True)

    (raw_dir / "query.json").write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Registry JSON-LD (NO copied prose; only derived signals + provenance)
    record = {
        "@context": "https://registry.parasks/ontology/v1/context.jsonld",
        "@id": f"https://registry.parasks/id/{out_id}",
        "@type": "Entity",
        "rdfs:label": {"en": resolved_title},
        "registry:status": "active",
        "registry:issuedAt": retrieved,
        "registry:tags": tags,
        "registry:source": {
            "name": "Wikipedia",
            "pageTitle": resolved_title,
            "pageId": pageid,
            "pageUrl": fullurl,
            "wikidataQid": qid,
            "retrievedAt": retrieved
        }
    }

    out_path = Path("data") / f"{out_id}.jsonld"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"OK: wrote {out_path}")
    print(f"OK: raw saved {raw_dir}/query.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
