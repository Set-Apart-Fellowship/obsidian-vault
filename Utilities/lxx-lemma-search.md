<%*
const INDEX_PATH = "Utilities/data/lxx-lemma-index.json";

// Session cache — JSON is large; avoid re-parsing on every search
if (!window._lxxLemmaIndex) {
  new Notice("Loading LXX lemma index…");
  let raw;
  try {
    raw = await app.vault.adapter.read(INDEX_PATH);
  } catch(e) {
    new Notice("lxx-lemma-index.json not found. Run import_lxx_morph.py first.");
    return;
  }
  window._lxxLemmaIndex = JSON.parse(raw);
  new Notice("Lemma index loaded.");
}

const { forms, lemmas, books, glosses = {} } = window._lxxLemmaIndex;

function stripAccents(str) {
  return str.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function cleanToken(str) {
  // Match Python's clean_token: strip accents then non-word chars
  return stripAccents(str).replace(/[^\p{L}]/gu, "");
}

const IRREGULAR_FORMS = {
  "say":   ["say","said","saith","saidst","saying"],
  "speak": ["speak","spoke","spoken","spake","speaketh","speaking"],
  "go":    ["go","went","gone","goeth","going"],
  "come":  ["come","came","cometh","coming"],
  "see":   ["see","saw","seen","seeth","seeing"],
  "know":  ["know","knew","known","knoweth","knowing"],
  "give":  ["give","gave","given","giveth","giving"],
  "take":  ["take","took","taken","taketh","taking"],
  "be":    ["be","am","is","are","was","were","been","being"],
  "have":  ["have","had","has","hath","having"],
  "do":    ["do","did","done","doeth","doing"],
  "make":  ["make","made","maketh","making"],
  "sit":   ["sit","sat","sitting","sitteth"],
  "stand": ["stand","stood","standing","standeth"],
  "bring": ["bring","brought","bringeth","bringing"],
  "send":  ["send","sent","sendeth","sending"],
  "hear":  ["hear","heard","heareth","hearing"],
  "call":  ["call","called","calleth","calling"],
  "fall":  ["fall","fell","fallen","falleth","falling"],
  "arise": ["arise","arose","arisen","ariseth","arising"],
  "dwell": ["dwell","dwelt","dwelleth","dwelling"],
  "set":   ["set","setting"],
  "put":   ["put","putting"],
};

function buildGlossPattern(gloss) {
  const word = gloss.toLowerCase().split(/\s+/)[0].replace(/[^a-z]/g, "");
  if (IRREGULAR_FORMS[word]) {
    const alts = IRREGULAR_FORMS[word].join("|");
    return new RegExp(`\\b(${alts})\\b`, "gi");
  }
  const esc = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`\\b${esc}\\w*`, "gi");
}

function highlightGloss(text, gloss) {
  if (!gloss || !text) return text;
  return text.replace(buildGlossPattern(gloss), m => `==${m}==`);
}

function glossMatches(text, gloss) {
  if (!gloss || !text) return false;
  return buildGlossPattern(gloss).test(text);
}

function findBrentonWithGloss(bookNum, bookName, ch, vs, gloss) {
  const candidates = [vs, vs-1, vs+1, vs-2, vs+2, vs-3, vs+3, vs-4, vs+4].filter(v => v >= 1);
  for (const v of candidates) {
    const text = getBrenton(bookNum, bookName, ch, v);
    if (text && glossMatches(text, gloss)) return { text, actualVs: v, matched: true };
  }
  // ±4 failed — scan whole chapter for large versification offsets
  const num = String(bookNum).padStart(2, "0");
  const path = `${brentonRoot}/${num} - ${bookName}/${bookName} ${ch}.md`;
  const chContent = brentonCache[path] || "";
  const allVerses = [...chContent.matchAll(/^v(\d+) /mg)].map(m => parseInt(m[1]));
  for (const v of allVerses) {
    if (Math.abs(v - vs) <= 4) continue;
    const text = getBrenton(bookNum, bookName, ch, v);
    if (text && glossMatches(text, gloss)) return { text, actualVs: v, matched: true };
  }
  return { text: getBrenton(bookNum, bookName, ch, vs) || "", actualVs: vs, matched: false };
}


const query = await tp.system.prompt(
  "Search LXX lemma (any Greek form — e.g. εἶπεν finds all forms of the same lemma)"
);
if (!query || !query.trim()) return;

const input = query.trim();

// Resolve form → lemma; try cleaned token first, then accent-stripped only
let lemmaKey = forms[cleanToken(input)] ?? forms[stripAccents(input)];

// If still not found, try the input itself as a lemma key
if (!lemmaKey) {
  const stripped = stripAccents(input);
  if (lemmas[stripped]) lemmaKey = stripped;
}

if (!lemmaKey || !lemmas[lemmaKey]) {
  new Notice(`No lemma found for "${input}"`);
  return;
}

const occurrences = lemmas[lemmaKey];
new Notice(`${occurrences.length} occurrences of lemma "${lemmaKey}"…`);

// Sort: book → chapter → verse
occurrences.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);

const MAX    = 500;
const capped = occurrences.length > MAX;
const shown  = capped ? occurrences.slice(0, MAX) : occurrences;

const lxxRoot     = "Bible Versions/LXX";
const brentonRoot = "Bible Versions/BRENTON";
const brentonCache = {};

// Pre-load all needed Brenton chapters in parallel
const brentonPaths = [...new Set(shown.map(([b, c]) => {
  const num = String(b).padStart(2, "0");
  const bk  = books[b] || `Book${b}`;
  return `${brentonRoot}/${num} - ${bk}/${bk} ${c}.md`;
}))];

await Promise.all(brentonPaths.map(async path => {
  try { brentonCache[path] = await app.vault.adapter.read(path); }
  catch(e) { brentonCache[path] = ""; }
}));

function getBrenton(bookNum, bookName, ch, vs) {
  const num  = String(bookNum).padStart(2, "0");
  const path = `${brentonRoot}/${num} - ${bookName}/${bookName} ${ch}.md`;
  const m    = (brentonCache[path] || "").match(new RegExp(`^v${vs} (.+)$`, "m"));
  return m ? m[1] : "";
}

const gloss = glosses[lemmaKey] || "";

let block = `## LXX Lemma: "${lemmaKey}"${gloss ? ` — _${gloss}_` : ""}\n\n`;
block += `_${occurrences.length} occurrence${occurrences.length !== 1 ? "s" : ""}`;
if (capped) block += ` — showing first ${MAX}`;
block += `_\n\n---\n\n`;

for (const [bookNum, ch, vs, surface] of shown) {
  const bookName = books[bookNum] || `Book ${bookNum}`;
  const num      = String(bookNum).padStart(2, "0");
  const ref      = `[[${lxxRoot}/${num} - ${bookName}/${bookName} ${ch}|${bookName} ${ch}:${vs}]]`;
  const { text: brentonText, actualVs, matched } = findBrentonWithGloss(bookNum, bookName, ch, vs, gloss);
  block += `**${ref}**\n`;
  block += `GK: ${surface}${gloss ? ` (${gloss})` : ""}\n`;
  if (matched && brentonText) {
    const vsNote = actualVs !== vs ? ` _(v${actualVs})_` : "";
    block += `EN${vsNote}: ${highlightGloss(brentonText, gloss)}\n`;
  } else {
    block += `EN: _(no Brenton match)_\n`;
  }
  block += "\n";
}

block += "---\n";
tR += block;
%>
