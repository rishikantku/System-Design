# -*- coding: utf-8 -*-
"""Tiny box-and-arrow SVG builder. Colours come from CSS variables so diagrams follow the theme."""
from html import escape as E

_N = [0]

class D:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.parts = w, h, title, []
        _N[0] += 1; self.uid = f'd{_N[0]}'

    def box(self, x, y, w, h, label, sub=None, kind='n'):
        self.parts.append(f'<rect class="b-{kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>')
        cy = y + h / 2 + (-6 if sub else 4)
        self.parts.append(f'<text class="t-l" x="{x + w/2}" y="{cy}" text-anchor="middle">{E(label)}</text>')
        if sub:
            for i, line in enumerate(sub.split('\n')):
                self.parts.append(f'<text class="t-s" x="{x + w/2}" y="{cy + 15 + i*13}" text-anchor="middle">{E(line)}</text>')
        return (x, y, w, h)

    def zone(self, x, y, w, h, label):
        self.parts.append(f'<rect class="z" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>')
        self.parts.append(f'<text class="t-z" x="{x + 8}" y="{y + 15}">{E(label)}</text>')

    def text(self, x, y, s, cls='t-s', anchor='start'):
        self.parts.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{E(s)}</text>')

    def arrow(self, x1, y1, x2, y2, label=None, kind='a', lx=None, ly=None):
        self.parts.append(f'<line class="l-{kind}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#{self.uid}-{kind})"/>')
        if label:
            lx = (x1 + x2) / 2 if lx is None else lx
            ly = (y1 + y2) / 2 - 5 if ly is None else ly
            self.parts.append(f'<text class="t-a" x="{lx}" y="{ly}" text-anchor="middle">{E(label)}</text>')

    def right(self, a, b, label=None, kind='a'):
        """arrow from right edge of box a to left edge of box b, at a's vertical centre"""
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        y = ay + ah / 2
        self.arrow(ax + aw, y, bx - 2, by + bh / 2 if abs((by + bh/2) - y) > 1 else y, label, kind)

    def down(self, a, b, label=None, kind='a'):
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        self.arrow(ax + aw / 2, ay + ah, bx + bw / 2, by - 2, label, kind, lx=ax + aw/2 + 6, ly=(ay+ah+by)/2 + 4)

    def render(self, cap=None, verify=False):
        defs = ''.join(f'<marker id="{self.uid}-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path class="m-{k}" d="M0,0 L10,5 L0,10 z"/></marker>' for k in ('a', 'h', 'x'))
        svg = (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{E(self.title)}" preserveAspectRatio="xMidYMid meet">'
               f'<defs>{defs}</defs>{"".join(self.parts)}</svg>')
        tag = '<span class="lab lab-verify">VERIFY</span> ' if verify else ''
        c = f'<figcaption>{tag}{E(cap)}</figcaption>' if cap else ''
        return f'<figure class="dg"><div class="dg-t">{E(self.title)}</div><div class="dg-s">{svg}</div>{c}</figure>'


def row(d, x0, y, labels, w=120, h=52, gap=36, kinds=None, subs=None, arrows=True, alabels=None):
    out = []
    for i, lab in enumerate(labels):
        k = kinds[i] if kinds else 'n'
        s = subs[i] if subs else None
        out.append(d.box(x0 + i * (w + gap), y, w, h, lab, s, k))
    if arrows:
        for i in range(len(out) - 1):
            d.right(out[i], out[i + 1], alabels[i] if alabels else None)
    return out


# ------------------------------------------------------------------ the diagrams
def pipeline():
    d = D(860, 150, 'A data pipeline, end to end')
    row(d, 10, 50, ['Sources', 'Ingest', 'Land raw', 'Transform', 'Serve'], w=140, gap=36,
        subs=['ERP · CRM · events', 'batch pull / CDC', 'bronze, unchanged', 'silver → gold', 'BI · ML · agents'],
        kinds=['s', 'n', 'b', 'n', 'g'])
    d.text(430, 135, 'every stage: idempotent · observable · safe to re-run', 't-n', 'middle')
    return d.render('Same shape as a service chain — the unit of work is a dataset, and correctness is measured on the data.')

