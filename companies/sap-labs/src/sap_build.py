# -*- coding: utf-8 -*-
"""Build companies/sap-labs/index.html — one self-contained page, no external dependencies.

    python3 sap_build.py
"""
import os, json
from html import escape as E

import sap_role as R
import sap_concepts1, sap_concepts2
import sap_design as SD
import sap_behav as B
import svg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'index.html')
CARDS = sap_concepts1.CARDS + sap_concepts2.CARDS
BYID = {c['id']: c for c in CARDS}
assert len(BYID) == len(CARDS), 'duplicate card id'

SECTIONS = [  # (id, nav title, group)
 ('m-overview', 'SAP FDE Overview', 'The role'), ('m-role', 'Role Expectations', 'The role'),
 ('m-de', 'Data Engineering', 'Data engineering'), ('m-lakehouse', 'Lakehouse', 'Data engineering'), ('m-parquet', 'Parquet', 'Data engineering'),
 ('m-delta', 'Delta Lake', 'Data engineering'), ('m-spark', 'Spark', 'Data engineering'), ('m-databricks', 'Databricks', 'Data engineering'),
 ('m-airflow', 'Airflow', 'Data engineering'), ('m-kafka', 'Kafka', 'Data engineering'), ('m-hana', 'SAP HANA', 'Data engineering'), ('m-sql', 'SQL', 'Data engineering'),
 ('m-quality', 'Data Quality', 'Trust'), ('m-governance', 'Governance', 'Trust'),
 ('m-agentic', 'Agentic AI', 'AI'), ('m-rag', 'RAG', 'AI'), ('m-entai', 'Enterprise AI', 'AI'), ('m-llmeval', 'LLM Evaluation', 'AI'),
 ('m-design', 'System Design', 'Interview'), ('m-scenarios', 'FDE Scenarios', 'Interview'), ('m-behav', 'Behavioral', 'Interview'),
 ('m-exp', 'My Experience → SAP', 'Interview'), ('m-qbank', 'Interview Question Bank', 'Interview'), ('m-final', 'Final Revision', 'Interview'),
]
assert len(SECTIONS) == 24
SEC_IDS = {s[0] for s in SECTIONS}
for c in CARDS: assert c['mod'] in SEC_IDS, c['id']

LAB = {'JD': ('lab-jd', 'SAP JOB REQUIREMENT'), 'GENERAL': ('lab-gen', 'GENERAL KNOWLEDGE'), 'GEN': ('lab-gen', 'GENERAL KNOWLEDGE'),
       'VERIFY': ('lab-verify', 'VERIFY WITH SAP DOCS'), 'INFER': ('lab-infer', 'INFERENCE'), 'RESUME': ('lab-res', 'FROM YOUR RESUME'),
       'GAP': ('lab-gap', 'USER INPUT REQUIRED')}
PRIO = {'must': ('p-must', 'Must know'), 'should': ('p-should', 'Should know'), 'nice': ('p-nice', 'Nice to know')}

def lab(src):
    c, t = LAB[src]; return f'<span class="lab {c}">{t}</span>'
def prio(p):
    c, t = PRIO[p]; return f'<span class="pr {c}">{t}</span>'
def ul(items): return '<ul>' + ''.join(f'<li>{E(i)}</li>' for i in items) + '</ul>'
def table(head, rows, cls=''):
    h = ''.join(f'<th>{E(x)}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{x if isinstance(x, Raw) else E(x)}</td>' for x in r) + '</tr>' for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'
class Raw(str): pass
def note(kind, title, body): return f'<div class="note n-{kind}"><div class="nt">{E(title)}</div>{body}</div>'

