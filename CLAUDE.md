# CLAUDE.md — Distributed Systems Deep Guide

Context for continuing work on **`index.html`**, a single-file
study guide for Google L6 / Staff Engineer system design prep.

This file is portable: keep it in the same folder as the HTML. All paths below are
relative to that folder unless stated otherwise.

**Companion files in this folder:**
- `index.html` — the artifact (renamed from Distributed_Systems_Deep_Guide.html for Vercel)
- `questions-google.html` — **one question-bank page per company.** See §2b before adding another.
- `Distributed_Systems_Deep_Guide.backup.html` — pre-enrichment original
- `DDIA_REFERENCE.md` — source-book structural index + synthesis notes
- `Designing Data Intensive Applications by Martin Kleppmann.pdf` — the source book

---

## 1. Who this is for, and how to behave

The reader is preparing for a **Google L6 / Staff Software Engineer** system design
interview.

**Act as a tutor, not an interviewer.** This is an explicit, repeated instruction:

- Explain clearly, build intuition, connect concepts across chapters.
- Do **not** simulate a Google interviewer, run mock interviews, or score answers.
- "Q&A" means *teaching* questions **with the answers supplied** — never questions posed
  back at the reader to test them.
- Content should aim at: *after reading this, I can reason about it in a real design
  discussion* — not *I have memorised a definition*.

The reader is an experienced backend engineer. Skip programming basics. Explain
distributed systems concepts from first principles.

---

## 2. What the artifact is

| | |
|---|---|
| **File** | `index.html` — single self-contained file, ~1.5 MB |
| **Backup** | `Distributed_Systems_Deep_Guide.backup.html` — the original before any enrichment |
| **Content** | ~102,300 words |
| **Deps** | None. One Google Fonts `@import`. No JS libraries. Opens offline from `file://` |
| **Structure** | 1 `<style>` block, 5 `<script>` blocks (early state-restore in `<body>`, glossary data, glossary engine, search palette, left-nav engine, view-size engine) |

### Document layout (in DOM order)

```
.top-nav                     sticky nav — brand + 4 links + badge
.cover                       title page
#master-toc                  full table of contents
#part1-theory                Part 1 banner
  #ch1 … #ch15               15 chapters (div.chapter + div.content pairs)
#part2-designs               Part 2 banner
  #design-url, #design-twitter, #design-kv, #design-whatsapp, #design-youtube,
  #design-jobs, #design-kafka, #design-drive, #design-uber, #design-crawler,
  #design-metrics, #design-cache, #design-typeahead, #design-rag   ← D11–D14, the infra round
  #design-ml-inference, #design-ml-platform, #design-maps, #design-fleet-upgrade,
  #design-booking, #design-collab, #design-denylist, #design-sort,
  #design-social-graph                                             ← D15–D23, the question-bank gaps
#part3-toolkit               Part 3 banner
  #toolkit-framework, #toolkit-numbers, #toolkit-tradeoffs, #toolkit-behavioral
#part3-mentalmodel
  #toolkit-mentalmodel       "T5" — DDIA mental model + pattern cheat sheet + 20 mistakes
#part3-questionbank
  #toolkit-questionbank      "T6" — what Google actually asks + the L4/L5/L6 rubric ladder
#part3-video
  #toolkit-video             "T7" — video/lecture references, channels ranked, gaps named
#part4-glossary              Part 4 banner
  #glossary-index            searchable 199-term glossary index
<script> GLOSSARY data </script>
<script> glossary engine </script>
#cp-wrap                     search palette (Cmd/Ctrl-F, Cmd/Ctrl-K, /)
#side-nav + #side-backdrop   left navigation: docked >=1200px, drawer below
#vs-ctl                      floating view-size control (fixed, bottom-right)
<script> view-size engine </script>
.footer
```

### The canonical 9-step design template

**Every design in Part 2 runs steps 1&ndash;9 in order. Verify with the audit snippet below
after touching any of them** &mdash; two designs had steps out of order and five were missing
steps entirely before this was enforced.

| # | Class | Header | Notes |
|---|---|---|---|
| 1 | `req` | Requirements | Opens with a `.clarify` block, then Functional / Non-Functional |
| 2 | `est` | Capacity Estimation | Opens with an `.assume` block, then `.ng` number cells |
| 3 | `api` | API Design | `.api-code` |
| 4 | `schema` | Schema Design | `.schema-code` |
| 5 | `arch` | High-Level Architecture | `.dc-diagram` SVG or a `.flow` |
| 6 | `deep` | Component Deep Dives | |
| 7 | `tradeoff` | Trade-off Analysis | `table.to` with `td.chosen` / `td.rej` |
| 8 | `fault` | Fault Tolerance | `.ft-row` > `.ft-fail` + `.ft-fix` |
| 9 | `concl` | Conclusion | `.concl-grid` &mdash; four cards, see the vocabulary table |

