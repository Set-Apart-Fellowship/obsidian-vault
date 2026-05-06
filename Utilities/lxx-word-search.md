<%*
const query = await tp.system.prompt("Search LXX (Greek root, accents optional — e.g. βδελυγμ or βδέλυγμ)");
if (!query || !query.trim()) return;
const term = query.trim();

// Strip diacritics for accent-insensitive matching
function stripAccents(str) {
  return str.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}
const termStripped = stripAccents(term);

const lxxRoot     = "Bible Versions/LXX";
const brentonRoot = "Bible Versions/BRENTON";

const lxxFiles = app.vault.getFiles().filter(f =>
  f.path.startsWith(lxxRoot + "/") && f.path.endsWith(".md")
);

if (!lxxFiles.length) {
  new Notice("No LXX files found. Run import_lxx.py first.");
  return;
}

new Notice(`Searching ${lxxFiles.length} LXX chapters…`);

// Parse "01 - Genesis/Genesis 3.md" → { num, bookName, chapter }
function parseLxxPath(path) {
  const m = path.match(/\/(\d+) - ([^/]+)\/([^/]+) (\d+)\.md$/);
  if (!m) return null;
  return { num: m[1], bookName: m[2], chapter: parseInt(m[4]) };
}

const results = [];

// Process in parallel batches of 50
const BATCH = 50;
for (let i = 0; i < lxxFiles.length; i += BATCH) {
  const batch = lxxFiles.slice(i, i + BATCH);
  const batchData = await Promise.all(batch.map(f => app.vault.read(f)));

  for (let j = 0; j < batch.length; j++) {
    const file = batch[j];
    const info = parseLxxPath(file.path);
    if (!info) continue;

    const lines = batchData[j].split("\n");
    for (const line of lines) {
      const vm = line.match(/^v(\d+) (.+)$/);
      if (!vm || !stripAccents(vm[2]).includes(termStripped)) continue;
      results.push({
        num:      info.num,
        bookName: info.bookName,
        chapter:  info.chapter,
        verse:    parseInt(vm[1]),
        greek:    vm[2],
      });
    }
  }
}

if (!results.length) {
  new Notice(`No results for "${term}"`);
  return;
}

// Sort by book num → chapter → verse
results.sort((a, b) => {
  if (a.num !== b.num) return a.num.localeCompare(b.num);
  if (a.chapter !== b.chapter) return a.chapter - b.chapter;
  return a.verse - b.verse;
});

// Fetch matching Brenton verses
const brentonCache = {};
async function getBrenton(num, bookName, chapter, verse) {
  const path = `${brentonRoot}/${num} - ${bookName}/${bookName} ${chapter}.md`;
  if (!(path in brentonCache)) {
    try {
      brentonCache[path] = await app.vault.adapter.read(path);
    } catch(e) {
      brentonCache[path] = "";
    }
  }
  const m = brentonCache[path].match(new RegExp(`^v${verse} (.+)$`, "m"));
  return m ? m[1] : "";
}

let block = `## LXX: "${term}"\n\n`;
block += `_${results.length} result${results.length !== 1 ? "s" : ""}_\n\n`;
block += "---\n\n";

for (const r of results) {
  const brenton = await getBrenton(r.num, r.bookName, r.chapter, r.verse);
  const ref = `[[${lxxRoot}/${r.num} - ${r.bookName}/${r.bookName} ${r.chapter}|${r.bookName} ${r.chapter}:${r.verse}]]`;
  block += `**${ref}**\n`;
  block += `GK: ${r.greek}\n`;
  if (brenton) block += `EN: ${brenton}\n`;
  block += "\n";
}

block += "---\n";

tR += block;
%>