# ------------------------------------------------------------------ concept card
def card(c):
    fq, fa = c['fu']
    code = ''
    if c['code']:
        lang, src = c['code']
        code = f'<div class="blk" data-depth="2"><div class="bh">Example code <span class="muted">({E(lang)})</span></div><pre class="code">{E(src)}</pre></div>'
    ans = (f'<div class="blk ans"><div class="bh">Interview answer</div>'
           f'<div class="tabs" role="tablist"><button class="tab on" data-t="15">15 seconds</button><button class="tab" data-t="30">30 seconds</button><button class="tab" data-t="2m">2 minutes</button></div>'
           f'<div class="tp on" data-t="15">{E(c["a15"])}</div><div class="tp" data-t="30">{E(c["a30"])}</div><div class="tp" data-t="2m">{E(c["a2m"])}</div></div>')
    body = (
        f'<div class="blk what"><div class="bh">What it is</div><p>{E(c["what"])}</p></div>'
        f'<div class="blk why"><div class="bh">Why it exists</div><p>{E(c["why"])}</p></div>'
        f'<div class="blk ana"><div class="bh">Analogy</div><p>{E(c["analogy"])}</p></div>'
        f'<div class="blk bridge"><div class="bh">You already know this — backend connection</div><p>{E(c["bridge"])}</p></div>'
        f'<div class="blk tech" data-depth="2"><div class="bh">How it works</div><p>{E(c["tech"])}</p></div>'
        f'<details class="blk expert" data-depth="3"><summary class="bh">Expert depth</summary><p>{E(c["expert"])}</p></details>'
        f'<div class="blk ex"><div class="bh">Example</div><p>{E(c["example"])}</p></div>'
        f'{code}{ans}'
        f'<details class="blk fu"><summary class="bh">Senior follow-up: {E(fq)}</summary><p>{E(fa)}</p></details>'
        f'<div class="blk mis"><div class="bh">Common mistake</div><p>{E(c["mistake"])}</p></div>')
    return (f'<article class="card" id="c-{c["id"]}" data-card="{c["id"]}" data-sec="{c["mod"]}">'
            f'<header class="ch"><button class="ct" aria-expanded="false"><span class="caret"></span>{E(c["title"])}</button>'
            f'<span class="cm">{prio(c["prio"])}{lab(c["src"])}'
            f'<button class="bm" title="Bookmark" aria-label="Bookmark">☆</button>'
            f'<label class="dn"><input type="checkbox"> done</label></span></header>'
            f'<div class="cb">{body}</div></article>')

def cards_for(sec): return ''.join(card(c) for c in CARDS if c['mod'] == sec)

def head(sec_id, title, lead, src=None):
    return f'<div class="sh"><h1>{E(title)}</h1>{lab(src) if src else ""}</div><p class="lead">{E(lead)}</p>'

# ------------------------------------------------------------------ sections
S = {}

S['m-overview'] = (
  head('m-overview', 'SAP FDE Overview', 'What the role is, what SAP\'s posting actually says, and how this guide is organised.') +
  note('info', 'How to read the labels', Raw(
    f'<p>{lab("JD")} quoted or paraphrased from SAP\'s posting for requisition 458124. {lab("GENERAL")} general industry knowledge. '
    f'{lab("VERIFY")} SAP-specific detail from public sources — check SAP\'s latest documentation before quoting it. {lab("INFER")} my reading of what the role implies; SAP has not said it. '
    f'{lab("RESUME")} a fact from your resume. {lab("GAP")} something only you can fill in.</p>'
    '<p>Questions in this guide are <b>likely questions based on the job description</b>, not questions SAP is known to ask.</p>')) +
  '<h2>The posting, in SAP\'s words</h2>' + lab('JD') +
  table(['', 'What the posting says'], [(k, v) for k, v in R.JD_FACTS]) +
  '<p class="muted">Sources: ' + ' · '.join(f'<a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a>' for t, u in R.JD_SOURCES) + '. SAP\'s own page did not render for automated reading; the mirror and search snippets supplied the text. Re-read the live posting before the interview.</p>' +
  '<h2>What a Forward Deployed Engineer is</h2>' +
  ''.join(f'<div class="pt"><div class="pth">{E(t)} {lab(s)}</div><p>{E(b)}</p></div>' for t, s, b in R.FDE_NOTES) +
  '<h2>FDE vs neighbouring roles</h2>' + lab('GENERAL') +
  table(['Role', 'What they do', 'Output', 'Code ownership'], R.FDE_COMPARE) +
  '<h2>How to use this guide</h2>' + ul([
    'Depth (top bar): Simple shows the idea and the interview answer; Intermediate adds mechanics and code; Expert adds production depth. Default is Intermediate.',
    'Backend Engineer Mode moves the "you already know this" bridge to the top of every concept and highlights it.',
    'Interview Answer Mode moves the 15-second / 30-second / 2-minute answers to the top.',
    'Tick "done" on a concept to track progress; star it to bookmark. Everything is saved in this browser.',
    'Press / or Ctrl-K to search every concept, question and section.',
    'The night before: Final Revision. Ten minutes before: "Open before interview" in the top bar.']))