```python
st = "".join(x[1] for x in re.findall(r'class="ds-header">\[(\w+)\] (\d)\.', design_html))
assert st == "123456789"
```

### The 15 chapters

| id | Title | Enriched? |
|---|---|---|
| `ch1` | Why Are Distributed Systems Hard? | ✅ |
| `ch2` | Consistency Models | ✅ |
| `ch3` | CAP & PACELC | ✅ |
| `ch4` | Replication | ✅ |
| `ch5` | Partitioning (Sharding) | ✅ |
| `ch6` | Consensus | ✅ |
| `ch7` | Distributed Transactions | ✅ |
| `ch8` | Distributed Time & Clocks | ✅ |
| `ch9` | Caching | ✅ |
| `ch10` | Load Balancing & Rate Limiting | ✅ |
| `ch11` | Message Queues & Streaming | ✅ |
| `ch12` | Database Internals (+ data models, OLAP) | ✅ |
| `ch13` | Microservices & Resilience | ✅ |
| `ch14` | Observability & SRE | ✅ |
| `ch15` | Security & API Design (+ encoding/evolution) | ✅ |

---

## 2b. The question-bank pages — one file per company

`questions-google.html` is a standalone, self-contained page holding **78 Google-tagged**
system design questions. It is deliberately *not* part of `index.html`: the guide teaches
concepts, the bank lists questions, and mixing them made T6 unreadable.

**To add a company, copy the file — do not add a company filter.** The pattern is one page
per company (`questions-meta.html`, `questions-amazon.html`, …). Each page:

1. Holds its questions in a single `var Q = [...]` array at the bottom. Fields:
   `q` (text), `mo` (months ago, for sorting), `age` (display label), `ans` (answer count or
   `null`), `kind` (`eng` | `pm` | `fermi`), `cl` (topic cluster), `ref` (anchor in
   `index.html`, or `null` for a gap), `lab` (badge shown on the cross-link).
2. Carries a **company strip** (`.cos`) at the top. Adding a company means adding one
   `<a class="co-tab">` to that strip **on every existing page** — that is the only
   cross-file edit, and it is why the strip is markup rather than generated.
3. Defaults the Type facet to `eng`. This matters: the upstream bank filters by "system
   design" across *every* role, so 18 of the Google 78 are product-manager questions
   ("Design the US flag", "How would you price the Amazon Kindle?") and 5 are Fermi
   estimation. Only **55 are engineering questions**. Do not present the raw list unfiltered.
4. **Every engineering question maps to a section.** D15-D23 were written specifically to
   close the gaps this page exposed, so `kind: "eng"` with `ref: null` should now be empty.
   If a new company page adds uncovered questions, that is the backlog.
5. Sorts by recency, never by popularity — answer counts grow with age, so a popularity
   sort just surfaces the oldest questions.

**Every `ref` must be a real id in `index.html`.** Nothing checks this automatically; the
guide's broken-anchor sweep only looks at `href^="#"` within itself. Verify with:

```python
ids = set(re.findall(r'id="([\w-]+)"', open('index.html').read()))
# assert every ref in the Q array is in ids
```

`index.html` links to the bank from six places: the cover CTA, the master TOC, the sidebar,
and three points inside T6. T6 keeps only the *analysis* — the two-round finding, the
clusters, the rubric ladder — and hands the list itself to the page.

## 3. Source material

**Primary source:** Martin Kleppmann, *Designing Data-Intensive Applications* (1st ed, 613pp).
The PDF now sits in this folder.

**➜ Read `DDIA_REFERENCE.md` first.** It has a 507-entry structural index (every section
heading with its line number in the text extraction) plus per-chapter synthesis notes
marking what has already been used and what has not. It contains no reproduced book
text — regenerate `ddia.txt` from the PDF to make the line numbers usable.

**Rule: paraphrase and explain. Never reproduce copyrighted passages.** DDIA supplies the
rigor and the failure cases; the prose, diagrams, examples and exercises are original.

To work with it efficiently — do **not** read it as PDF images:

