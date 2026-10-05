#!/usr/bin/env python3
"""
Build LXX lemma index for the lxx-lemma-search Templater script.

Uses the eliranwong/LXX-Rahlfs-1935 repo (wordlist + lexemes + English
glosses) as a surface-form→lemma dictionary, then applies that dictionary
to the Swete word list (same source as import_lxx.py) combined with the
Swete versification to produce a lemma-occurrence index.

Output: Utilities/data/lxx-lemma-index.json

Usage (from the vault folder):
    python3 import_lxx_morph.py      (Windows: python import_lxx_morph.py)
"""

import bisect
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

VAULT       = Path(__file__).resolve().parent   # script lives at the vault root
OUT_PATH    = VAULT / "Utilities" / "data" / "lxx-lemma-index.json"
SWETE_BASE  = "https://raw.githubusercontent.com/eliranwong/LXX-Swete-1930/master"
RAHLFS_BASE = "https://raw.githubusercontent.com/eliranwong/LXX-Rahlfs-1935/master"

# Swete book code → (vault_num_int, vault_name) — mirrors import_lxx.py
BOOKS = {
    "Gen": (1,  "Genesis"),       "Exo": (2,  "Exodus"),
    "Lev": (3,  "Leviticus"),     "Num": (4,  "Numbers"),
    "Deu": (5,  "Deuteronomy"),   "Jos": (6,  "Joshua"),
    "Jdg": (7,  "Judges"),        "Rut": (8,  "Ruth"),
    "1Sa": (9,  "1 Samuel"),      "2Sa": (10, "2 Samuel"),
    "1Ki": (11, "1 Kings"),       "2Ki": (12, "2 Kings"),
    "1Ch": (13, "1 Chronicles"),  "2Ch": (14, "2 Chronicles"),
    "Ezr": (15, "Ezra"),          "Neh": (16, "Nehemiah"),
    "Est": (17, "Esther"),        "Job": (18, "Job"),
    "Psa": (19, "Psalms"),        "Pro": (20, "Proverbs"),
    "Ecc": (21, "Ecclesiastes"),  "Sol": (22, "Song of Solomon"),
    "Isa": (23, "Isaiah"),        "Jer": (24, "Jeremiah"),
    "Lam": (25, "Lamentations"),  "Eze": (26, "Ezekiel"),
    "Dan": (27, "Daniel"),        "Hos": (28, "Hosea"),
    "Joe": (29, "Joel"),          "Amo": (30, "Amos"),
    "Oba": (31, "Obadiah"),       "Jon": (32, "Jonah"),
    "Mic": (33, "Micah"),         "Nah": (34, "Nahum"),
    "Hab": (35, "Habakkuk"),      "Zep": (36, "Zephaniah"),
    "Hag": (37, "Haggai"),        "Zec": (38, "Zechariah"),
    "Mal": (39, "Malachi"),
}


def strip_accents(s):
    nfd = unicodedata.normalize("NFD", s)
    return re.sub(r"[̀-ͯ]", "", nfd).lower()


def clean_token(s):
    """Strip accents and punctuation — used as forms-map key."""
    return re.sub(r"[^\w]", "", strip_accents(s), flags=re.UNICODE)


def fetch(url, retries=3, label=""):
    headers = {"User-Agent": "Mozilla/5.0 (Bible vault importer/1.0)"}
    desc = label or url.split("/")[-1]
    print(f"Downloading {desc}... ", end="", flush=True)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            print("done")
            return data
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f"FAILED: {e}")
                raise RuntimeError(f"Cannot fetch {url}: {e}")


def build_rahlfs_lookup():
    """
    Build {normalized_surface: (normalized_lemma, gloss)} from Rahlfs data.

    Rahlfs wordlist, lexemes, and glosses all share the same OSSP word index,
    so we join on that index then key the result by normalized surface form.
    This dictionary is then used to lemmatize Swete words by surface-form match.
    """
    # ossp_id → accented surface form
    raw = fetch(f"{RAHLFS_BASE}/01_wordlist_unicode/text_accented.csv",
                label="Rahlfs wordlist").decode("utf-8")
    ossp_to_surface = {}
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            try:
                ossp_to_surface[int(parts[1])] = parts[2]
            except ValueError:
                pass

    # ossp_id → lemma
    raw = fetch(f"{RAHLFS_BASE}/02_lexemes/OSSP_lexemes.csv",
                label="Rahlfs lexemes").decode("utf-8")
    ossp_to_lemma = {}
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            try:
                ossp_to_lemma[int(parts[0])] = parts[1]
            except ValueError:
                pass

    # ossp_id → English gloss (HTML <br> → ", ")
    raw = fetch(f"{RAHLFS_BASE}/06_English_gloss/beta.csv",
                label="Rahlfs glosses").decode("utf-8")
    ossp_to_gloss = {}
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            try:
                gloss = re.sub(r"<br\s*/?>", ", ", parts[1], flags=re.IGNORECASE)
                gloss = re.sub(r"<[^>]+>", "", gloss).strip()
                ossp_to_gloss[int(parts[0])] = gloss
            except ValueError:
                pass

    # Join: normalized surface → (normalized lemma, gloss)
    lookup = {}
    for ossp_id, surface in ossp_to_surface.items():
        lemma = ossp_to_lemma.get(ossp_id)
        if not lemma:
            continue
        gloss       = ossp_to_gloss.get(ossp_id, "")
        norm_surface = strip_accents(surface)
        norm_lemma   = strip_accents(lemma)
        clean_surface = clean_token(surface)
        # Store both accent-stripped and punctuation-stripped keys
        for key in {norm_surface, clean_surface}:
            if key and key not in lookup:
                lookup[key] = (norm_lemma, gloss)

    return lookup


