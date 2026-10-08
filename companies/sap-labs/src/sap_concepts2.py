# -*- coding: utf-8 -*-
"""Concept cards, part 2: Databricks, Airflow, Kafka for DE, SAP HANA, SQL, quality, governance,
agentic AI, RAG, enterprise AI, LLM evaluation. Same schema as sap_concepts1.C."""

from sap_concepts1 import C

CARDS = [
# ================================================================ Databricks
C('databricks', 'm-databricks', 'What Databricks is, and why companies use it', 'must', 'JD',
  'A managed data and AI platform built around Spark and Delta Lake: notebooks, jobs, SQL warehouses, ML tooling and a governance catalogue, running on your cloud account.',
  'Running Spark yourself means managing clusters, versions, security, storage formats and governance. Databricks packages all of it, so teams spend time on pipelines rather than infrastructure.',
  'Spark is the engine; Databricks is the whole car — dashboard, fuel system, service plan.',
  'Like moving from self-managed Kafka on EC2 to a managed service: same core technology, but someone else runs upgrades, autoscaling, security integration and the control plane.',
  'Workspace (notebooks, repos, jobs); compute (all-purpose clusters for development, job clusters for production, serverless, SQL warehouses for BI); Delta Lake as the storage format; Unity Catalog for governance (catalog.schema.table, permissions, lineage, audit); Workflows/Jobs for scheduling multi-task pipelines; Delta Live Tables / Lakeflow declarative pipelines with built-in expectations; MLflow for ML lifecycle; Model Serving and vector search for AI.',
  'Architecture: a control plane run by Databricks and a compute plane in the customer\'s cloud account (or serverless in Databricks\' account) — data stays in customer storage. Cost control: job clusters over all-purpose for production, autoscaling and auto-termination, Photon for SQL-heavy work, cluster policies. SAP and Databricks announced a partnership (SAP Databricks inside SAP Business Data Cloud) — VERIFY the current scope against SAP documentation before discussing details.',
  'Production pipeline: a Databricks Workflow with three tasks (ingest → silver → gold) on job clusters, tables governed in Unity Catalog, triggered nightly or by Airflow.',
  'Databricks is a managed lakehouse platform: Spark, Delta Lake, governance and AI tooling as one service.',
  'Databricks is a managed platform built on Spark and Delta Lake. It gives you notebooks for development, job clusters and workflows for production, SQL warehouses for BI, Unity Catalog for governance and lineage, and ML and AI tooling — so teams build pipelines instead of running infrastructure.',
  'Databricks is the commercial lakehouse platform from the creators of Spark. The core is Spark for compute and Delta Lake for storage, with a control plane managed by Databricks and data kept in the customer\'s own cloud storage. Around that it adds what an enterprise needs: notebooks and Git repos for development; job clusters and Workflows to run production pipelines; SQL warehouses so analysts can query the same tables; Unity Catalog for a single governance layer — permissions, lineage, audit — across data and AI assets; declarative pipelines with data-quality expectations; and MLflow, model serving and vector search for AI. Companies use it to consolidate warehouse, lake and ML platforms on one copy of data. In production I would run on job clusters with policies and auto-termination, keep code in Git with CI deploying jobs, and govern everything through the catalogue.',
  ('How do you control Databricks cost?', 'Job clusters (not all-purpose) for production, autoscaling + auto-termination, cluster policies, right-sized instance types, Photon where SQL-heavy, file compaction so queries scan less, and tagging for chargeback.'),
  'Claiming hands-on Databricks experience you do not have — say you understand the architecture and have built the equivalent on Spark/Kafka.'),

C('notebook-prod', 'm-databricks', 'Notebook vs production pipeline', 'should', 'JD',
  'A notebook is for exploring; a production pipeline is versioned, tested, parameterised, scheduled, monitored code.',
  'Notebooks are fast to iterate in, but hidden state, manual runs and no tests make them fragile in production.',
  'A sketchbook versus the engineering drawing that goes to the factory.',
  'The same gap as a REPL script versus a deployed service with CI, config, logging and alerts.',
  'Production practice: code in Git (Databricks Repos or packaged wheels), parameters not hard-coded, unit tests for transformation functions, data tests on outputs, CI/CD deploying jobs (e.g., Databricks Asset Bundles), job clusters, alerts on failure and on data SLOs, idempotent writes.',
  'Keep notebooks thin: they call tested library functions. Separate environments (dev/stage/prod catalogs), promote via CI. Treat data contracts and schemas as code.',
  'An analyst\'s notebook that computes churn is refactored into a package with tests, scheduled as a Workflow job, writing to a governed gold table.',
  'Notebooks are for exploration; production means Git, tests, parameters, CI/CD, scheduling and monitoring.',
  'I use notebooks to explore, but production code lives in Git as tested functions, deployed through CI/CD to scheduled jobs with parameters, alerts and idempotent writes. Notebooks in production become thin entry points.',
  'Notebooks are excellent for exploration but their properties — hidden cell state, run-in-any-order, manual execution, no tests — are exactly what you do not want in production. My path from notebook to production: pull the logic into functions in a Git repo, unit-test them with small DataFrames, add data tests on the output, parameterise dates and environments, deploy through CI/CD as a job on job clusters, and add alerting on both failure and data freshness. The notebook, if it stays, is a thin entry point. This is the same discipline as any service I have shipped, applied to data.',
  ('How do you unit-test PySpark code?', 'Local SparkSession in pytest, small hand-built DataFrames, assert on collected results; keep transformations as pure functions DataFrame → DataFrame.'),
  'Scheduling a notebook directly as the production job with hard-coded paths.'),

# ================================================================ Airflow
C('airflow', 'm-airflow', 'Airflow: DAGs, tasks, scheduler, operators', 'must', 'JD',
  'Airflow is a workflow orchestrator: you define pipelines as DAGs of tasks in Python, and it schedules them, runs them in dependency order, retries failures and records history.',
  'Real pipelines have many steps with dependencies, schedules, retries and backfills. Cron cannot express "run B after A succeeds, retry 3 times, alert on failure, re-run last week".',
  'Airflow is the conductor: it does not play an instrument, it tells each section when to play.',
  'You know workflow engines and job schedulers. Airflow is a scheduler with a dependency graph and a run history database — like a durable job queue where each job knows its upstreams.',
  'DAG: Python file defining tasks and dependencies. Task: an operator instance (BashOperator, PythonOperator, DatabricksSubmitRunOperator, SparkSubmitOperator, KubernetesPodOperator…). Sensor: waits for a condition (file arrives, upstream table updated). Scheduler: creates DAG runs per schedule and queues ready tasks; executors (Celery, Kubernetes) run them on workers. Metadata DB stores state. Each run has a logical date (data interval) used to parameterise what it processes.',
  'Airflow should orchestrate, not process: heavy work goes to Spark/Databricks/warehouse; Airflow tasks trigger and wait. Make tasks idempotent and parameterised by the data interval, so retries and backfills are safe. Avoid top-level code in DAG files (parsed constantly). Use datasets/data-aware scheduling to trigger on upstream data rather than time where possible.',
  'Daily DAG: wait for SAP extract file (sensor) → Databricks ingest job → silver job → data-quality check → gold job → notify.',
  'Airflow orchestrates pipelines as DAGs of tasks with schedules, dependencies, retries and backfills.',
  'Airflow lets you define a pipeline as a DAG of tasks in Python. The scheduler runs tasks in dependency order on a schedule, retries failures, and keeps history so you can backfill. I keep Airflow as the orchestrator and push heavy processing to Spark or Databricks.',
  'Airflow is an orchestrator. A DAG, written in Python, declares tasks and their dependencies; the scheduler creates a run for each schedule interval, queues tasks whose upstreams have succeeded, and executors run them on workers, with all state in a metadata database. Operators are the task types — trigger a Databricks job, run SQL, call an API — and sensors wait for conditions like a file landing. Each run carries its data interval, so tasks are parameterised by the period they process. That is what makes retries and backfills safe, provided each task is idempotent — overwrite the partition for that interval. The main design rule: Airflow decides when and in what order; Spark or the warehouse does the processing.',
  ('Why should a task not do heavy processing inside the Airflow worker?', 'Workers are sized for orchestration; heavy work starves the scheduler fleet, does not scale out, and couples compute to the orchestrator. Delegate to Spark/Databricks and poll.'),
  'Using datetime.now() inside tasks instead of the run\'s data interval, which breaks backfills.',
  ('python', """from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from datetime import datetime, timedelta

with DAG("orders_daily", start_date=datetime(2026, 1, 1), schedule="@daily", catchup=True,
         default_args={"retries": 3, "retry_delay": timedelta(minutes=10)}) as dag:

    landed = FileSensor(task_id="wait_for_extract",
                        filepath="/landing/orders/{{ ds }}/_SUCCESS", poke_interval=300)

    silver = DatabricksRunNowOperator(task_id="build_silver", job_id=101,
                                      notebook_params={"run_date": "{{ ds }}"})
    gold = DatabricksRunNowOperator(task_id="build_gold", job_id=102,
                                    notebook_params={"run_date": "{{ ds }}"})

    landed >> silver >> gold   # each task overwrites the {{ ds }} partition: safe to retry""")),

C('airflow-ops', 'm-airflow', 'Retries, idempotency, backfill, monitoring', 'must', 'JD',
  'Retries re-run failed tasks; idempotency makes re-runs safe; backfill runs a DAG for past intervals; monitoring tells you when runs fail, run late, or produce bad data.',
  'Pipelines fail constantly — network, quotas, late files. The question is never "will it fail" but "is it safe and obvious when it does".',
  'A retry is pressing the button again; idempotency is making sure pressing it twice does not order two pizzas.',
  'Exactly your instincts from distributed services: retries with backoff, idempotency keys, at-least-once delivery. Backfill is replaying the log for a date range.',
  'retries / retry_delay / retry_exponential_backoff per task; execution_timeout; SLAs or deadline alerts; on_failure_callback to page or post. Backfill: catchup=True or airflow dags backfill -s -e. Idempotency patterns: overwrite partition by data interval (replaceWhere), MERGE on keys, write to temp then atomic swap. Monitor: run duration trends, task failures, sensor timeouts, data freshness of outputs.',
  'Backfills compete with daily runs for compute — use max_active_runs and pools. Keep task boundaries at durable checkpoints (each task writes a table) so a retry starts from the last good step. Alert on lateness (no success by 07:00), not just failures.',
  'The ERP extract was late for three days; after it lands, a backfill re-runs those three intervals; each overwrites its own date partition, so no duplicates.',
  'Retries handle transient failure; idempotent, interval-parameterised tasks make retries and backfills safe.',
  'I configure retries with backoff, but rely on idempotency for safety: each task processes its data interval and overwrites that partition or MERGEs on keys, so retries and backfills never duplicate. I alert on lateness and data freshness, not just failures.',
  'Retries are cheap to add and dangerous without idempotency. Each task in my DAGs processes exactly its data interval and either overwrites that partition or MERGEs on a business key, so a retry, a manual re-run or a backfill of last month produces the same result as the first run. Retries use backoff and a timeout; sensors have timeouts so they do not hold slots forever. For backfills I cap concurrency with max_active_runs and pools so they do not starve the daily run. And I monitor three things: failures, lateness against an SLA, and the data itself — freshness and volume of the output tables — because a successful run that wrote zero rows is still an incident.',
  ('A backfill of 90 days ran and now some days are doubled. Why?', 'Those tasks append rather than overwrite, or depend on datetime.now(). Make them interval-parameterised and overwrite by partition; re-run.'),
  'Adding retries to a non-idempotent append task.'),

C('airflow-vs-spark', 'm-airflow', 'Airflow vs Spark', 'must', 'JD',
  'Airflow orchestrates. Spark processes.',
  'Candidates new to data engineering often blur them. Interviewers check that you put work in the right layer.',
  'Airflow is the project manager with the schedule; Spark is the team doing the work.',
  'Airflow is your scheduler/workflow engine (like a Step Functions state machine); Spark is your compute fleet.',
  'Airflow: when to run, in what order, retries, dependencies, backfill, alerting; lightweight Python tasks. Spark: distributed transformation of large data; partitions, shuffles, executors. Typical integration: Airflow triggers a Spark/Databricks job, waits, checks the result, triggers the next.',
  'Inside Databricks, Workflows can orchestrate Databricks tasks, so some teams skip Airflow; Airflow remains strong for cross-system orchestration (SAP extract, external APIs, multiple platforms). Choose one orchestrator per pipeline to avoid two schedulers fighting.',
  'Airflow at 02:00 triggers a Databricks job that transforms 3 TB; Airflow then runs a quality check and notifies finance.',
  'Airflow orchestrates; Spark processes.',
  'Airflow decides when and in what order things run, with retries and backfills. Spark does the distributed data processing. Airflow triggers the Spark job and reacts to its result; it should never do the heavy lifting itself.',
  'They solve different problems. Airflow is the control plane: schedules, dependencies, retries, backfills, alerting, and coordination across systems — the SAP extract, the Databricks job, the quality check, the notification. Spark is the data plane: it takes a large dataset, partitions it across executors, and transforms it. In a pipeline, Airflow triggers a Spark or Databricks job, waits for it, checks the outcome and moves on. If everything lives inside Databricks, its own Workflows can replace Airflow; Airflow earns its place when you orchestrate across many systems.',
  ('Would you use Airflow or Databricks Workflows?', 'Databricks Workflows if the pipeline is all inside Databricks; Airflow if orchestration spans many external systems or the customer already runs it. One orchestrator per pipeline.'),
  'Doing pandas transformations of large data inside Airflow tasks.'),

# ================================================================ Kafka
C('kafka-de', 'm-kafka', 'Kafka in data engineering', 'must', 'JD',
  'In data engineering Kafka is the durable, replayable ingestion backbone: events and database changes land on topics, and stream processors or sink connectors move them into the lakehouse.',
  'It decouples hundreds of producing systems from consuming pipelines, buffers spikes, and lets you replay history when a pipeline changes.',
  'A conveyor belt with a recording: every parcel passes by, and you can rewind the tape.',
  'You already know Kafka deeply. The shift is in what consumers do: instead of services reacting to events, the consumer is a pipeline landing data into Delta tables, and correctness is "every event exactly once in the table".',
  'Shapes: Debezium/Kafka Connect source (CDC) → topics → Spark Structured Streaming or Kafka Connect sink → bronze Delta; Schema Registry with Avro/Protobuf for schema evolution; topics partitioned by business key for ordering. Streaming jobs track offsets in checkpoints and write to Delta with idempotent/transactional semantics, giving end-to-end exactly-once.',
  'Retention and replay: keep enough retention (or tiered storage) to rebuild bronze. Lag is the freshness SLO of the pipeline. Schema evolution: enforce compatibility (BACKWARD) in the registry so producers cannot break consumers. Exactly-once in practice = idempotent writes + offset tracking in the same commit (Spark checkpoint + Delta transaction), not Kafka transactions alone.',
  'Order events (Kafka, keyed by order_id) → Structured Streaming every 30 s → bronze Delta; consumer lag alert at 5 minutes.',
  'Kafka is the replayable ingestion backbone; stream processors land events into the lakehouse exactly once.',
  'In data engineering I use Kafka as the ingestion backbone: CDC and application events land on topics, and Spark Structured Streaming or a sink connector writes them to bronze Delta tables. Checkpointed offsets plus Delta\'s atomic commits give exactly-once in the table, and retention lets me replay.',
  'I have used Kafka as a service backbone; in data engineering the same properties do different work. Durability and retention mean the raw history can be replayed to rebuild bronze when logic changes. Partitioning by business key keeps per-entity order, which matters when applying CDC. Schema Registry with compatibility rules turns producer schemas into enforced contracts. On the consuming side, Spark Structured Streaming reads topics, tracks offsets in its checkpoint, and writes to Delta; because the offset checkpoint and the Delta commit are coordinated, each event lands exactly once even after a crash. Consumer lag becomes the pipeline\'s freshness metric, and I alert on it. Where I need simple movement rather than transformation, a Kafka Connect sink is less code.',
  ('How do you get exactly-once from Kafka into Delta?', 'Structured Streaming with a checkpoint (offsets) and Delta sink: the sink commit is idempotent per batch id, so a replayed batch is not written twice. For foreachBatch, use MERGE or txnAppId/txnVersion for idempotency.'),
  'Assuming Kafka "exactly-once" settings alone make the whole pipeline exactly-once.',
  ('python', """events = (spark.readStream.format("kafka")
          .option("kafka.bootstrap.servers", BROKERS)
          .option("subscribe", "sap.orders.cdc")
          .option("startingOffsets", "earliest")
          .load())

parsed = events.select(F.from_json(F.col("value").cast("string"), schema).alias("e"), "offset", "partition") \\
               .select("e.*", "offset", "partition")

(parsed.writeStream.format("delta")
       .option("checkpointLocation", "/chk/bronze_orders")   # offsets + progress: enables exactly-once
       .trigger(processingTime="30 seconds")
       .toTable("bronze.orders_cdc"))""")),

C('stream-proc', 'm-kafka', 'Stream processing: windows, watermarks, late data, lag', 'should', 'JD',
  'Stream processing computes over continuous data — counts per minute, joins of streams — using windows on event time, and watermarks to decide when a window is complete.',
  'Events arrive late and out of order. Without event-time windows and watermarks, counts are wrong or state grows forever.',
  'A teacher collecting homework: accepts late submissions up to a deadline (watermark), then marks the batch.',
  'Like handling out-of-order messages in a consumer, but systematically: event time instead of arrival time, bounded lateness instead of waiting forever.',
  'Window types: tumbling, sliding, session. Watermark = max event time seen − allowed lateness; state for windows older than the watermark is finalised and dropped. Output modes: append (final results), update, complete. Stateful operations need checkpointing. Stream-static joins enrich events with dimension tables; stream-stream joins need watermarks on both sides.',
  'Choosing lateness is a business trade: longer = more correct, more state, later results. Reconcile with batch for financial accuracy. Monitor lag (offset behind), processing rate vs input rate, batch duration vs trigger interval, and state size.',
  'Machine telemetry aggregated per 5-minute window with 10 minutes allowed lateness; readings older than that go to a late-data table for batch correction.',
  'Use event-time windows with a watermark to bound lateness and state.',
  'Streams arrive out of order, so I window on event time and set a watermark — how late I accept data — which lets Spark finalise windows and drop old state. The lateness is a business trade-off between correctness and latency, and I reconcile financially important numbers with batch.',
  'The key distinction is event time versus processing time. Aggregating by arrival time is easy and wrong, because mobile, IoT and cross-region events arrive late and out of order. So I window by event time and set a watermark: how far behind the newest event I still accept data. Windows older than the watermark are emitted and their state dropped, which keeps memory bounded. Choosing the lateness is a business decision — longer is more correct but later and more stateful — and anything later still goes to a side table for batch correction. Operationally I watch consumer lag, input rate versus processing rate, micro-batch duration against the trigger interval, and state size.',
  ('Your streaming job\'s memory keeps growing. Why?', 'Stateful aggregation or stream-stream join without a watermark, so state is never dropped. Add watermarks; bound dedup state.'),
  'Windowing by processing time for business metrics.'),

# ================================================================ HANA
C('hana', 'm-hana', 'SAP HANA — interview-safe understanding', 'should', 'JD',
  'SAP HANA is SAP\'s in-memory, column-oriented database. It underpins S/4HANA (SAP\'s ERP) and is designed to run transactions and analytics on the same data.',
  'Traditional ERP needed separate systems for transactions and reporting, with batch copies in between. Keeping data in memory and in columns made real-time analytics on live transactional data practical.',
  'Instead of photocopying the ledger to a separate reporting office every night, the accountant reads the live ledger — fast enough because it is all on the desk, sorted by column.',
  'You know the OLTP/OLAP split and CDC replication. HANA\'s design argument is: remove the copy. You know in-memory stores (Redis) and columnar analytics; HANA combines in-memory and columnar with full SQL and ACID.',
  'Column store (default) with compression and a write-optimised delta store merged into the main store; row store for some cases; in-memory primary storage with persistence (savepoints + logs) to disk; SQL plus calculation views for modelling; HANA Cloud is the managed cloud offering. Enterprise data reaching a lakehouse typically comes through SAP-supported integration and extraction tools rather than direct database access — VERIFY which mechanisms apply to the customer\'s landscape and licence.',
  'Integration considerations for a lakehouse: respect SAP licensing and supported extraction paths; preserve business semantics (SAP tables are cryptic; business meaning lives in views and the application layer); handle CDC for deltas; reconcile totals with SAP reports. SAP Datasphere and SAP Business Data Cloud are SAP\'s data-platform offerings, and HANA Cloud has a vector engine for AI use cases — all VERIFY against current SAP documentation.',
  'A customer\'s S/4HANA sales orders feed an AI agent via a governed data product, with semantics from SAP views preserved, joined in the lakehouse with CRM and web data.',
  'HANA is SAP\'s in-memory columnar database, designed to run transactions and analytics on one copy of data.',
  'SAP HANA is SAP\'s in-memory, column-oriented database, the foundation of S/4HANA. Its core idea is running transactional and analytical workloads on the same data, removing the batch copy to a separate warehouse. I have not worked with HANA hands-on; I understand it through columnar storage and OLTP/OLAP design, which I know well.',
  'HANA is SAP\'s in-memory, columnar, ACID database, and the platform S/4HANA runs on. Its design removes the traditional split between a transactional database and a separate reporting warehouse: data lives in memory in compressed columns, with a write-optimised delta store merged in the background, so analytical queries run on live transactional data. To be transparent, I have not operated HANA myself — but the mechanics are the same columnar and in-memory principles I know from analytical systems and caches. In an FDE context the practical questions are integration: getting SAP data into a lakehouse through supported extraction paths, preserving the business semantics that live in SAP views rather than raw tables, applying changes incrementally, and reconciling with SAP\'s own reports so the business trusts the numbers.',
  ('Why not read SAP tables directly into Spark over JDBC?', 'Licensing and support constraints, load on the production ERP, and raw tables lack business semantics. Use SAP-supported extraction and semantic views; verify the options for the landscape.'),
  'Claiming HANA hands-on experience, or inventing SAP product details.'),

# ================================================================ SQL
C('sql-joins', 'm-sql', 'Joins, GROUP BY, HAVING, CTEs, subqueries', 'must', 'JD',
  'The core of analytical SQL: combine tables (joins), summarise (GROUP BY), filter groups (HAVING), and structure complex queries into readable steps (CTEs).',
  'Most data-engineering logic — and most live SQL interview questions — are compositions of these.',
  'A CTE is naming an intermediate result on a whiteboard so the next step can refer to it.',
  'You write SQL already; the shift is scale and semantics: a wrong join silently multiplies rows across a billion-row table.',
  'INNER / LEFT / FULL / anti-join (LEFT JOIN … WHERE b.key IS NULL or NOT EXISTS) / semi-join (EXISTS). WHERE filters rows before grouping; HAVING filters groups after. CTEs (WITH) name steps; correlated subqueries run per row (often rewritable as joins or windows). NULL semantics: NULL = NULL is unknown; COUNT(col) skips NULLs; NOT IN with a NULL returns nothing.',
  'Check cardinality after every join. Prefer NOT EXISTS over NOT IN. Filter early. Know that the optimiser may inline CTEs (no materialisation guarantee).',
  'Customers with no orders this month: anti-join customers to orders filtered to the month.',
  'Joins combine, GROUP BY summarises, HAVING filters groups, CTEs make steps readable.',
  'I build analytical queries as named steps with CTEs: filter early, join with known cardinality, aggregate with GROUP BY, and filter aggregates with HAVING. I watch NULL semantics, especially NOT IN.',
  'I structure queries as a pipeline of CTEs, each one a clear step, which is easier to reason about and test. Joins are where most bugs hide: I know the expected cardinality before I write one, and check counts after, because a many-to-many join silently inflates totals. WHERE filters rows before aggregation and HAVING filters groups after. For "exists / does not exist" questions I use EXISTS and NOT EXISTS — NOT IN with a NULL in the subquery returns no rows, a classic trap.',
  ('Why does NOT IN return nothing here?', 'The subquery contains a NULL; x NOT IN (…, NULL) evaluates to unknown for every row. Use NOT EXISTS.'),
  'Joining without checking for duplicate keys on the "one" side.'),

C('sql-window', 'm-sql', 'Window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD, running totals', 'must', 'JD',
  'Window functions compute a value for each row using a set of related rows (a partition), without collapsing rows like GROUP BY does.',
  'Ranking, deduplication, top-N per group, period-over-period change and running totals are everyday data-engineering tasks — and the most common live SQL questions.',
  'GROUP BY gives each class one average; a window gives each student their rank within the class while keeping every student on the list.',
  'Like computing a per-key rolling value in a stream processor, but declaratively over a table.',
  'func() OVER (PARTITION BY … ORDER BY … ROWS/RANGE BETWEEN …). ROW_NUMBER: unique 1..n (ties broken arbitrarily unless ordered fully). RANK: ties share, gaps after (1,1,3). DENSE_RANK: ties share, no gaps (1,1,2). LAG/LEAD: previous/next row\'s value. SUM() OVER (ORDER BY … ROWS UNBOUNDED PRECEDING) = running total. Filtering on a window result needs a subquery/CTE (or QUALIFY where supported).',
  'Make ORDER BY deterministic (add a tiebreaker) or ROW_NUMBER results change between runs — a real source of flaky dedup. Default frame with ORDER BY is RANGE UNBOUNDED PRECEDING to CURRENT ROW, which treats ties as peers; specify ROWS for exact running totals. Windows over huge partitions cause skew in Spark.',
  'Latest record per customer from CDC: ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY lsn DESC) = 1.',
  'Window functions compute per-row values over a partition without collapsing rows — used for dedup, top-N and running totals.',
  'Window functions compute across a partition of rows while keeping each row. I use ROW_NUMBER for deduplication and latest-record, RANK or DENSE_RANK for rankings with ties, LAG and LEAD for change over time, and SUM over an ordered window for running totals.',
  'A window function computes a value for each row using related rows — the partition — ordered within it, without collapsing the rows as GROUP BY does. The three ranking functions differ only on ties: ROW_NUMBER always gives unique numbers, RANK gives ties the same rank and leaves gaps, DENSE_RANK gives ties the same rank without gaps. ROW_NUMBER partitioned by key and ordered by a change sequence descending is my standard dedup and latest-record pattern; I always add a tiebreaker so it is deterministic. LAG and LEAD give period-over-period comparisons, and SUM over an ordered frame gives running totals — specifying ROWS rather than the default RANGE so ties do not jump together. To filter on a window result I wrap it in a CTE or use QUALIFY where available.',
  ('Top 3 products by revenue per region, with ties included?', 'DENSE_RANK() OVER (PARTITION BY region ORDER BY revenue DESC) <= 3 in an outer query. Use ROW_NUMBER if exactly 3 rows are required.'),
  'Non-deterministic ORDER BY in ROW_NUMBER dedup.',
  ('sql', """-- 1. Latest version of each customer (dedup)
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC, lsn DESC) AS rn
  FROM bronze.customers)
SELECT * FROM ranked WHERE rn = 1;

-- 2. Top 3 products per region (ties kept)
WITH r AS (
  SELECT region, product_id, SUM(amount) AS revenue,
         DENSE_RANK() OVER (PARTITION BY region ORDER BY SUM(amount) DESC) AS dr
  FROM gold.order_lines GROUP BY region, product_id)
SELECT * FROM r WHERE dr <= 3;

-- 3. Month-over-month change and running total
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month)                          AS mom_change,
       SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING)           AS running_total
FROM gold.monthly_revenue;""")),

C('sql-perf', 'm-sql', 'SQL optimisation: plans, indexes, partitioning', 'should', 'JD',
  'Making queries fast by reading less data and moving less data — guided by the execution plan.',
  'At lakehouse scale a bad query is not just slow, it costs real money and blocks others.',
  'A good plan is the shortest route; the execution plan is the route the satnav actually chose.',
  'Same as tuning service-database queries with EXPLAIN — but in OLAP, indexes are mostly replaced by partition pruning, file statistics and clustering.',
  'Read the plan: scans (how many files/partitions), filters pushed down, join strategy, shuffles/exchanges, spill. OLTP: B-tree indexes, covering indexes, avoid functions on indexed columns. OLAP/lakehouse: partition by low-cardinality filter columns (date), cluster/Z-order on frequent filters and join keys, keep files 128 MB–1 GB, compute statistics, avoid SELECT *.',
  'Make predicates sargable (filter on the raw column, not a function of it). Push filters before joins. Pre-aggregate in gold for dashboards. Use materialised views or summary tables for repeated heavy queries. Compare cost per query, not only latency.',
  'Dashboard query scanning 4 TB is rewritten to filter on the partition column and read a pre-aggregated gold table: 12 GB scanned, 40× cheaper.',
  'Read the plan, scan less (pruning, clustering), move less (broadcast, pre-aggregate).',
  'I start from the execution plan: how much is scanned, whether filters are pushed down, how joins execute. In a lakehouse the levers are partition pruning, clustering for data skipping, file sizes and pre-aggregation, rather than classic indexes.',
  'I start every optimisation from the plan rather than guessing: how many partitions and files are scanned, whether predicates were pushed down, which join strategy ran, and where data was shuffled or spilled. Then the levers are reading less and moving less. Reading less: filter on the partition column directly, select only needed columns, cluster or Z-order on common filters so file statistics skip data, keep file sizes healthy. Moving less: broadcast small joins, filter before joining, pre-aggregate into gold tables for repeated dashboard queries. In OLTP the equivalent tools are indexes; in OLAP they are layout and statistics. And I measure cost per query, because at this scale cost is the metric the customer feels.',
  ('Why is WHERE YEAR(order_date) = 2026 slow on a date-partitioned table?', 'The function on the partition column can prevent pruning. Use order_date >= \'2026-01-01\' AND order_date < \'2027-01-01\'.'),
  'Optimising without looking at the plan.'),

# ================================================================ quality
C('dq-dims', 'm-quality', 'Data quality dimensions and checks', 'must', 'JD',
  'Data quality is measured on dimensions: completeness, accuracy, consistency, validity, uniqueness and freshness — each turned into automated checks.',
  'Decisions and AI agents are only as good as the data. Enterprise customers lose trust in a platform after one wrong number in a board report.',
  'A quality inspection line in a factory: measure every batch against the spec before it ships.',
  'Like contract tests and health checks — but on datasets. A null rate is an error rate; freshness is latency.',
  'Completeness: required fields present, expected row counts. Accuracy: matches reality / source of truth (reconcile totals with SAP). Consistency: same fact agrees across tables. Validity: types, ranges, allowed values, formats. Uniqueness: no duplicate keys. Freshness: updated within SLA. Implement with expectations (Delta Live Tables / Lakeflow expectations, Great Expectations, dbt tests) at layer boundaries; decide per check: warn, drop/quarantine rows, or fail the pipeline.',
  'Tier checks by impact: critical financial tables fail the pipeline; others quarantine bad rows to a table with reasons. Track quality metrics over time (trend, not only pass/fail). Reconciliation against the source system is the check finance trusts most.',
  'Silver orders: order_id unique, amount ≥ 0, currency in ISO list, customer_id exists in customers (quarantine otherwise), row count within ±20% of 7-day average, total reconciles with ERP within 0.1%.',
  'Measure completeness, accuracy, consistency, validity, uniqueness and freshness with automated checks at layer boundaries.',
  'I define quality on six dimensions — completeness, accuracy, consistency, validity, uniqueness, freshness — and implement them as automated checks at each layer boundary. Each check has an action: warn, quarantine bad rows, or fail the pipeline, depending on how critical the table is.',
  'I treat data quality like service reliability: defined dimensions, automated checks, and an action for each failure. Completeness and uniqueness catch broken loads and duplicate keys; validity catches bad types and values; consistency checks that the same fact agrees across tables; accuracy, in an enterprise, usually means reconciling totals with the source system — for SAP data, with SAP\'s own reports, because that is what the business trusts; and freshness is the latency SLO. Checks run at layer boundaries. For critical tables a failure blocks promotion; for others bad rows are quarantined with a reason so the good data still flows. I track the metrics over time, and every check has an owner.',
  ('A quality check fails at 3 am on the finance table. What should happen?', 'Pipeline stops promoting to gold (yesterday\'s data stays visible, marked stale), owner is alerted with the failing rows, consumers see a freshness warning. Never silently publish.'),
  'Only checking for nulls and calling it data quality.'),

C('contracts', 'm-quality', 'Data contracts and schema validation', 'should', 'GENERAL',
  'A data contract is an agreement between a producer and its consumers about a dataset\'s schema, meaning, quality and SLAs — enforced automatically.',
  'Most pipeline breakages start with an unannounced upstream change: a renamed column, a new status code, a unit change.',
  'An API contract, but for tables and event streams.',
  'Exactly API versioning and contract testing — schemas in a registry, compatibility rules, consumer-driven tests — applied to data producers.',
  'Contract contents: schema (names, types, nullability), semantics (definitions, units), quality rules, freshness SLA, owner, versioning policy. Enforcement: schema registry compatibility (Kafka), Delta schema enforcement, CI checks on producer changes, validation at ingestion that quarantines violations.',
  'Contracts shift responsibility to producers and make breaking changes explicit (new version, migration period). Hardest part is organisational — getting source teams to own them; FDEs often start by documenting implicit contracts with the customer\'s source owners.',
  'Contract for "orders" topic: Avro schema with BACKWARD compatibility, amount in minor units, status enum, 99.9% of events within 5 min, owner: order-platform team.',
  'Data contracts make producer–consumer expectations explicit and enforced, like API contracts for data.',
  'A data contract is an API contract for a dataset: schema, meaning, quality rules, freshness and an owner, enforced by schema registries, Delta schema enforcement and CI. It turns silent upstream changes into explicit versioned ones.',
  'From backend work I treat datasets like APIs. A data contract states the schema, what fields mean and their units, quality rules, the freshness SLA, the owner and how changes are versioned. Enforcement happens in several places: schema registry compatibility for Kafka topics, schema enforcement on Delta tables, CI checks when a producer changes, and validation at ingestion that quarantines violations. The technology is easy; the hard part is ownership. In a customer engagement I would start by writing down the implicit contracts with the source owners, because that is where most incidents originate.',
  ('Upstream renamed a column and your pipeline silently filled NULLs. How do you prevent it?', 'Schema enforcement/validation at ingestion that fails or quarantines on unexpected schema; contract with compatibility rules; alert on null-rate jumps.'),
  'Relying on "schema-on-read" so changes are discovered by dashboard users.'),

# ================================================================ governance
C('governance', 'm-governance', 'Governance: catalogue, lineage, access control, audit, retention', 'must', 'JD',
  'Governance is knowing what data you have, who owns it, who may use it for what, and proving it — through a catalogue, lineage, access controls, audit logs and retention rules.',
  'Enterprises are regulated. They must answer "who accessed this customer\'s data?" and delete it when required. Without governance, an AI agent can leak data across business units.',
  'A library\'s catalogue, membership cards and check-out records — plus a policy on which books are reference-only.',
  'You know IAM, RBAC, audit logging and tenant isolation. Governance applies them to tables, columns and rows, and adds lineage and lifecycle.',
  'Catalogue: central metadata (Unity Catalog, SAP-side catalogues, etc.) with owners, descriptions, tags (PII, confidential). Access: RBAC/ABAC on catalog/schema/table, column masking, row-level filters, tag-based policies. Lineage: auto-captured. Audit: who queried what, when. Lifecycle: retention periods, archival, deletion (GDPR right to erasure — with Delta, DELETE then VACUUM to physically remove).',
  'Design for least privilege by default and grant via groups. Tag at ingestion so policies follow data downstream. Erasure must reach every copy: bronze, silver, gold, caches, vector indexes, and backups per policy. AI agents should query through the same governed layer with the user\'s identity, not a super-user service account.',
  'A data product "customer_orders" is tagged PII; analysts in India see masked emails, the EU support agent sees rows only for EU customers, and every query is audited.',
  'Governance = catalogue + ownership + access control + lineage + audit + lifecycle.',
  'Governance means a catalogue with owners and classifications, fine-grained access control — table, column masking, row filters — automatic lineage, audit logs, and retention and deletion policies. I apply the same least-privilege principles I used for tenant isolation, and make AI agents go through the same controls.',
  'Governance answers four questions: what data do we have and who owns it — the catalogue with classifications; who can see what — role- or attribute-based access down to columns and rows, ideally driven by tags applied at ingestion; where did it come from and where does it go — lineage; and can we prove it — audit logs and retention. Lifecycle matters too: retention rules and erasure that reaches every copy, including derived tables, caches and vector indexes. My Isolated Cloud work at Atlassian was largely a governance problem at infrastructure level — tenant isolation, controlled egress, policy-driven enforcement — and the same instincts apply here. One AI-specific rule: agents access data through the governed layer with the end user\'s permissions, never through a privileged service account.',
  ('A customer invokes GDPR erasure. What do you delete in a lakehouse?', 'Every copy: bronze/silver/gold via DELETE + VACUUM (beyond time-travel retention), derived aggregates if re-identifiable, caches, feature stores, vector indexes and embeddings; record the erasure in an audit log.'),
  'Giving pipelines and agents a single admin service account.'),

C('pii', 'm-governance', 'PII protection: masking, tokenisation, encryption', 'must', 'JD',
  'Techniques to protect personal data: masking hides it from viewers, tokenisation replaces it with a reversible surrogate held in a vault, encryption makes stored or transmitted data unreadable without keys.',
  'The JD names PII protection explicitly. A leak is a regulatory, legal and trust failure — and AI systems create new leak paths (prompts, logs, embeddings).',
  'Masking: showing only the last four digits of a card. Tokenisation: a cloakroom ticket for your coat. Encryption: a locked safe.',
  'You know TLS, KMS and secrets management. Add field-level protection and the data-specific leak paths: joins re-identifying people, logs, model inputs.',
  'Classify and tag PII at ingestion. Encryption at rest (KMS, customer-managed keys) and in transit (TLS). Tokenisation of identifiers (deterministic tokens keep joinability without exposing values). Dynamic masking by role at query time. Pseudonymisation for analytics; aggregation thresholds to avoid re-identification. For AI: redact before sending to models, do not log raw prompts with PII, govern embeddings like the source text.',
  'Deterministic tokenisation enables joins but is vulnerable to dictionary attacks on low-entropy values — use keyed (HMAC) tokens. Masking is a view-level control, not protection of the underlying storage. Data residency may constrain where processing (including model inference) happens. Customer-managed keys let the customer revoke access.',
  'National ID tokenised at ingestion (HMAC with a vaulted key); email masked except for the support role; prompts to the LLM redact names and IDs; vector index built only from approved fields.',
  'Classify PII, then encrypt, tokenise or mask by use — and cover AI leak paths.',
  'I classify PII at ingestion and protect it by use: encryption at rest and in transit, tokenisation for identifiers that must stay joinable, dynamic masking by role, and redaction before data reaches an LLM or logs. Embeddings are governed like the text they came from.',
  'I start by classifying and tagging PII as it lands, because policies can only follow data that is labelled. Then I pick the control by use. Encryption at rest and in transit is the baseline, ideally with customer-managed keys. Identifiers that analytics needs to join on are tokenised with a keyed hash, so joins work but the raw value is not exposed. Fields people need to see partially are masked dynamically by role. For AI there are new leak paths: prompts, model logs, and embeddings that can reproduce source text. So I redact before inference, avoid logging raw prompts, keep vector indexes under the same access control as their source, and respect data residency for where the model runs. This is very close to my Isolated Cloud work, where customer data could not leave the customer\'s boundary.',
  ('Is masking enough to protect PII?', 'No — it is a presentation control. Storage, copies, logs, extracts and model inputs still hold the raw value. Combine with tokenisation/encryption and access control.'),
  'Forgetting logs, prompts and embeddings as places PII ends up.'),

# ================================================================ agentic + RAG + enterprise AI + eval
C('agentic', 'm-agentic', 'Agentic AI: agents, tools, planning, memory, guardrails', 'must', 'JD',
  'An AI agent is an LLM in a loop: it decides the next step, calls tools (APIs, queries, actions), observes the results, and continues until the goal is reached or it hands back to a human.',
  'A plain LLM can only produce text from what it already knows. Business processes need it to look things up in live systems and take actions — under control.',
  'A capable new assistant with a list of systems they may use, a checklist, and a manager who approves anything risky.',
  'An agent is an orchestrator whose control flow is decided by a model at runtime instead of code. Tools are APIs with schemas; the agent loop is a workflow engine; guardrails are authorisation and validation middleware. Everything you know about API design, idempotency and authz applies.',
  'Components: model; tools (function definitions with schemas — read tools and write tools); planning/reasoning; memory (conversation state; long-term memory in a store); retrieval (RAG) for knowledge; orchestration (single agent loop or multi-agent with a supervisor); guardrails (input/output filters, tool allowlists, parameter validation, spending/step limits); human-in-the-loop approval for consequential actions; observability (traces of every step).',
  'Prefer deterministic workflows with LLM steps where the path is known; use agents where the path genuinely varies. Tools should be narrow, idempotent, permission-checked with the end user\'s identity, and return structured data. Write actions need confirmation and audit. Failure modes: loops, wrong tool, hallucinated parameters, prompt injection via tool outputs, runaway cost.',
  'A procurement agent checks inventory (read tool on a governed data product), finds a shortfall, drafts a purchase requisition (write tool), and routes it to a buyer for approval before anything is created in the ERP.',
  'An agent is an LLM that plans, calls tools, observes results and iterates — with guardrails and human approval on consequential actions.',
  'An agent runs an LLM in a loop: it plans the next step, calls a tool such as a data query or a business API, reads the result, and repeats until done. In enterprises the engineering is in the controls: narrow permission-checked tools, validation, step and cost limits, human approval for actions, and full tracing.',
  'An agent is an LLM in a control loop. Given a goal, it decides on a step, calls a tool — query a data product, look up an order, create a draft requisition — observes the result, and continues, possibly handing off to other agents or a human. The model provides the reasoning; the engineering provides everything that makes it safe in a business process. Tools are narrow, typed, idempotent APIs that check authorisation with the end user\'s identity. Read tools are cheap; write tools require confirmation or human approval and are audited. Guardrails cap steps and spend, validate parameters, and treat tool outputs as untrusted to resist prompt injection. Every step is traced so you can debug and evaluate. And I only use an agent where the path really varies — if the steps are known, a deterministic workflow with LLM calls in it is cheaper and more reliable. For a data engineer the biggest lever is data: agents are only as good as the governed, well-described data products they can query.',
  ('Where would you NOT use an agent?', 'Fixed, auditable processes with known steps (use a workflow), high-volume low-latency paths, and anything where an error is irreversible without human approval.'),
  'Giving an agent broad write access through a service account "to make the demo work".'),

C('llm-rag-agent', 'm-agentic', 'LLM vs RAG vs Agent', 'must', 'GENERAL',
  'An LLM answers from its training. RAG retrieves relevant documents or data first and answers grounded in them. An agent plans and calls tools — possibly including retrieval — to complete multi-step tasks and take actions.',
  'Choosing the simplest pattern that solves the problem is the most important AI architecture decision.',
  'LLM: an expert answering from memory. RAG: the expert who first looks things up in your files. Agent: the expert who also picks up the phone and gets things done.',
  'Pure function → function with a database lookup → orchestrator calling multiple services.',
  'LLM: prompt → response; knowledge frozen; hallucination risk on specifics. RAG: query → retrieve (vector / keyword / hybrid / SQL) → augment prompt → generate with citations; fresh, private knowledge; quality bounded by retrieval. Agent: goal → plan → tool calls (including RAG, SQL, APIs) → observe → iterate → act; handles tasks, not just questions; most powerful and most risk.',
  'Escalate only as needed: prompt engineering → RAG → workflow with tools → agent. Evaluation difficulty and risk rise at each step.',
  '"What is our return policy?" → RAG. "Why did my order ship late?" → agent with order and logistics lookups. "Write a tagline" → LLM.',
  'LLM answers from memory; RAG grounds answers in retrieved data; agents plan and take actions with tools.',
  'An LLM answers from training data; RAG retrieves the relevant enterprise documents or data first so answers are grounded and current; an agent goes further, planning and calling tools to complete tasks. I pick the simplest one that solves the problem, because risk and evaluation cost rise with each.',
  'They are three levels of capability. A bare LLM generates from what it learned in training — fluent, but not aware of your data, and prone to inventing specifics. RAG adds a retrieval step: find the relevant policies, documents or records, put them in the prompt, and answer with citations — so answers are current, private and checkable, and quality depends mostly on retrieval. An agent adds planning and tools: it can run several retrievals, query structured data, call business APIs, and take actions, iterating until a task is done. Each step up adds capability, risk and evaluation difficulty, so I choose the simplest pattern that meets the need, and often the best design is a fixed workflow with RAG at one step rather than a free-roaming agent.',
  ('A customer wants an agent. How do you decide if they need one?', 'Ask what decisions vary per request and what actions are required. If it is Q&A over documents, RAG. If steps are fixed, a workflow. Agent only when the path varies and actions are needed.'),
  'Jumping to multi-agent systems for a document Q&A problem.'),

C('rag', 'm-rag', 'RAG: chunking, embeddings, vector search, hybrid retrieval, reranking', 'must', 'JD',
  'Retrieval-augmented generation: find the most relevant pieces of your content for a question, give them to the LLM, and ask it to answer only from them.',
  'LLMs do not know your private, current data, and they invent plausible details. Grounding answers in retrieved sources fixes both — if retrieval is good.',
  'An open-book exam: the quality of the answer depends on finding the right page.',
  'It is a search system with an LLM on the end. Indexing is an ETL pipeline; retrieval is a search query; the prompt is a template; freshness and access control are your usual cache-invalidation and authorisation problems.',
  'Ingest: extract text, clean, chunk (by structure; 200–800 tokens with overlap), attach metadata (source, date, ACL). Embed chunks into vectors; store in a vector index (Databricks Vector Search, HANA Cloud vector engine — VERIFY — pgvector, etc.). Query: embed the question, retrieve top-k by similarity, often hybrid with keyword (BM25) for names and codes, filter by metadata/ACL, rerank with a cross-encoder, then prompt with sources and require citations. For structured data, retrieval is SQL against governed tables (text-to-SQL or predefined tools), not vectors.',
  'Most RAG failures are retrieval failures: bad chunking, missing metadata filters, stale index, no keyword search for exact identifiers. Enforce access control at retrieval time (filter by the user\'s permissions) — never rely on the prompt. Keep the index fresh with incremental pipelines (CDC on documents). Evaluate retrieval separately (recall@k) from generation (faithfulness).',
  'Support assistant over 40,000 product manuals and tickets: hybrid retrieval, filtered to products the customer owns, reranked to 5 chunks, answer with citations; index updated hourly from a Delta table.',
  'RAG retrieves relevant, permitted content and asks the LLM to answer only from it, with citations.',
  'RAG indexes content as chunks with embeddings and metadata, retrieves the most relevant permitted chunks for a question — usually hybrid vector plus keyword search with reranking — and has the LLM answer from them with citations. Most quality problems are retrieval problems, so I evaluate retrieval separately.',
  'RAG is a search system with a generator on the end, and I engineer it that way. Indexing is a data pipeline: extract and clean documents, chunk them along their structure, attach metadata including access-control labels, embed, and load an index — incrementally, so it stays fresh. At query time, I combine vector similarity with keyword search, because semantic search misses exact identifiers like order numbers and part codes; filter by the user\'s permissions at retrieval time, never in the prompt; rerank; and pass a small set of chunks with an instruction to answer only from them and cite. For structured enterprise data, the "retrieval" is a governed SQL query, not a vector search. I evaluate in two layers — retrieval recall and generation faithfulness — because when RAG is wrong, it is usually because the right chunk was never retrieved. At Atlassian I designed AI features using LLM orchestration and RAG with LangChain and the GitHub API, so this is familiar ground.',
  ('Your RAG assistant answers confidently but cites the wrong policy version. Fix?', 'Index freshness and metadata: version/effective-date metadata, filter to current versions, incremental re-indexing on change, and a recency signal in ranking; add an eval case.'),
  'Tuning the prompt when the retrieval is wrong.'),

C('ent-ai', 'm-entai', 'Enterprise AI: security, authorisation, observability, cost, latency', 'must', 'JD',
  'Taking an AI system from demo to production inside an enterprise: the data foundation, security and authorisation, observability, evaluation, cost and latency controls around the model.',
  'Demos are easy; enterprises need the AI to respect permissions, protect data, be auditable, cost what was budgeted, and be measurably correct.',
  'Hiring a brilliant contractor: you still need badge access rules, a supervisor, timesheets and quality reviews.',
  'This is your Staff-level platform experience: gateways, authn/z, rate limits, observability, SLOs, cost attribution — applied to model calls and agents.',
  'Stack: governed data products → retrieval / tools layer → orchestration (agent/workflow) → model gateway (routing, rate limits, caching, redaction, logging) → application. Security: end-user identity propagated to every tool and retrieval; least privilege; secrets out of prompts. Threats: prompt injection (direct and indirect via retrieved content/tool output), data exfiltration through tools, over-privileged actions. Observability: traces per request (prompt, retrieved docs, tool calls, tokens, latency, cost), feedback signals. Cost/latency: model routing (small model first), caching, prompt size control, batching, streaming.',
  'Treat model output as untrusted input to the next system. Separate instructions from data in prompts; constrain tools rather than trusting the model to refuse. Budget per request and per tenant. Keep a human-in-the-loop for consequential actions and a kill switch.',
  'An AI assistant for finance: queries only gold data products via tools that check the user\'s cost-centre permissions, logs every trace, routes simple questions to a smaller model, and requires approval before posting anything.',
  'Enterprise AI is the platform around the model: governed data, identity-aware tools, security against injection, tracing, evaluation, and cost controls.',
  'Taking AI to production in an enterprise is mostly platform engineering: governed data, tools that enforce the end user\'s permissions, a model gateway with redaction, limits and logging, defences against prompt injection, full tracing, continuous evaluation, and cost and latency budgets.',
  'The model is the smallest part. Underneath it, the data foundation decides answer quality: governed, documented data products. Around it, security: every retrieval and tool call carries the end user\'s identity, so the agent can never see more than the user could; tools are least-privilege; and model output and retrieved content are treated as untrusted, which is the defence against prompt injection — constrain what tools can do rather than hoping the model refuses. A model gateway centralises routing, rate limits, caching, PII redaction and logging. Every request produces a trace — prompt, retrieved documents, tool calls, tokens, latency, cost — which feeds debugging and evaluation. Cost and latency are managed by routing easy requests to smaller models, caching, and keeping prompts tight. This is the same shape as the cross-product GraphQL Gateway I architected at Atlassian: one governed entry point with identity, limits and observability in front of many backends.',
  ('How do you defend against indirect prompt injection in retrieved documents?', 'Treat retrieved text as data, not instructions; limit tool permissions so injected instructions cannot do harm; require confirmation for writes; filter/flag suspicious content; monitor tool-call anomalies.'),
  'Relying on a system prompt ("never reveal…") as the security control.'),

C('llm-eval', 'm-llmeval', 'LLM evaluation: model, retrieval, system, safety, business', 'must', 'JD',
  'Measuring whether an AI system is good enough, at several levels: is the model\'s answer right, did retrieval find the right content, does the whole system complete tasks, is it safe, and does it move a business metric.',
  'LLM output is non-deterministic and open-ended; without evaluation, every prompt or model change is a guess, and quality regressions reach customers.',
  'Like testing a new employee: written quiz (model), whether they find the right files (retrieval), whether they finish real jobs (system), whether they follow the rules (safety), and whether the team performs better (business).',
  'Evaluation is the test suite and the monitoring for AI. Golden datasets are regression tests; online metrics are SLOs; LLM-as-judge is an automated reviewer that itself needs validating.',
  'Model: correctness vs reference, faithfulness/groundedness to sources, relevance, completeness, format. Retrieval: recall@k, precision, MRR, context relevance. System/agent: task success rate, correct tool selection and parameters, steps, latency, cost per task. Safety: PII leakage, toxicity, jailbreak and prompt-injection resistance, policy compliance. Business: resolution rate, time saved, deflection, user satisfaction, error cost. Methods: golden sets (curated with domain experts), LLM-as-judge with rubrics (calibrated against human labels), human review, A/B and online feedback, regression gating in CI.',
  'Accuracy alone is not enough: an answer can be accurate but ungrounded (lucky), grounded but incomplete, correct but leak PII, or correct but too slow or expensive to use. Weight errors by business cost — a wrong invoice amount is not equal to a clumsy sentence. Version prompts, models, retrievers and datasets together so results are reproducible.',
  'Before switching models for a support agent: run 500 golden cases; faithfulness 0.92 → 0.95, task success 81% → 84%, but cost +30% and p95 latency 4.1 s → 6.0 s — route only complex cases to the new model.',
  'Evaluate at five levels — model, retrieval, system, safety, business — because accuracy alone hides most failures.',
  'I evaluate AI systems at five levels: model output quality like faithfulness and correctness, retrieval quality like recall, system task success including tool use, latency and cost, safety such as PII leakage and injection resistance, and business impact. Golden datasets with experts, calibrated LLM judges and human review, gated in CI.',
  'I treat evaluation as the test suite and monitoring of an AI system, and I measure at five levels because each hides different failures. Model level: is the answer correct, faithful to its sources, complete. Retrieval level: did we fetch the right content — if recall is low, no prompt will fix it. System level: for agents, did the task succeed, were the right tools called with the right parameters, at what latency and cost. Safety: PII leakage, prompt-injection and jailbreak resistance, policy compliance. Business: did resolution rate, time saved or error cost actually improve. Accuracy alone is not enough — an answer can be right by luck, right but leaking personal data, or right but too slow and expensive to deploy. Practically: a golden set built with the customer\'s domain experts, LLM-as-judge with rubrics calibrated against human labels, regression gates in CI for prompt and model changes, and online feedback in production. My current work at xAI is expert evaluation of AI-generated code against multi-dimensional rubrics — correctness, security, reliability, production readiness — so this is an area where I have direct experience.',
  ('How do you know your LLM-as-judge is trustworthy?', 'Calibrate it on a human-labelled sample (agreement rate / Cohen\'s kappa), use explicit rubrics and reference answers, check for position and verbosity bias, and re-validate when the judge model changes.'),
  'Reporting one accuracy number on a handful of hand-picked examples.'),
]
