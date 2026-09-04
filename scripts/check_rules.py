#!/usr/bin/env python3
"""Deterministic copy checks for SEO title tags, meta descriptions, and body copy.

Companion to check_lengths.py. That script owns character counts; this one owns
the other rules a computer can verify exactly, so you run a check instead of
restating the rule in prose (which drifts) or asking a model to self-police.

What it checks
  Titles (--title):
    * FAIL  no leftover placeholder marker
    * WARN  a content word repeated in the keyword portion (the brand after the
            last ' | ' is exempt, since Google usually strips it from the SERP)
  Metas (--meta, needs --company for the company-name rule):
    * FAIL  no leftover placeholder marker
    * FAIL  the company name appears. Omit it: Google appends or strips the
            brand in SERPs, so spending characters on it wastes them
    * FAIL  no double quote (") or exclamation point (!)
    * WARN  the company's distinctive first word appears (possible brand leak)
  Batch (a file or piped input, one item per line):
    * FAIL  duplicates, because every page needs a unique title / description
  Body copy (--banned / --banned-file): scans a whole draft or page for the
  phrases that read as AI-written, plus dash punctuation.
    * FAIL  any banned phrase appears (reword it)
    * FAIL  any em-dash or en-dash appears. Rewrite with a comma, period,
            colon, or parentheses. Hyphens inside compound words are fine.

Usage
    python3 check_rules.py --title "Emergency Plumber Marietta | Acme Plumbing"
    python3 check_rules.py --meta "Fast local repairs. Call today." --company "Acme Plumbing"
    python3 check_rules.py --meta-file metas.txt --company "Acme Plumbing"   # + uniqueness
    python3 check_rules.py --title-file titles.txt                           # + uniqueness
    printf '%s\\n' "Title One | Brand" "Title Two | Brand" | python3 check_rules.py --title -
    python3 check_rules.py --banned-file draft.md          # scan a blog/page draft
    cat draft.md | python3 check_rules.py --banned         # or pipe it

Exit code is 0 if nothing FAILs (warnings do not fail), 1 if any FAIL is found.
"""
import re
import sys

PLACEHOLDER = "\U0001F7E8"  # the yellow-square placeholder marker, if you use one.
# It must never survive into published copy.

# tiny connector words that may legitimately repeat in a title phrase
CONNECTORS = {
    "and", "&", "for", "in", "the", "a", "an", "of", "to", "with",
    "your", "near", "me", "on", "at", "by", "or",
}

# Phrases that read as AI-written. Keep this list in one place and let every
# check inherit it, rather than restating it in prose that drifts. Add your own.
BANNED = [
    "meticulous", "navigating", "complexities", "realm", "bespoke", "tailored",
    "towards", "underpins", "ever-changing", "ever-evolving", "the world of",
    "not only", "seeking more than just", "designed to enhance", "it's not merely",
    "our suite", "it is advisable", "daunting", "in the heart of", "when it comes to",
    "in the realm of", "amongst", "unlock the secrets", "unveil the secrets", "robust",
]


def split_brand(title):
    """Return (keyword_portion, brand) splitting on the LAST ' | '. Brand may be ''."""
    if " | " in title:
        kw, brand = title.rsplit(" | ", 1)
        return kw.strip(), brand.strip()
    return title.strip(), ""


def check_title(t):
    """Return (fails, warns) lists of message strings for one title."""
    fails, warns = [], []
    if PLACEHOLDER in t:
        fails.append("contains a placeholder marker. Fill it before shipping.")
    kw, _brand = split_brand(t)
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9']+", kw)]
    seen = {}
    for w in words:
        if w in CONNECTORS:
            continue
        seen[w] = seen.get(w, 0) + 1
    repeats = [w for w, c in seen.items() if c > 1]
    if repeats:
        warns.append("repeated word(s) in the keyword portion: "
                     + ", ".join(sorted(repeats)) + " (brand is exempt)")
    return fails, warns


def check_meta(t, company):
    """Return (fails, warns) lists of message strings for one meta description."""
    fails, warns = [], []
    if PLACEHOLDER in t:
        fails.append("contains a placeholder marker. Fill it before shipping.")
    if '"' in t:
        fails.append('contains a double quote ("), which breaks the HTML attribute')
    if "!" in t:
        fails.append("contains an exclamation point (!), which does not belong in a meta description")
    if company:
        low = t.lower()
        if company.lower() in low:
            fails.append(f'contains the company name "{company}". Omit it from the meta.')
        else:
            first = re.findall(r"[A-Za-z0-9']+", company)
            if first and len(first[0]) >= 5 and re.search(rf"\b{re.escape(first[0])}\b", t, re.I):
                warns.append(f'contains "{first[0]}" (company\'s first word). Check it is not a brand leak.')
    return fails, warns