def build_versification_index():
    """Return (sorted_starts, entries) for binary-search verse lookup."""
    raw = fetch(f"{SWETE_BASE}/00-Swete_versification.csv",
                label="Swete versification").decode("utf-8")
    entries = []
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue
        m = re.match(r"(\w+)\.(\d+):(\d+)", parts[1])
        if not m or m.group(1) not in BOOKS:
            continue
        try:
            entries.append((
                int(parts[0]),
                BOOKS[m.group(1)][0],
                int(m.group(2)),
                int(m.group(3)),
            ))
        except ValueError:
            pass
    entries.sort(key=lambda x: x[0])
    starts = [e[0] for e in entries]
    return starts, entries


def lookup_verse(word_idx, starts, entries):
    pos = bisect.bisect_right(starts, word_idx) - 1
    if pos < 0:
        return None
    e = entries[pos]
    return e[1], e[2], e[3]


def build_swete_words():
    raw = fetch(f"{SWETE_BASE}/01-Swete_word_with_punctuations.csv",
                label="Swete word list").decode("utf-8")
    words = {}
    for line in raw.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            try:
                words[int(parts[0])] = parts[1]
            except ValueError:
                pass
    return words


def build_vault_token_set(vault):
    """
    Build set of (book_int, ch, vs, clean_token) from vault LXX files.
    Used to reject Swete word-list tokens whose verse attribution doesn't
    match the actual text on disk (e.g. appendix words stranded on last verse).
    """
    token_set = set()
    lxx_root = vault / "Bible Versions" / "LXX"
    for book_code, (book_int, book_name) in BOOKS.items():
        num = str(book_int).zfill(2)
        book_dir = lxx_root / f"{num} - {book_name}"
        if not book_dir.exists():
            continue
        for ch_file in book_dir.glob("*.md"):
            m = re.search(r"(\d+)\.md$", ch_file.name)
            if not m:
                continue
            ch = int(m.group(1))
            for line in ch_file.read_text(encoding="utf-8").splitlines():
                vm = re.match(r"^v(\d+)\s+(.*)", line)
                if not vm:
                    continue
                vs = int(vm.group(1))
                for word in vm.group(2).split():
                    ct = clean_token(word)
                    if ct:
                        token_set.add((book_int, ch, vs, ct))
    return token_set


def main():
    print("=== LXX Lemma Index Builder ===\n")
    print("Source: eliranwong/LXX-Rahlfs-1935 (lemmas + glosses)")
    print("Text:   eliranwong/LXX-Swete-1930 (versification + word list)\n")

    rahlfs_lookup = build_rahlfs_lookup()
    print(f"  Rahlfs lookup: {len(rahlfs_lookup):,} normalized surface forms\n")

    vers_starts, vers_entries = build_versification_index()
    idx_to_word = build_swete_words()

    print("Building vault token set for validation...", end=" ", flush=True)
    vault_tokens = build_vault_token_set(VAULT)
    print(f"done ({len(vault_tokens):,} tokens)")

    print(f"\nLemmatizing {len(idx_to_word):,} Swete tokens...", end=" ", flush=True)

    forms          = {}   # normalized surface → normalized lemma
    lemmas         = {}   # normalized lemma   → [[book_int, ch, vs, surface], ...]
    glosses_per_lem = {}  # normalized lemma   → English gloss
    unmatched      = 0
    invalid_ref    = 0

    for idx, surface in sorted(idx_to_word.items()):
        ref = lookup_verse(idx, vers_starts, vers_entries)
        if ref is None:
            continue
        book_int, ch, vs = ref

        norm_surface  = strip_accents(surface)
        clean_surface = clean_token(surface)

        # Reject tokens whose verse attribution doesn't match vault text
        if clean_surface and (book_int, ch, vs, clean_surface) not in vault_tokens:
            invalid_ref += 1
            continue

        if norm_surface in rahlfs_lookup:
            norm_lem, gloss = rahlfs_lookup[norm_surface]
        elif clean_surface in rahlfs_lookup:
            norm_lem, gloss = rahlfs_lookup[clean_surface]
        else:
            norm_lem = norm_surface or clean_surface  # surface = its own lemma fallback
            gloss    = ""
            unmatched += 1

        if clean_surface:
            forms[clean_surface] = norm_lem
        lemmas.setdefault(norm_lem, []).append([book_int, ch, vs, surface])
        if gloss and norm_lem not in glosses_per_lem:
            glosses_per_lem[norm_lem] = gloss

    print("done")

    total = len(idx_to_word)
    valid = total - invalid_ref
    pct   = 100 * (valid - unmatched) / valid if valid else 0
    print(f"  {invalid_ref:,} tokens rejected (verse attribution mismatch)")
    print(f"  {valid - unmatched:,}/{valid:,} valid tokens lemmatized ({pct:.1f}%)")
    print(f"  {len(forms):,} surface forms → {len(lemmas):,} lemmas")
    print(f"  {len(glosses_per_lem):,} lemmas with English glosses")

    # books list: index 0 unused; 1 = "Genesis" … 39 = "Malachi"
    book_names = [""] * 40
    for _, (num, name) in BOOKS.items():
        book_names[num] = name

    data = {
        "forms":   forms,
        "lemmas":  lemmas,
        "books":   book_names,
        "glosses": glosses_per_lem,
    }

    print(f"\nWriting {OUT_PATH}...", end=" ", flush=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"done ({OUT_PATH.stat().st_size / 1e6:.1f} MB)")
    print("\nDone. Run lxx-lemma-search in Obsidian Templater.")


if __name__ == "__main__":
    main()
