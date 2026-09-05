#!/usr/bin/env python3
"""
Duplication analysis for the five location pages.

Why this exists: Google indexed 3 of 38 URLs. The location pages were built from one
template with the city name swapped, which reads to a crawler as one page repeated five
times. This script measures that objectively so "we fixed it" is a number, not a vibe.

Two measurements, because they answer different questions:

  RAW        — shingle overlap on the body copy as written. This is what a crawler
               comparing two URLs sees.
  CITY-MASKED— same, but every city/county/road/landmark proper noun is replaced with a
               token first. This is the honest one. Raw similarity drops the moment you
               swap "Cary" for "Durham" in an otherwise identical sentence, so a page can
               look distinct on RAW while still being a doorway page. If MASKED is high,
               the pages are templated no matter what RAW says.

Body copy only: nav, header, footer, script, style, svg and the shared review carousel
are excluded, because those are *supposed* to be identical and counting them would drown
out the signal we care about.

Usage:  python3 scripts/dup-check.py [--json] [--show-dupes N]
"""

import re
import sys
import json
import unicodedata
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent

PAGES = [
    "mobile-detailing-cary.html",
    "mobile-detailing-durham.html",
    "mobile-detailing-wake-forest.html",
    "mobile-detailing-apex.html",
    "mobile-detailing-chapel-hill.html",
]

# Containers whose contents are shared site furniture by design.
STRIP_TAGS = ["script", "style", "svg", "nav", "footer", "header", "noscript"]

# Sections that are intentionally identical across pages (shared components).
# Matched on the class attribute of a <section>.
STRIP_SECTION_CLASSES = [
    "rev-section",      # review carousel — same testimonials sitewide
    "social-section",   # instagram embed
    "trustbar",
]

SHINGLE = 8  # words per shingle; long enough that a shared sentence registers,
             # short enough that a reworded clause still counts as overlap.

# Proper nouns that legitimately differ per page. Masked for the CITY-MASKED pass so we
# measure sentence *structure* rather than the swapped noun.
GEO_TERMS = [
    # cities / towns
    "chapel hill", "wake forest", "holly springs", "fuquay-varina", "morrisville",
    "hillsborough", "carrboro", "knightdale", "garner", "clayton", "youngsville",
    "rolesville", "raleigh", "durham", "cary", "apex", "wakefield", "brier creek",
    "north hills", "research triangle park", "rtp", "the triangle", "triangle",
    "wake county", "durham county", "orange county", "chatham county",
    # neighborhoods / landmarks / roads that vary by page
    "preston", "weycroft", "amberly", "macgregor downs", "lochmere", "cary park",
    "trinity park", "forest hills", "hope valley", "duke park", "watts hospital",
    "old west durham", "woodcroft", "southpoint", "brightleaf", "ninth street",
    "heritage", "traditions", "st. andrews", "stadium drive", "wake forest reservoir",
    "scotts mill", "salem village", "haddon hall", "sweetwater", "beaver creek",
    "meadowmont", "southern village", "briar chapel", "governors club", "franklin street",
    "duke university", "unc", "nc state", "american tobacco", "umstead",
    "i-40", "i-540", "540", "us-1", "us 1", "us-15-501", "15-501", "us-70", "nc-55",
    "nc 55", "nc-54", "nc 54", "capital boulevard", "falls of neuse", "harrison avenue",
]
GEO_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(t) for t in GEO_TERMS),
                                             key=len, reverse=True)) + r")\b", re.I)
NUM_RE = re.compile(r"\b\d+\b")


def strip_html(html: str) -> str:
    """Return visible body copy, minus shared furniture."""
    s = html
    for tag in STRIP_TAGS:
        s = re.sub(rf"<{tag}\b.*?</{tag}>", " ", s, flags=re.S | re.I)
        s = re.sub(rf"<{tag}\b[^>]*/?>", " ", s, flags=re.I)
    for cls in STRIP_SECTION_CLASSES:
        # non-greedy to the next </section>; these sections are not nested
        s = re.sub(rf'<section\b[^>]*class="[^"]*{re.escape(cls)}[^"]*".*?</section>',
                   " ", s, flags=re.S | re.I)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "\n", s)
    return s


def unescape(s: str) -> str:
    import html as _h
    return _h.unescape(s)


def paragraphs(html: str):
    """Normalized text blocks of >= 6 words, as they'd read to a person."""
    text = unescape(strip_html(html))
    text = unicodedata.normalize("NFKD", text)
    out = []
    for block in text.split("\n"):
        block = re.sub(r"\s+", " ", block).strip()
        if len(block.split()) >= 6:
            out.append(block)
    return out