def check_banned(text):
    """Return [(phrase, count), ...] for every banned AI-tell phrase in the text."""
    low = text.lower()
    found = []
    for phrase in BANNED:
        pat = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
        n = len(re.findall(pat, low))
        if n:
            found.append((phrase, n))
    return found


def check_dashes(text):
    """Return (em_count, en_count) for em-dash (—) and en-dash (–) punctuation.

    Regular hyphens (-, U+002D) inside compound words are NOT counted. Only the
    true em-dash U+2014 and en-dash U+2013, used as a pause or punctuation
    device, which is one of the most recognizable AI-writing tells.
    """
    return text.count("—"), text.count("–")


def report_banned(text):
    words = len(re.findall(r"\S+", text))
    found = check_banned(text)
    em, en = check_dashes(text)
    print(f"Scanned {words} words for AI-tell phrases and dash punctuation:\n")
    if not found and not em and not en:
        print("  [ ok ] no banned AI-tell words found.")
        print("  [ ok ] no em-dashes / en-dashes found.")
        print("\nAll good.")
        return 0
    for phrase, n in sorted(found, key=lambda x: -x[1]):
        s = "" if n == 1 else "s"
        print(f'  [FAIL] "{phrase}" x{n} occurrence{s}. Reword: it is an AI-tell phrase.')
    if em:
        s = "" if em == 1 else "es"
        print(f"  [FAIL] em-dash x{em}. Rewrite with a comma, period, colon, or parentheses.")
    if en:
        s = "" if en == 1 else "es"
        print(f"  [FAIL] en-dash x{en}. Rewrite with a comma, period, colon, or parentheses.")
    total = len(found) + (1 if em else 0) + (1 if en else 0)
    print(f"\n{total} issue(s) found. Fix them, then re-run.")
    return 1


def report(kind, items, checker):
    print(f"Checking {len(items)} {kind}(s):\n")
    any_fail = False
    for t in items:
        fails, warns = checker(t)
        if fails:
            any_fail = True
            tag = "FAIL"
        elif warns:
            tag = "warn"
        else:
            tag = "ok"
        print(f"  [{tag:>4}] {t}")
        for m in fails:
            print(f"         ✗ {m}")
        for m in warns:
            print(f"         ! {m}")
    # uniqueness across the batch
    dupes = sorted({t for t in items if items.count(t) > 1})
    if dupes:
        any_fail = True
        print("\n  [FAIL] duplicate " + kind + "(s). Each page needs a unique one:")
        for d in dupes:
            print(f"         ✗ {d}")
    print()
    print("All good." if not any_fail else "Fix the FAIL lines, then re-run.")
    return 1 if any_fail else 0


def read_file(path):
    with open(path, encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def main(argv):
    mode = None            # "title" or "meta"
    company = ""
    items = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--company":
            company = argv[i + 1]; i += 2; continue
        if a in ("--title", "--meta"):
            mode = a[2:]
            # a following value that isn't a flag / isn't '-' is an inline item
            if i + 1 < len(argv) and argv[i + 1] not in ("-",) and not argv[i + 1].startswith("--"):
                items.append(argv[i + 1]); i += 2; continue
            i += 1; continue
        if a in ("--title-file", "--meta-file"):
            mode = a[2:-5]
            items.extend(read_file(argv[i + 1])); i += 2; continue
        if a == "--banned":
            mode = "banned"
            if i + 1 < len(argv) and argv[i + 1] not in ("-",) and not argv[i + 1].startswith("--"):
                items.append(argv[i + 1]); i += 2; continue
            i += 1; continue
        if a == "--banned-file":
            mode = "banned"
            with open(argv[i + 1], encoding="utf-8") as fh:
                items.append(fh.read())
            i += 2; continue
        items.append(a); i += 1

    if mode is None:
        print(__doc__); return 0

    # allow piped input (one item per line) when asked with '-' or no inline items
    if not items and not sys.stdin.isatty():
        items = [ln.strip() for ln in sys.stdin if ln.strip()]

    if not items:
        print(__doc__); return 0

    if mode == "banned":
        return report_banned("\n".join(items))
    if mode == "title":
        return report("title tag", items, check_title)
    return report("meta description", items, lambda t: check_meta(t, company))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