```bash
pdftotext -layout "Designing Data Intensive Applications by Martin Kleppmann.pdf" ddia.txt
grep -n "^\s*CHAPTER [0-9]" ddia.txt                # chapter line offsets
grep -nE "^[A-Z][A-Za-z0-9 ,'-/()]{4,60}$" ddia.txt # section headings
```

Chapter line offsets in the 1st edition extraction (verify if re-extracting):
`ch1:606  ch2:1502  ch3:3168  ch4:4678  ch5:6059  ch6:7873  ch7:8646  ch8:10679  ch9:12580  ch10:15221`

**DDIA → this guide mapping** (already applied for the ✅ chapters):

| DDIA | Goes into |
|---|---|
| Ch 1 Reliable/Scalable/Maintainable | `ch1` (faults) + `ch14` (percentiles, load params) |
| Ch 2 Data Models | `ch12` (folded in *front* of storage engines) |
| Ch 3 Storage & Retrieval | `ch12` |
| Ch 4 Encoding & Evolution | `ch15` |
| Ch 5 Replication | `ch4` |
| Ch 6 Partitioning | `ch5` |
| Ch 7 Transactions | `ch7` (isolation foundation goes *before* the 2PC content) |
| Ch 8 Trouble with Distributed Systems | `ch1` + `ch8` |
| Ch 9 Consistency & Consensus | `ch2` + `ch3` + `ch6` |

**Structural decision — do not renumber chapters.** The glossary's `ch` field and the TOC
both depend on `ch1..ch15`. DDIA topics with no natural home were folded into the closest
existing chapter rather than inserted as new ones.

---

## 4. The glossary system (data-driven — do not hand-edit prose)

199 terms. **Inline links are generated at page load, not written into the HTML.**
To add or change a term, edit the `GLOSSARY` object in the **first** `<script>` block only.

```js
"fencing-token": {
  t:   "Fencing Token",              // display title
  cat: "Consensus",                  // category — drives the filter chips
  ch:  "ch6",                        // chapter anchor for the "jump to chapter" chip
  aka: ["fencing","epoch number"],   // extra match patterns for auto-linking
  cs:  true,                         // OPTIONAL: case-sensitive match (acronyms: CAP, NTP, REST)
  one: "…",                          // one-sentence definition (shown as the hero line)
  why: "…",                          // the problem it solves
  how: ["…","…"],                    // mechanics bullets; supports **bold** and `code`
  analogy: "…",
  ex:  "…",                          // concrete worked example
  gotcha: "…",                       // where it bites in production
  ask: "…",                          // what an L6 interviewer probes
  rel: ["lease","split-brain"]       // related slugs; unknown slugs are filtered at render
}
```

Every field except `t` and `one` is optional — the renderer skips empties.

**How the auto-linker works** (second `<script>` block):
builds one alternation regex from all `t` + `aka` values sorted longest-first, walks text
nodes, wraps matches in `<span class="gt" data-gl="slug">`. Clicking opens a slide-in panel.

- **`MAX_PER_ZONE = 2`** — at most 2 links per term per zone. Zones are `.design-card`,
  `.toolkit-card`, then `div.content` / `div.chapter`. Keeps links from becoming noise.
- **`SKIP_CLASS`** excludes: `codeblock, schema-code, api-code, flow, top-nav, cover,
  toc-section, gl-, gt, nav-, toc-card, toc-badge, ch-num, part-tag, ng-val, dc-meta`
- Also skips tags: `SCRIPT STYLE CODE PRE A BUTTON INPUT TEXTAREA SVG`

**Nice property:** any new prose you add gets glossary links automatically on next load.

---

## 4a. Navigation and search

**Left sidebar (`#side-nav`).** Docked at `>=1200px` (adds `padding-left: 272px` to
`body`, which is safe because `* { box-sizing: border-box }`), an overlay drawer with a
backdrop below that. State lives on `<html>` as `.nav-open`, set **before first paint** by
the early inline script; it only auto-opens on a wide screen, never as a drawer on a phone.
Desktop preference persists in `dsg.nav`.

- **The 37 links are generated from `#master-toc`**, not hand-written, so the sidebar cannot
  drift out of sync. If you add a section, add it to the TOC and regenerate.
- Toggling the dock changes the content box, so it fires a synthetic `resize` to make the
  Fit engine remeasure.
- Scroll-spy is a rAF-throttled scroll listener picking the last section above a 70px line.
  Design ids sit on a `<span>` inside the heading, so it resolves to `.closest('.design-card')`
  for a usable box.