def etl_elt():
    d = D(860, 210, 'ETL vs ELT')
    d.text(10, 30, 'ETL', 't-h')
    row(d, 70, 10, ['Extract', 'Transform', 'Load'], w=150, h=40, gap=100, subs=None, kinds=['s', 'h', 'g'], alabels=['', 'only results'])
    d.text(732, 35, 'raw data is not kept', 't-n')
    d.text(10, 130, 'ELT', 't-h')
    row(d, 70, 110, ['Extract', 'Load raw', 'Transform in platform'], w=150, h=40, gap=100, kinds=['s', 'b', 'h'])
    d.text(70, 185, 'raw kept → replay when business logic changes · but the raw zone holds PII → restrict or tokenise at ingestion', 't-n')
    return d.render('ELT is the lakehouse default; light ETL at the edge is still right for data that must never be stored raw.')

def medallion():
    d = D(880, 230, 'Medallion lakehouse')
    src = [d.box(10, 20 + i * 50, 120, 38, s, None, 's') for i, s in enumerate(['SAP ERP', 'CRM', 'Kafka events', 'Files'])]
    br = d.box(200, 60, 140, 110, 'Bronze', 'raw, as arrived\n+ load metadata\nrestricted', 'b')
    sv = d.box(430, 60, 140, 110, 'Silver', 'typed, deduped\nconformed keys\nPII tokenised', 'n')
    gd = d.box(660, 60, 120, 110, 'Gold', 'stars, aggregates\ndata products\nreconciled', 'g')
    for s in src: d.arrow(130, s[1] + 19, 198, 115)
    d.right(br, sv, 'quality gate'); d.right(sv, gd, 'quality gate')
    for i, c in enumerate(['BI', 'ML', 'AI agents']):
        b = d.box(810, 50 + i * 45, 66, 34, c, None, 'g')
        d.arrow(780, 115, 808, b[1] + 17)
    d.text(440, 215, 'catalogue · lineage · access policies span every layer', 't-n', 'middle')
    return d.render('Each layer can be rebuilt from the one below — keep transforms idempotent.')

def csv_parquet():
    d = D(860, 250, 'CSV (row) vs Parquet (column)')
    cols = ['id', 'date', 'region', 'amount']
    d.text(20, 25, 'CSV — rows stored together', 't-h')
    for r in range(4):
        for c, name in enumerate(cols):
            d.parts.append(f'<rect class="b-{"h" if c == 3 else "n"}" x="{20 + c*85}" y="{40 + r*34}" width="80" height="28" rx="2"/>')
            d.text(60 + c*85, 58 + r*34, f'{name} {r+1}', 't-s', 'middle')
    d.text(20, 195, 'SUM(amount) must read every row, every field', 't-n')
    d.text(470, 25, 'Parquet — columns stored together', 't-h')
    for c, name in enumerate(cols):
        hit = c == 3
        d.parts.append(f'<rect class="b-{"g" if hit else "x"}" x="{470 + c*95}" y="40" width="85" height="130" rx="2"/>')
        d.text(512 + c*95, 60, name, 't-l', 'middle')
        for r in range(4): d.text(512 + c*95, 85 + r*22, f'{name} {r+1}', 't-s', 'middle')
    d.text(470, 195, 'SUM(amount) reads one column chunk', 't-n')
    d.text(470, 213, 'footer min/max statistics skip whole row groups', 't-n')
    d.text(470, 231, 'same-type neighbours compress far better', 't-n')
    return d.render('Column pruning + predicate pushdown + partition pruning = read a small fraction of the data.')

