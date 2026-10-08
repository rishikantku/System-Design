# -*- coding: utf-8 -*-
"""Bridges, comparison tables, behavioural answers, experience mapping, question bank, final revision.

Personal facts come only from the resume (Rishikant.pdf). Anything the reader must supply is a
[INSERT …] placeholder. Motivations (why SAP, why FDE) are drafts to personalise, labelled as such.
"""

# "You already know this" bridges — module 2
BRIDGES = [
 ('Kafka', 'Data-engineering ingestion', 'Topics become the raw landing zone; consumers become pipelines writing Delta tables; replay rebuilds bronze; lag is the freshness SLO.'),
 ('Distributed systems', 'Spark', 'Partitioning, shuffles (re-keying), stragglers (hot shards), recompute-from-log fault tolerance, coordinator (driver) and workers (executors).'),
 ('Databases', 'Warehousing / lakehouse', 'OLTP vs OLAP, row vs column storage, WAL → Delta transaction log, MVCC → snapshot isolation, indexes → partition pruning and file statistics.'),
 ('Microservices', 'Pipelines', 'Service chain → DAG of tasks; API contracts → data contracts; health checks → data-quality checks; idempotency keys → partition overwrite / MERGE.'),
 ('APIs and gateways', 'Agentic AI', 'Tools are typed APIs; the agent loop is a runtime-decided orchestrator; authz, rate limits, tracing and audit are exactly what a model gateway needs.'),
 ('Tenant isolation (Isolated Cloud)', 'Governance and PII', 'Least privilege, data boundaries, controlled egress, policy-driven enforcement — applied to tables, columns, rows and agents.'),
 ('Event-driven billing (Salesforce)', 'Streaming correctness', 'Usage events must count exactly once — the same problem as exactly-once ingestion into a lakehouse.'),
 ('Code evaluation (xAI)', 'LLM evaluation', 'Rubric-based, multi-dimensional evaluation of model output is the core skill of evaluating AI systems in production.'),
]

LAKE_TABLE = [
 ('Data', 'Structured, modelled', 'Anything: structured, semi, unstructured', 'Anything, with tables on top'),
 ('Storage', 'Proprietary / managed', 'Open files on object storage', 'Open files + open table format'),
 ('Transactions', 'Yes', 'No', 'Yes (transaction log)'),
 ('Schema', 'On write', 'On read', 'Enforced on write, evolvable'),
 ('Cost at scale', 'High', 'Low', 'Low–medium'),
 ('Workloads', 'BI / SQL', 'Data science, raw archive', 'BI, ML, streaming, AI on one copy'),
 ('Weakness', 'Cost, lock-in, poor for unstructured/ML', 'Swamps, no ACID, slow without care', 'Needs file-layout discipline and a catalogue'),
]
WHEN_TO_CHOOSE = [
 ('Warehouse', 'Curated, high-concurrency SQL reporting with well-known structure; statutory finance reporting already running there.'),
 ('Lake (alone)', 'Cheap archive of raw data, exploratory data science — rarely the end state today.'),
 ('Lakehouse', 'Mixed workloads (BI + ML + streaming + AI) over diverse data, open formats, one governed copy — the default for new enterprise platforms.'),
]
CSV_PARQUET = [
 ('Layout', 'Row', 'Column'), ('Types', 'Text, untyped', 'Typed, schema in footer'), ('Compression', 'Poor (or whole-file gzip)', 'Per-column encoding + codec, typically several× smaller'),
 ('Read one column', 'Parse every byte', 'Read only that column'), ('Skip data', 'No', 'Row-group statistics, partition pruning'), ('Splittable for parallel read', 'Only uncompressed', 'Yes, by row group'),
]
PARQUET_DELTA = [
 ('What it is', 'File format', 'Table format (Parquet + transaction log)'), ('ACID', 'No', 'Yes'), ('Update / delete / MERGE', 'No (rewrite manually)', 'Yes'),
 ('Schema enforcement', 'Per file only', 'Table-level, with evolution'), ('Time travel / audit', 'No', 'Yes, bounded by VACUUM'), ('Concurrent writers', 'Unsafe', 'Optimistic concurrency'),
 ('Streaming sink', 'Risky', 'Exactly-once with checkpoints'),
]
SPARK_QUICK = [
 ('Driver', 'Plans and schedules', 'Coordinator / control plane'), ('Executor', 'Runs tasks, caches, writes shuffle', 'Worker instance'), ('Cluster manager', 'Allocates executors', 'Autoscaler / scheduler'),
 ('Partition', 'Slice of data', 'Shard'), ('Task', 'One partition × one stage', 'One unit of work on one shard'), ('Stage', 'Tasks between shuffles', 'A pipeline step without a network hop'),
 ('Job', 'Triggered by one action', 'One request through the system'), ('Shuffle', 'Redistribute by key', 'Re-keying a Kafka topic'), ('Broadcast', 'Copy small table to all executors', 'Local reference cache'),
 ('Skew', 'Hot key overloads one task', 'Hot shard'), ('Lineage', 'Recipe to recompute', 'Replay from log'),
]