- `html { scroll-padding-top: 66px }` stops anchor jumps landing under the sticky nav —
  this fixes every anchor in the document, not just the sidebar's.

**Search palette (`#cp-wrap`).** Opens on **Cmd/Ctrl-F**, Cmd/Ctrl-K, `/`, or the nav
magnifier. Searches **both** corpora: the 37 sections and all 199 glossary terms (it reads
the global `var GLOSSARY` and opens results through `window.openGlossary(slug)`). An empty
query lists everything, sections first.

- **Cmd-F pressed again while the palette is open closes it and does not `preventDefault`,
  so the browser's own find-in-page opens.** Native find is never taken away — important in
  a 71k-word document. The footer says so.
- Ranking is substring + word-start bonus, then a retry against a lightly stemmed haystack
  (`(ing|ed|es|s|e)$` stripped) so "cache" finds "Caching" and "quorums" finds "Quorum".
  **A subsequence fallback was tried and removed** — it made `raft` return Failover,
  Checksum and Heartbeat. Predictable beats clever on a corpus of short titles.
- Every query token must match, and each group header renders once.

## 4b. The view-size system (`--fscale` + Fit)

Two independent controls in `#vs-ctl`, both persisted in `localStorage`
(`dsg.fscale`, `dsg.fit`) inside try/catch, since storage throws in private mode.

**1. Reading size — `--fscale`.** Every `font-size` in the stylesheet was rewritten to
`calc(Npx * var(--fscale, 1))` — 125 declarations, plus the 7 inline `style="font-size:"`
in the body. Steps are `[0.85, 1, 1.15, 1.30, 1.45]`, default `1`.

- **If you add a rule with a raw `font-size: Npx`, it will not scale.** Write
  `calc(Npx * var(--fscale, 1))`.
- **Deliberately excluded:** `.nav-brand`, `.nav-links a`, `.nav-badge` (scaling them
  re-wraps the 50px sticky nav that section 6 rule 6 warns about) and `#vs-ctl` itself.
- A tiny inline script immediately after `<body>` restores the saved scale **before first
  paint**, otherwise a 130% reader gets a flash of 100%.

**2. Fit.** Shrinks `.flow, .codeblock, .schema-code, .api-code` to the largest font at
which the widest line fits, by setting an inline `font-size`. Default **ON**.

- It never grows past the stylesheet size — it is *max font **to fit***, not "fill".
- Monospace scales linearly, so one measure pass suffices:
  `f = base × (availText / neededText) × 0.995`, computed on the **text** box
  (`clientWidth − padding`), because padding does not scale with the font.
- Runs in three phases — clear all, measure all, write all — so there is one layout pass
  rather than 68 read/write ping-pongs.
- **`MIN_PX = 9`, and below it Fit gives up entirely rather than clamping.** Clamping
  produced smaller text *and* a scrollbar, which is strictly worse than leaving it alone.
  This is what happens to the wide ASCII diagrams on a phone: they need ~6.5px at 390px, so
  they keep their 12px and keep scrolling. Fit still helps the blocks it can (`.api-code`
  overflow goes 4 → 1 at 390px).
- Recomputed on resize (150ms debounce) and on `document.fonts.ready` — JetBrains Mono
  loads async and changes the metrics the first pass measured.

Effect of the default: **desktop diagram scrolling goes from 9 of 45 to 0.**

## 5. Component vocabulary

Reuse these. Do not invent new block types without a reason.

### Original blocks (present before enrichment)
`.analogy` · `.insight` · `.warning` · `.deep` · `.scenario` · `.google-bar` ·
`.qa-section` (interview Q&A) · `.compare` > `.compare-card` · `.summary-box` ·
`.steps` · `.diagram` (SVG) · `table.to` (with `td.chosen` / `td.rej`) · `.ng` > `.ng-cell`

### Teaching blocks (added for the DDIA enrichment)