def words(paras):
    joined = " ".join(paras).lower()
    joined = re.sub(r"[^a-z0-9\s'-]", " ", joined)
    return joined.split()


def mask(paras):
    joined = " ".join(paras)
    joined = GEO_RE.sub(" __GEO__ ", joined)
    joined = NUM_RE.sub(" __NUM__ ", joined)
    joined = joined.lower()
    joined = re.sub(r"[^a-z0-9_\s'-]", " ", joined)
    return joined.split()


def shingles(ws, n=SHINGLE):
    return {" ".join(ws[i:i + n]) for i in range(max(0, len(ws) - n + 1))}


def overlap_pct(a: set, b: set) -> float:
    """Symmetric overlap: shared shingles / shingles in the smaller page.

    Not Jaccard. If a short page is wholly contained in a long one it is 100%
    duplicated, and Jaccard would understate that by dividing by the union.
    """
    if not a or not b:
        return 0.0
    return 100.0 * len(a & b) / min(len(a), len(b))


def main():
    as_json = "--json" in sys.argv
    show_n = 12
    if "--show-dupes" in sys.argv:
        show_n = int(sys.argv[sys.argv.index("--show-dupes") + 1])

    data = {}
    for p in PAGES:
        fp = ROOT / p
        if not fp.exists():
            print(f"MISSING: {p}", file=sys.stderr)
            continue
        html = fp.read_text(encoding="utf-8")
        paras = paragraphs(html)
        raw_w = words(paras)
        data[p] = {
            "paras": paras,
            "words": len(raw_w),
            "raw": shingles(raw_w),
            "masked": shingles(mask(paras)),
        }

    names = list(data)
    short = {p: p.replace("mobile-detailing-", "").replace(".html", "") for p in names}

    # ---- word counts
    print("=" * 74)
    print("BODY WORD COUNT  (nav/header/footer/reviews/instagram excluded)")
    print("=" * 74)
    for p in names:
        print(f"  {short[p]:<12} {data[p]['words']:>6} words")
    print()

    # ---- pairwise
    rows = []
    for a, b in combinations(names, 2):
        rows.append({
            "a": short[a], "b": short[b],
            "raw": overlap_pct(data[a]["raw"], data[b]["raw"]),
            "masked": overlap_pct(data[a]["masked"], data[b]["masked"]),
        })

    print("=" * 74)
    print("PAIRWISE BODY-COPY OVERLAP        RAW = as written   MASKED = city swapped out")
    print("=" * 74)
    print(f"  {'pair':<28}{'RAW':>10}{'MASKED':>10}")
    print("  " + "-" * 48)
    for r in sorted(rows, key=lambda r: -r["masked"]):
        flag = "  <-- FAIL" if r["masked"] >= 40 or r["raw"] >= 40 else ""
        print(f"  {r['a']+' / '+r['b']:<28}{r['raw']:>9.1f}%{r['masked']:>9.1f}%{flag}")
    print("  " + "-" * 48)
    print(f"  {'AVERAGE':<28}{sum(r['raw'] for r in rows)/len(rows):>9.1f}%"
          f"{sum(r['masked'] for r in rows)/len(rows):>9.1f}%")
    print(f"  {'WORST PAIR':<28}{max(r['raw'] for r in rows):>9.1f}%"
          f"{max(r['masked'] for r in rows):>9.1f}%")
    print()

    # ---- shared paragraphs
    seen = {}
    for p in names:
        for para in data[p]["paras"]:
            key = re.sub(r"\s+", " ", para.strip().lower())
            seen.setdefault(key, {"text": para, "pages": set()})["pages"].add(short[p])
    dupes = [v for v in seen.values() if len(v["pages"]) > 1]
    dupes.sort(key=lambda v: (-len(v["pages"]), -len(v["text"])))

    print("=" * 74)
    print(f"VERBATIM PARAGRAPHS ON >1 PAGE: {len(dupes)}")
    print("=" * 74)
    if not dupes:
        print("  none")
    for v in dupes[:show_n]:
        print(f"  [{len(v['pages'])} pages: {','.join(sorted(v['pages']))}]")
        print(f"    {v['text'][:150]}{'...' if len(v['text'])>150 else ''}")
    if len(dupes) > show_n:
        print(f"  ... and {len(dupes)-show_n} more (--show-dupes N)")
    print()

    if as_json:
        print(json.dumps({
            "words": {short[p]: data[p]["words"] for p in names},
            "pairs": rows,
            "verbatim_shared_paragraphs": len(dupes),
        }, indent=2))


if __name__ == "__main__":
    main()
