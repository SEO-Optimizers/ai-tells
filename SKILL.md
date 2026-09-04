---
name: ai-tells
description: >
  Write and verify SEO title tags and meta descriptions, and catch AI-writing tells in body
  copy, using deterministic scripts instead of asking a model to count or self-police. Use when
  writing or auditing title tags and meta descriptions, when checking character counts, when
  checking a set of pages for duplicate titles or descriptions, or when scanning a draft for
  phrases and punctuation that read as AI-written. TRIGGER on "title tag", "meta description",
  "SEO title", "character count", "duplicate titles", "AI tells", "does this read like AI",
  "em-dash check", "AI writing detector", "sounds like ChatGPT".
---

# SEO copy check

Two deterministic scripts plus the rules they enforce. The point is that a model cannot
reliably count characters or notice its own habits, so those two jobs get handed to code.

Both scripts are Python 3 standard library only. No install, no dependencies.

## The tools

```bash
python3 scripts/check_lengths.py "Emergency Plumber Marietta | Acme Plumbing"
python3 scripts/check_lengths.py --meta "Your description here."
python3 scripts/check_rules.py --title-file titles.txt
python3 scripts/check_rules.py --banned-file draft.md
```

Both exit 0 on pass and 1 on failure, so they drop into a pre-publish check.

**Always run these before approving copy.** Never approve a character count you eyeballed,
and never trust a model's own claim about its length or its phrasing.

## Title tags

**Length: 60 characters on the keyword portion.** The appended company name does not count,
because Google usually strips the brand from the visible SERP title. `check_lengths.py`
splits on the last `|` and judges only the left side. This is the single most common thing
people get wrong: they count the whole string and needlessly cut real keywords.

**Format:** `Keywords | Company Name`

**Keywords plus small connectors only** (`for`, `&`, `to`). No benefit or ad-copy phrases.
"To help you get found" and "that grows your business" belong in the meta description, never
in the title.

**Front-load the focus keyword** where it reads naturally. Google truncates the visible title,
so the term that matters most should land early. It still has to read as a real phrase, not a
keyword list.

**No repeated words,** with the company name exempt. Distinct synonyms that are their own real
searches are encouraged (lawyer / attorney / law firm). `check_rules.py --title` warns on
repeats and skips the brand.

**Abbreviate where natural.** Use `&`, not "and". You are buying characters.

**Title Case.** No exclamation points, no ALL CAPS, no emojis, and no double quotes, since
quotes break the HTML attribute.

**Every page gets a unique title.** Run a batch through `--title-file` and the script fails on
duplicates.

**Exactly one `<title>` tag per page.** The browser tab shows only the one Google picked, so
it hides the problem. Search the page source for `<title` and confirm a single hit. A page can
pass every other check here and still show the wrong title for this one reason.

**Homepage:** your highest-value title. Lead with the primary service or keyword plus the
brand. Do not waste it on "Home" or a vague tagline.

**Large catalogs:** hand-write the homepage, top categories, and priority products. For the
long tail use a template filled from product data, varied enough that titles are not
boilerplate differing by one word.

## Meta descriptions

**Length: 160 characters.** Mobile truncates around 120, so the keyword and the main hook
belong in the first 120. The most expendable element goes last, so it is what gets cut.

**Read the live page first.** Pull the hook from the actual content. Do not invent details,
and do not copy the first sentence and append "Learn more."

**Lead with the benefit, not the keyword.** Front-loading means the keyword lands within the
first 120 characters, not that it is the first word. Open with a benefit, a pain point, or a
differentiator and let the keyword fall in naturally. Vary your openings across pages, and
never reuse a "[keyword] that..." skeleton.

**Omit the company name.** Google appends or strips the brand in SERPs, so spending characters
on it wastes them. `check_rules.py --meta --company "Name"` fails on this.

**Do not repeat the title tag.** The description complements it, it does not echo it.

**Voice:** third person for the descriptive part. Imperative calls to action are encouraged
("Call today", "Shop now", "Get a free quote"). Match the call to action to the page type.

**Local and service pages:** include the target city.

**No double quotes and no exclamation points.** Both are checked.

**Write complete sentences, and do not use dashes as connectors.** See below.

## AI-writing tells in body copy

```bash
python3 scripts/check_rules.py --banned-file draft.md
cat draft.md | python3 scripts/check_rules.py --banned
```

Two categories, both hard failures:

**Phrases.** A list of words and constructions that cluster heavily in machine-written copy:
delve-adjacent vocabulary like "meticulous", "navigating", "complexities", "realm", "bespoke",
"tailored", "robust", and stock scaffolding like "when it comes to", "in the heart of",
"unlock the secrets", "designed to enhance". The list lives at the top of `check_rules.py`.
Edit it to taste. None of these words are crimes on their own, but a draft carrying six of
them reads as generated to anyone who reads a lot of copy.

**Dash punctuation.** The em-dash and the en-dash used as a pause device are among the most
recognizable tells. Rewrite with a comma, a period, a colon, or parentheses. Hyphens inside
compound words (same-day, family-owned, 24-hour) are not counted and are always fine.

One caveat worth stating plainly: this is a lint, not a verdict. It catches habits, it does
not judge whether the writing is good. Passing it does not make copy worth publishing.

## Suggested workflow

1. Draft the title and description against the rules above.
2. `check_lengths.py` for real counts.
3. `check_rules.py` for repeats, brand leaks, forbidden characters, and duplicates across the batch.
4. `check_rules.py --banned-file` on any body copy going out with it.
5. Fix every FAIL. Warnings are judgment calls.
6. Publish, then load the live page with a cache-buster (`?v=1`) and confirm the rendered
   tag matches what you entered. Caches, plugins, and themes override these more often than
   you would expect.