| Class | Purpose | Inner structure |
|---|---|---|
| `.flow` | Dark monospace ASCII diagram | `.fl-hi` green/good · `.fl-bad` red/failure · `.fl-key` orange/emphasis · `.fl-dim` grey annotation · `.fl-note` blue italic. Follow with `.flow-cap` caption |
| `.exercise` | Mini exercise | `.label`, `.ex-q`, then `<details><summary>Show the worked answer</summary><div class="ex-a">` |
| `.misconception` | "Many engineers assume X" | `.label`, `.mc-wrong` (the false belief, gets a ✗), `.mc-right` (the correction) |
| `.teach-qa` | Teaching Q&A (≠ `.qa-section`) | `h3`, `.tq-sub`, then `.tq` > `.tq-q` + `.tq-a` |
| `.usecase` | System-archetype table | `.label`, then `.uc-row` > `.uc-sys` + `.uc-why` |
| `.takeaway` | Green chapter closer | `.label`, `<p>`, `<ul>` |
| `.recall` | "Before this chapter, remember X" | `.rc-icon` + a `<div>` |
| `.srcref` | Small inline chapter chip | `<span class="srcref">Ch 4, 12</span>` |
| `.quickref` | Scannable decision table at the **top** of a chapter, for a reader who already knows the material and just needs the answer | `.label`, `.qr-sub`, then a 4-column table: *If you need… / Reach for / Because / **Used in***. The last column carries real systems (`Envoy`, `resilience4j`, Kafka) and `<span class="srcref">` links to designs. Wrap the table in `.tw`. Collapses to stacked cards under 680px |
| `.buildup` | Progressive derivation — build the naive design, break it, fix it, repeat | `.label`, then `.bu-step` > `.bu-n` + `.bu-body` containing `.bu-try` (the attempt), `.bu-break` (the exact failure, red), `.bu-learn` (what it teaches, green); closing `.bu-end`. **The best device in the toolkit for genuinely hard topics** — the reader arrives at the real answer having felt why every simpler answer fails |
| `.assume` | Stated assumptions **with the consequence of each being wrong**, inside step 2 | `.label`, then `.as-row` > `.as-a` (the assumption) + `.as-b` (what breaks). A bare list of numbers is not an assumptions section |
| `.concl-grid` | Step 9 closing summary | Four `.cc` cards: dominant constraint, what I would build first (`.cc.first`), what I deliberately did not build, biggest risk (`.cc.risk`) |
| `.clarify` | The clarifying questions to ask in the first five minutes, one per design, inside step 1 | `.label`, then `.cq-row` > `.cq-q` (the question) + `.cq-w` (**what the answer changes** — not what the answer is), closing `.cq-note`. The rationale column is the point: a list of questions without consequences teaches nothing |
| `.vidref` | Video/lecture references, red left border | `.label`, then `<ul><li>` with `<a target="_blank" rel="noopener">` + `.vr-meta` runtime span + one sentence on *why that video*. Optional closing `.vr-none` for "no good video exists, read this instead" |

### Chapter section shape that works

```
.recall              — dependency reminder, links back to earlier chapters
h3 / h4 + prose      — the mechanism
.flow + .flow-cap    — diagram of the mechanism or its failure
.misconception       — the belief this corrects
.exercise            — apply it, with a revealed worked answer
.teach-qa            — 4–7 understanding-check questions with answers
.usecase             — which real systems make which choice
.takeaway            — 4–6 bullets + a sentence handing off to the next chapter
```

---

## 6. Editing workflow — read this before touching the file

**The file is ~960 KB. Never rewrite it wholesale.** Use surgical anchored insertion:

```python
python3 - <<'PYEOF'
import io
p = "index.html"
h = io.open(p, encoding="utf-8").read()

ANCHOR = "<some exact unique existing string>"
assert h.count(ANCHOR) == 1, "anchor not unique"   # ALWAYS assert
h = h.replace(ANCHOR, ANCHOR + NEW_HTML, 1)

io.open(p, "w", encoding="utf-8").write(h)
PYEOF
```

Rules that came from actually getting these wrong:

1. **Always `assert h.count(ANCHOR) == 1`** before replacing. Silent no-match wastes a cycle.
2. **Beware entity mismatch when picking anchors.** The file mixes `&` and `&amp;`, and
   raw `—` alongside `&mdash;`. Grep the real bytes first rather than typing the anchor
   from what the rendered page shows.
3. **`.flow` blocks use `white-space: pre`.** Pad ASCII boxes **programmatically** —
   hand-counted spacing comes out ragged. Build lines with `.ljust(width)` and print the
   lengths to verify they match before inserting.
4. Avoid box-drawing characters (`╔═╗║`) in `.flow` — they render at a different width
   than text in JetBrains Mono and the right border goes ragged. Plain ASCII (`#`, `|`,
   `+`) is safe. `│ ┌ ┐ ▼ ─` are acceptable and used in places.