S['m-role'] = (
  head('m-role', 'Role Expectations', 'What SAP is really evaluating, and where your gaps are against each requirement.') +
  '<h2>What SAP is really evaluating</h2>' +
  table(['Area', 'The question behind it', 'Basis'], [(a, q, Raw(lab(s))) for a, q, s in R.EVALUATING]) +
  '<h2>Requirement → priority → your likely gap</h2>' +
  '<p>Gap is my estimate from your resume. A <b>large</b> gap means: understand it deeply, be honest that it is not hands-on, and connect it to what you have built.</p>' +
  table(['Requirement', 'Basis', 'Priority', 'Gap', 'Study', 'Note'],
        [(r, Raw(lab(s)), Raw(prio(p)), Raw(f'<span class="gap g-{g}">{g}</span>'), Raw(f'<a href="#{m}">{E(dict((x[0], x[1]) for x in SECTIONS)[m])}</a>'), n) for r, s, p, g, m, n in R.REQ_MATRIX]) +
  note('warn', 'The honesty line', Raw('<p>The posting asks for "hands-on experience with PySpark, Databricks". Your resume does not list them. Say what is true: you understand the architecture and failure modes in depth, you have built the equivalent distributed systems (Kafka, event pipelines at scale), and you are ramping on the specific tools. Never claim hands-on use you do not have.</p>')))

S['m-de'] = (
  head('m-de', 'Data Engineering', 'The fundamentals, explained through what you already know from backend systems.') +
  '<h2>You already know this</h2>' + table(['You know', 'Maps to', 'How'], B.BRIDGES) +
  svg.pipeline() + svg.etl_elt() + '<h2>Concepts</h2>' + cards_for('m-de'))

S['m-lakehouse'] = (
  head('m-lakehouse', 'Lake, Warehouse, Lakehouse', 'Where analytical data lives, and why the lakehouse became the default.') +
  table(['', 'Warehouse', 'Lake', 'Lakehouse'], B.LAKE_TABLE, 'cmp') +
  '<h2>When to choose which</h2>' + table(['Choose', 'When'], B.WHEN_TO_CHOOSE) +
  svg.medallion() + '<h2>Concepts</h2>' + cards_for('m-lakehouse'))

S['m-parquet'] = (
  head('m-parquet', 'Parquet', 'The columnar file format that every lakehouse sits on.') + svg.csv_parquet() +
  table(['', 'CSV', 'Parquet'], B.CSV_PARQUET, 'cmp') + '<h2>Concepts</h2>' + cards_for('m-parquet'))

S['m-delta'] = (
  head('m-delta', 'Delta Lake', 'How a folder of Parquet files becomes a reliable table.') + svg.delta_log() +
  table(['', 'Parquet', 'Delta Lake'], B.PARQUET_DELTA, 'cmp') + '<h2>Concepts</h2>' + cards_for('m-delta'))

S['m-spark'] = (
  head('m-spark', 'Spark and PySpark', 'The deepest module. Every term maps onto something from distributed systems.') +
  '<h2>Spark vocabulary in one table</h2>' + table(['Term', 'Simple', 'Backend analogy'], B.SPARK_QUICK) +
  svg.spark_arch() + svg.shuffle() + '<h2>Concepts</h2>' + cards_for('m-spark'))

