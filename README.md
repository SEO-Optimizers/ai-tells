# ai-tells

A Claude skill that stops Claude from writing like Claude, plus two standalone scripts
you can run on any text.

It catches the phrases and punctuation that make copy read as AI-written, and it checks
SEO title tags and meta descriptions against real character counts.

Python 3 standard library only. Nothing to install.

## Why

Language models are bad at two things this work depends on:

1. **Noticing their own habits.** Ask a model to avoid sounding like a model and it will
   agree, then write "navigating the complexities of the digital realm."
2. **Counting characters.** Ask a model whether a title is under 60 characters and it will
   guess, confidently, and be wrong often enough to matter.

Neither improves by asking more nicely. Both are jobs for code. That is all this is.

## Use it as a Claude skill

This is the point of the repo. Install it and Claude runs the checks on its own output
before handing you a draft, instead of promising it avoided the words and then using them.

```bash
git clone https://github.com/SEO-Optimizers/ai-tells.git
cp -r ai-tells ~/.claude/skills/          # every project
# or, for one project only:
cp -r ai-tells /path/to/project/.claude/skills/
```

Claude picks it up from the description in `SKILL.md` whenever a conversation involves
title tags, meta descriptions, or whether something reads as AI-written. `SKILL.md` also
carries the full title tag and meta description rules, so the model has the standard and
the checker in one place.

Works the same in Claude Code and the Claude apps.

## Or run it as a plain CLI

No Claude required. Python 3 ships with macOS and most Linux.

```bash
# Scan a draft for AI-writing tells
python3 scripts/check_rules.py --banned-file draft.md

# Real character counts. The brand after the last "|" is not counted.
python3 scripts/check_lengths.py "Emergency Plumber Marietta | Acme Plumbing"

# Meta descriptions, 160-char limit
python3 scripts/check_lengths.py --meta "Fast local repairs from licensed pros. Call today."

# Repeated words, brand leaks, forbidden characters, duplicates across a batch
python3 scripts/check_rules.py --title-file titles.txt
python3 scripts/check_rules.py --meta-file metas.txt --company "Acme Plumbing"
```

Both scripts exit 0 on pass and 1 on any failure, so they drop into a pre-commit hook or CI.

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

**This is a lint, not a verdict.** It catches habits. It does not claim to detect whether a
machine wrote something, because that claim cannot be made honestly: we scanned 218 of our
own posts going back to 2007 and 67% tripped a check, nearly all of it written by people.

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

## Want us to run it on your site?

We will scan your published pages and send back a report: every page ranked by
issues found, the specific phrases with counts, and your dash totals.

[Get a free AI writing check](https://seooptimizers.com/ai-writing-check/)

The scan is the same code in this repo, pointed at your sitemap instead of ours.

## Who made this

Built by [SEO Optimizers](https://seooptimizers.com), an SEO agency in Los Angeles. We wrote
these checks for our own work and use them on every page we ship.

The phrase list came out of scanning our own blog archive: 218 posts, 311,845 words, going
back to 2007. 67% of them tripped at least one check.

## License

MIT. Take it, change it, ship it.