5. **Do not remove `flow` from `SKIP_CLASS`.** The glossary's `°` marker adds characters
   and destroys monospace alignment inside diagrams.
6. **Keep the nav to one line — it is now full.** `.nav-inner` holds a hamburger, a search
   button, the brand, 4 links and a badge. Adding the two buttons wrapped it to 91px on
   desktop until the link labels were shortened to `.nl-abbr` at every width (they were the
   long "Part 1: 15 Theory Chapters" form). At `<=680px` the links are hidden entirely and
   the brand drops to "L6 Guide" — two buttons plus four links overflowed a 320px nav.
   **There is no room left: anything new goes in the sidebar, not the nav.**

---

## 7. Verifying — do not ship on assumption

A `browser-automation` skill is available and was used throughout. Typical check:

```bash
node ~/.claude/skills/browser-automation/browser.mjs \
  "file:///ABSOLUTE/PATH/index.html" \
  --eval "({ gt: document.querySelectorAll('.gt').length,
             gtInFlow: document.querySelectorAll('.flow .gt').length,
             broken: [...document.querySelectorAll('a[href^=\"#\"]')]
               .map(a=>a.getAttribute('href').slice(1))
               .filter(id=>id && !document.getElementById(id)) })"
```

Note: the harness's `page.evaluate` runs in an **isolated world** — DOM is shared but page
globals are not. `window.GLOSSARY` and `window.openGlossary` will read as `undefined` even
though they exist. Drive the page by clicking real elements, not by calling its functions.

**Baseline to regress against** (current, after the Google-question-bank work):

```
totalWords 102280 · designs 23 (207 steps, all 1-9) · toolkitCards 7
quickref 10 · buildup 3 · all 15 chapters enriched
clarify 23 · assume 23 · concl 23 · tradeoff 23 · glossaryTerms 199 · designSteps 105 · flows 45
vidrefs 22 · externalLinks 63 (all target=_blank rel=noopener, all verified 200)
flowsScrollingOnDesktop 0 (was 9; Fit is on by default) · gtInCtl 0
questions-google.html: 78 questions · 55 eng · 60 cross-linked · 0 engineering gaps
at 145% scale: 0 overflowing elements at 1440/430/390/360/320, navHeight unchanged
exercises 14 · teachingQs 61 · misconceptions 21 · takeaways 14 · usecaseTables 8
recalls 7 · glossaryTerms 199 · inlineLinks 1178 · tables 42 (all wrapped in .tw)
gtInFlow 0 · gtInCodeOrLink 0 · brokenAnchors [] · navHeight 59 · consoleErrors 0
tablesScrollingOnDesktop 0 · sidebarLinks 37 · paletteCorpus 237
```

*Previous baseline, for reference: totalWords 53792 · flows 34 · exercises 12 ·
teachingQs 49 · misconceptions 16 · takeaways 11 · usecaseTables 6 · recalls 5 ·
glossaryTerms 181 · inlineLinks 1017.*

**Verifying `.flow` alignment — do not eyeball it.** Two alignment bugs got shipped
and caught this way. Extract the rendered text and assert column positions:

```python
flows = re.findall(r'<div class="flow">(.*?)</div>', h, re.S)
txt   = html.unescape(re.sub(r'<[^>]+>', '', flow))   # strip spans, resolve entities
# then check .index(token) per line
```

Two traps that caused real bugs:
1. **Never `.ljust()` a string containing HTML entities.** `&lt;` is 4 characters to
   Python and 1 on screen. Build lines in *plain* text, pad, and escape only at render.
2. **Never apply colour by `str.replace(substring)`.** A `("/", "bad")` replacement
   matched inside a `</span>` and corrupted a heading; a `("TWO CHOICES", "hi")` one
   matched inside its own title. Colour by explicit `(line, start, end)` column ranges.

**Mobile baseline** (same run, after the mobile pass — check at 320 / 360 / 390 / 430 px):

```
scrollWidth == viewport at every width · overflowingElements 0 · navHeight 50
navPosition sticky · navInner does not overflow · tapTargetsUnder32px 0
desktop: tablesScrolling 0 · navHeight 52 · tocColumns 2
```

Exclude `#gl-panel`, `#gl-backdrop` and `#gl-hint` from any overflow sweep — the glossary
panel is *deliberately* parked off-canvas and will always report as overflowing.

---

### Verifying external links — the rule that made this trustworthy

