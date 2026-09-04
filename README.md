# seo-copy-check

A Claude skill (and two standalone scripts) for writing SEO title tags and meta descriptions,
and for catching the phrases and punctuation that make copy read as AI-written.

Python 3 standard library only. Nothing to install.

## Why

Language models are bad at two things this work depends on:

1. **Counting characters.** Ask a model whether a title is under 60 characters and it will
   guess, confidently, and be wrong often enough to matter.
2. **Noticing their own habits.** Ask a model to avoid sounding like a model and it will
   agree, then write "navigating the complexities of the digital realm."

Both are jobs for code. That is all this is.

## Quick start

```bash
git clone https://github.com/YOURNAME/seo-copy-check.git
cd seo-copy-check

# Real character counts. The brand after the last "|" is not counted.
python3 scripts/check_lengths.py "Emergency Plumber Marietta | Acme Plumbing"

# Meta descriptions, 160-char limit
python3 scripts/check_lengths.py --meta "Fast local repairs from licensed pros. Call today."

# Repeated words, brand leaks, forbidden characters, duplicates across a batch
python3 scripts/check_rules.py --title-file titles.txt
python3 scripts/check_rules.py --meta-file metas.txt --company "Acme Plumbing"

# Scan a draft for AI-writing tells
python3 scripts/check_rules.py --banned-file draft.md
```

Both scripts exit 0 on pass and 1 on any failure, so they work in a pre-commit hook or CI.

## The 60-character thing

Most character counters measure your whole title. That is the wrong number.

Titles are written as `Keywords | Company Name`, and Google usually strips the brand from the
visible SERP title. So the 60-character budget applies to the keyword portion only.
`check_lengths.py` splits on the last `|` and judges the left side, while still reporting the
full length for reference:

```
  [   ok]  39/60  Tarzana Plumber for Leak & Drain Repair | ABC Plumbing  (full incl. brand: 54)
  [ OVER]  68/60  We Are The Best Plumbers To Help You Get Your Pipes Fixed Fast Today | ABC Plumbing
```

Counting the whole string makes you cut real keywords to make room for your own brand name.

## The AI-tell linter

```
$ python3 scripts/check_rules.py --banned-file draft.md
Scanned 29 words for AI-tell phrases and dash punctuation:

  [FAIL] "navigating" x1 occurrence. Reword: it is an AI-tell phrase.
  [FAIL] "complexities" x1 occurrence. Reword: it is an AI-tell phrase.
  [FAIL] "bespoke" x1 occurrence. Reword: it is an AI-tell phrase.
  [FAIL] em-dash x1. Rewrite with a comma, period, colon, or parentheses.
```

The phrase list is at the top of `scripts/check_rules.py`. Edit it. It is a starting point,
not scripture.

Dash detection only counts the true em-dash (U+2014) and en-dash (U+2013) used as pause
punctuation. Hyphens in compound words like `same-day` and `family-owned` are never flagged.

**This is a lint, not a verdict.** It catches habits. It does not tell you whether the writing
is any good, and passing it does not make copy worth publishing.

## Use as a Claude skill

Drop the folder into your skills directory:

```bash
cp -r seo-copy-check ~/.claude/skills/          # available in every project
# or, for one project only:
cp -r seo-copy-check /path/to/project/.claude/skills/
```

Claude picks it up from the description in `SKILL.md` and runs the scripts instead of
estimating. `SKILL.md` also carries the full title tag and meta description rules.

## License

MIT. Take it, change it, ship it.