# Behavioural — 13 questions. structure, looks_for (INFER), draft built from resume facts + placeholders.
BEHAV = [
 ('Tell me about yourself (90 seconds)', 'Present → past highlights relevant to the role → why this role now', 'Clarity, relevance to data + AI + customers, seniority without arrogance',
  'I am a principal-level engineer with 16+ years building distributed systems and platforms — at xAI, Atlassian, Salesforce, Microsoft and Adobe. At Atlassian I architected and drove rollout of the cross-product GraphQL Gateway at about 76K QPS, and led the architecture of Isolated Cloud — tenant isolation for regulated enterprise customers. At Salesforce I led consumption-based billing on Kafka and DynamoDB, where every usage event had to count exactly once. Today at xAI I evaluate AI-generated code for correctness, security and production readiness. What connects these is building reliable platforms for enterprise data, and judging AI output critically. [INSERT ONE SENTENCE ON YOUR DATA-ENGINEERING HANDS-ON WORK, IF ANY]. This role puts that together: embedded with customers, building data foundations that AI agents can safely run on.'),
 ('Why SAP?', 'Specific → personal → forward-looking', 'Understanding that SAP holds the core business data of large enterprises; genuine interest',
  'DRAFT — personalise. Most large enterprises run their core processes on SAP, so the data that matters for business AI — orders, finance, supply chain — sits there. Agentic AI only works on that data if someone builds the governed foundation inside the customer\'s landscape. [INSERT YOUR OWN REASON: a customer conversation, an SAP product you have seen, a person, location].'),
 ('Why Forward Deployed Engineering?', 'What you enjoy → evidence you have done it → why now', 'Comfort with customers and ambiguity; bias to ship',
  'DRAFT — personalise. The work I enjoyed most was closest to customers with hard constraints: Isolated Cloud was driven by regulated enterprises\' compliance needs, and billing at Salesforce was about how enterprise customers are charged. [INSERT A MOMENT WHERE WORKING DIRECTLY WITH A CUSTOMER CHANGED YOUR DESIGN]. FDE puts that at the centre: ship in the customer\'s environment, then turn it into reusable patterns.'),
 ('Why move from Principal Engineering to this role?', 'Not a step down — a different lever; honest about the move', 'Motivation stability; humility; will you stay hands-on?',
  'DRAFT — personalise. At principal level my impact was through platform strategy and architecture across many teams. I want to be closer to where value is realised — real customer data, real processes — and data plus AI is where that is happening. I stay hands-on: [INSERT RECENT HANDS-ON EXAMPLE]. My breadth helps in an FDE role because the first weeks with a customer are architecture decisions under ambiguity.'),
 ('Tell me about a time you worked directly with a customer', 'STAR, with customer\'s words, your action, measurable result', 'Listening, translating needs into technical solutions',
  '[INSERT YOUR ATLASSIAN EXAMPLE — e.g., a regulated enterprise customer whose compliance requirements shaped Isolated Cloud. State: what they needed, what you asked, what you changed in the design, what happened.]'),
 ('Describe a project with very ambiguous requirements', 'How you created clarity: questions, prototypes, decisions written down', 'Structured discovery; decisive under uncertainty',
  '[INSERT YOUR ATLASSIAN EXAMPLE — Isolated Cloud is a natural candidate: define what "isolation" had to guarantee before choosing architecture.] Make the method explicit: who you talked to, what you wrote down, what you decided to defer.'),
 ('Tell me about a time you influenced without authority', 'Context → resistance → how you built agreement → outcome', 'Staff-level influence across teams',
  'Candidate story from the resume: establishing GraphQL as the standardized integration layer across Atlassian services, partnering with product and infrastructure teams. [INSERT: who resisted, why, what evidence or compromise changed minds, adoption result.]'),
 ('Tell me about a failure', 'Own it → what you learned → what you changed', 'Self-awareness, accountability',
  '[INSERT A REAL FAILURE — a production incident, a wrong design call, a missed deadline. Do not invent one. End with the mechanism you put in place afterwards.]'),
 ('Delivering fast under pressure', 'Constraint → what you cut and why → result', 'Pragmatism — FDEs ship',
  'Candidate story: Bing Shopping Black Friday / Cyber Monday campaigns — fixed date, high traffic. [INSERT: what you de-scoped, how you managed risk, how it performed.]'),
 ('Learning an unfamiliar technology quickly', 'What, how, how fast, what you shipped', 'Ability to ramp on Spark / Databricks / SAP',
  '[INSERT YOUR EXAMPLE.] Also say how you are ramping on the data stack for this role: what you built to learn Spark/Delta/Airflow, honestly scoped.'),
 ('Disagreement on a technical decision', 'Both positions fairly → data → resolution → relationship after', 'Respectful conflict; disagree-and-commit',
  '[INSERT YOUR ATLASSIAN EXAMPLE — a gateway or isolation architecture decision.]'),
 ('Mentoring or growing others', 'Who, what you did, how they grew', 'Expert-level role includes raising others',
  'Candidate context: Sell Side Design Squad at Compass — architecture reviews and technical standards. [INSERT A NAMED PERSON YOU GREW AND HOW.]'),
 ('Handling a dissatisfied stakeholder or customer', 'Listen → acknowledge → plan → follow through', 'Composure and ownership in customer-facing work',
  '[INSERT YOUR EXAMPLE — an escalation from an enterprise customer or internal product team.]'),
]

