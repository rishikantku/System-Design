# CLAUDE.md — Distributed Systems Deep Guide

Context for continuing work on **`index.html`**, a single-file
study guide for Google L6 / Staff Engineer system design prep.

This file is portable: keep it in the same folder as the HTML. All paths below are
relative to that folder unless stated otherwise.

**Companion files in this folder:**
- `index.html` — the artifact (renamed from Distributed_Systems_Deep_Guide.html for Vercel)
- `questions-google.html` — **one question-bank page per company.** See §2b before adding another.
- `specialization-aic.html` — **retrospective prep for the reader's own project.** See §2c.
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
| **Content** | ~179,500 words |
| **Deps** | None. One Google Fonts `@import`. No JS libraries. Opens offline from `file://` |
| **Structure** | 1 `<style>` block, 5 `<script>` blocks (early state-restore in `<body>`, glossary data, glossary engine, search palette, left-nav engine, view-size engine) |

### Document layout (in DOM order)

```
.top-nav                     sticky nav — brand + 4 links + badge
.cover                       title page
#start-here                  orientation: 3 reading paths + the conventions table
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
  #design-push, #design-game, #design-adbilling                    ← D24–D26, reader-supplied Google questions
#part3-toolkit               Part 3 banner
  #toolkit-framework, #toolkit-numbers, #toolkit-tradeoffs, #toolkit-behavioral
#part3-mentalmodel
  #toolkit-mentalmodel       "T5" — DDIA mental model + pattern cheat sheet + 20 mistakes
#part3-questionbank
  #toolkit-questionbank      "T6" — what Google actually asks + the L4/L5/L6 rubric ladder
#part3-video
  #toolkit-video             "T7" — video/lecture references, channels ranked, gaps named
#part3-drills
  #toolkit-drills            "T8" — 24 scenario drills, click to reveal the answer
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

**Every design in Part 2 runs these nine steps in this order.** The order was changed on the
reader's instruction &mdash; the old one (requirements &rarr; capacity &rarr; API &rarr; schema
&rarr; architecture &rarr; deep dives &rarr; trade-offs &rarr; fault tolerance &rarr; conclusion)
"read like it was machine generated", and opening on "Clarify first" never showed the reader
the question being answered. All 26 designs were converted.

| # | Class | Header | Notes |
|---|---|---|---|
| 0 | &mdash; | *(the prompt)* | An `.asked` block **before step 1**, outside the steps: the question as an interviewer would pose it, plus what makes it hard |
| 1 | `req` | Understanding the question | Plain-English framing: what is actually being asked, where the difficulty hides, what the interviewer is listening for. Ends with the `.clarify` block |
| 2 | `fr` | Functional requirements | What it must do, and which requirement is quietly doing all the work |
| 3 | `nfr` | Non-functional requirements | `table.to` with the target and *what it forces*, not a bare list |
| 4 | `schema` | Data model and API | `.schema-code` then `.api-code`, with prose explaining why the model is shaped that way |
| 5 | `est` | Capacity estimation | `.assume` block, `.ng` number cells, then the arithmetic that *decides* something |
| 6 | `tradeoff` | The key trade-offs | `table.to` with `td.chosen` / `td.rej`, then 2&ndash;3 prose subsections on the choices that matter |
| 7 | `arch` | High-level design | The `.anim` block, then a `.flow` + `.flow-cap` |
| 8 | `wflow` | Workflows &mdash; what actually happens | **3&ndash;5 `.wf` blocks.** The most readable thing in a design: named people, real numbers, one happy path and several failures |
| 9 | `deep` | Deep dives, and what breaks | Prose subsections, then the `.ft-row` fault table and the `.concl-grid` |
| &mdash; | &mdash; | *(follow-ups)* | A `.followup` block **after step 9**, outside the steps: 4&ndash;5 interviewer pushback questions, answers supplied |

**Verify the order after touching any design** &mdash; two designs had steps out of order and five
were missing steps entirely before this was enforced:

```python
ORDER = ["req","fr","nfr","schema","est","tradeoff","arch","wflow","deep"]
st = re.findall(r'class="design-step (\w+)"', design_html)
assert st == ORDER
```

**The voice matters as much as the order.** Short sentences mixed with long. Concrete before
abstract. No bolded aphorism opening every paragraph. Named people with clock times ("Priya
shortens a link", "Dev is in the London Underground") rather than "exactly one writer sees one
row affected". Step 1 explains the problem to someone who has not seen it; the `.wf` blocks
narrate rather than enumerate. **Read D1 (`design-url`) or D9 (`design-uber`) before writing a
new one.**

**The tooling that did the conversion** lives in `scratchpad/conv/` &mdash; `lib.py` has
`card_span`, `grab` (pulls the reusable blocks out of an existing card: header, asked, clarify,
assume, ng, schema_code, api_code, anim, tradeoff_table, ft_rows, concl, followup), `build`
(reassembles in the new order, asserting div balance) and `replace` (asserts the old span *and*
the whole document stay balanced). `c1.py`&ndash;`c25.py` are the per-design conversions.


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

`questions-google.html` is a standalone, self-contained page holding **81 Google-tagged**
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
   estimation. **58 are engineering questions.** Do not present the raw list unfiltered.
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

## 2c. `specialization-aic.html` — the Isolated Cloud retrospective page

Prep for the reader's **LinkedIn Staff-level design retrospective** — a 1-hour interview about
one real past project (~40 min drilling it, ~15 min their questions). Not a system-design round.

**~12,500 words, 22 sections, 3 parts.** Most of the growth is collapsed (the question bank) or was explicitly requested by the reader. It reached 17,400 words and 36
sections and the reader said it had become unreadable. The cut is documented in commit
`9305e4f`; the fuller research version is at `864b9f0` if a detail is ever needed back.

| Part | Sections | Contains |
|---|---|---|
| 1 The system | §1–2 | What AIC is; the two-tag provenance key |
| 2 What you built | §3–16 | Thesis, §4 why it is hard, architecture §5–10, **§11 infrastructure deep dive**, §12 team migration, §13 tenant data, §14 isolation guarantees, §15 cache/data/databases, §16 GraphQL gateway + DataLoader |
| 3 The interview | §17–22 | Format, 90-second story, §19 full journey, §20 question bank (71), their questions, one-page revision |

### §11 infrastructure deep dive

The reader interviews with a LinkedIn **infra** team. §11 covers provisioning, networking (IP
allocation, the one-way management channel), placement, fleet rollout and per-tenant rollback,
failure domains and SLOs, backups under customer keys, cost, and production numbers.

It was first built facts-only with a checklist; **at the reader's explicit request the checklist
was replaced with constructed production answers**, marked `data-src="story"`. Keep those
figures identical everywhere they appear (§11, the journey's "Running it in production" chapter,
and the bank's Infrastructure group):

| Figure | Value |
|---|---|
| Provisioning | ~2 days (pilot) → ~5 hours (phase two) |
| IP blocks | /20 default, /19 large tenants, non-overlapping from one reserved range |
| Rollout | commercial → wave 0 (3 Atlassian-owned) → wave 1 canaries, 24h bake → wave 2 |
| Version skew | max two versions; security patches exempt from freezes |
| Internal targets | 99.95% per environment, 99.99% shared entry path |
| Backups | PITR ~5 min data at risk; shard restore 1–2 h; environment within a day |
| Cost floor | smallest tenant ~4–6× commercial; right-sizing cut ~⅓ of baseline |
| Production | ~a dozen customer environments; >100 shards each; 2 self-caused incidents in year one |

Journey data is now `scratchpad/journey/data6.py`, bank `scratchpad/bank/data5.py`.

### Where the generated content lives

The journey and bank are generated from data files, not hand-edited HTML. Latest versions:
`scratchpad/journey/data5.py` (journey, `("say"|"story", text)` blocks) and
`scratchpad/bank/data3.py` (bank phases). `scratchpad/hardprob/apply2.py` shows the rebuild
pattern: shift `ch-num` and `&sect;` refs, insert sections by div-depth span, regenerate both
blocks, then re-run `scratchpad/nav/build.py`. §12–§15 carry `data-src="story"` on their
`.chapter` div, meaning the whole section is constructed design around the reader's architecture.
**Nadel** facts (combines many GraphQL services into one API; hydration calls other services,
batched) are public, from github.com/atlassian-labs/nadel, and tagged PUBLIC.

### Left navigation

Same look as the guide's sidebar (it reuses `#side-nav`, `.sn-*` from the shared stylesheet), but
the page has no top nav, so it opens from a floating `#side-toggle.aic-float` button. Docked open
at >=1200px (preference in `localStorage` key `aic.nav`), a drawer below that. Links are
**generated from the page's own headings** by `scratchpad/nav/build.py`, which is idempotent
(everything sits between `AIC-NAV` comment markers) — **re-run it after adding or renaming a
section.** The §14 journey chapters and §15 bank groups appear as sub-links that expand for the
section you are in. `/` focuses the filter; Escape closes the drawer.

