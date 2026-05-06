# Set Apart Fellowship — Obsidian Vault

Biblical research tools for studying scripture on its own terms.

## What's Included

**Bible Versions/** — Public domain translations:

| Code | Translation |
|------|-------------|
| BSB | Berean Standard Bible (public domain, 2023) |
| KJV | King James Version |
| ASV | American Standard Version |
| YLT | Young's Literal Translation |
| DARBY | Darby Translation |
| WEYMOUTH | Weymouth New Testament (NT only) |
| LXX | Swete Greek Septuagint (1909–1930) |
| BRENTON | Brenton's English LXX (1851) |
| INTERLINEAR | Hebrew/Greek with transliteration, Strong's, and morphology |

> BASIC (Bible in Basic English) is not included — still under copyright. Source your own copy and drop it into `Bible Versions/BASIC/` following the folder structure below.

**Utilities/** — Templater scripts for verse lookup and LXX search.

## Requirements

- [Obsidian](https://obsidian.md)
- [Templater plugin](https://github.com/SilentVoid13/Templater) — set templates folder to `Utilities/`

## Utilities

### verse-lookup.md

Fetches a verse across all translations plus interlinear. Invoke via Templater Insert Template.

```
John 3:16              → all translations + interlinear
John 3:16 BSB          → BSB text only
Genesis 1:1-3 KJV      → KJV multi-verse
John 1:1 INTERLINEAR   → interlinear table only
```

Valid version codes: `BSB` `KJV` `YLT` `ASV` `DARBY` `BASIC` `WEYMOUTH` `INTERLINEAR`

Missing translations are silently skipped — a sparse vault works fine.

### lxx-word-search.md

Search LXX Greek text by word or root. Accent-insensitive. Returns matching verses with Brenton English translation.

### lxx-lemma-search.md

Search by lemma — finds all morphological forms of a Greek word. Requires the lemma index:

```bash
python3 import_lxx_morph.py
```

This generates `Utilities/data/lxx-lemma-index.json`.

## Bible Versions Folder Structure

```
Bible Versions/
  {TRANSLATION}/
    {NN} - {Book Name}/
      {Book Name} {Chapter}.md
```

Example: `Bible Versions/BSB/01 - Genesis/Genesis 1.md`

Verses are marked inline: `v1 In the beginning...`

Interlinear tokens are pipe-delimited: `v1 בָּרָא|bā·rā|created|H1254|V-Qal-Perf-3ms`

## License

[CC0 1.0 Universal](LICENSE) — dedicated to the public domain.
