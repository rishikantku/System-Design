# -*- coding: utf-8 -*-
"""Concept cards, part 1: data engineering fundamentals, lakehouse, Parquet, Delta Lake, Spark.

Card fields (the teaching structure the reader asked for):
 what · why · analogy · bridge (backend-engineer connection) · tech (intermediate) · expert (expert depth) ·
 example · a15 / a30 / a2m (interview answers) · fu (senior follow-up, answer) · mistake · code (optional)
src: JD (skill named in the posting) | GENERAL | VERIFY
"""

def C(id, mod, title, prio, src, what, why, analogy, bridge, tech, expert, example, a15, a30, a2m, fu, mistake, code=None):
    return dict(id=id, mod=mod, title=title, prio=prio, src=src, what=what, why=why, analogy=analogy, bridge=bridge, tech=tech,
                expert=expert, example=example, a15=a15, a30=a30, a2m=a2m, fu=fu, mistake=mistake, code=code)

CARDS = [
# ================================================================ data engineering fundamentals
C('pipeline', 'm-de', 'Data pipeline', 'must', 'JD',
  'A chain of steps that moves data from where it is produced to where it is used, changing its shape on the way.',
  'Operational systems are built to run the business, not to answer questions about it. A pipeline gets their data somewhere it can be combined, cleaned and queried without hurting the source.',
  'A water treatment plant: intake, filtration, storage, distribution — each stage hands clean output to the next.',
  'You already build service chains with queues between them. A pipeline is the same shape, but the unit of work is a dataset or a batch of records, and correctness is measured on the data, not on the response.',
  'Stages: ingest (pull or receive), land raw data unchanged, transform into clean and modelled tables, serve to BI, ML or APIs. Each stage should be idempotent (re-running it gives the same result), observable (row counts, freshness, failures) and isolated (a failure in one table does not corrupt others).',
  'Design for re-runs, not for success: partition outputs by date and overwrite a partition on retry, so a retried day replaces itself instead of duplicating. Separate compute from orchestration (Spark does the work, Airflow decides when). Treat schemas as contracts with producers.',
  'Nightly: SAP S/4HANA sales orders + Salesforce opportunities + web events → lakehouse → a revenue table the finance team trusts by 7 am.',
  'A pipeline moves data from source systems to where it is used, and the engineering is making each step idempotent, observable and safe to re-run.',
  'A pipeline ingests data from sources, lands it raw, transforms it into clean modelled tables and serves it. The hard parts are not the happy path: they are re-runs, late data, schema changes and knowing when the data is wrong. So I design every stage to be idempotent and observable.',
  'I think of a pipeline as a chain of stages with contracts between them: ingest, land raw, transform, serve. I keep the raw landing untouched so I can always reprocess. Each transform writes to a partitioned output that a retry overwrites, so failures are safe to re-run. Orchestration — when and in what order — is separate from compute — how the transformation runs. And I treat quality as a first-class output: row counts, freshness and validation results are produced alongside the data, so a bad load stops before it reaches a dashboard or an AI agent. Coming from backend systems, the mindset is the same as a service chain; what changes is that correctness is a property of the dataset.',
  ('A nightly job failed halfway and someone re-ran it. Now revenue is doubled. Why, and how would you prevent it?', 'The job appended instead of overwriting, so the re-run duplicated rows. Make writes idempotent: overwrite the partition for that run date, or MERGE on a business key, never blind append.'),
  'Designing only the happy path — appending on every run, so retries create duplicates.'),

C('etl-elt', 'm-de', 'ETL vs ELT', 'must', 'JD',
  'ETL transforms data before loading it into the warehouse. ELT loads raw data first and transforms it inside the warehouse or lakehouse.',
  'ETL came from the era of expensive warehouse storage and compute. Cheap storage and elastic compute made it practical to keep everything raw and transform later — which also lets you reprocess when logic changes.',
  'ETL: wash and chop vegetables before putting them in the fridge. ELT: put the groceries straight in, prepare them when you cook — and you still have the originals if the recipe changes.',
  'Compare it to validating at the API edge (ETL) versus storing the raw event and deriving views from it (ELT) — like event sourcing: keep the facts, rebuild the projections.',
  'ELT is the default in lakehouses: land raw (bronze), clean (silver), aggregate (gold), all inside the platform with SQL or Spark. ETL still makes sense when data must be filtered before it lands — PII that must never be stored, or huge sources where you only need a fraction.',
  'The real decision is where governance and cost sit. ELT keeps raw data (great for replay and audit) but means raw PII may land — so you need masking or a restricted raw zone. ETL reduces stored volume but loses replay. Many platforms are hybrid: light ETL at ingestion (drop or tokenise PII, normalise types), ELT for business logic.',
  'Raw SAP and CRM extracts land unchanged in a bronze zone; dbt or Spark SQL builds silver and gold tables; tokenisation of national IDs happens before landing.',
  'ETL transforms before loading; ELT loads raw first and transforms in the platform — the modern default because it keeps replay.',
  'ETL transforms data before it lands; ELT lands it raw and transforms inside the lakehouse or warehouse. ELT is the modern default because storage is cheap and keeping raw data lets you reprocess when logic changes. I still do light ETL at the edge for things that must never be stored raw, like PII.',
  'The difference is where transformation happens. ETL transforms in flight and loads only the result; ELT loads raw data first and transforms inside the platform. ELT won in the lakehouse era because storage became cheap and compute elastic, and because keeping the raw layer means you can rebuild every downstream table when business logic changes — the same reason event sourcing keeps events. The cost is governance: raw data includes sensitive fields, so the raw zone needs tight access, or you tokenise PII at ingestion. In practice I run a hybrid: minimal ETL at the edge for privacy and type normalisation, and ELT in medallion layers for business logic.',
  ('When would you deliberately choose ETL?', 'When data must not be stored raw (regulated PII), when the source is huge and you need a small slice, or when the target cannot do the transformation efficiently.'),
  'Saying ELT is "better" without mentioning governance of the raw zone.'),

C('batch-stream', 'm-de', 'Batch vs streaming', 'must', 'JD',
  'Batch processes data in bounded chunks on a schedule; streaming processes an unbounded flow continuously as events arrive.',
  'Different questions need different freshness. Month-end finance needs complete, correct data; fraud detection needs it in seconds.',
  'Batch is collecting post and opening it once a day; streaming is answering the phone.',
  'You know request/response vs async consumers. Batch is a cron job over a table; streaming is a long-running Kafka consumer with state. The streaming hard parts are the ones you already know: ordering, retries, state, backpressure, exactly-once.',
  'Batch: simpler, cheaper, easy to re-run, latency of the schedule. Streaming: low latency, but you must handle late and out-of-order events (event time vs processing time, watermarks), state, and continuous operation. Micro-batch (Spark Structured Streaming) sits between: small batches every few seconds with batch-like semantics.',
  'Most enterprise platforms are both: stream into the raw layer for freshness, batch for heavy transforms and reconciliation. A Lambda architecture runs two paths (batch for truth, stream for speed) and pays for it in duplicated logic; Kappa uses one streaming path with replay. With Delta tables, one engine can serve both, which is much of the lakehouse argument.',
  'Orders stream from Kafka into a bronze Delta table within a minute; an hourly batch builds the revenue table; a nightly batch reconciles against the ERP.',
  'Batch handles bounded data on a schedule; streaming handles unbounded data continuously — choose by the freshness the business actually needs.',
  'Batch processes bounded data on a schedule and is simple and cheap to re-run; streaming processes events continuously for low latency but must handle late data, state and exactly-once. I ask what freshness the decision actually needs, and often stream into the raw layer while doing heavy transforms in batch.',
  'The question I ask first is: what freshness does the decision need? Month-end close needs complete, reconciled data; fraud needs seconds. Batch gives simplicity, cheap re-runs and natural backfills. Streaming gives latency but brings the problems I know from Kafka systems: out-of-order and late events, which you handle with event time and watermarks; state, which must be checkpointed; and end-to-end exactly-once, which needs idempotent or transactional sinks. Spark Structured Streaming\'s micro-batches are a pragmatic middle. A common pattern is to stream raw data into Delta for freshness and run batch for heavy modelling and reconciliation — one storage layer serving both, which avoids the duplicated logic of a Lambda architecture.',
  ('Your stream shows yesterday\'s revenue lower than the batch report. Why?', 'Late-arriving events: the stream closed the window before they arrived. Use event-time windows with a watermark that matches real lateness, and reconcile with batch.'),
  'Choosing streaming because it sounds modern, when the business needs a daily report.'),

C('cdc', 'm-de', 'Change Data Capture (CDC)', 'must', 'JD',
  'Capturing every insert, update and delete in a source database as a stream of change events, usually by reading the database\'s transaction log.',
  'Full extracts of large tables are slow and heavy on the source, and polling "updated_at" misses deletes and in-between states. Reading the log captures every change with little load.',
  'Instead of photocopying the whole ledger every night, you get a copy of each new line as it is written.',
  'You know the outbox pattern and event sourcing. Log-based CDC is the database emitting its own events from the write-ahead log, so no application change is needed. Debezium → Kafka is the common open-source shape.',
  'Log-based CDC (Debezium reading MySQL binlog / Postgres WAL, Oracle LogMiner, vendor tools for SAP) emits change events with before/after images and an operation type. Downstream, a MERGE applies them to a target table keyed by primary key. Ordering per key matters, so partition the Kafka topic by primary key.',
  'Hard parts: the initial snapshot plus switching to the log without gaps; schema changes in the source; deletes (soft vs hard) and GDPR erasure; ordering across tables in one transaction; and idempotent apply (use the source log position as a version to ignore stale events). For SAP sources, extraction usually goes through SAP-supported mechanisms rather than reading the database log directly — verify against current SAP documentation.',
  'Customer master changes in an ERP flow through CDC → Kafka → a Delta table updated with MERGE every minute, so the AI assistant answers with current addresses.',
  'CDC turns a database\'s transaction log into a stream of change events, so you replicate changes instead of re-extracting tables.',
  'CDC reads the source database\'s log and emits every insert, update and delete as events — usually into Kafka. Downstream I apply them with a MERGE keyed on the primary key. It captures deletes, puts almost no load on the source, and gives near-real-time freshness.',
  'Change data capture turns the database\'s write-ahead log into a stream of change events, each with the operation and the before and after values. Compared with nightly full extracts it is lighter on the source, near real-time, and captures deletes, which timestamp polling misses. I put the events on Kafka partitioned by primary key so changes to one row stay ordered, and apply them with MERGE into a Delta table. The engineering is in the edges: a consistent initial snapshot and hand-over to the log, schema changes, hard deletes for compliance, and idempotent apply using the log position so replays do not move a row backwards. For SAP systems I would use SAP-supported extraction rather than raw log reading.',
  ('How do you make CDC apply idempotent?', 'Carry the source log sequence number (LSN/SCN) as a version; MERGE only when the incoming version is newer than the stored one.'),
  'Forgetting deletes, or ignoring per-key ordering so updates apply out of order.'),

C('modeling', 'm-de', 'Data modelling: star schema, grain, SCD Type 2', 'should', 'JD',
  'Shaping tables so questions are easy and fast: facts (events you measure) surrounded by dimensions (things you describe them by).',
  'Normalised OLTP schemas are great for writes and terrible for analysis — a simple question becomes a dozen joins. Dimensional models make analytical queries simple and fast.',
  'A receipt (the fact: what was bought, how much) and the address book, product catalogue and calendar it refers to (dimensions).',
  'You normalise for write integrity in OLTP. Analytics deliberately denormalises for read speed — the same trade you make when you build a read model or a cache in CQRS.',
  'Star schema: one fact table at a declared grain (one row per order line) with foreign keys to dimensions (customer, product, date). Grain is the first decision and the most common mistake. Slowly Changing Dimensions: Type 1 overwrites; Type 2 keeps history with valid_from / valid_to / is_current so a fact joins to the dimension as it was at the time.',
  'Lakehouse layers map onto this: silver holds cleaned, conformed entities; gold holds star schemas or wide aggregated tables for consumption. Wide denormalised tables are common in columnar storage because joins cost more than storage. Data Vault suits integration of many changing sources; Kimball stars suit consumption.',
  'Sales fact (order line grain) with customer as SCD2, so revenue by region uses the customer\'s region at order time, not today\'s.',
  'Model facts at a clear grain surrounded by dimensions; use SCD Type 2 when history of a dimension matters.',
  'I model analytics as facts at a declared grain with dimensions around them — a star schema. The first decision is the grain. Where a dimension changes and history matters, like a customer\'s region, I use SCD Type 2 so each fact joins to the version that was true at the time.',
  'Analytical modelling starts with the grain: what does one row of the fact table mean — an order, an order line, a daily snapshot? Then dimensions describe the facts: customer, product, date. That is a star schema, and it trades the write-integrity of OLTP normalisation for simple, fast reads — the same trade as a read model in CQRS. Dimensions change, and the business decides whether history matters: Type 1 overwrites, Type 2 keeps versioned rows with validity dates, so revenue by region last year uses last year\'s region. In a lakehouse, silver holds clean conformed entities and gold holds the stars or wide tables the consumers actually query.',
  ('Revenue by region changed for last year after a customer moved. What went wrong?', 'The customer dimension was Type 1 (overwritten). Use SCD Type 2 and join facts to the version valid at the transaction date.'),
  'Not declaring the grain, so facts at different grains get mixed and totals double-count.',
  ('sql', """-- SCD Type 2: close the current row, insert the new version
MERGE INTO dim_customer t
USING staged_customers s
ON t.customer_id = s.customer_id AND t.is_current = true
WHEN MATCHED AND t.region <> s.region THEN
  UPDATE SET is_current = false, valid_to = s.changed_at;
-- then insert the new current versions
INSERT INTO dim_customer
SELECT customer_id, region, changed_at AS valid_from, NULL AS valid_to, true AS is_current
FROM staged_customers s
WHERE NOT EXISTS (SELECT 1 FROM dim_customer t
                  WHERE t.customer_id = s.customer_id AND t.is_current AND t.region = s.region);""")),

C('lineage-obs', 'm-de', 'Lineage and data observability', 'should', 'JD',
  'Lineage records where each dataset came from and what it feeds. Observability watches the data itself — freshness, volume, schema, distribution — not just whether jobs succeeded.',
  'A job can succeed and still produce wrong data. When a dashboard is wrong you need to know which upstream change caused it, and who else is affected.',
  'Lineage is the family tree of a number on a dashboard; observability is its health check-up.',
  'You know distributed tracing (lineage is the trace across tables) and SLOs (freshness and volume are the golden signals of data). "Job green, data wrong" is the data version of a 200 with a wrong body.',
  'Lineage: table- and column-level, captured from SQL/Spark plans or the catalogue (e.g., Unity Catalog, OpenLineage). Observability signals: freshness (last update), volume (row count vs expected), schema (unexpected change), distribution (nulls, ranges, cardinality), and quality test results. Alert on these, with owners.',
  'Use lineage for impact analysis before changing a column, and for root cause after an incident. Put data SLOs on gold tables ("revenue table fresh by 07:00, 99% of days"). Make quality checks blocking at layer boundaries for critical tables so bad data stops instead of propagating to agents and dashboards.',
  'Gold revenue drops 40% overnight; lineage shows a silver table filtered by a new status code from the ERP; the volume alert on silver fired first.',
  'Lineage tells you where data came from and what depends on it; observability tells you whether the data itself is healthy.',
  'Lineage maps each table to its sources and consumers, so you can do impact analysis and root cause. Data observability monitors freshness, volume, schema and distributions, because a job can succeed and still produce wrong data. I put SLOs and owners on the critical tables.',
  'Two complementary things. Lineage answers "where did this number come from, and what breaks if I change this column?" — it is distributed tracing for tables, captured from query plans or the catalogue. Observability answers "is the data healthy right now?" through freshness, volume, schema and distribution checks, because a green job can still produce nonsense — the data equivalent of an HTTP 200 with the wrong body. I put data SLOs and named owners on the tables that matter, make quality checks block promotion between layers for critical data, and use lineage both before changes and during incidents.',
  ('A finance dashboard is wrong but every job is green. How do you investigate?', 'Walk lineage upstream from the dashboard, check freshness/volume/distribution at each hop, find where the data diverged, then fix and add a check there so it fails loudly next time.'),
  'Monitoring only job success, not the data.'),

# ================================================================ lakehouse
C('lake-wh', 'm-lakehouse', 'Data lake, data warehouse, lakehouse', 'must', 'JD',
  'A warehouse stores structured, modelled data for SQL analytics. A lake stores any data as files on cheap object storage. A lakehouse puts warehouse features — transactions, schemas, performance — on top of lake files.',
  'Warehouses were reliable but expensive and closed; lakes were cheap and flexible but became "data swamps" without transactions or quality. The lakehouse tries to get both.',
  'Warehouse: a library with a catalogue. Lake: a warehouse full of unlabelled boxes. Lakehouse: the boxes, but with a catalogue and a librarian who records every change.',
  'Think of object storage (S3) as a giant immutable blob store. A lake is just files there. A lakehouse adds what you would add to make a blob store behave like a database: a transaction log, schema, and indexes — open formats (Parquet + Delta/Iceberg) so many engines can read the same data.',
  'Warehouse: proprietary storage + SQL engine; strong performance and governance; storage and compute historically coupled. Lake: Parquet/JSON/CSV on S3/ADLS/GCS; any engine; no ACID; schema-on-read. Lakehouse: open table format (Delta Lake, Apache Iceberg, Hudi) adds ACID, schema enforcement, time travel and file-level statistics; one copy of data serves BI, ML and streaming.',
  'Trade-offs: lakehouses still need file-layout care (small files, compaction, clustering) to match warehouse performance; governance comes from the catalogue (Unity Catalog, etc.). Many enterprises keep both: a warehouse for curated finance reporting, a lakehouse for everything else. Open formats matter for avoiding lock-in and for sharing data across platforms without copies.',
  'An enterprise keeps SAP finance data in its warehouse for statutory reporting, and builds a lakehouse combining SAP, CRM, IoT and documents for analytics and AI.',
  'Warehouse = structured and governed; lake = cheap files of anything; lakehouse = warehouse guarantees on open lake files.',
  'A warehouse holds modelled, structured data with strong SQL performance and governance. A lake holds any data cheaply as files but has no transactions. A lakehouse adds a transactional table format like Delta Lake on top of lake files, so one copy serves BI, ML and streaming with ACID guarantees.',
  'A data warehouse is a database built for analytics: structured, modelled, fast SQL, strong governance, historically proprietary and costly. A data lake is just files on object storage — any format, very cheap, any engine — but without transactions, writes can collide, schemas drift, and it turns into a swamp. The lakehouse adds a transactional table format, Delta Lake or Iceberg, on top of the lake files: a transaction log gives ACID, schema enforcement and time travel, file statistics give performance, and because the format is open, Spark, SQL engines and ML tools all read one copy. You still need discipline on file layout and a catalogue for governance. I choose based on workload: curated statutory reporting may stay in a warehouse; mixed analytics, streaming and AI on diverse data fits a lakehouse.',
  ('Why not just put everything in the warehouse?', 'Cost at scale, unstructured and semi-structured data, ML workloads that want files, and lock-in. The warehouse remains good for curated, high-concurrency SQL.'),
  'Describing a lakehouse as "a lake with SQL" and missing the transaction log, which is the actual innovation.'),

C('oltp-olap', 'm-lakehouse', 'OLTP vs OLAP', 'must', 'JD',
  'OLTP systems run the business — many small reads and writes. OLAP systems analyse the business — few huge reads over many rows.',
  'The two workloads want opposite storage layouts and indexes, so running heavy analytics on the transactional database slows the business down.',
  'OLTP is the checkout till; OLAP is the accountant reading a year of receipts.',
  'You know this from production: you never run a big reporting query against the primary. OLTP = your service database (row store, B-tree indexes, normalised). OLAP = columnar, scans, aggregates, denormalised.',
  'OLTP: row-oriented storage, point lookups by key, high concurrency, normalised, ACID per transaction. OLAP: columnar storage, scans and aggregations over few columns of many rows, compression, partitioning, vectorised execution, denormalised star schemas. HTAP systems (SAP HANA is the classic enterprise example) try to serve both from one store.',
  'Separation is usually achieved by replication (CDC to the analytical store), which introduces freshness lag; HTAP removes the copy but needs careful workload management so analytics does not starve transactions.',
  'Order entry runs on the ERP\'s transactional tables; a sales-trend dashboard reads a columnar copy refreshed every few minutes.',
  'OLTP is many small transactions on rows; OLAP is large analytical scans on columns.',
  'OLTP serves the running business — many small, concurrent, row-level reads and writes, normalised, row-stored. OLAP serves analysis — large scans and aggregations over a few columns of many rows, so columnar, compressed and denormalised. You separate them so analytics never slows transactions, usually with CDC into the analytical store.',
  'OLTP and OLAP are opposite workloads. OLTP is the order system: thousands of small concurrent transactions touching a few rows, so row storage, B-tree indexes, normalisation and per-transaction ACID. OLAP is the analyst: a handful of queries each scanning millions of rows but only a few columns, so columnar storage, compression, partitioning and vectorised execution win. Historically you separate them and replicate with CDC, accepting a freshness lag. In-memory columnar systems like SAP HANA were designed to serve both from one copy — that is the main idea behind HANA — but you still need workload management so analytics does not starve the transactions.',
  ('Why is a columnar store bad at OLTP?', 'Writing one row touches every column file/segment; point updates are expensive. Columnar stores buffer writes (delta stores) and merge them in the background.'),
  'Running analytics on the OLTP primary "because the data is there".'),

C('medallion', 'm-lakehouse', 'Medallion architecture (bronze / silver / gold) and data marts', 'must', 'GENERAL',
  'Three layers of quality: bronze is raw as it arrived, silver is cleaned and conformed, gold is modelled for a specific use. A data mart is a gold subset for one domain or team.',
  'Separating layers means you can always reprocess from raw, debug by comparing layers, and give each consumer exactly the shape and access they need.',
  'Ore (bronze), refined metal (silver), finished parts (gold).',
  'Like keeping the raw event log, a normalised domain model, and purpose-built read models — each layer a contract with its consumers.',
  'Bronze: append-only, source schema, plus ingestion metadata (source, load time). Silver: deduplicated, typed, validated, conformed keys, PII handled. Gold: star schemas, aggregates, feature tables, AI-ready data products. Quality checks gate promotion between layers. Data marts: gold slices for finance, sales, supply chain with their own access rules.',
  'Medallion is a naming convention, not a standard — define what each layer guarantees, and keep transformations idempotent so a layer can be rebuilt from the one below. Treat gold tables as products: owner, SLA, documentation, versioned schema.',
  'Bronze: raw SAP order extracts; silver: orders deduplicated with customer keys conformed to CRM; gold: daily revenue by region and an "order facts" table the AI agent queries.',
  'Bronze raw, silver clean and conformed, gold business-ready; each layer can be rebuilt from the one below.',
  'I organise a lakehouse in layers: bronze keeps raw data as it arrived so I can always reprocess; silver is cleaned, deduplicated and conformed; gold is modelled for consumers — stars, aggregates, data products. Quality checks gate promotion between layers.',
  'Medallion architecture is a layering convention. Bronze stores data exactly as it arrived, plus ingestion metadata, so nothing is lost and everything can be replayed. Silver applies the engineering: types, deduplication, validation, conformed business keys across sources, and PII handling. Gold is shaped for consumption: star schemas for BI, aggregates, feature tables, and governed data products that an AI agent or an API can use. Quality checks gate each promotion, so bad data stops at a boundary. The important part is defining what each layer guarantees and keeping transforms idempotent, so any layer can be rebuilt from the one below — the same discipline as rebuilding read models from an event log.',
  ('Where do you handle PII in medallion?', 'Restrict bronze tightly (or tokenise at ingestion), and mask/tokenise in silver so gold and consumers never see raw identifiers unless authorised.'),
  'Letting consumers read bronze directly, so raw quirks leak into reports.'),

# ================================================================ Parquet
C('columnar', 'm-parquet', 'Row vs columnar storage', 'must', 'JD',
  'Row storage keeps each record\'s fields together; columnar storage keeps each column\'s values together.',
  'Analytical queries read a few columns of many rows. With columnar layout they read only those columns, and similar values compress far better.',
  'A row store is a pile of filled-in forms; a column store is a stack of separate lists — all the names, all the prices — so totalling prices means reading one list.',
  'Your OLTP database is row-oriented because a request touches a whole record. Analytics is the opposite access pattern, like scanning one field across a whole Kafka topic — you would want it laid out by field.',
  'Columnar benefits: I/O only for needed columns (column pruning); compression via encodings that exploit same-type adjacency (dictionary, run-length, bit-packing); vectorised execution on column batches; min/max statistics per chunk enabling skipping.',
  'Costs: writes and single-row updates are expensive, which is why columnar systems batch writes, keep delta stores, and compact. File layout (sorting/clustering) determines how effective min/max skipping is.',
  'SELECT SUM(amount) FROM orders over 1 billion rows and 80 columns reads one column — roughly 1/80th of the data before compression helps further.',
  'Columnar stores read only the columns a query needs and compress them well — ideal for analytics.',
  'Row stores keep records together, which suits transactions touching whole rows. Columnar stores keep columns together, so analytical queries read only the columns they need, compress them well, and process them in vectorised batches.',
  'The access pattern decides the layout. A transaction reads or writes a whole record, so rows are stored together. An analytical query aggregates one or two columns across millions of rows, so storing each column contiguously means the engine reads only those columns, compresses them dramatically because adjacent values share a type and often a value, and processes them in CPU-friendly vectors. Per-chunk statistics like min and max let it skip data entirely. The cost is writes: updating one row touches many column segments, so columnar systems batch and compact writes. That is the core reason analytics systems — Parquet, warehouses, HANA\'s column store — are columnar.',
  ('Why does sorting data before writing Parquet speed up queries?', 'Sorted data gives tight min/max ranges per row group, so filters skip more row groups, and runs compress better.'),
  'Saying columnar is "faster" without saying for which access pattern.'),

C('parquet', 'm-parquet', 'Parquet: pruning, pushdown, compression', 'must', 'JD',
  'Parquet is an open columnar file format, the standard storage format of data lakes.',
  'CSV and JSON are row-based, untyped, uncompressed and must be fully parsed. Parquet is typed, compressed and self-describing, and lets engines skip most of a file.',
  'A book with an index and chapter summaries, versus a book you have to read cover to cover to find one fact.',
  'Think of a Parquet file as an immutable, compressed, columnar SSTable with metadata in the footer — you read the footer first, then fetch only the byte ranges you need from S3.',
  'Structure: file → row groups (~128 MB) → column chunks → pages, with schema and per-chunk statistics (min, max, null count) in the footer. Column pruning reads only referenced columns. Predicate pushdown uses row-group statistics to skip chunks that cannot match. Partition pruning (directory layout like date=2026-10-09/) skips whole files before opening them. Encodings + compression (Snappy/ZSTD) cut size 5–10× vs CSV, typically.',
  'Parquet files are immutable — no updates or deletes, no transactions, no concurrent-write safety. Thousands of tiny files kill performance (metadata and request overhead), so compact. Over-partitioning on high-cardinality columns creates small files; partition on low-cardinality filters like date.',
  'A query for one region\'s October orders opens only date=2026-10-* folders (partition pruning), reads 3 of 60 columns (column pruning), and skips row groups whose region min/max exclude it (pushdown).',
  'Parquet is an open columnar file format with statistics that let engines read only the columns and row groups a query needs.',
  'Parquet is the standard columnar file format of data lakes. It stores data by column in row groups with min/max statistics in the footer, so engines read only needed columns, skip row groups with predicate pushdown, and skip folders with partition pruning. It is typed and compressed — usually several times smaller than CSV.',
  'Parquet is an open, typed, columnar file format. Each file holds row groups, each row group holds column chunks, and the footer holds the schema and statistics like min, max and null counts per chunk. That enables three kinds of skipping: partition pruning skips whole directories based on the folder layout, column pruning reads only the columns the query references, and predicate pushdown uses the statistics to skip row groups that cannot match. Add dictionary and run-length encoding plus compression, and files are typically several times smaller and far faster to scan than CSV. What Parquet does not give you is transactions: files are immutable, and there is no safe way for two writers to update a table — which is exactly what Delta Lake adds.',
  ('Your Parquet table has 2 million small files. What happens and what do you do?', 'Listing and opening files dominates query time. Compact into ~128 MB–1 GB files (OPTIMIZE in Delta), and fix the writer — fewer output partitions, no over-partitioning.'),
  'Partitioning by a high-cardinality column like customer_id, creating millions of tiny files.'),

# ================================================================ Delta
C('delta', 'm-delta', 'Delta Lake and its transaction log', 'must', 'JD',
  'Delta Lake is an open table format: Parquet data files plus a transaction log that records which files make up the table at each version.',
  'Plain Parquet folders have no transactions. A failed job leaves half-written files, readers see partial data, two writers corrupt each other, and you cannot update or delete rows.',
  'Parquet files are pages; the Delta log is the table of contents that says which pages belong to the book right now — and keeps every previous edition.',
  'You know write-ahead logs and optimistic concurrency. The _delta_log is a WAL for a table on object storage: each commit is a JSON file listing files added and removed; readers reconstruct the table from the log; writers commit with optimistic concurrency.',
  'Each write produces new Parquet files then atomically commits a new log entry (000…N.json) recording add/remove actions plus schema and statistics. Periodic checkpoints (Parquet) summarise the log. Readers see a consistent snapshot (snapshot isolation). Writers check for conflicts at commit time (optimistic concurrency) and retry. Deletes and updates rewrite affected files and mark old ones removed.',
  'Because data files are immutable and the log is the source of truth, you get ACID, time travel (read version N), audit (DESCRIBE HISTORY), and schema enforcement. Operational care: OPTIMIZE compacts small files, Z-ORDER / liquid clustering co-locates data for skipping, VACUUM deletes unreferenced files after a retention period (which limits time travel). Deletion vectors avoid rewriting whole files for small deletes.',
  'A streaming job appends orders every minute while an analyst queries; the analyst always sees a consistent snapshot, and a failed batch never shows half its rows.',
  'Delta Lake = Parquet files + a transaction log, giving ACID, schema enforcement and time travel on a data lake.',
  'Delta Lake adds a transaction log on top of Parquet files. Every write is an atomic commit listing which files were added and removed, so readers get consistent snapshots, concurrent writers are safe, and you can update, delete, MERGE and time-travel — none of which plain Parquet supports.',
  'Delta Lake is a table format, not a different file format: the data is still Parquet. What it adds is the _delta_log, which works like a write-ahead log for a table on object storage. A write first creates new Parquet files, then atomically commits a log entry saying "add these files, remove those". Readers build a snapshot from the log, so they never see partial writes; concurrent writers use optimistic concurrency and retry on conflict. Because files are immutable and the log keeps history, you get ACID, time travel to earlier versions, an audit history, and schema enforcement. Updates, deletes and MERGE work by rewriting affected files. Operationally you compact with OPTIMIZE, cluster for data skipping, and VACUUM old files — remembering VACUUM limits how far back time travel can go.',
  ('Two jobs MERGE into the same Delta table at once. What happens?', 'Optimistic concurrency: both write files, the first commit wins, the second detects a conflict if it touched the same files/partitions and retries or fails. Partition the work or serialise writers to avoid repeated conflicts.'),
  'Saying Delta is "a better Parquet". The data is still Parquet; the log is what is new.'),

C('parquet-vs-delta', 'm-delta', 'Parquet vs Delta Lake — the distinction', 'must', 'JD',
  'Parquet is a file format. Delta Lake is a table format built on Parquet files plus a transaction log.',
  'Interviewers use this to check whether you understand what makes a lakehouse reliable.',
  'Parquet is a brick; Delta is a building with a land registry recording which bricks belong to it.',
  'Parquet is like an immutable data file on disk; Delta is that plus the database\'s commit log and catalogue — the difference between files in a folder and a table.',
  'Parquet: columnar storage, compression, statistics, schema per file; no transactions, no updates/deletes, no table-level schema enforcement, no history. Delta: everything Parquet has, plus ACID commits, snapshot isolation, MERGE/UPDATE/DELETE, schema enforcement and evolution, time travel, audit history, streaming source/sink semantics, file-level data skipping and compaction tooling.',
  'Alternatives with the same idea: Apache Iceberg and Apache Hudi. Delta UniForm can expose Iceberg metadata for interoperability (verify current support for your platform). The choice among them is about ecosystem and engine support more than fundamentals.',
  'Same 1 TB of Parquet data: as a folder it cannot be updated safely; as a Delta table it supports daily MERGE of CDC changes and rollback to yesterday.',
  'Parquet is the file; Delta is the table — Parquet plus a transaction log.',
  'Parquet is a columnar file format. Delta Lake is a table format that stores data as Parquet files and adds a transaction log, so you get ACID writes, MERGE and deletes, schema enforcement and time travel. Parquet alone gives you efficient storage; Delta gives you a reliable table.',
  'The cleanest way to say it: Parquet is a file format, Delta Lake is a table format. A folder of Parquet files is efficient to read — columnar, compressed, with statistics — but it is not a table: there are no transactions, so a failed write leaves partial data; no safe concurrent writers; no updates or deletes; nothing stops a writer adding a file with a different schema; and no history. Delta keeps the data in Parquet and adds the transaction log, which turns the folder into a table with ACID commits, MERGE, schema enforcement and evolution, and time travel. Iceberg and Hudi solve the same problem; the choice is mostly ecosystem.',
  ('Can you read a Delta table with a plain Parquet reader?', 'You can read the files, but you will see files that were logically deleted or not yet committed. Always read through the log.'),
  'Treating them as competitors rather than layers.'),

C('delta-ops', 'm-delta', 'Schema enforcement, evolution, time travel, MERGE', 'must', 'JD',
  'Delta rejects writes that do not match the table schema (enforcement), allows controlled schema changes (evolution), keeps old versions (time travel), and supports upserts (MERGE).',
  'Pipelines meet changing sources, late corrections and bad loads. These features make the table safe to change and easy to repair.',
  'Enforcement is a bouncer at the door; evolution is updating the guest list on purpose; time travel is the CCTV footage.',
  'Enforcement is schema validation at the API boundary; evolution is a backward-compatible API change; time travel is point-in-time restore; MERGE is an upsert keyed on a business key.',
  'Enforcement: mismatched columns/types fail the write. Evolution: mergeSchema adds new columns explicitly. Time travel: SELECT … VERSION AS OF n / TIMESTAMP AS OF; RESTORE TABLE to roll back. MERGE INTO target USING source ON key WHEN MATCHED UPDATE / DELETE WHEN NOT MATCHED INSERT — the workhorse for CDC and SCD.',
  'MERGE performance depends on how many files the match touches: partition or cluster on the merge key, prune with extra predicates, and deduplicate the source first (MERGE fails if multiple source rows match one target row). Time travel is bounded by VACUUM retention, and is not a backup strategy across regions.',
  'A bad load corrupted yesterday\'s silver table: RESTORE to the previous version in seconds, fix, re-run.',
  'Delta enforces schema on write, evolves it on purpose, keeps versions for time travel, and supports upserts with MERGE.',
  'Delta enforces the schema so bad writes fail instead of corrupting the table, lets you evolve it deliberately, keeps versions so you can query or restore earlier states, and supports MERGE for upserts — the standard way to apply CDC changes or build SCD Type 2.',
  'Four features that make a lake table safe to operate. Schema enforcement rejects writes that do not match, so a source change fails loudly instead of silently corrupting data. Schema evolution lets you add columns deliberately. Time travel lets you query an older version or RESTORE the table after a bad load — very fast incident recovery, though bounded by VACUUM retention. And MERGE gives upserts keyed on a business key, which is how CDC changes and slowly changing dimensions are applied. For MERGE at scale I deduplicate the source first, and partition or cluster on the merge key so it rewrites few files.',
  ('MERGE fails with "multiple source rows matched". Why?', 'The source has duplicates per key. Deduplicate (e.g., ROW_NUMBER by key ordered by change sequence, keep 1) before MERGE.'),
  'Using time travel as the backup and disaster-recovery plan.',
  ('sql', """-- Apply a deduplicated batch of CDC changes
MERGE INTO silver.customers AS t
USING (
  SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY lsn DESC) AS rn
    FROM bronze.customer_changes WHERE batch_id = :batch
  ) WHERE rn = 1
) AS s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED AND s.lsn > t.lsn THEN UPDATE SET *
WHEN NOT MATCHED AND s.op <> 'D' THEN INSERT *;""")),

# ================================================================ Spark
C('spark-arch', 'm-spark', 'Spark architecture: driver, executors, cluster manager', 'must', 'JD',
  'Spark splits a large dataset into partitions and processes them in parallel on many machines. A driver plans the work; executors do it.',
  'One machine cannot process terabytes in reasonable time. Spark gives a simple programming model over a cluster and handles distribution and failure for you.',
  'A head chef (driver) writes the plan and hands out stations; line cooks (executors) each cook their share; the restaurant manager (cluster manager) decides how many cooks you get.',
  'You already understand horizontal scaling and work queues. The driver is a coordinator that turns your code into a DAG of tasks; executors are long-lived worker processes that run tasks on partitions — like a job scheduler fanning work out to a worker fleet, with the data split by key or range.',
  'Driver: runs your program, builds the logical plan, optimises it (Catalyst), splits it into stages and tasks, schedules tasks, collects results. Executors: JVM processes on worker nodes with cores and memory; each core runs one task at a time on one partition; they cache data and write shuffle files. Cluster manager (YARN, Kubernetes, standalone, or Databricks\' own) allocates executors. PySpark: Python API; DataFrame operations run in the JVM, Python UDFs run in Python workers (slower).',
  'Driver is a single point of failure for a job and a memory hotspot: collect() or huge broadcast variables can OOM it. Executor sizing (cores × memory) trades parallelism against per-task memory; too many cores per executor causes GC and memory pressure. Prefer built-in DataFrame functions over Python UDFs; use pandas UDFs (Arrow) when you must.',
  'A 2 TB daily orders job: driver plans 16,000 tasks; 50 executors × 4 cores run 200 tasks at a time; finishes in ~12 minutes.',
  'The driver plans and schedules; executors run tasks on partitions in parallel; the cluster manager provides the executors.',
  'Spark runs a driver that turns my code into a plan of stages and tasks, and executors on worker nodes that each run tasks on partitions of the data in parallel. The cluster manager — YARN, Kubernetes or Databricks — provides the executors. It is horizontal scaling applied to data processing.',
  'You can think of Spark as horizontal scaling for data. The dataset is split into partitions. The driver runs my program: it builds a logical plan, the Catalyst optimiser rewrites it, and the scheduler cuts it into stages and tasks — one task per partition per stage. Executors are worker processes on the cluster; each core runs one task at a time and keeps intermediate data in memory or on local disk. The cluster manager allocates those executors. In PySpark the DataFrame operations still execute in the JVM, so built-in functions are fast while Python UDFs pay serialisation costs. The operational things I watch: never collect large data to the driver, size executors sensibly, and avoid Python UDFs on hot paths.',
  ('The driver runs out of memory. Common causes?', 'collect() or toPandas() on large data, broadcasting a too-large table, or a huge number of tiny files/partitions bloating the plan and task metadata.'),
  'Using collect() or toPandas() on a large DataFrame.',
  ('python', """from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("daily-revenue").getOrCreate()

orders = spark.read.format("delta").load("/lake/silver/orders")      # lazy: nothing runs yet
daily = (orders
         .filter(F.col("order_date") == "2026-10-08")                    # narrow
         .groupBy("region")                                               # wide: shuffle by region
         .agg(F.sum("amount").alias("revenue")))

daily.write.format("delta").mode("overwrite") \\
     .option("replaceWhere", "order_date = '2026-10-08'") \\
     .save("/lake/gold/daily_revenue")                                   # action: the job runs here""")),

C('lazy', 'm-spark', 'Transformations, actions, lazy evaluation, jobs/stages/tasks', 'must', 'JD',
  'Transformations (filter, select, join) only describe what to do; actions (count, write, collect) make Spark actually run it. Each action becomes a job, split into stages at shuffles, and stages into tasks per partition.',
  'Waiting until an action lets Spark see the whole computation and optimise it — combine steps, push filters down, skip columns — before touching data.',
  'Writing a shopping list (transformations) versus actually going to the shop (action). Seeing the whole list lets you plan the route.',
  'Like building a query or a lazy stream pipeline (Java Streams, LINQ): nothing executes until the terminal operation. The optimiser is a query planner for your whole program.',
  'Transformation → builds a DAG. Action → submits a job. The DAG scheduler splits the job into stages at wide (shuffle) boundaries; each stage has one task per partition; tasks run on executors. Catalyst performs predicate pushdown, column pruning, constant folding and join reordering; Adaptive Query Execution (AQE) re-plans at runtime using shuffle statistics (coalescing partitions, switching join strategies, splitting skewed partitions).',
  'Reusing a DataFrame in two actions recomputes it twice unless cached. explain() shows the physical plan — learn to read Exchange (shuffle), BroadcastHashJoin vs SortMergeJoin, and pushed filters. The Spark UI shows stages, task time distribution (skew), spill and shuffle sizes.',
  'Ten chained transformations produce no work; the final write triggers one job with three stages because two operations needed a shuffle.',
  'Transformations are lazy; actions trigger a job; jobs split into stages at shuffles and stages into tasks per partition.',
  'Spark is lazy: transformations build a plan and nothing runs until an action like write or count. That lets the optimiser see the whole computation — push filters down, prune columns, pick join strategies. Each action becomes a job, cut into stages at shuffle boundaries, with one task per partition.',
  'Spark separates describing work from doing it. Transformations like filter, select and join only add to a logical plan; an action — write, count, collect — submits a job. Because Spark sees the whole plan first, Catalyst can push filters to the source, read only needed columns and choose join strategies, and Adaptive Query Execution can re-plan at runtime from real shuffle statistics. The job is split into stages wherever data must be redistributed — a shuffle — and each stage runs one task per partition on the executors. Practically: read explain() to see Exchanges and join types, and cache a DataFrame you reuse across actions, because otherwise each action recomputes it.',
  ('Why did my job run twice as long after I added a count() for logging?', 'count() is an action; it executed the whole lineage once, then the write executed it again. Cache/persist if you need both, or log from the written output.'),
  'Assuming each line of PySpark executes immediately.'),

C('shuffle', 'm-spark', 'Narrow vs wide transformations and the shuffle', 'must', 'JD',
  'Narrow transformations work within each partition (filter, map). Wide transformations need rows from many partitions brought together by key (groupBy, join, distinct) — that redistribution is the shuffle.',
  'The shuffle is usually the most expensive part of a Spark job: it writes data to disk, sends it across the network, and reads it back.',
  'Narrow: each cook prepares their own ingredients. Wide: everyone has to send all the onions to one station and all the tomatoes to another before the next step.',
  'A shuffle is a repartition-by-key across the network — like re-keying a Kafka topic so all events for one customer land on one partition. Same cost profile: serialization, network, disk, and skew if one key is hot.',
  'Wide ops create a stage boundary: map tasks write shuffle files partitioned by key hash; reduce tasks fetch their partition from every map output. spark.sql.shuffle.partitions (default 200) controls reducer count; AQE can coalesce small ones. Costs: disk I/O, network, serialization, spill when memory is short.',
  'Reduce shuffles: filter and project early, broadcast small join sides, pre-aggregate (reduceByKey-style partial aggregation happens automatically for groupBy), bucket/cluster tables on join keys so repeated joins avoid shuffles, and avoid unnecessary distinct/repartition.',
  'A join of 2 TB orders with 50 GB customers shuffles both sides by customer_id — ~2 TB across the network — unless restructured.',
  'Narrow transformations stay within partitions; wide ones like groupBy and join shuffle data across the network, which is usually the dominant cost.',
  'Narrow transformations like filter work partition by partition; wide transformations like groupBy and join need all rows with the same key together, so Spark shuffles data across the network, creating a stage boundary. Shuffles dominate cost, so I filter early, broadcast small tables and cluster on join keys.',
  'Every transformation is either narrow — each output partition depends on one input partition, like filter or select — or wide — rows must be regrouped by key, like groupBy, join, distinct. Wide transformations force a shuffle: each upstream task writes its output split by key hash to local disk, and each downstream task fetches its share from all of them over the network. It is the same operation as re-keying a Kafka topic, with the same costs: serialization, network, disk, and skew if one key is hot. It also creates a stage boundary. So most Spark tuning is shuffle reduction: filter and select early, broadcast the small side of a join, pre-aggregate, and lay out tables clustered on join keys.',
  ('How do you see shuffles in a plan?', 'Look for Exchange nodes in explain(), and shuffle read/write sizes per stage in the Spark UI.'),
  'Calling repartition() everywhere "for performance", adding shuffles.'),

C('joins', 'm-spark', 'Joins and broadcast joins', 'must', 'JD',
  'Spark joins large tables by shuffling both sides by the key (sort-merge join), or — if one side is small — by copying it to every executor (broadcast join) and avoiding the shuffle.',
  'Joins are the most common expensive operation. Picking the right strategy can turn a 40-minute job into 4.',
  'Instead of mailing every order to where the customer list lives, give every warehouse its own small copy of the customer list.',
  'Broadcast join = a local cache of a small reference table on every node, like loading a config map into every service instance instead of calling a central service per request.',
  'Sort-merge join: shuffle both sides by key, sort, merge — scales to any size, costs two shuffles. Broadcast hash join: small side (default threshold spark.sql.autoBroadcastJoinThreshold ~10 MB; often raised) collected and sent to all executors; large side is not shuffled. Shuffle hash join exists for medium cases. AQE can convert to broadcast at runtime when one side turns out small. Hint with F.broadcast(df).',
  'Broadcast too-large tables and you OOM the driver or executors. Join keys with nulls never match (use null-safe <=> if intended). Exploding joins (many-to-many) multiply rows — check cardinality. For repeated joins on the same key, bucketing or clustering both tables avoids shuffles.',
  'Orders (2 TB) join product (200 MB): broadcast product; the job drops from two 2 TB shuffles to none.',
  'Large-large joins shuffle both sides; large-small joins should broadcast the small side to avoid the shuffle.',
  'By default Spark joins large tables with a sort-merge join, shuffling both sides by key. When one side is small enough, a broadcast join copies it to every executor so the large side is never shuffled — often the biggest single optimisation in a pipeline.',
  'Spark picks a join strategy from table sizes. For two large tables it uses sort-merge: shuffle both by the join key, sort and merge — scalable but two expensive shuffles. If one side is small — a dimension, a lookup — it broadcasts it to every executor and joins locally, so the big side never moves; it is like giving every service instance its own copy of a reference table. I make sure broadcasts happen where they should, with a hint or a higher threshold, and that they do not happen where the "small" side is actually large, which can run executors or the driver out of memory. AQE helps by switching to broadcast at runtime. I also check join cardinality, because an accidental many-to-many join silently multiplies rows.',
  ('Your join suddenly OOMs after months of working. What changed?', 'The "small" side grew past what fits in memory but is still being broadcast (hint or raised threshold). Remove the hint or pre-filter the small side.'),
  'Not checking for duplicate keys, turning a join into a row explosion.'),

C('skew', 'm-spark', 'Data skew', 'must', 'JD',
  'Skew is when a few keys hold far more rows than the rest, so one task does most of the work while the others wait.',
  'A job is only as fast as its slowest task. One hot key can make a 5-minute stage take an hour, or run out of memory.',
  'One checkout lane gets every customer because it is the only one that takes a certain card.',
  'A hot partition in Kafka or a hot shard in a database — same problem, same family of fixes: split the key, spread the load.',
  'Symptoms in the Spark UI: one or few tasks far longer than the median, with much larger shuffle read and spill. Fixes: AQE skew-join handling (splits skewed partitions automatically), broadcast the other side, salting (append a random suffix to hot keys on the big side and replicate the small side per suffix), handling null/default keys separately, or isolating the hot keys and processing them on a separate path.',
  'Salting trades extra data (replicating the small side N times) for parallelism. Choose N by the hot key\'s size relative to the median partition. Skew is also a modelling smell: "unknown" customer IDs and default values often cause it — clean them in silver.',
  'In retail data, one marketplace seller has 30% of orders; the join on seller_id leaves one task running for 50 minutes. Salting the seller key across 32 sub-keys brings it to 4 minutes.',
  'Skew is a few hot keys overloading single tasks; fix with AQE, broadcast, or salting the hot keys.',
  'Skew is when a few keys hold most of the rows, so one task does most of the work — you see it as a straggler task in the Spark UI. I first let AQE split skewed partitions, broadcast the other side if it is small, and otherwise salt the hot keys to spread them across tasks.',
  'Skew is the data version of a hot partition. When a few keys hold a large share of rows — a huge customer, or a null or default key — the shuffle sends them all to one task, and the stage waits for that straggler or it spills and runs out of memory. I diagnose it in the Spark UI by comparing max and median task time and shuffle read. Fixes in order: enable AQE skew handling, which splits oversized partitions automatically; broadcast the other side to avoid the shuffle; handle null or default keys separately because they are often the culprit; and for genuinely hot keys, salt — append a random suffix to the hot key on the large side and replicate the small side per suffix, trading some duplication for parallelism.',
  ('How does salting work in a join?', 'Large side: key → key + "_" + rand(0..N-1). Small side: explode each row into N copies with suffixes 0..N-1. Join on the salted key; aggregate back by the original key.'),
  'Adding executors to fix skew — the hot task is still on one core.',
  ('python', """from pyspark.sql import functions as F
N = 32  # salt buckets for hot keys

big = orders.withColumn("salt", (F.rand() * N).cast("int")) \\
            .withColumn("k", F.concat_ws("_", "seller_id", "salt"))
small = (sellers.crossJoin(spark.range(N).withColumnRenamed("id", "salt"))
                .withColumn("k", F.concat_ws("_", "seller_id", "salt")))

joined = big.join(small.drop("seller_id", "salt"), "k")""")),

C('cache-repart', 'm-spark', 'Caching, repartition vs coalesce', 'should', 'JD',
  'cache/persist keeps a DataFrame in memory for reuse. repartition changes the number of partitions with a full shuffle; coalesce reduces partitions without a shuffle by merging neighbours.',
  'Reusing a computed result avoids recomputing it; the right partition count balances parallelism against overhead and file sizes.',
  'Caching is keeping the chopped vegetables for the next dish. Repartition is re-sorting all the orders into new piles; coalesce is just pushing adjacent piles together.',
  'Cache = memoisation of an expensive intermediate. Repartition = rebalancing a consumer group with a full reshuffle; coalesce = merging partitions locally, cheap but possibly uneven.',
  'cache() = persist(MEMORY_AND_DISK) for DataFrames; materialises on first action; unpersist when done. repartition(n, col) does a hash shuffle, producing even partitions (also useful before writing partitioned output). coalesce(n) only decreases, avoids a shuffle, but can create uneven partitions and reduce upstream parallelism.',
  'Cache only what is reused and expensive; caching everything evicts useful data and adds GC pressure. Before writing, coalesce or repartition to control file count; repartition by the output partition column to avoid each task writing to every partition directory (file explosion). With AQE, many manual repartitions are unnecessary.',
  'A cleaned DataFrame feeds three aggregations: cache it once. Writing the result: repartition("order_date") so each date gets a few large files.',
  'Cache what you reuse; repartition reshuffles to any count; coalesce merges down without a shuffle.',
  'I cache a DataFrame only when several actions reuse an expensive result. repartition does a full shuffle to change partition count or partition by a column; coalesce only reduces partitions and avoids the shuffle — I use it to control the number of output files.',
  'Caching is memoisation: Spark recomputes the full lineage for every action, so if three outputs reuse an expensive cleaned DataFrame, I persist it once and unpersist after. I do not cache by default — it competes for executor memory. For partitioning: repartition triggers a full shuffle and gives evenly sized partitions, optionally by a column, which I use before writing a partitioned table so each partition directory gets a few large files instead of one file per task. Coalesce only reduces the count by merging neighbouring partitions without a shuffle — cheap, but it can leave uneven partitions and, placed too early, reduce the parallelism of the whole stage. With AQE on, I let Spark coalesce shuffle partitions automatically and only intervene for output file layout.',
  ('Why did coalesce(1) make my whole job slow?', 'It propagated upstream and reduced the stage to one task. Use repartition(1) (a shuffle) at the end, or better, avoid single-file outputs.'),
  'Caching everything, or coalesce(1) on large data.'),

C('fault', 'm-spark', 'Fault tolerance in Spark', 'should', 'JD',
  'If an executor dies, Spark recomputes the lost partitions from their lineage — the recipe of transformations — instead of replicating data.',
  'Large clusters lose machines routinely. Recomputing from lineage is cheaper than replicating every intermediate result.',
  'If a cook drops a dish, they remake it from the recipe and the ingredients still in the fridge.',
  'Like rebuilding state by replaying from a durable log rather than keeping replicas — the source data and the deterministic transformation are the "log".',
  'Failed tasks are retried (spark.task.maxFailures, default 4). Lost executors: their shuffle outputs are recomputed by re-running the upstream map tasks. Speculative execution can re-launch stragglers. Checkpointing truncates long lineages (iterative jobs, streaming). Structured Streaming uses checkpoints (offsets + state) and idempotent/transactional sinks for exactly-once.',
  'Lineage recompute assumes deterministic transformations and replayable sources — non-deterministic UDFs or reading a changing source break it. Driver failure kills the job; resilience there is at the orchestration layer (Airflow retry) plus idempotent writes. Delta writes are atomic, so a failed job leaves no partial table version.',
  'An executor is pre-empted mid-job; Spark re-runs its 40 tasks on others; the job finishes 3 minutes later, and the Delta write commits once.',
  'Spark recovers lost partitions by recomputing them from lineage and retrying failed tasks.',
  'Spark tolerates failures by recomputing lost partitions from lineage — the chain of transformations from durable input — and retrying failed tasks. Driver failure kills the job, so I make the job idempotent and let the orchestrator retry it; Delta\'s atomic commits mean a failed run leaves no partial output.',
  'Spark\'s fault tolerance is recompute rather than replicate. Every DataFrame knows its lineage — the transformations from durable input — so when an executor dies, Spark re-runs only the tasks needed to rebuild the lost partitions, including upstream map tasks whose shuffle files were lost. Failed tasks are retried, and stragglers can be speculatively re-launched. That assumes deterministic transformations and replayable inputs. The driver is the weak point: if it dies the job dies, so resilience moves up a level — the orchestrator retries the whole job, and because writes are idempotent and Delta commits are atomic, a retry is safe. Streaming adds checkpointed offsets and state for recovery.',
  ('Why might a retry produce different results?', 'Non-deterministic logic (rand without seed, current_timestamp, unordered first()) or a source that changed between attempts. Pin inputs (Delta version) and make logic deterministic.'),
  'Assuming the driver is also fault-tolerant.'),
]
