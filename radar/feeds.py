"""Free RSS/Atom discovery with a separate baseline per publisher."""
from __future__ import annotations

import hashlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from . import UA, snap, terms


def parse(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    atom = "{http://www.w3.org/2005/Atom}"
    entries = root.findall("./channel/item") if root.tag == "rss" else root.findall(atom + "entry")
    rows = []
    for entry in entries:
        if root.tag == "rss":
            title, url = entry.findtext("title", ""), entry.findtext("link", "")
            identity = entry.findtext("guid") or url or title
        else:
            title = entry.findtext(atom + "title", "")
            links = entry.findall(atom + "link")
            url = next((e.get("href", "") for e in links if e.get("rel", "alternate") == "alternate"), "")
            identity = entry.findtext(atom + "id") or url or title
        if title and identity:
            rows.append({"id": identity, "title": title, "url": url})
    return rows


def discover(cfg: dict, state: Path) -> dict:
    statuses, found, articles = {}, {}, []
    for name, settings in cfg.get("feeds", {}).items():
        try:
            request = urllib.request.Request(settings["url"], headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=30) as response:
                rows = parse(response.read())
            digest = hashlib.sha256(settings["url"].encode()).hexdigest()[:16]
            path = state / f"feed-{digest}.json.gz"
            before = snap.load(path)
            seen = set(before or [])
            fresh = [r for r in rows if before is not None and r["id"] not in seen]
            pattern = settings.get("include", "")
            for row in fresh:
                if pattern and not re.search(pattern, row["title"], re.I):
                    continue
                articles.append({"source": name, **row})
                for term in sorted(terms.names(row["title"]))[:5]:
                    lead = found.setdefault(term, {"term": term, "recent": 0, "examples": [], "note": ""})
                    lead["recent"] += 1
                    lead["examples"].append(f"{row['title']} ({row['url']})")
                    lead["note"] = f"Publisher feed: {lead['recent']} new article(s)"
            snap.save(path, list(dict.fromkeys([r['id'] for r in rows] + list(before or [])))[:5000])
            statuses[name] = {"items": len(rows), "new": len(fresh), "first_run": before is None}
        except (OSError, ValueError, ET.ParseError) as exc:
            statuses[name] = {"error": f"{type(exc).__name__}: {str(exc)[:160]}"}
    return {"sources": statuses, "terms": list(found.values()), "articles": articles}
