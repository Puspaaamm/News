#!/usr/bin/env python3
"""Rail News: RSS feeds se khabrein kheench kar news.json banata hai (sirf stdlib)."""
import json, re, html, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

GN = "https://news.google.com/rss/search?q={}&hl=en-IN&gl=IN&ceid=IN:en"
FEEDS = [
    ("The Hindu", "https://www.thehindu.com/news/national/feeder/default.rss"),
    ("The Hindu", "https://www.thehindu.com/news/international/feeder/default.rss"),
    ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC", "https://feeds.bbci.co.uk/news/rss.xml"),
    # Reuters aur ANI ke official public RSS nahi hain, isliye Google News RSS (site filter).
    ("Reuters", GN.format("site:reuters.com%20when:1d")),
    ("ANI", GN.format("site:aninews.in%20when:1d")),
]
PER_SOURCE = 15
GOOGLE_SOURCES = ("Reuters", "ANI")
HEADERS = {"User-Agent": "Mozilla/5.0 (RailNewsBot)"}


def clean(s):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return ET.fromstring(r.read())


def parse(source, root):
    out = []
    for it in root.iter("item"):
        title = clean(it.findtext("title"))
        link = (it.findtext("link") or "").strip()
        if not title or not link:
            continue
        if source in GOOGLE_SOURCES:
            title = re.sub(r"\s+-\s+[^-]+$", "", title)  # "Headline - Reuters" -> "Headline"
            text = ""
        else:
            text = clean(it.findtext("description"))[:150]
        try:
            d = parsedate_to_datetime(it.findtext("pubDate"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
        except Exception:
            d = datetime.now(timezone.utc)
        out.append({"source": source, "title": title, "text": text, "url": link,
                    "date": d.astimezone(timezone.utc).isoformat()})
    return out


def main():
    buckets, seen = {}, set()
    for source, url in FEEDS:
        try:
            items = parse(source, fetch(url))
        except Exception as e:
            print("WARN:", source, url, e, file=sys.stderr)
            continue
        for n in items:
            if n["url"] in seen:
                continue
            seen.add(n["url"])
            buckets.setdefault(source, []).append(n)
    for s in buckets:
        buckets[s].sort(key=lambda n: n["date"], reverse=True)
        buckets[s] = buckets[s][:PER_SOURCE]
    mixed = []
    for i in range(PER_SOURCE):  # round-robin: har source ki khabar track par aaye
        for s in buckets:
            if i < len(buckets[s]):
                mixed.append(buckets[s][i])
    if not mixed:
        print("Koi khabar nahi mili, news.json badla nahi gaya.", file=sys.stderr)
        sys.exit(1)
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(), "items": mixed},
                  f, ensure_ascii=False, indent=1)
    print("OK:", len(mixed), "khabrein,", {s: len(v) for s, v in buckets.items()})


if __name__ == "__main__":
    main()