# My experience → SAP requirement → how to explain. Only resume facts.
EXPERIENCE = [
 ('Salesforce — consumption-based billing on Kafka + DynamoDB', 'Real-time pipelines, Kafka, data correctness', 'Usage events had to be counted exactly once and turned into money — the same correctness problem as streaming ingestion into a lakehouse: idempotency, ordering, reconciliation.', 'RESUME'),
 ('Atlassian — Isolated Cloud (tenant isolation for regulated enterprises)', 'Governance, compliance, PII protection', 'I designed data and compliance boundaries for regulated customers: least privilege, controlled egress, policy-driven enforcement. In a lakehouse those become access policies, masking and residency.', 'RESUME'),
 ('Atlassian — cross-product GraphQL Gateway ~76K QPS', 'Scalable architecture; enterprise AI platform', 'One governed entry point with identity, limits and observability in front of many backends — the same shape as a model gateway and a governed tool layer for agents.', 'RESUME'),
 ('Atlassian — AI features with LLM orchestration + RAG (LangChain, GitHub API)', 'Agentic AI context', 'Designed retrieval-grounded AI features; know chunking, retrieval and orchestration trade-offs first-hand.', 'RESUME'),
 ('xAI — expert evaluation of AI-generated code', 'Responsible use of AI agents; evaluation', 'Daily work is rubric-based evaluation and failure analysis of model and coding-agent output — directly transferable to evaluating agents in business processes.', 'RESUME'),
 ('Atlassian — platform strategy; GraphQL as standard integration layer', 'Embedding in customer teams; influence', 'Driving adoption across many teams is the internal version of embedding with a customer\'s teams.', 'RESUME'),
 ('Compass — reusable 3P platform; design squad', 'Reusable patterns from engagements', 'Turned repeated work into a reusable platform — exactly how an FDE turns engagements into templates.', 'RESUME'),
 ('Microsoft Bing Shopping — Black Friday/Cyber Monday scale', 'Scale and reliability', 'Designed for peak seasonal traffic; capacity planning and degradation.', 'RESUME'),
 ('Python, SQL, Docker, CI/CD, AWS', 'Python, SQL, Docker, Git, CI/CD', 'Listed on the resume; mention data-specific CI (tests on data).', 'RESUME'),
 ('PySpark / Databricks / Airflow / SAP HANA hands-on', 'JD: "Hands-on experience with PySpark, Databricks…"', '[USER INPUT REQUIRED — the resume does not list these. If you have hands-on use, state it precisely. If not, say so and show depth of understanding plus the equivalent systems you built.]', 'GAP'),
 ('6+ years data engineering', 'JD: "6+ years experience in data engineering"', '[USER INPUT REQUIRED — frame which roles involved data pipelines (billing events, gateway telemetry, etc.) honestly. Do not stretch.]', 'GAP'),
]