def delta_log():
    d = D(880, 240, 'Delta Lake = Parquet files + a transaction log')
    d.zone(10, 10, 400, 220, '_delta_log/')
    a = d.box(25, 35, 370, 44, '00000.json', 'add part-1.parquet, add part-2.parquet  (create)', 'n')
    b = d.box(25, 95, 370, 44, '00001.json', 'add part-3.parquet  (append)', 'n')
    c = d.box(25, 155, 370, 44, '00002.json', 'remove part-1, add part-4  (MERGE rewrote one file)', 'h')
    d.zone(450, 10, 420, 220, 'table data (Parquet, immutable)')
    for i, (f, k) in enumerate([('part-1', 'x'), ('part-2', 'g'), ('part-3', 'g'), ('part-4', 'g')]):
        d.box(470 + i * 98, 45, 86, 40, f + '.parquet' if False else f, None, k)
    d.text(470, 120, 'Reader at version 2 sees: part-2, part-3, part-4', 't-l')
    d.text(470, 145, 'Reader at version 1 (time travel): part-1, part-2, part-3', 't-s')
    d.text(470, 170, 'Commit = atomically write the next N.json (optimistic concurrency)', 't-s')
    d.text(470, 195, 'VACUUM deletes part-1 after retention → time travel ends there', 't-s')
    return d.render('The log, not the folder listing, defines the table — that is what makes writes atomic and history queryable.')

def spark_arch():
    d = D(880, 290, 'Spark architecture')
    drv = d.box(20, 95, 170, 80, 'Driver', 'your program\nplan → stages → tasks', 'h')
    cm = d.box(260, 15, 170, 50, 'Cluster manager', 'YARN · K8s · Databricks', 's')
    d.arrow(105, 95, 300, 67, 'request executors')
    for i in range(3):
        y = 85 + i * 62
        d.zone(300, y, 560, 52, f'Executor {i+1}  (JVM on a worker)')
        for t in range(4):
            d.box(490 + t * 92, y + 12, 82, 32, f'task p{i*4+t}', None, 'n')
        d.arrow(190, 135, 298, y + 26)
    d.text(20, 282, 'one task = one partition × one stage · each core runs one task at a time', 't-n')
    return d.render('Horizontal scaling for data: a coordinator plans; long-lived workers process partitions in parallel.')

def shuffle():
    d = D(860, 260, 'Narrow vs wide — the shuffle')
    d.text(20, 22, 'Stage 1 (narrow: read, filter)', 't-h')
    d.text(560, 22, 'Stage 2 (after groupBy region)', 't-h')
    m = [d.box(20, 40 + i * 52, 170, 40, f'partition {i}', 'EU · US · APAC rows', 'n') for i in range(4)]
    r = [d.box(600, 50 + i * 65, 200, 46, f'reducer: {k}', 'all rows for this key', 'g') for i, k in enumerate(['EU', 'US', 'APAC'])]
    for a in m:
        for b in r:
            d.arrow(190, a[1] + 20, 598, b[1] + 23, kind='x')
    d.text(395, 250, 'shuffle = write to local disk → send over network → read back · creates a stage boundary', 't-n', 'middle')
    return d.render('Same operation as re-keying a Kafka topic — and the same costs: serialization, network, disk, and skew if one key is hot.')

def airflow_dag():
    d = D(880, 170, 'An Airflow DAG')
    bs = row(d, 10, 45, ['wait_for_extract', 'ingest_bronze', 'build_silver', 'quality_check', 'build_gold', 'notify'], w=118, h=50, gap=27,
             subs=['FileSensor', 'Databricks job', 'Databricks job', 'blocks on fail', 'Databricks job', 'Slack / mail'],
             kinds=['s', 'n', 'n', 'h', 'g', 'n'])
    d.text(10, 130, 'Airflow decides when and in what order, retries, backfills. Spark/Databricks does the processing.', 't-n')
    d.text(10, 150, 'Each task processes {{ ds }} and overwrites that partition → retries and backfills are safe.', 't-n')
    return d.render('Airflow orchestrates. Spark processes.')

