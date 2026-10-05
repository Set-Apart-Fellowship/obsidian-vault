<%*
const books = [
  "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
  "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra",
  "Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon",
  "Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos",
  "Obadiah","Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah",
  "Malachi","Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians",
  "2 Corinthians","Galatians","Ephesians","Philippians","Colossians","1 Thessalonians",
  "2 Thessalonians","1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James",
  "1 Peter","2 Peter","1 John","2 John","3 John","Jude","Revelation"
];

const ntBooks = new Set([
  "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
  "Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians",
  "1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter",
  "1 John","2 John","3 John","Jude","Revelation"
]);

const versions = [
  { name: "BSB",      folder: "BSB",      ntOnly: false },
  { name: "KJV",      folder: "KJV",      ntOnly: false },
  { name: "YLT",      folder: "YLT",      ntOnly: false },
  { name: "ASV",      folder: "ASV",      ntOnly: false },
  { name: "DARBY",    folder: "DARBY",    ntOnly: false },
  { name: "BASIC",    folder: "BASIC",    ntOnly: false },
  { name: "WEYMOUTH", folder: "WEYMOUTH", ntOnly: true  },
];

const bibleRoot = "Bible Versions";
const interlinearRoot = "Bible Versions/INTERLINEAR";

const bookAliases = {
  "gen":"Genesis","exo":"Exodus","exod":"Exodus","lev":"Leviticus","num":"Numbers",
  "deu":"Deuteronomy","deut":"Deuteronomy","jos":"Joshua","josh":"Joshua",
  "jdg":"Judges","judg":"Judges","rut":"Ruth","1sa":"1 Samuel","1sam":"1 Samuel",
  "2sa":"2 Samuel","2sam":"2 Samuel","1ki":"1 Kings","1kin":"1 Kings",
  "2ki":"2 Kings","2kin":"2 Kings","1ch":"1 Chronicles","1chr":"1 Chronicles",
  "2ch":"2 Chronicles","2chr":"2 Chronicles","ezr":"Ezra","neh":"Nehemiah",
  "est":"Esther","job":"Job","psa":"Psalms","psal":"Psalms","ps":"Psalms",
  "pro":"Proverbs","prov":"Proverbs","ecc":"Ecclesiastes","eccl":"Ecclesiastes",
  "sos":"Song of Solomon","song":"Song of Solomon","isa":"Isaiah","jer":"Jeremiah",
  "lam":"Lamentations","eze":"Ezekiel","ezek":"Ezekiel","dan":"Daniel",
  "hos":"Hosea","joe":"Joel","joel":"Joel","amo":"Amos","oba":"Obadiah",
  "jon":"Jonah","mic":"Micah","nah":"Nahum","hab":"Habakkuk","zep":"Zephaniah",
  "zeph":"Zephaniah","hag":"Haggai","zec":"Zechariah","zech":"Zechariah",
  "mal":"Malachi","mat":"Matthew","matt":"Matthew","mark":"Mark","mar":"Mark","mrk":"Mark",
  "luk":"Luke","joh":"John","jhn":"John","act":"Acts","rom":"Romans",
  "1co":"1 Corinthians","1cor":"1 Corinthians","2co":"2 Corinthians",
  "2cor":"2 Corinthians","gal":"Galatians","eph":"Ephesians","php":"Philippians",
  "phi":"Philippians","phil":"Philippians","col":"Colossians","1th":"1 Thessalonians",
  "1the":"1 Thessalonians","1thes":"1 Thessalonians","2th":"2 Thessalonians",
  "2the":"2 Thessalonians","2thes":"2 Thessalonians","1ti":"1 Timothy",
  "1tim":"1 Timothy","2ti":"2 Timothy","2tim":"2 Timothy","tit":"Titus",
  "phm":"Philemon","heb":"Hebrews","jam":"James","jas":"James","1pe":"1 Peter",
  "1pet":"1 Peter","2pe":"2 Peter","2pet":"2 Peter","1jo":"1 John","1joh":"1 John",
  "2jo":"2 John","2joh":"2 John","3jo":"3 John","3joh":"3 John","jud":"Jude",
  "rev":"Revelation"
};

const bookIndex = {};
books.forEach((b, i) => bookIndex[b] = String(i + 1).padStart(2, "0"));

const versionNames = new Set(versions.map(v => v.name));
versionNames.add("INTERLINEAR");

function parseRef(input) {
  const match = input.trim().match(/^(.+?)\s+(\d+):(\d+)(?:-(\d+))?\s*([A-Z]+)?$/);
  if (!match) return null;
  let book = match[1];
  const lookup = bookAliases[book.toLowerCase()];
  if (lookup) book = lookup;
  return {
    book,
    chapter:       parseInt(match[2]),
    verseStart:    parseInt(match[3]),
    verseEnd:      match[4] ? parseInt(match[4]) : parseInt(match[3]),
    versionFilter: match[5] || null
  };
}