S['m-databricks'] = head('m-databricks', 'Databricks', 'The managed platform around Spark and Delta, and how production work runs on it.') + cards_for('m-databricks')
S['m-airflow'] = head('m-airflow', 'Airflow', 'Airflow orchestrates. Spark processes.') + svg.airflow_dag() + cards_for('m-airflow')
S['m-kafka'] = head('m-kafka', 'Kafka for Data Engineering', 'Your strongest area — reframed for CDC, lake ingestion and stream processing.') + svg.kafka_flow() + cards_for('m-kafka')
S['m-hana'] = (head('m-hana', 'SAP HANA', 'Interview-safe understanding. Know the idea and the integration questions; never claim hands-on use.') +
  note('warn', 'Say this if asked about HANA experience', Raw('<p>"I have not worked with HANA hands-on. I understand its design — in-memory, columnar, running transactional and analytical work on one copy — and the integration questions that matter for a lakehouse: supported extraction, preserving business semantics, incremental changes and reconciliation."</p>')) +
  svg.hana() + svg.sap_platform() + cards_for('m-hana'))
S['m-sql'] = head('m-sql', 'SQL', 'The live-coding staples: joins, aggregation, window functions, dedup, top-N, optimisation.') + cards_for('m-sql')
S['m-quality'] = head('m-quality', 'Data Quality', 'The JD says "ensure data quality". This is how you make that concrete.') + cards_for('m-quality')
S['m-governance'] = head('m-governance', 'Governance and PII', 'Catalogue, access, lineage, audit, lifecycle — and the AI-specific leak paths.') + cards_for('m-governance')
S['m-agentic'] = head('m-agentic', 'Agentic AI', 'The JD asks you to "operate effectively in an Agentic AI context". Here is what that means in engineering terms.') + svg.llm_rag_agent() + cards_for('m-agentic')
S['m-rag'] = head('m-rag', 'RAG', 'A search system with a generator on the end — engineer it that way.') + svg.rag() + cards_for('m-rag')
S['m-entai'] = head('m-entai', 'Enterprise AI', 'From demo to production: data, identity, security, observability, cost.') + svg.ent_ai_stack() + cards_for('m-entai')

EVAL_LEVELS = [('Model', 'correctness, faithfulness, relevance, completeness, format', 'Is the answer right and supported?'),
               ('Retrieval', 'recall@k, precision, MRR, context relevance', 'Did we fetch the right content?'),
               ('System / agent', 'task success, tool choice and parameters, steps, latency, cost', 'Does the whole thing complete the job?'),
               ('Safety', 'PII leakage, injection and jailbreak resistance, policy compliance', 'Can it be trusted with enterprise data?'),
               ('Business', 'resolution rate, time saved, error cost, satisfaction', 'Did it move the metric we agreed?')]
S['m-llmeval'] = (head('m-llmeval', 'LLM Evaluation', 'Five levels, because accuracy alone hides most failures.') +
  table(['Level', 'Metrics', 'Question'], EVAL_LEVELS) +
  note('info', 'Why accuracy alone is not enough', Raw(ul(['Right by luck: accurate but not grounded in the sources.', 'Right but incomplete: missed the exception that mattered.', 'Right but unsafe: leaked personal data while answering.', 'Right but unusable: too slow or too expensive to deploy.', 'Errors are not equal: a wrong invoice amount costs more than a clumsy sentence — weight by business cost.']))) +
  cards_for('m-llmeval'))