def kafka_flow():
    d = D(880, 220, 'Kafka → Spark → Delta')
    src = [d.box(10, 20 + i * 60, 120, 44, s, sub, 's') for i, (s, sub) in enumerate([('Orders DB', 'CDC (Debezium)'), ('Apps', 'events'), ('IoT', 'telemetry')])]
    k = d.box(190, 40, 140, 120, 'Kafka', 'topics keyed by\nbusiness key\nretention = replay', 'n')
    for s in src: d.arrow(130, s[1] + 22, 188, 100)
    ss = d.box(390, 40, 170, 120, 'Structured Streaming', 'dedup · windows\nwatermarks\ncheckpoint = offsets', 'h')
    d.right(k, ss)
    b = d.box(620, 30, 110, 44, 'Bronze', None, 'b'); s2 = d.box(620, 88, 110, 44, 'Silver (MERGE)', None, 'n'); g = d.box(620, 146, 110, 44, 'Gold', None, 'g')
    for t in (b, s2, g): d.arrow(560, 100, 618, t[1] + 22)
    d.box(760, 88, 110, 44, 'BI / agents', None, 'g'); d.arrow(730, 168, 815, 134)
    d.text(10, 210, 'checkpointed offsets + Delta atomic commit ⇒ each event lands exactly once · consumer lag = freshness SLO', 't-n')
    return d.render('Your Kafka experience, reframed: the consumer is a pipeline and correctness is "every event exactly once in the table".')

def hana():
    d = D(860, 230, 'SAP HANA in an enterprise landscape (simplified)')
    app = d.box(20, 20, 220, 50, 'S/4HANA applications', 'finance · supply chain · sales', 's')
    d.zone(20, 90, 220, 120, 'SAP HANA')
    d.box(35, 115, 90, 40, 'column store', None, 'g'); d.box(135, 115, 90, 40, 'in-memory', None, 'n')
    d.text(130, 185, 'OLTP + OLAP on one copy', 't-s', 'middle')
    d.arrow(130, 70, 130, 88)
    ex = d.box(330, 100, 200, 60, 'SAP-supported extraction', 'semantics preserved', 'h')
    d.arrow(240, 130, 328, 130)
    lk = d.box(620, 100, 220, 60, 'Lakehouse', 'joined with non-SAP data', 'g')
    d.right(ex, lk)
    d.text(430, 205, 'Which extraction or sharing mechanism applies depends on the landscape and licence — verify.', 't-n', 'middle')
    return d.render('Interview-safe: know the idea (in-memory columnar, HTAP) and the integration questions; do not claim hands-on use.', verify=True)

def llm_rag_agent():
    d = D(880, 250, 'LLM vs RAG vs Agent')
    xs = [10, 300, 590]
    heads = [('LLM', 'answers from training'), ('RAG', 'retrieve, then answer'), ('Agent', 'plan, call tools, act')]
    for x, (h, s) in zip(xs, heads):
        d.zone(x, 10, 280, 230, f'{h} — {s}')
    q = d.box(30, 45, 240, 36, 'question', None, 's'); m = d.box(30, 115, 240, 36, 'model', None, 'n'); a = d.box(30, 185, 240, 36, 'answer (may invent specifics)', None, 'x')
    d.down(q, m); d.down(m, a)
    q = d.box(320, 40, 240, 32, 'question', None, 's'); r = d.box(320, 92, 240, 32, 'retrieve permitted sources', None, 'h'); m = d.box(320, 144, 240, 32, 'model + sources', None, 'n'); a = d.box(320, 196, 240, 32, 'grounded answer + citations', None, 'g')
    d.down(q, r); d.down(r, m); d.down(m, a)
    g = d.box(610, 40, 240, 32, 'goal', None, 's'); p = d.box(610, 92, 240, 32, 'plan next step', None, 'n'); t = d.box(610, 144, 240, 32, 'call tool (query · API · RAG)', None, 'h'); o = d.box(610, 196, 240, 32, 'observe → repeat or finish', None, 'g')
    d.down(g, p); d.down(p, t); d.down(t, o)
    d.parts.append(f'<path class="l-a" d="M 850 212 C 872 212, 872 108, 852 108" fill="none" marker-end="url(#{d.uid}-a)"/>')
    return d.render('Capability, risk and evaluation cost all rise left to right — pick the simplest that solves the problem.')