`index.html` now carries **63 external URLs** (22 `.vidref` blocks: 15 chapters + 7 designs,
plus the T7 card). Video IDs are exactly the thing a model will confidently invent, so none
of them were written from memory. The procedure, worth repeating for any future additions:

1. **Pull the real IDs from the live playlist**, never from recall. YouTube now renders
   playlists with `lockupViewModel` inside `ytInitialData`, so:
   ```python
   m = re.search(r'var ytInitialData\s*=\s*(\{.*?\});</script>', html, re.S)
   # walk the JSON for 'lockupViewModel' -> contentId + metadata.lockupMetadataViewModel.title
   ```
   (The older `playlistVideoRenderer` path returns nothing now.) A playlist page only
   contains ~20 lazily-loaded entries, which happened to be enough here.
2. **Check every URL resolves**, extracted from the file itself rather than from the script
   that wrote it: `curl -s -o /dev/null -w "%{http_code}" -L`.
3. **Check each video ID matches its claimed title** via the oEmbed endpoint —
   `https://www.youtube.com/oembed?url=…&format=json` returns the real title and author, and
   fails for dead or private videos where a plain fetch may still return 200. Compare
   normalised token sets; a naive substring match produces ~30 false mismatches because the
   labels are reworded (`Kleppmann — 5.2 Quorums` vs `Distributed Systems 5.2: Quorums`).

Last full check: **63/63 resolved, 50/50 video titles matched, 0 mismatches.**

All external anchors carry `target="_blank" rel="noopener"`. The broken-anchor sweep only
looks at `href^="#"`, so it will never catch a dead external link — re-run the curl + oEmbed
pass if links are touched.

## 8. State and what's next

**Done:** chapters 1–10, 12, 14, 15 enriched; Part 3 gained the mental-model card (T5)
and the Google question bank (T6); Part 2 grew from 10 designs to 14; the glossary went
from 181 to 199 terms and gained an **AI Systems** category.

### The Google-question research and what it changed

A web-research pass over eight public question banks and candidate reports produced one
load-bearing finding, and the last round of work was organised around it:

> **At L6 the loop contains two design rounds, not one, split by kind — one
> product/applied, one infrastructure/architecture.** L5 gets a single round.
> Corroborated independently by Hello Interview and Design Gurus.

Nine of the guide's original ten designs were the product round, so half the loop was
unrehearsed. Google's reported pool also skews much harder to infrastructure and
operations than the public canon does — *"upgrade 5000 servers"*, *"log messages in
order"*, *"design a metrics and logging service"*, *"design a distributed LRU cache"*,
*"deny service to banned IPs"*. That is fleet management, observability and admission
control, not feeds and timelines.

Three of the four un-enriched chapters turned out to *be* that infra round, which is why
`ch9` and `ch10` were the ones enriched and why D11–D14 are the designs that were added.

**T6 carries the full tiered list**, each question mapped to the chapter or design that
answers it, with remaining gaps marked in red. Coverage of the Tier 1 list went 6/15 →
10/15. Provenance caveat is stated in the card itself: none of it is confirmed by Google,
and vendor lists are biased toward what they sell content for.

**All 15 chapters are now enriched.** `ch11` and `ch13` were the last two and are done;
`ch3` was rebuilt because it was the thinnest of the nominally-enriched chapters and covers
the field's most-misunderstood result.

**Remaining thin spots, in priority order** (measured by word count and missing block types):

| Chapter | Words | Missing |
|---|---|---|
| `ch1` | 2,057 | recall, teach-qa, usecase, takeaway — the foundation chapter, and the thinnest |
| `ch14` | 2,133 | recall, usecase, quickref |
| `ch15` | 2,444 | usecase, quickref |
| `ch8` | 3,289 | recall, usecase, quickref |
| `ch5` | 3,608 | quickref |

**Not done — the five Tier 1 questions still marked as gaps in T6:**

| Question | Note |
|---|---|
| Google Maps | Geospatial indexing exists in D9 (Uber H3) but there is no Maps design |
| Collaborative editing (Google Docs) | CRDT theory is in `ch4`; no end-to-end design |
| Denylist / banned-IP blocking | Reported twice; entirely absent |
| Notification fan-out (push/email/SMS) | Reported twice; entirely absent |
| Ticket booking under contention | The invariant-on-one-row idea is in `ch7` |

**Also never covered:** DDIA Ch 10 (Batch Processing) and Ch 12 (The Future of Data
Systems). Ch 12's "derived data" framing would strengthen `ch12`'s CQRS/materialised-view
material if the reader wants it.