# Question bank. Card-linked rows pull short/detail/senior/followup/mistake from the card.
# (question, tier, module, card_id)  or  (question, tier, module, None, short, detail, senior, (fu_q, fu_a), mistake)
QBANK = [
 ('Explain the difference between ETL and ELT.', 'must', 'm-de', 'etl-elt'),
 ('Batch vs streaming — how do you choose?', 'must', 'm-de', 'batch-stream'),
 ('What is CDC and how would you use it?', 'must', 'm-de', 'cdc'),
 ('How do you design an idempotent pipeline?', 'must', 'm-de', 'pipeline'),
 ('Data lake vs warehouse vs lakehouse?', 'must', 'm-lakehouse', 'lake-wh'),
 ('What is the medallion architecture?', 'must', 'm-lakehouse', 'medallion'),
 ('Why is Parquet faster than CSV for analytics?', 'must', 'm-parquet', 'parquet'),
 ('What is the difference between Parquet and Delta Lake?', 'must', 'm-delta', 'parquet-vs-delta'),
 ('How does Delta Lake provide ACID transactions?', 'must', 'm-delta', 'delta'),
 ('How would you apply CDC changes to a Delta table?', 'must', 'm-delta', 'delta-ops'),
 ('Explain Spark architecture.', 'must', 'm-spark', 'spark-arch'),
 ('What is lazy evaluation in Spark?', 'must', 'm-spark', 'lazy'),
 ('What is a shuffle and why is it expensive?', 'must', 'm-spark', 'shuffle'),
 ('When do you use a broadcast join?', 'must', 'm-spark', 'joins'),
 ('How do you handle data skew?', 'must', 'm-spark', 'skew'),
 ('What is Databricks and why do companies use it?', 'must', 'm-databricks', 'databricks'),
 ('How does Airflow work?', 'must', 'm-airflow', 'airflow'),
 ('Airflow vs Spark?', 'must', 'm-airflow', 'airflow-vs-spark'),
 ('How do you get exactly-once from Kafka into the lakehouse?', 'must', 'm-kafka', 'kafka-de'),
 ('Explain window functions and the difference between RANK and DENSE_RANK.', 'must', 'm-sql', 'sql-window'),
 ('How do you ensure data quality?', 'must', 'm-quality', 'dq-dims'),
 ('How do you protect PII in a data platform?', 'must', 'm-governance', 'pii'),
 ('What is an AI agent, and how do you make it safe in a business process?', 'must', 'm-agentic', 'agentic'),
 ('LLM vs RAG vs agent — when do you use each?', 'must', 'm-agentic', 'llm-rag-agent'),
 ('How does RAG work, and why does it fail?', 'must', 'm-rag', 'rag'),
 ('How do you evaluate an LLM-based system?', 'must', 'm-llmeval', 'llm-eval'),
 ('What does a Forward Deployed Engineer do?', 'must', 'm-overview', None,
  'An engineer embedded with a customer who builds and deploys working software on the customer\'s data, then turns it into reusable patterns.',
  'Unlike a consultant, the FDE owns a working outcome in production; unlike a product engineer, they work inside one customer\'s landscape; unlike a solutions architect, they write and run the code.',
  'An FDE closes the gap between a platform\'s capability and a customer\'s outcome. In week one that means discovery — processes, data, constraints, success measures. Then a thin end-to-end slice in production on real data, iterated with users. The part that makes it scale is harvesting: every engagement should leave a reusable ingestion template, quality rule set, data product or agent tool, and feedback to the product team.',
  ('How is that different from consulting?', 'Ownership of a working production outcome, speed, and feeding reusable patterns back to the product rather than billing hours to a statement of work.'),
  'Describing FDE as "pre-sales" or "support".'),
 ('Your first week with a new customer — what do you do?', 'must', 'm-scenarios', None,
  'Understand the business problem, the data landscape and constraints, agree a measurable first outcome.',
  'Meet business owners and users, map source systems and owners, check access and compliance constraints, identify the one use case with value and available data, and agree success metrics.',
  'I treat week one as discovery with a deliverable. Business: what decision or process are we improving, and how is it measured today? People: who owns the data, who will use the result, who signs off. Landscape: sources, extraction options, existing platforms, security and residency rules. Then I write a one-page plan — the first thin slice, success metric, risks, what we will not do yet — and get it agreed. By the end of week two I want real data flowing through a skeleton pipeline, because nothing surfaces problems faster.',
  ('What if the customer wants everything at once?', 'Agree a sequence: the first slice that proves value end to end, with the rest on a visible roadmap. Show progress weekly.'),
  'Starting with architecture diagrams before understanding the business problem.'),
 ('Write SQL to deduplicate records keeping the latest per key.', 'must', 'm-sql', None,
  'ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC, tiebreaker DESC) and keep rn = 1.',
  'Use a CTE with ROW_NUMBER partitioned by the business key, ordered by the change timestamp plus a deterministic tiebreaker, then filter rn = 1.',
  'WITH r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, lsn DESC) rn FROM t) SELECT * FROM r WHERE rn = 1. I add a tiebreaker so it is deterministic across runs, and in Spark I watch for skew if one key has huge history.',
  ('Why not GROUP BY with MAX(updated_at) and join back?', 'Works, but costs an extra join and returns duplicates on ties; ROW_NUMBER is one pass and deterministic with a tiebreaker.'),
  'No tiebreaker, so dedup results change between runs.'),
 ('Explain OLTP vs OLAP.', 'should', 'm-lakehouse', 'oltp-olap'),
 ('Row vs columnar storage?', 'should', 'm-parquet', 'columnar'),
 ('Explain star schema and SCD Type 2.', 'should', 'm-de', 'modeling'),
 ('What is SAP HANA?', 'should', 'm-hana', 'hana'),
 ('How do you take a notebook to production?', 'should', 'm-databricks', 'notebook-prod'),
 ('How do retries and backfills work safely in Airflow?', 'should', 'm-airflow', 'airflow-ops'),
 ('How do watermarks work in streaming?', 'should', 'm-kafka', 'stream-proc'),
 ('Repartition vs coalesce; when to cache?', 'should', 'm-spark', 'cache-repart'),
 ('How does Spark recover from failures?', 'should', 'm-spark', 'fault'),
 ('How do you optimise a slow SQL query?', 'should', 'm-sql', 'sql-perf'),
 ('What is data governance in practice?', 'should', 'm-governance', 'governance'),
 ('What are data contracts?', 'should', 'm-quality', 'contracts'),
 ('How do you secure an enterprise AI system?', 'should', 'm-entai', 'ent-ai'),
 ('What is lineage and why does it matter?', 'nice', 'm-de', 'lineage-obs'),
 ('Joins, HAVING vs WHERE, NOT IN vs NOT EXISTS?', 'nice', 'm-sql', 'sql-joins'),
]