def design_block(d):
    parts = [
      ('Problem', f'<p>{E(d["problem"])}</p>'), ('Requirements', ul(d['requirements'])), ('Clarifying questions', ul(d['clarify'])),
      ('Architecture', table(['Layer', 'What'], d['arch'])), ('Data flow', f'<p class="flowline">{E(d["flow"])}</p>'),
      ('Technology choices', table(['Choice', 'Why'], d['tech'])), ('Trade-offs', ul(d['tradeoffs'])), ('Scalability', ul(d['scale'])),
      ('Failure handling', ul(d['failures'])), ('Security and governance', ul(d['security'])), ('AI integration', ul(d['ai'])),
      ('Follow-up questions', ''.join(f'<details class="fq"><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in d['followups']))]
    body = ''.join(f'<div class="dsec"><div class="dsh">{i+1}. {E(t)}</div>{b}</div>' for i, (t, b) in enumerate(parts))
    say = f'<div class="blk ans"><div class="bh">Say it in two minutes</div><p>{E(d["say"])}</p></div>'
    return (f'<article class="card" id="c-{d["id"]}" data-card="{d["id"]}" data-sec="m-design"><header class="ch"><button class="ct" aria-expanded="false"><span class="caret"></span>{E(d["title"])}</button>'
            f'<span class="cm">{lab(d["src"])}<button class="bm" title="Bookmark" aria-label="Bookmark">☆</button><label class="dn"><input type="checkbox"> done</label></span></header>'
            f'<div class="cb">{say}{body}</div></article>')

S['m-design'] = (head('m-design', 'System Design', 'Five likely scenarios, each worked through the same twelve parts. Scenarios are inferred from the job description.') +
  note('info', 'The opening move', Raw('<p>Every design starts with the business outcome and the constraints — sources, freshness, regulation — before any box is drawn. That is the FDE habit SAP is looking for.</p>')) +
  ''.join(design_block(d) for d in SD.DESIGNS))

def fde_block(f):
    body = (f'<p>{E(f["context"])}</p>' +
            '<div class="steps5">' +
            f'<div class="st"><div class="sth">1 · Discovery</div>{ul(f["discovery"])}</div>'
            f'<div class="st"><div class="sth">2 · Architecture</div><p>{E(f["architecture"])}</p></div>'
            f'<div class="st"><div class="sth">3 · Implementation</div>{ul(f["implementation"])}</div>'
            f'<div class="st"><div class="sth">4 · Deployment</div><p>{E(f["deployment"])}</p></div>'
            f'<div class="st"><div class="sth">5 · Business outcome</div><p>{E(f["outcome"])}</p></div></div>'
            f'<p class="lesson"><b>Lesson:</b> {E(f["lesson"])}</p>')
    return (f'<article class="card" id="c-{f["id"]}" data-card="{f["id"]}" data-sec="m-scenarios"><header class="ch"><button class="ct" aria-expanded="false"><span class="caret"></span>{E(f["title"])}</button>'
            f'<span class="cm">{lab(f["src"])}<button class="bm" title="Bookmark" aria-label="Bookmark">☆</button><label class="dn"><input type="checkbox"> done</label></span></header><div class="cb">{body}</div></article>')

S['m-scenarios'] = (head('m-scenarios', 'FDE Customer Scenarios', 'Discovery → architecture → implementation → deployment → outcome. Illustrative engagements; no results are claimed.') +
  ''.join(fde_block(f) for f in SD.FDE))

def behav_block(i, b):
    q, struct, looks, draft = b
    bid = f'bh-{i+1}'
    return (f'<article class="card" id="c-{bid}" data-card="{bid}" data-sec="m-behav"><header class="ch"><button class="ct" aria-expanded="false"><span class="caret"></span>{E(q)}</button>'
            f'<span class="cm"><button class="bm" title="Bookmark" aria-label="Bookmark">☆</button><label class="dn"><input type="checkbox"> done</label></span></header>'
            f'<div class="cb"><div class="blk"><div class="bh">Answer structure</div><p>{E(struct)}</p></div>'
            f'<div class="blk"><div class="bh">What SAP is likely looking for {lab("INFER")}</div><p>{E(looks)}</p></div>'
            f'<div class="blk ans"><div class="bh">Draft</div><p>{hl(draft)}</p></div></div></article>')

def hl(s):
    """escape, then highlight [INSERT …] / [USER INPUT …] placeholders and DRAFT markers"""
    import re
    s = E(s)
    s = re.sub(r'\[(INSERT[^\]]*|USER INPUT[^\]]*|Illustrative[^\]]*)\]', r'<mark class="ph">[\1]</mark>', s)
    return s.replace('DRAFT — personalise.', '<span class="lab lab-gap">DRAFT — PERSONALISE</span>')

S['m-behav'] = (head('m-behav', 'Behavioral', 'Thirteen likely questions. Drafts use only facts from your resume; every story detail is yours to fill in.') +
  note('warn', 'Fill the placeholders before the interview', Raw('<p>Highlighted <mark class="ph">[INSERT …]</mark> markers are deliberate. A behavioural answer with invented detail falls apart on the first follow-up.</p>')) +
  ''.join(behav_block(i, b) for i, b in enumerate(B.BEHAV)))

S['m-exp'] = (head('m-exp', 'How to Position My Atlassian Experience for SAP', 'Your experience → the SAP requirement it answers → how to say it.') +
  table(['My experience', 'SAP requirement', 'How to explain it', 'Basis'], [(a, b, Raw(hl(c)), Raw(lab(s))) for a, b, c, s in B.EXPERIENCE]) +
  note('info', 'The positioning in one sentence', Raw('<p>"I have spent sixteen years building the platforms enterprise data flows through — event pipelines that must count exactly once, isolation boundaries for regulated customers, a gateway at 76K QPS — and I now evaluate AI output for a living. This role combines those: governed data foundations that agents can safely run on, built inside the customer\'s landscape."</p>')))

def qrow(i, q):
    if q[3]:
        c = BYID[q[3]]; short, detail, senior, fu, mis = c['a15'], c['a30'], c['a2m'], c['fu'], c['mistake']
    else:
        short, detail, senior, fu, mis = q[4], q[5], q[6], q[7], q[8]
    qid = f'q-{i+1}'
    return (f'<article class="card qcard" id="c-{qid}" data-card="{qid}" data-sec="m-qbank" data-tier="{q[1]}"><header class="ch"><button class="ct" aria-expanded="false"><span class="caret"></span>{E(q[0])}</button>'
            f'<span class="cm">{prio(q[1])}<button class="bm" title="Bookmark" aria-label="Bookmark">☆</button><label class="dn"><input type="checkbox"> done</label></span></header>'
            f'<div class="cb"><div class="blk"><div class="bh">Short answer</div><p>{E(short)}</p></div>'
            f'<div class="blk"><div class="bh">Detailed answer</div><p>{E(detail)}</p></div>'
            f'<div class="blk ans"><div class="bh">Senior-level answer</div><p>{E(senior)}</p></div>'
            f'<details class="blk fu"><summary class="bh">Follow-up: {E(fu[0])}</summary><p>{E(fu[1])}</p></details>'
            f'<div class="blk mis"><div class="bh">Common mistake</div><p>{E(mis)}</p></div>'
            + (f'<p class="muted">Studied in <a href="#{q[2]}">{E(dict((x[0], x[1]) for x in SECTIONS)[q[2]])}</a></p>') + '</div></article>')

counts = {t: sum(1 for q in B.QBANK if q[1] == t) for t in PRIO}
S['m-qbank'] = (head('m-qbank', 'Interview Question Bank', 'Likely questions based on the job description — not a list SAP is known to use.') +
  '<div class="qf"><input id="qfilter" type="search" placeholder="Filter questions…" aria-label="Filter questions">' +
  ''.join(f'<label class="qt"><input type="checkbox" data-tier="{t}" checked> {PRIO[t][1]} ({counts[t]})</label>' for t in PRIO) + '</div>' +
  ''.join(qrow(i, q) for i, q in enumerate(B.QBANK)))

top20 = [q[0] for q in B.QBANK if q[1] == 'must'][:20]
S['m-final'] = (head('m-final', 'Final Revision — 30 minutes before the interview', 'Read top to bottom once. Then open the one-screen cheat sheet.') +
  '<button class="btn" data-open-cheat>Open the one-screen cheat sheet</button>' +
  '<div class="grid2">' +
  f'<div class="pane"><h3>10 concepts</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_CONCEPTS)}</ol></div>' +
  f'<div class="pane"><h3>10 architecture patterns</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_PATTERNS)}</ol></div>' +
  f'<div class="pane"><h3>10 AI concepts</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_AI)}</ol></div>' +
  f'<div class="pane"><h3>10 data-engineering rules</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_DE)}</ol></div>' +
  f'<div class="pane"><h3>5 FDE principles</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_FDE)}</ol></div>' +
  f'<div class="pane"><h3>5 mistakes to avoid</h3><ol>{"".join(f"<li>{E(x)}</li>" for x in B.REV_MISTAKES)}</ol></div></div>' +
  f'<h2>20 questions to be able to answer</h2><ol class="cols2">{"".join(f"<li>{E(x)}</li>" for x in top20)}</ol>' +
  '<h2>Your openers</h2>' +
  ''.join(f'<div class="pt"><div class="pth">{E(q)}</div><p>{hl(d)}</p></div>' for q, _, _, d in B.BEHAV[:4]))

# ------------------------------------------------------------------ cheat sheet overlay
CHEAT = (
 '<div id="cheat" class="ov" hidden><div class="ovp" role="dialog" aria-label="Cheat sheet"><button class="x" data-close-cheat aria-label="Close">×</button>'
 '<h2>Open this right before the interview</h2><div class="cs">'
 '<div><h4>Definitions</h4><ul>'
 '<li><b>Parquet</b> = columnar file. <b>Delta</b> = Parquet + transaction log (ACID, MERGE, time travel).</li>'
 '<li><b>Lakehouse</b> = warehouse guarantees on open lake files.</li>'
 '<li><b>Spark</b>: driver plans; executors run tasks; stages split at shuffles.</li>'
 '<li><b>Shuffle</b> is the cost → filter early, broadcast small, salt hot keys.</li>'
 '<li><b>Airflow orchestrates. Spark processes.</b></li>'
 '<li><b>Kafka → Structured Streaming → Delta</b>, checkpoint = exactly-once.</li>'
 '<li><b>ROW_NUMBER</b> dedup · <b>DENSE_RANK</b> top-N with ties · <b>LAG</b> change.</li></ul></div>'
 '<div><h4>AI</h4><ul><li>LLM → RAG → agent: simplest that works.</li><li>ACL at retrieval; tools run as the user.</li><li>Writes need approval + audit.</li><li>Evaluate: model, retrieval, system, safety, business.</li><li>Retrieved text is untrusted (injection).</li></ul>'
 '<h4>FDE</h4><ul><li>Discovery before architecture.</li><li>Thin slice on real data, early.</li><li>Agreed business metric.</li><li>Trust via reconciliation.</li><li>Leave reusable patterns.</li></ul></div>'
 '<div><h4>Never</h4><ul><li>Claim hands-on PySpark / Databricks / HANA you do not have.</li><li>Invent SAP product facts — "I would verify against SAP\'s current docs."</li><li>Append on retry.</li><li>Agent where a workflow will do.</li></ul>'
 '<h4>Your line</h4><p>"Sixteen years building the platforms enterprise data flows through — exactly-once billing events, isolation for regulated customers, a 76K QPS gateway — and I now evaluate AI output for a living."</p></div>'
 '</div></div></div>')

# ------------------------------------------------------------------ search index
IDX = []
for sid, t, g in SECTIONS: IDX.append(dict(k='Section', t=t, h=sid, x=g))
for c in CARDS: IDX.append(dict(k='Concept', t=c['title'], h=c['mod'], c=c['id'], x=c['what'][:140]))
for d in SD.DESIGNS: IDX.append(dict(k='Design', t=d['title'], h='m-design', c=d['id'], x=d['problem'][:140]))
for f in SD.FDE: IDX.append(dict(k='Scenario', t=f['title'], h='m-scenarios', c=f['id'], x=f['context'][:140]))
for i, b in enumerate(B.BEHAV): IDX.append(dict(k='Behavioral', t=b[0], h='m-behav', c=f'bh-{i+1}', x=b[1]))
for i, q in enumerate(B.QBANK): IDX.append(dict(k='Question', t=q[0], h='m-qbank', c=f'q-{i+1}', x=PRIO[q[1]][1]))

# ------------------------------------------------------------------ page
def nav():
    out, grp = [], None
    for i, (sid, t, g) in enumerate(SECTIONS):
        if g != grp:
            out.append(f'<div class="ng">{E(g)}</div>'); grp = g
        out.append(f'<a class="nl" href="#{sid}" data-sec="{sid}"><span class="nn">{i+1}</span><span class="nt2">{E(t)}</span><span class="np" data-np="{sid}"></span></a>')
    return ''.join(out)

CSS = open(os.path.join(HERE, 'sap.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'sap.js'), encoding='utf-8').read()

def build():
    secs = ''.join(f'<section class="sec" id="{sid}" data-title="{E(t)}" hidden>{S[sid]}'
                   f'<div class="pager">{pager(i)}</div></section>' for i, (sid, t, g) in enumerate(SECTIONS))
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SAP Labs FDE Prep</title>
<meta name="description" content="Study guide for SAP Labs — Forward Deployed Data Engineering Expert (Req. 458124)">
<style>{CSS}</style></head>
<body>
<header class="top">
  <button id="navbtn" class="ib" aria-label="Toggle navigation">☰</button>
  <a class="brand" href="../index.html" title="All companies">Companies</a><span class="crumb">/ SAP Labs · FDE Data Engineering Expert</span>
  <button id="searchbtn" class="sb" aria-label="Search">Search <kbd>/</kbd></button>
  <div class="ctl">
    <div class="seg" role="group" aria-label="Depth"><button data-d="1">Simple</button><button data-d="2">Intermediate</button><button data-d="3">Expert</button></div>
    <label class="tg"><input type="checkbox" id="be"> Backend Engineer Mode</label>
    <label class="tg"><input type="checkbox" id="im"> Interview Answer Mode</label>
    <button class="btn sm" data-open-cheat>Open before interview</button>
  </div>
  <div class="prog" title="Concepts done"><div class="pb"><div class="pf" id="pf"></div></div><span id="pt">0%</span></div>
</header>
<nav id="side" aria-label="Sections"><div class="bmk"><div class="ng">Bookmarks</div><div id="bml" class="bml"><span class="muted">None yet — star a concept.</span></div></div>{nav()}</nav>
<div id="backdrop"></div>
<main id="main">{secs}</main>
<div id="sr" class="ov" hidden><div class="ovp srp" role="dialog" aria-label="Search"><input id="sq" type="search" placeholder="Search concepts, questions, sections…" autocomplete="off" aria-label="Search"><div id="sres"></div><div class="muted sm">Enter opens · ↑↓ move · Esc closes</div></div></div>
{CHEAT}
<script>var IDX={json.dumps(IDX, ensure_ascii=False)};</script>
<script>{JS}</script>
</body></html>'''
    open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote', os.path.relpath(OUT), f'{len(html)/1024:.0f} KB', len(CARDS), 'concepts,', len(B.QBANK), 'questions')

def pager(i):
    p = SECTIONS[i - 1] if i > 0 else None
    n = SECTIONS[i + 1] if i + 1 < len(SECTIONS) else None
    a = f'<a href="#{p[0]}">← {E(p[1])}</a>' if p else '<span></span>'
    b = f'<a href="#{n[0]}">{E(n[1])} →</a>' if n else '<span></span>'
    return a + b

if __name__ == '__main__':
    build()
