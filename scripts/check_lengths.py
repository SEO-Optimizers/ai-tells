#!/usr/bin/env python3
"""Deterministic character-count check for SEO title tags (and meta descriptions).

Models are unreliable at counting characters, so after drafting title tags run
this to get the REAL counts instead of trusting the model's estimate.

Convention: title tags are written as "Keywords | Company Name". The
60-character limit applies to the KEYWORD PORTION only. The appended company
name does not count, because Google usually strips the brand from the visible
SERP title. This script reports both, but PASS/OVER is judged on the keyword
portion against the limit.

Usage:
    python3 check_lengths.py "Keywords Here | Company Name" "Another Title | Company"
    printf '%s\\n' "Title One | Brand" "Title Two | Brand" | python3 check_lengths.py
    python3 check_lengths.py --limit 60 "..."        # override limit (default 60)
    python3 check_lengths.py --meta "..."            # check meta descriptions (limit 160)

Exit code is 0 if every line passes, 1 if any line is OVER the limit.
"""
import sys

def split_brand(title):
    """Return (keyword_portion, brand) splitting on the LAST ' | '. Brand may be ''."""
    if " | " in title:
        kw, brand = title.rsplit(" | ", 1)
        return kw.strip(), brand.strip()
    return title.strip(), ""

def main(argv):
    limit = 60
    minimum = 0
    is_meta = False
    titles = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--limit":
            limit = int(argv[i + 1]); i += 2; continue
        if a == "--min":
            minimum = int(argv[i + 1]); i += 2; continue
        if a == "--meta":
            is_meta = True; limit = 160; i += 1; continue
        if a == "--gbp":
            # Google Business Profile descriptions: a 700-750 range, not just a ceiling.
            limit, minimum, is_meta = 750, 700, True; i += 1; continue
        titles.append(a); i += 1

    # allow piped input (one title per line)
    if not titles and not sys.stdin.isatty():
        titles = [ln.strip() for ln in sys.stdin if ln.strip()]

    if not titles:
        print(__doc__)
        return 0

    kind = "meta description" if is_meta else "title tag (keyword portion)"
    target = f"{minimum}-{limit}" if minimum else str(limit)
    print(f"Checking {len(titles)} {kind}(s) against a {target}-char target:\n")
    any_bad = False
    for t in titles:
        if is_meta:
            counted, brand = t.strip(), ""
        else:
            counted, brand = split_brand(t)
        n = len(counted)
        total = len(t.strip())
        over = n > limit
        under = n < minimum
        any_bad = any_bad or over or under
        flag = "OVER" if over else ("UNDER" if under else "ok")
        extra = f"  (full incl. brand: {total})" if brand else ""
        print(f"  [{flag:>5}] {n:>3}/{target}  {t}{extra}")
    print()
    if any_bad:
        print("Fix the OVER lines (shorten) and the UNDER lines (add content), then re-run.")
    else:
        print(f"All within the {target}-char target.")
    return 1 if any_bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