function getVerses(content, verseStart, verseEnd) {
  const results = [];
  for (let v = verseStart; v <= verseEnd; v++) {
    const re = new RegExp(`^v${v} (.+)$`, "m");
    const match = content.match(re);
    if (match) results.push({ verse: v, text: match[1].trim() });
  }
  return results;
}

function getInterlinearWords(content, verseStart, verseEnd) {
  const results = [];
  const lines = content.split("\n");
  for (const line of lines) {
    const match = line.match(/^v(\d+) (.+)$/);
    if (!match) continue;
    const verse = parseInt(match[1]);
    if (verse < verseStart || verse > verseEnd) continue;
    const parts = match[2].split("|");
    if (parts.length < 5) continue;
    // Parsing can itself contain pipes (e.g. "Art | N-fs"), so anchor on
    // the Strong's field and keep everything after it as the parsing.
    let s = 3;
    while (s < parts.length - 1 && !/^[HG]\d/.test(parts[s].trim())) s++;
    results.push({
      verse,
      orig:     parts[0],
      translit: parts[1],
      english:  parts.slice(2, s).join("|"),
      strongs:  parts[s],
      parsing:  parts.slice(s + 1).join("|").trim()
    });
  }
  return results;
}

const input = await tp.system.prompt("Enter reference (e.g. John 3:16 or Genesis 1:1-3 — add version to filter: John 3:16 BSB)");
if (!input) return;

const ref = parseRef(input);
if (!ref) {
  new Notice("Could not parse reference. Use format: Book Chapter:Verse or Book Chapter:Verse-Verse");
  return;
}

const { book, chapter, verseStart, verseEnd, versionFilter } = ref;
const singleVersion = versionFilter && versionNames.has(versionFilter) ? versionFilter : null;

if (!bookIndex[book]) {
  new Notice(`Book "${book}" not found. Use full book name.`);
  return;
}

const num = bookIndex[book];
const isNT = ntBooks.has(book);
const chapterFile = `${book} ${chapter}`;
const folderPath = `${num} - ${book}`;

let heading = verseStart === verseEnd
  ? `**${book} ${chapter}:${verseStart}**`
  : `**${book} ${chapter}:${verseStart}-${verseEnd}**`;

let block = heading + "\n\n";

// Translation versions
for (const version of versions) {
  if (singleVersion === "INTERLINEAR") continue;
  if (singleVersion && version.name !== singleVersion) continue;
  if (version.ntOnly && !isNT) continue;

  const path = `${bibleRoot}/${version.folder}/${folderPath}/${chapterFile}.md`;

  let fileContent;
  try {
    fileContent = await app.vault.adapter.read(path);
  } catch(e) {
    continue;
  }

  const verses = getVerses(fileContent, verseStart, verseEnd);
  if (!verses.length) continue;

  let text;
  if (verseStart === verseEnd) {
    text = verses[0].text;
  } else {
    text = verses.map(v => `<sup>${v.verse}</sup>${v.text}`).join(" ");
  }

  const link = `[[${bibleRoot}/${version.folder}/${folderPath}/${chapterFile}|${version.name}]]`;
  block += `${link}: ${text}\n`;
}

// Interlinear
const interlinearPath = `${interlinearRoot}/${folderPath}/${chapterFile}.md`;
let interlinearContent;
try {
  interlinearContent = await app.vault.adapter.read(interlinearPath);
} catch(e) {
  interlinearContent = null;
}

const showInterlinear = !singleVersion || singleVersion === "INTERLINEAR";
if (showInterlinear && interlinearContent) {
  const words = getInterlinearWords(interlinearContent, verseStart, verseEnd);
  if (words.length) {
    const lang = isNT ? "Greek" : "Hebrew";
    block += `\n**Interlinear (${lang})**\n\n`;
    block += "| V | Original | Translit | English | Strongs | Parsing |\n";
    block += "|---|----------|----------|---------|---------|--------|\n";
    // Escape pipes so they don't split table cells
    const cell = s => s.replace(/\|/g, "\\|");
    for (const w of words) {
      const vnum = verseStart === verseEnd ? "" : w.verse;
      block += `| ${vnum} | ${cell(w.orig)} | ${cell(w.translit)} | ${cell(w.english)} | ${cell(w.strongs)} | ${cell(w.parsing)} |\n`;
    }
  }
}

block += "\n---\n";

tR += block;
%>