### Rules for this page

- **Plain English. Short sentences.** No "which is precisely why", "it is worth noting". Lead
  with the point. Tables over paragraphs when it is genuinely a list.
- **Two tags only:** `PUBLIC` (.tag-c, Atlassian docs, citable) and `YOURS` (.tag-y, the
  reader's own work, not citable but first-hand). The old four-tag scheme was cut with the
  research sections.
- **The journey and bank read as first-hand experience, on the reader's instruction.** Details
  the reader did not supply (who pushed back, the pilot bank, the rehearsal, the two production
  incidents, the five-step tool, timings like "about a quarter") were constructed as a coherent
  principal-engineer story. **Constructed journey paragraphs carry an invisible
  `data-src="story"` attribute** — keep it on anything added, and never present those details
  elsewhere as the reader's documented facts. The bank must stay consistent with the journey.
- **Do not re-add hypothetical design.** A retrospective rewards decisions actually made.
  Inventing a migration platform actively trains the wrong instinct.
- **If adding something, cut something.** This page's value is that it can be read in one
  sitting.

### The architecture it must state correctly

The reader supplied this as source of truth. Getting it wrong has happened twice.

| Term | Means |
|---|---|
| **Control plane** | Shared. Provisioning, lifecycle. **Not on the request path.** |
| **Customer data plane** | Dedicated per customer. Serves traffic. |
| **Global Edge** | Handles request, forwards to Router. Does **not** decide placement. |
| **Router** | Decides **commercial vs isolated only**. Caches tenant context; miss → Tenant Context Service. |
| **Tenant Context** | Static: identity, environment, entitlements. |
| **Shard Manager** | Runtime placement + shard lifecycle. |
| **Shard** | **Logical** isolated runtime for a **tenant + product**. Holds multiple replicas. |
| **Replica** | A runtime copy inside a shard. |
| **Shard descriptor** | Per-shard config. Service descriptor describes the service. |
| **Shard configuration repository** | **Source of truth** for placement. |
| **Egress Gateway** | Centralized outbound policy enforcement. |

Path: Client → Global Edge → Router → Tenant Context → {commercial | Shard Manager → shard →
replicas → dedicated data} → Egress Gateway.

**Five things that were wrong before — do not reintroduce:**

1. A shard is **not** a service instance or an EC2 instance. Shard ≠ replica.
2. **Replica failure ≠ shard replacement.** Only a shard change updates placement and
   invalidates the cache.
3. The **Router must be present**, scoped to commercial-vs-isolated.
4. **Caches are never the source of truth.**
5. **No Kubernetes.** AWS-native Auto Scaling. (A drill titled "Why not Kubernetes?" is
   intended — it answers the anticipated question.)

Also: **never name a policy engine** (e.g. OPA). Say "policy-driven enforcement". 178 teams is
the reader's own figure; other numbers come from the constructed story and must stay identical
across the journey and the bank.

## 2e. `companies/` — per-company interview workspaces

`companies/index.html` is the level between the guide and a company. Today it lists two:
the **LinkedIn Staff full-loop workspace** and the existing Google question bank.

### `companies/linkedin/` — the Staff full-loop workspace

The reader **cleared the LinkedIn design retrospective** and is preparing for the four-round loop:
coding, AI coding, system design, hiring manager. Five pages plus shared assets:

| File | Holds |
|---|---|
| `index.html` | Dashboard: readiness rings, today's plan, **recent interview intelligence**, the question database, "what recent interviews are telling us", sources |
| `01-coding.html` | 18 patterns with C# templates, 14 worked problems (9-stage progressive reveal), 33-problem bank, complexity/edge-case/quality/communication checklists, 3 mocks |
| `02-ai-coding.html` | The AI-enabled round: reported format and rubric, 22 AI-engineering concepts, 11 C# exercises, 2 progressive-requirement simulations, 2 mocks |
| `03-system-design.html` | 16-step framework, numbers, staff lens, 8 interactive designs (the page asks before it tells), catalogue linking the guide's 26 designs, 3 mocks |
| `04-hiring-manager.html` | 12-story bank **built only from `specialization-aic.html`**, 20 behavioural questions, craftsmanship round, Why-LinkedIn worksheet, 3 mocks |
| `assets/prep.css`, `assets/prep.js` | Shared visual language and the state engine |
| `assets/manifest.js` | Generated: every trackable item with round, topic, weight. The dashboard computes readiness from this plus localStorage |
| `src/*.py` | The generators. `python3 src/build.py` rewrites all five pages and the manifest. `coding_official.py` + `coding_drills.py` (Staff Coding), `aicoding_drills.py` (CWAI DS&A drills), `sysdesign_official.py` + `sysdesign_infra.py` (design) hold the content added after the pack arrived |

**State model.** Everything is stored in `localStorage` under `lp.v1` (`items`, `mocks`, `log`).
Chromium shares `file://` storage across the folder, so the dashboard sees what the round pages
write — verified. `LP.stats(round)` weights items: solved = 1, revise/slow/hint = 0.5, failed = 0.25,
and a "done" item with confidence ≤ 2 is capped at 0.8.

**Mock mode is a chat handoff.** The page runs the question, timer and notes; the *Grade this with
Claude* button copies a prompt asking for SCORE / WHAT WAS STRONG / WHAT IS MISSING / STAFF-LEVEL
SIGNAL / HOW TO IMPROVE / LIKELY FOLLOW-UP. The pages never pretend to grade.

### The official prep pack — authoritative

The recruiter sent **`Staff SI Onsite Prep - CWAI (1).pdf`** ("LinkedIn Interview Preparation,
Staff Virtual Onsite, Systems & Infrastructure"). It sits in the repo root and is git-ignored by
the `*.pdf` rule. Its contents are encoded in `src/research.py` as `OFFICIAL_ROLE`,
`OFFICIAL_MODULES`, `OFFICIAL_LOGISTICS` and `OFFICIAL_RESOURCES`, and every page opens with an
**"The official module"** section rendered by `lib.official_module()`.

**The pack overrides the web research wherever they disagree** — say so on the page when they do
(the AI round is CoderPad AI Assist, not the HackerRank variant one candidate reported).

| Module (60 min each) | What the pack says it scores |
|---|---|
| Systems and Infrastructure Design | Completeness, quality of decisions, reasoning about scalability/performance/reliability/fault tolerance/extensibility. Example question in the pack: **Bit.ly**, with four named sub-questions |
| Host Leader | Five focus areas: **communication, culture, influence, mentorship, conflict** |
| Coding with AI (CWAI) | Fundamentals + intentional AI use + critical evaluation of output + iteration + communication. **Using AI is expected**; you own the solution |
| Staff Coding | **Modularity and extensibility**, and **finding and fixing bugs**; pointers, edge cases, abstraction. No AI. Example question: **Firefighting Strategy** |

**Coverage after the pack** (Sep 2026): Staff Coding 18 patterns + 22 worked problems (8 of them bug-hunt or extensibility drills) + 33 reps; CWAI 8 DS&A drills run the AI way + 22 AI-engineering concepts + 11 exercises; Design 14 interactive designs including 5 SI classics (replicated KV, stream processing, CDC, OLAP serving, coordination); Host Leader 12 stories + 19 questions.

**The CWAI correction worth remembering:** the round is *ordinary coding with an assistant*, not building AI systems. The first build of `02-ai-coding.html` was AI-engineering only; `aicoding_drills.py` is what actually prepares for the module (plan → prompt → verify → defend, with the specific defects assistants produce per problem).

Both example questions are worked in full: `src/coding_official.py` (Firefighting Strategy, plus a
bug-hunt drill and an extensibility drill) and `src/sysdesign_official.py` (Bit.ly, with the four
sub-questions as the deep dives).

**Two honest gaps** the pack exposed in the reader's material, flagged on the Host Leader page and
deliberately left for them to fill: **culture** (a team culture they built) and **mentorship** (a
named person they grew). The Isolated Cloud retrospective is a platform story, not a team-lead story.

### The research layer — two passes, kept separate

`src/research.py` is **pass 1** (21 Sep 2026): the loop shape, 15 sources, the themes that drive each round page's
"what reports say" section. It also holds the official pack (`OFFICIAL_*`).

`src/research2.py` is **pass 2** (22 Sep 2026): a question hunt across more sources, with stricter rules, rendered by
`src/researchpage.py` into **`05-research.html`** — a page that updates independently of the prep content.

- A question is `reported` **only** if a candidate described being asked it, or the reader supplied it. Guides and
  "top questions" lists go in `GENERAL`; my own readings go in `INFERENCE`. Never blur the three.
- Fields per question: LeetCode name/number/URL, report date, level, location, round, follow-ups, variations,
  constraints, expected complexity, sources, independent report count, recurrence, confidence, and `covers`
  (the workspace item id, or `None` → it shows as a gap).
- `HIGH` = several independent recent reports **or** reader-supplied first-party; `MEDIUM` = one strong recent report;
  `LOW` = single/thin/old. Copies of one original report never count twice.
- **The reader's own list of past LinkedIn questions is the strongest signal in the file.** It drove
  `src/coding_linkedin.py` — 13 worked problems including the keyed n-ary tree merge, minimum degree of connection
  (bidirectional BFS), compact tree, valid triangle and the booths problem.
- Sources that block fetching (LeetCode, Glassdoor, 1Point3Acres) are read via search summaries and graded down; that
  limitation is stated on the page rather than hidden.

#### Pass 1 detail

One web-research pass (21 Sep 2026) over 15 sources: Hello Interview, Coditioning, Exponent
(question bank + a ≈Mar 2026 candidate report), Taro (India Staff, May 2025), Blind (Senior SWE
Infra, Sep 2025 + levelling threads), LeetCode Discuss (Staff, Jun 2025), Glassdoor, Prepfully,
DesignGurus, company-tag datasets.

- Every question carries `d` (date), `role`, `loc`, `src`, `rec` (high/medium/one-off) and `conf`
  (**A** first-hand recent · **B** aggregator or thin first-hand · **C** single/undated/older).
- **Never present C as confirmed**, and never phrase any of it as a prediction. The dashboard says
  "recent candidates reported X, so X is a preparation signal".
- To refresh: add entries to `Q`, update `THEMES`/`LOOP`, bump `DATE`, rebuild. Old entries stay so
  passes can be compared.

**What the research changed** (documented on the dashboard): rate limiter leads the design list;
every AI exercise ends in concurrency + productionisation; debug-then-extend drills exist because
that is the reported AI-round arc; graphs/nested-tree patterns are P0; migration-at-scale and
career-arc are the first two HM stories; a craftsmanship section exists at all.

### Rules for this workspace

- **Personal experience comes only from `specialization-aic.html`.** The HM page tags it
  `Your experience`; general interview knowledge is tagged `General knowledge`. Do not invent
  projects, metrics or motivations — "Why LinkedIn" is a worksheet the reader fills in, deliberately.
- **C# for all code**, unless the reader asks otherwise.
- `rich()` escapes HTML but lets `<b> <i> <br> <code> <small>` through; anything richer belongs in a
  raw block. Accordion titles use `titled()` + `raw=True` or they render escaped markup.
- Keep `assets/prep.js` dependency-free and defensive: `localStorage` is wrapped in try/catch.
- Verify with the browser skill at 390px and 1440px; the pages currently have zero overflow at both.

---

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
| `.anim` | Animated architecture diagram — inline SVG + CSS keyframes, **never a GIF** (the file must stay self-contained and open from `file://`) | `.an-head` (title + Pause + "What goes wrong"), `<svg>`, `.an-legend`, then **two** captions: `.an-cap.ok-only` and `.an-cap.fail-only`. Elements marked `.fail-only` appear and `.ok-only` hide when the container gets `.is-fail`. **Generate the geometry** with `scratchpad/anim/mk.py` — hand-placed coordinates collide, exactly as with the ASCII diagrams |
| `.drill` | Scenario drill — a `<details>` with a situational-judgement question and a revealed answer | `<summary>` holds `.dr-n` + `.dr-q` + `.dr-cue`; body is `.dr-a` ending in a `.dr-key` principle line. **Distinct from `.exercise`** (mechanism practice) and `.teach-qa` (understanding checks): these are decisions, and most have no single right answer |
| `.asked` | The prompt, once per design, immediately inside `.dc-body` | Two columns: `.ak-q` (the question, italic, as asked) + `.ak-h` (what makes it hard — the tension, **without giving away the answer**, since the derivation is the point). Stacks under 760px |
| `.method` | The nine-step method, explained **once** at the top of Part 2 | `.mrow` > `.mnum` + `.mwhat` + `.mwhy`, closing `.mnote`. Explaining the method once and keeping every design identical is what makes 26 designs navigable — repeating the explanation per design would be noise |
| `.startcard` | The "Start here" orientation, once, after the cover | Three reading paths + a conventions table. Teaching the reader the document's conventions is what makes 104k words navigable |
| `.quickref` | Scannable decision table at the **top** of a chapter, for a reader who already knows the material and just needs the answer | `.label`, `.qr-sub`, then a 4-column table: *If you need… / Reach for / Because / **Used in***. The last column carries real systems (`Envoy`, `resilience4j`, Kafka) and `<span class="srcref">` links to designs. Wrap the table in `.tw`. Collapses to stacked cards under 680px |
| `.buildup` | Progressive derivation — build the naive design, break it, fix it, repeat | `.label`, then `.bu-step` > `.bu-n` + `.bu-body` containing `.bu-try` (the attempt), `.bu-break` (the exact failure, red), `.bu-learn` (what it teaches, green); closing `.bu-end`. **The best device in the toolkit for genuinely hard topics** — the reader arrives at the real answer having felt why every simpler answer fails |
| `.assume` | Stated assumptions **with the consequence of each being wrong**, inside step 2 | `.label`, then `.as-row` > `.as-a` (the assumption) + `.as-b` (what breaks). A bare list of numbers is not an assumptions section |
| `.concl-grid` | Step 9 closing summary | Four `.cc` cards: dominant constraint, what I would build first (`.cc.first`), what I deliberately did not build, biggest risk (`.cc.risk`) |
| `.followup` | **Interviewer pushback** after you present, one block per design, at the end of `.dc-body` | `.fu-title` + `.fu-sub`, then `<details class="fu">` per question: `<summary>` holds `.fu-q` (the question, italic, in quotes) + `.fu-cue`; body is `.fu-a`. **Distinct from `.clarify`** — clarify is what *you* ask at the start, this is what *they* ask at the end. Answers are always supplied, per §1 |
| `.wf` | Workflow walkthrough — what actually happens, step by step, with real names and clock times | `.wf-title` + `.wf-sub`, then `<ol>` of steps, closing `.wf-out` (what actually happened). `.wf.alt` for the non-happy paths. **The most readable thing in a design.** Every design now has 3&ndash;5, and they are step 8. One happy path first, then the failures. End each on `.wf-out` &mdash; what actually happened and why it was the right trade |
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

**The file is ~1.5 MB. Never rewrite it wholesale.** Use surgical anchored insertion.

**Assert div balance before writing, whenever you replace a block rather than append one.**
A non-greedy `<div class="ds-body">(.*?)</div>` truncated every body containing nested divs,
which made one design card swallow the next seven. It renders without an error, so nothing
catches it but the count:

```python
assert new_segment.count('<div') - new_segment.count('</div>') == 0
```


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

**Baseline to regress against** (current, after the voice conversion of all 26 designs):

```
totalWords 179518 · designs 26 (234 steps, all in the req/fr/nfr/schema/est/
  tradeoff/arch/wflow/deep order) · toolkitCards 8
asked 26 · clarify 26 · assume 26 · concl 26 · tradeoff 26 · dsIcons 243
followup 26 · followupQs 108 (0 open by default)
wf 102 (3-5 per design; was 4, D19 only, before the conversion)
quickref 15 (every chapter) · buildup 3 · drills 24 · sidebarLinks 53
anims 29 (every design + ch4/ch7/ch10) · animChips 29
srcref 167 cross-reference chips (none are links — that is the convention)
flows 72 · tables 95 (all wrapped in .tw) · glossaryTerms 199 · gt 1628
externalLinks 76 (all target=_blank rel=noopener)
gtInFlow 0 · gtInCodeOrLink 0 · brokenAnchors [] · consoleErrors 0
navHeight 59 · flowsScrollingOnDesktop 0 · tablesScrollingOnDesktop 0
questions-google.html: 81 questions · 58 eng · 63 cross-linked · 0 gaps
```

**Two false positives to expect in an overflow sweep**, or you will chase them twice:
`#gl-panel`'s *descendants* (not just the panel itself) are parked off-canvas and always report
as overflowing; and the `.fl-*` spans inside `.flow` legitimately extend past a phone viewport
because their container scrolls. Exclude
`#gl-panel, #gl-backdrop, #gl-hint, .flow, .tw, .codeblock, .schema-code, .api-code, svg`
and the count is **0 at 320 / 360 / 390 / 430 / 1440**, with `scrollWidth == viewport` at each.


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

### Reader-supplied Google questions (D24–D26)

Three designs came from questions the reader was actually asked, rather than from the
scraped bank. Each leads with a decision that has **no recovery path if you get it wrong**,
which is what makes them good interview questions:

| | The decision everything hangs on |
|---|---|
| `D24` iOS push | One persistent connection per **device**, not per app. Per-app means 40 sockets and 40 keepalives on one phone, which is a battery cost users answer by disabling push |
| `D25` browser game | All 35K concurrent games fit in ~180 MB, so this is **not a scale problem** — it is stateful routing plus durability, and the move log collapses replay, history and crash recovery into one dataset |
| `D26` ad billing | The `impression_id` must be minted **on the TV** and reused across retries. Server-minted ids make a retry indistinguishable from a real impression *forever*, and no downstream engineering recovers from it |

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

**Fixed:** the `.ds-header` titles used to read `[list] 1. Requirements`,
`[chart] 2. Capacity Estimation`, `[plug]`, `[db]`, `[build]` — literal bracketed placeholder
text inherited from the original backup, on **all 234 step headers**. They are now the icons
they were named after, wrapped in `<span class="ds-ico">`. This was the single most visible
source of the document looking unfinished.

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