# Final revision — "30 minutes before the interview"
REV_CONCEPTS = ['Lakehouse = open files + transaction log (Delta) → ACID, MERGE, time travel', 'Parquet = columnar file; pruning (partition, column) + predicate pushdown', 'Delta = Parquet + _delta_log; optimistic concurrency; VACUUM limits time travel', 'Spark: driver plans, executors run tasks; job → stages (split at shuffle) → tasks per partition', 'Shuffle is the cost; broadcast small joins; salt hot keys', 'Lazy evaluation: transformations build a plan; actions run it', 'Airflow orchestrates, Spark processes; idempotent tasks per data interval', 'Kafka → Structured Streaming → Delta with checkpoint = exactly-once', 'Window functions: ROW_NUMBER (dedup), DENSE_RANK (top-N with ties), LAG (change)', 'Quality: completeness, accuracy, consistency, validity, uniqueness, freshness']
REV_PATTERNS = ['Medallion bronze → silver → gold with quality gates', 'CDC → Kafka (key = PK) → MERGE into Delta', 'Overwrite partition by run date (replaceWhere) for idempotency', 'Event-time windows + watermark + late-data side table', 'Broadcast join for dimension lookups', 'Salting for skewed joins', 'Data product with owner, SLA, contract, reconciliation', 'Hybrid RAG: vector + keyword, ACL filter, rerank, cite', 'Agent: deterministic detection + agent for the varying part + draft-only writes + human approval', 'Model gateway: identity, redaction, limits, tracing, cost']
REV_AI = ['LLM vs RAG vs agent — choose the simplest that works', 'Most RAG failures are retrieval failures', 'ACLs at retrieval time, not in the prompt', 'Tools run with the end user\'s identity', 'Treat retrieved content and tool output as untrusted (prompt injection)', 'Write actions need confirmation / approval + audit', 'Evaluate at model, retrieval, system, safety, business levels', 'Accuracy alone is not enough', 'Calibrate LLM-as-judge against humans', 'Trace every request: prompt, sources, tools, tokens, cost']
REV_DE = ['Declare the grain first', 'SCD Type 2 for history in dimensions', 'Keep raw (bronze) for replay', 'Tokenise PII at ingestion', 'Partition on low-cardinality filters (date)', 'Compact small files', 'Reconcile with the source system', 'Alert on freshness, not just failure', 'Check join cardinality', 'Deterministic ORDER BY in ROW_NUMBER']
REV_FDE = ['Discovery before architecture', 'Ship a thin end-to-end slice on real data early', 'Measure a business outcome, agreed up front', 'Earn trust with reconciliation and parallel runs', 'Leave reusable patterns behind']
REV_MISTAKES = ['Claiming hands-on experience you do not have (PySpark, Databricks, HANA)', 'Inventing SAP product details — say "I would verify against SAP\'s current documentation"', 'Jumping to an agent when RAG or a workflow suffices', 'Designing only the happy path — no retries, idempotency or late data', 'Talking architecture without asking about the business outcome']