**Glossary note:** `ch` on a glossary entry is rendered as a jump chip only if the value is
a key in `CH_TITLES` (in the second `<script>`). That map now includes the four new design
anchors (`'design-metrics'`, `'design-cache'`, `'design-typeahead'`, `'design-rag'`), so a
term can point at a *design* rather than a chapter. Add a `CH_TITLES` entry before using a
new anchor, or the chip silently disappears.

**Auto-linker note:** `MASTER_RX` wraps every pattern in `(^|[^\w-])(…)(?![\w-])`, so
short terms are safe from substring matches — `trie` does not fire inside `retrieval`. But
the same boundary means plurals need explicit `aka` entries (`embedding` will not match
`embeddings`).

**Mobile view — fixed.** The page used to have a `scrollWidth` of ~564 px at a 390 px
viewport (564 in the untouched backup too). It is now exactly viewport-width at 320 / 360 /
390 / 430 px, with zero overflowing elements. What was done, all under
`@media (max-width: 680px)` in the **MOBILE HARDENING** block at the end of the `<style>`:

| Problem | Fix |
|---|---|
| 35 wide tables widened the page | Each wrapped in `<div class="tw">` (`overflow-x: auto`). On mobile `.tw > table` is `width: max-content; min-width: 100%; max-width: 560px` — a narrow table fills the column and does *not* scroll; a wide one caps at 560 px and scrolls rather than crushing cells to one word per line |
| `.toc-grid` / `.gl-grid` / `.ng` clipped below their track minimum | `minmax(310px, 1fr)` → `minmax(min(310px, 100%), 1fr)` (same for 268px and 170px) |
| Nav wrapped to 3 rows / 112 px, so it had been made `position: static` | Nav is **sticky again at 50 px**: brand hidden, badge hidden, and each link carries a `.nl-full` + `.nl-abbr` span pair so labels become Theory / Designs / Toolkit / Glossary |
| Scroll affordance was dead CSS | The old `float + position: sticky + height: 100%` `::after` computed to `height: 0px` and never painted. Replaced with styled `::-webkit-scrollbar` (+ `scrollbar-width/color`) on `.tw` and `.flow`, which renders persistently instead of as a gesture-only overlay |
| 24 tap targets under 32 px | Nav links get `padding: 9px 8px`, `.gl-cat` gets `8px 14px`, `.gl-close` is 40×40. Now zero |
| `.flow` ASCII diagrams at 10.5 px | Raised to 12 px. They have to scroll at any phone width regardless, so the width is better spent on legibility. Monospace scales uniformly, so alignment is unaffected |
| 36 px padding on a 350 px card | `.toc-section` → `22px 16px`, `.deep` / `.analogy` → `18px 16px`, `.footer` → `56px 20px` |

Guard rails also added globally (not media-scoped): `html, body { max-width: 100%;
overflow-x: hidden }`, `svg { max-width: 100% }` (10 diagrams live outside `.diagram`),
and `overflow-wrap` on prose so long URLs cannot widen the page.

Desktop is byte-for-byte unaffected in behaviour: 0 tables scroll at 1440 px, the nav is
52 px with full labels, and the TOC is still 2 columns.

**Still open, unrelated to mobile:** the `.ds-header` titles read `[list] 1. Requirements`,
`[chart] 2. Capacity Estimation`, `[plug]`, `[db]`, `[build]` — literal bracketed
placeholder text, present in the original backup. Never raised, never fixed.

---

## 9. Voice — how the enriched prose reads

Match this or the document stops feeling like one book:

- **Lead with why it exists**, then the mechanism. Never "X is a technique where…".
- **Name the trade explicitly.** "You have traded a correctness problem for a load
  problem, which is almost always the right trade because load problems have more solutions."
- **Give real numbers.** `0.999⁵ ≈ 99.5%`, `~7–14 ms of commit-wait`, `1 − 0.99¹⁰⁰ = 63%`.
- **End exercises on a transferable principle**, and cross-reference where it recurs. The
  recurring spine is: *make the constraint local instead of coordinating* — it appears in
  ch4 (partition by conversation), ch5 (partition the crawler by host), ch6 (keep the
  balance on one shard), ch7 (move the invariant onto one row).
- **Correct misconceptions by quoting the false sentence**, then dismantling it.
- British-leaning spelling is used throughout (`behaviour` ×14, `optimise` ×8, `organised`) —
  though technical terms keep their standard forms (`serializability`, `linearizability`).
