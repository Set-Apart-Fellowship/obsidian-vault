# Set Apart Fellowship — Obsidian Vault

Biblical research tools for studying scripture on its own terms — comparing translations, reading original languages, and looking up verses without leaving your notes.

---

## What You Need First

Before anything else, you need two free things installed on your computer:

1. **Obsidian** — a note-taking app that stores everything as plain text files on your computer (nothing goes to a cloud you don't control). Download at [obsidian.md](https://obsidian.md).

2. **The Templater plugin** — a plugin for Obsidian that lets you run the lookup scripts in this vault. Instructions for installing it are in the Setup section below.

---

## Step 1 — Get This Vault onto Your Computer

You have two options:

**Option A — Download as a ZIP (easiest)**
1. Click the green **Code** button at the top of this GitHub page
2. Click **Download ZIP**
3. Unzip it somewhere on your computer (e.g. your Documents folder)

**Option B — Clone with Git (if you know what that means)**
```bash
git clone https://github.com/Set-Apart-Fellowship/obsidian-vault.git
```

---

## Step 2 — Open the Vault in Obsidian

1. Open Obsidian
2. On the startup screen, click **Open folder as vault**
3. Navigate to the folder you downloaded/unzipped and select it
4. Click **Open**

You should now see the vault files in the left sidebar.

---

## Step 3 — Install the Templater Plugin

Templater is what makes the scripts run. Without it, the scripts are just text files that do nothing.

1. In Obsidian, open **Settings** (gear icon, bottom-left)
2. Click **Community plugins** in the left menu
3. If it says "Safe mode is on," click **Turn on community plugins**
4. Click **Browse**
5. In the search box, type **Templater**
6. Click on **Templater** by SilentVoid13
7. Click **Install**, then click **Enable**
8. Close the plugin browser

---

## Step 4 — Point Templater at the Scripts Folder

Templater needs to know where the scripts live.

1. Go back to **Settings**
2. Click **Templater** in the left menu (it should now appear under "Community plugins")
3. Find the field labeled **Template folder location**
4. Type: `Utilities`
5. Close Settings

That's it. The scripts are now ready to use.

---

## Using the Scripts

### How to run any script

1. Open any note in Obsidian (or create a new one)
2. Place your cursor where you want the output to appear
3. Press **Cmd+P** (Mac) or **Ctrl+P** (Windows) to open the command palette
4. Type **Insert Template** and select **Templater: Insert Template**
5. Pick the script you want from the list
6. A small prompt box will appear — type your input and press Enter
7. The result appears in your note

---

### verse-lookup

Looks up a Bible verse (or range of verses) across every translation at once, plus the original Hebrew or Greek interlinear.

**How to use it:**

Run the script and type a reference into the prompt:

| What you type | What you get |
|---------------|-------------|
| `John 3:16` | All translations + interlinear table |
| `Genesis 1:1-3` | Verses 1–3 across all translations |
| `John 3:16 BSB` | BSB text only |
| `Genesis 1:1 KJV` | KJV text only |
| `John 1:1 INTERLINEAR` | Just the Greek interlinear table |

**Available translation codes:**

`BSB` `KJV` `YLT` `ASV` `DARBY` `WEYMOUTH` `INTERLINEAR`

> If a translation file is missing from your vault, it's silently skipped — no error, just not shown.

**What the interlinear looks like:**

Each word in the original Hebrew or Greek gets its own row showing the original text, how to pronounce it, what it means in English, its Strong's number, and its grammatical parsing.

---

### lxx-word-search

Searches the Greek Septuagint (the ancient Greek Old Testament) for any Greek word or root. Type a Greek word — accents are optional — and it returns every verse containing that string, with the Brenton English translation alongside.

**How to use it:**

Run the script and type any Greek word or partial word into the prompt. Example: `βδελυγμ` finds every occurrence of words built on that root.

---

### lxx-lemma-search

More powerful than word search — this finds every occurrence of a Greek word across all its different grammatical forms. For example, searching for any form of the verb "to say" (εἶπεν, εἶπον, λέγει, etc.) finds them all, because they all share the same underlying lemma.

**One-time setup required:** This script needs an index file to work. You only need to build it once:

1. Open your Terminal (Mac) or Command Prompt (Windows)
2. Navigate to your vault folder
3. Run: `python3 import_lxx_morph.py`

This takes a few minutes and creates a file at `Utilities/data/lxx-lemma-index.json`. After that, the script works instantly every time.

---

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

> **BASIC (Bible in Basic English)** is not included in this repo. It is public domain in the United States, but its copyright status outside the US is ambiguous due to GATT restoration and UK considerations. Users who want BBE can source it themselves and add it locally.

---

## Bible Versions Folder Structure

Each translation follows this pattern:

```
Bible Versions/
  {TRANSLATION}/
    {NN} - {Book Name}/
      {Book Name} {Chapter}.md
```

Example: `Bible Versions/BSB/01 - Genesis/Genesis 1.md`

Inside each chapter file, verses look like this:

```
v1 In the beginning God created the heavens and the earth.
v2 Now the earth was formless and empty...
```

Interlinear entries look like this (one token per line):

```
v1 בָּרָא|bā·rā|created|H1254|V-Qal-Perf-3ms
```

That's: `Original | Transliteration | English gloss | Strong's number | Grammatical parsing`

---

## License

[CC0 1.0 Universal](LICENSE) — dedicated to the public domain. Use it however you like.