def rag():
    d = D(880, 260, 'RAG — two pipelines')
    d.text(10, 22, 'Indexing (a data pipeline, incremental)', 't-h')
    row(d, 10, 35, ['Documents', 'Extract', 'Chunk', 'Metadata', 'Embed', 'Index'], w=125, h=44, gap=21,
        subs=['policies · manuals', 'text + clean', 'by structure', 'source · version · ACL', 'vectors', 'vector + keyword'],
        kinds=['s', 'n', 'n', 'h', 'n', 'g'])
    d.text(10, 125, 'Query', 't-h')
    row(d, 10, 138, ['Question', 'Retrieve', 'ACL filter', 'Rerank', 'LLM', 'Answer'], w=125, h=44, gap=21,
        subs=['+ user identity', 'hybrid search', 'user\'s permissions', 'top few chunks', 'only from sources', '+ citations'],
        kinds=['s', 'n', 'h', 'n', 'n', 'g'])
    d.parts.append(f'<path class="l-h" d="M 803 79 L 803 108 L 218 108 L 218 134" fill="none" marker-end="url(#{d.uid}-h)"/>')
    d.text(510, 103, 'search the index', 't-a', 'middle')
    d.text(10, 220, 'Most failures are retrieval failures: bad chunks, missing ACL/version metadata, stale index, no keyword search for IDs.', 't-n')
    d.text(10, 242, 'Structured data is reached through governed SQL tools, not vectors.', 't-n')
    return d.render('Evaluate retrieval (recall@k) separately from generation (faithfulness).')

def ent_ai_stack():
    d = D(880, 300, 'Enterprise AI stack')
    layers = [('Application / user experience', 'chat · embedded in business apps', 's'),
              ('Orchestration', 'workflows + agents · human approval for actions', 'n'),
              ('Model gateway', 'routing · rate limits · redaction · caching · cost', 'h'),
              ('Tools + retrieval', 'typed, least-privilege, user identity propagated', 'n'),
              ('Governed data products', 'catalogue · lineage · row/column policies', 'g'),
              ('Data platform', 'lakehouse (Delta) · streaming · SAP + non-SAP sources', 'b')]
    for i, (l, s, k) in enumerate(layers):
        d.box(20, 10 + i * 47, 600, 40, l, s, k)
    d.zone(650, 10, 220, 276, 'cross-cutting')
    for i, s in enumerate(['security & authz', 'prompt-injection defence', 'observability (traces)', 'evaluation', 'cost & latency budgets', 'audit']):
        d.text(665, 45 + i * 40, '• ' + s, 't-l')
    return d.render('The model is the smallest part; data, identity and evaluation decide whether it can go to production.')

def sap_platform():
    d = D(880, 260, 'An SAP-centred enterprise data platform (illustrative)')
    s1 = d.box(10, 30, 170, 50, 'SAP applications', 'e.g. S/4HANA', 's')
    s2 = d.box(10, 110, 170, 50, 'Non-SAP sources', 'CRM · IoT · files · web', 's')
    p = d.box(250, 40, 260, 110, 'SAP data platform layer', 'e.g. SAP Business Data Cloud,\nDatasphere, SAP Databricks\n(data products, semantics)', 'h')
    d.arrow(180, 55, 248, 80); d.arrow(180, 135, 248, 110)
    lk = d.box(580, 30, 280, 50, 'Lakehouse / ML', 'Spark · Delta · notebooks', 'n')
    ai = d.box(580, 110, 280, 50, 'AI agents and assistants', 'e.g. Joule agents · custom agents', 'g')
    d.arrow(510, 80, 578, 55); d.arrow(510, 115, 578, 135)
    d.text(10, 200, 'FDE work sits here: getting SAP and non-SAP data into governed, AI-ready products inside the customer\'s landscape.', 't-n')
    d.text(10, 222, 'Product names and integration options are from public SAP announcements; scope and availability change — verify before quoting.', 't-n')
    return d.render('Illustrative only. Use it to structure a conversation, not as a product claim.', verify=True)

ALL = dict(pipeline=pipeline, etl_elt=etl_elt, medallion=medallion, csv_parquet=csv_parquet, delta_log=delta_log, spark_arch=spark_arch,
           shuffle=shuffle, airflow_dag=airflow_dag, kafka_flow=kafka_flow, hana=hana, llm_rag_agent=llm_rag_agent, rag=rag,
           ent_ai_stack=ent_ai_stack, sap_platform=sap_platform)
