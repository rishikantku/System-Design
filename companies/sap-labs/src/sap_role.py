# -*- coding: utf-8 -*-
"""SAP Labs — Forward Deployed Data Engineering Expert (Req. 458124): role facts and modules 1–2.

Labels used everywhere:
  JD       quoted from SAP's own posting for req. 458124 (read 9 Oct 2026 via freehire.me mirror + search
           snippets of jobs.sap.com; SAP's own page did not render for automated reading)
  GENERAL  general industry knowledge
  VERIFY   SAP-specific claim from public sources — verify against the latest SAP documentation
  INFER    my reading of what the role implies — not stated by SAP
"""

JD_SOURCES = [
 ('SAP Careers — Forward Deployed Data Engineering Expert, Bangalore', 'https://jobs.sap.com/job/Bangalore-Forward-Deployed-Data-Engineering-Expert-KA-560066/1398931533/'),
 ('Mirror of the posting with Requisition ID 458124 (freehire.me)', 'https://freehire.me/jobs/forward-deployed-data-engineering-expert-sap-idwwqnp7'),
]

JD_FACTS = [
 ('Requisition', '458124 · Bangalore, India · Hybrid · 0–10% travel · Regular full time'),
 ('Team', '"a growing AI and industry expert team dedicated to serving customers across the region (Americas, Europe, Asia)"'),
 ('Mission', '"design, build, and operate scalable data pipelines and platforms that enable analytics, reporting, and advanced data driven use cases embedded directly within customer environments and fast-moving delivery teams"'),
 ('Experience', '"6+ years experience in data engineering, including the design and implementation of scalable data pipelines and data models"'),
 ('Stack', 'SQL; Python; "Hands-on experience with PySpark, Databricks, and big data processing frameworks"; Airflow; Kafka; SAP HANA; lakehouse (Parquet, Delta Lake)'),
 ('Pipelines', '"Develop and manage batch and real-time data pipelines leveraging workflow orchestration tools (e.g., Airflow) and streaming technologies such as Kafka"'),
 ('Governance', '"Ensure data quality, governance, compliance, and PII protection"; "Solid understanding of data quality, data governance, and data lifecycle management in enterprise environments"'),
 ('Engineering practice', '"implementing CI/CD pipelines and applying best practices with Docker and Git within data engineering workflows"'),
 ('AI', '"Ability to operate effectively in an Agentic AI context, contributing to the design, application, and responsible use of AI agents within complex business processes"'),
 ('Customer', '"Embed directly into customer projects and fast moving cross functional teams to rapidly understand business processes, technical landscapes, and operational challenges"; "translate business and analytical needs into robust technical data solutions"'),
]

# Requirement → priority → likely gap for this candidate → where it is taught
# priority: must | should | nice   gap: none | some | large
REQ_MATRIX = [
 ('Scalable ETL/ELT pipelines', 'JD', 'must', 'some', 'm-de', 'Pipeline thinking transfers from microservices; the batch/lakehouse idioms are new.'),
 ('PySpark / big data processing', 'JD', 'must', 'large', 'm-spark', 'The deepest gap and the most likely technical drill.'),
 ('Databricks', 'JD', 'must', 'large', 'm-databricks', 'Know what it is, why it exists, how jobs run in production.'),
 ('Lakehouse — Parquet, Delta Lake', 'JD', 'must', 'large', 'm-lakehouse', 'Expect "Parquet vs Delta" and "why a lakehouse".'),
 ('SQL (incl. window functions)', 'JD', 'must', 'some', 'm-sql', 'Window functions and dedup/top-N are the common live questions.'),
 ('Kafka, real-time pipelines', 'JD', 'must', 'none', 'm-kafka', 'Your strength — reframe it for CDC and lake ingestion.'),
 ('Airflow orchestration', 'JD', 'should', 'large', 'm-airflow', 'Concepts are easy; know retries, idempotency and backfill.'),
 ('SAP HANA', 'JD', 'should', 'large', 'm-hana', 'Interview-safe understanding; never claim hands-on.'),
 ('Data quality, governance, PII', 'JD', 'must', 'some', 'm-quality', 'Enterprise customers care; tie to your isolation/egress work.'),
 ('Agentic AI in business processes', 'JD', 'must', 'some', 'm-agentic', 'Your RAG + xAI evaluation work is a genuine edge.'),
 ('Customer embedding, translating needs', 'JD', 'must', 'some', 'm-scenarios', 'The FDE part: discovery before architecture.'),
 ('Docker, Git, CI/CD for data', 'JD', 'should', 'none', 'm-de', 'Known; mention data-specific CI (tests on data, not just code).'),
 ('Data modelling', 'JD', 'should', 'some', 'm-de', 'Star schema, SCD Type 2, grain.'),
]

FDE_COMPARE = [
 ('Forward Deployed Engineer', 'Ships production software inside a customer\'s environment, fast, then turns what worked into reusable patterns for the product.', 'Working system in the customer\'s hands; feedback to product', 'Writes and runs code; owns outcome'),
 ('Software Engineer (product)', 'Builds the product for many customers at once.', 'A feature used by everyone', 'Writes code; far from any one customer'),
 ('Solutions Architect', 'Designs how the product fits a customer\'s landscape; pre- and post-sales.', 'A design / reference architecture', 'Usually does not own production code'),
 ('Consultant', 'Delivers a project to a statement of work.', 'Hours / deliverables', 'Implements to spec; the engagement ends'),
]

FDE_NOTES = [
 ('What FDE means', 'GENERAL', 'An engineer embedded with a customer who builds and deploys real software against real data, with the speed of a startup and the accountability of an owner. Popularised by Palantir; now used by AI companies and enterprise vendors because AI value only appears once it runs on the customer\'s own data and processes.'),
 ('Why SAP would use it', 'INFER', 'SAP customers run their business on SAP systems, but AI and analytics value depends on getting that data — plus non-SAP data — into governed, AI-ready shape inside each customer\'s landscape. An embedded data engineer shortens the path from "interesting AI demo" to "agent running on our order data". The JD\'s team is "AI and industry expert", which fits that reading.'),
 ('Customer impact', 'INFER', 'Measured as a business outcome the customer can see — a process that runs faster, a report that is trusted, an agent that resolves a case — not as tickets closed.'),
 ('Reusable patterns', 'INFER', 'Every engagement should leave behind something the next one reuses: an ingestion template, a data-quality rule set, a governed data product, an agent tool. That is the difference between an FDE and a consultant.'),
 ('Expert level', 'INFER', 'Expected to lead the technical approach in an engagement without supervision, make architecture calls under ambiguity, talk to customer architects and executives, and mentor others — consistent with the JD\'s 6+ years in data engineering.'),
]

EVALUATING = [
 ('Technical depth', 'Can you build the pipeline yourself — PySpark, SQL, Delta, Airflow — not just draw it?', 'JD'),
 ('Architecture', 'Do your designs handle scale, failure, cost and governance, with explicit trade-offs?', 'INFER'),
 ('Data engineering judgement', 'Batch vs streaming, ETL vs ELT, modelling, quality — do you choose for reasons?', 'JD'),
 ('AI', 'Can you put agents on enterprise data responsibly — grounding, authorisation, evaluation?', 'JD'),
 ('Customer communication', 'Can you discover the real problem and explain trade-offs to non-engineers?', 'JD'),
 ('Problem solving under ambiguity', 'What do you do in week one with an unfamiliar landscape?', 'INFER'),
 ('Ownership', 'Do you own the outcome in production, not just the design?', 'INFER'),
]
