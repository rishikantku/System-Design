# -*- coding: utf-8 -*-
"""Frequency evidence, merges and new questions — 15 Oct 2026.

Sources:
  IDB   InterviewDB LinkedIn system design list, supplied by the reader (21 questions, Oct 2026)
  LCD   LeetCode Discuss reports supplied by the reader (15 Oct 2026), verbatim below
  EARLY reports found in my earlier research passes, already recorded in video/design/index.py
        (Exponent, Glassdoor, Blind, Taro, LeetCode Discuss). Counted only where clearly a different report.

Counting rule: one count per independent report. A report that might be the same interview as another
(e.g. an earlier LeetCode Discuss find that matches a pasted one) is counted once. The InterviewDB
listing counts as one report. "reports" is evidence, not a probability.
"""

LCD = 'LeetCode Discuss (supplied by you, Oct 2026)'

# Reports per question id. Each: (source, wording or summary, what happened — '' if not reported)
REPORTS = {
 'metrics': [
  (LCD, 'Design a metrics platform: services publish metrics; store, aggregate, and display on a dashboard; implement alerting thresholds.', ''),
  (LCD, 'Hundreds of machines, each exposing thousands of statistics as [source, metric-name, value]. Collect and aggregate them; consumers are a graphing system (plot sources t1→t2) and an alerting system (above/below a threshold).', ''),
  (LCD, 'Design metric monitoring system.', 'Self verdict: strong hire — explained everything, and even discussed out-of-scope things.'),
  (LCD, 'Metrics aggregator, monitoring system — metrics aggregating, querying, graphing and alarming.', ''),
  (LCD, 'Metrics aggregation and visualization.', 'Was driving the interview most of the time.'),
  ('InterviewDB', 'Host health across three data centres, hundreds of thousands of hosts, with history and a UI (merged here — same system).', ''),
  ('Earlier research', 'Metrics gathering and aggregation — Blind ×2, Glassdoor (lesson 2.3).', ''),
 ],
 'kvstore': [
  ('InterviewDB', 'Key-value store on a file interface: append, read bytes at an offset, create.', ''),
  (LCD, 'Design a Key-Value Store — components, data partitioning, replication, consistency model, use cases.', ''),
  (LCD, 'Design KV store — started with purpose, storage, compute, sharding.', 'Did not follow a standard structure.'),
  (LCD, 'Key-value based system — internal architecture, append-only log file management, log compaction, disk cleanup strategies.', 'Missed 2–3 follow-up questions.'),
 ],
 'topn': [
  ('InterviewDB', 'Top-N most requested items in the last 24 hours across several hundred machines.', ''),
  (LCD, 'Top K heavy hitters over time windows of 5 minutes, 1 hour and 24 hours.', 'Interviewer satisfied, but the candidate added a coordination service that was not needed and it caused a disagreement.'),
  ('Earlier research', 'Trending articles / Top-K videos — 2 LeetCode Discuss reports (lesson 11.2).', ''),
 ],
 'typeahead': [
  ('InterviewDB', 'Typeahead for the LinkedIn search bar, scaled to 1B users.', ''),
  ('Earlier research', 'Typeahead / autosuggest — Exponent ×2, Glassdoor (lesson 2.2).', ''),
 ],
 'denylist': [
  ('InterviewDB', 'Denylist malicious IPs and keep every web server up to date (isMalicious given).', ''),
  (LCD, 'Design a distributed IP deny list: a function says whether an IP should be denied; build the denylist and sync it with all the servers.', ''),
  (LCD, 'In a system like LinkedIn, intercept malicious requests and deny them. Assume a service isMaliciousRequest is available.', ''),
 ],
 'mq': [
  ('InterviewDB', 'Design a message queue system.', ''),
  ('Earlier research', 'Kafka-like queue — LeetCode Discuss, Blind (lesson 3.3).', ''),
 ],
 'notify': [
  ('InterviewDB', "LinkedIn's notification delivery across push, email and in-app.", ''),
  (LCD, 'Design a notification system. Add rate limiting on categories (e.g. 5 marketing notifications per day per user) and handle user preferences.', 'Verdict: No / Lean hire. The same round also asked how project success was measured (performance testing, p90).'),
 ],
 'scheduler': [
  (LCD, 'Design a distributed job scheduler. You are given an API to fetch machines for running jobs. Design a system that schedules jobs, executes them, and triggers alerts.', 'Onsite round 3 (HLD).'),
  ('Earlier research', 'Distributed job scheduler — Blind, Infrastructure loop, Sep 2025 (lesson 3.2).', ''),
 ],
 'ratelimit': [('InterviewDB', 'Design a rate limiter.', ''), ('Earlier research', '1 independent recent report (lesson 4.1).', '')],
 'feed': [('InterviewDB', 'Design a news feed system for LinkedIn.', ''), ('Earlier research', 'Recurring in aggregator lists (lesson 7.1).', '')],
 'calendar': [('InterviewDB', 'Design a calendar system.', ''), ('Earlier research', '1 recent report (lesson 8.3).', '')],
 'logging': [('InterviewDB', 'Distributed logging for an analytics service.', ''), ('Earlier research', '1 report in research pass 3 (lesson 6.3).', '')],
 'cache': [
  (LCD, 'Flexible in-memory cache with customisable capacity and eviction policies (LRU, lowest priority); LLD first, then HLD across many nodes — hot keys in a write-heavy setup, Redis internals.', 'Round opened with project and leadership questions; HLD extension after the LLD was agreed.'),
 ],
}
# Not placed: "Didn't feel great in this round, struggled on gateway, file logs" — too little detail to tell
# which question it was (possibly the logging system). Kept here so it is not lost; not counted.
UNPLACED = ['"Didn\'t feel great in this round — struggled on gateway, file logs." (LeetCode Discuss) — possibly the logging system; not counted.']

# Rank: by report count, ties by how recent and detailed the reports are. InterviewDB-only questions
# follow in the reader's InterviewDB order (most recently reported first).
ORDER = ['metrics', 'kvstore', 'topn', 'typeahead', 'denylist', 'mq', 'notify', 'scheduler', 'ratelimit', 'logging',
         'feed', 'calendar', 'cache',
         'coderpad', 'lynda', 'jobrec', 'photos', 'logistics', 'spell', 'quota', 'geoviz', 'inmail', 'svcauthz']

# The questions not in the InterviewDB list: their primary statement, verbatim from the reports.
NEW = {
 'metrics': dict(title='Metrics monitoring platform (collect, aggregate, graph, alert)', lesson='2.3 + 9.2', statement=
"""We have a big deployment with hundreds of machines each of which is exposing thousands of statistics. You can think that each statistic is represented by the tuple [source, metric-name, value].
We want to be able to collect and aggregate those tuples in a scalable manner. The main consumers for this system are:

A graphing system - For a certain metric-name, plot a set of sources from time t1 to t2
e.g. Memory usage of host-1, host-2, host-3 for the past week
An alerting system- Issue an alert (email, etc) when a certain metric-name goes above/below a certain threshold
e.g. Memory usage goes above 70%"""),
 'scheduler': dict(title='Distributed job scheduler (fetch machines, execute, alert)', lesson='3.2 + 11.5', statement=
"""Design a distributed job scheduler. You are given an API to fetch machines for running jobs. Design a system that schedules jobs, executes them, and triggers alerts."""),
 'cache': dict(title='Flexible in-memory cache — pluggable eviction, then distributed', lesson='11.3', statement=
"""Design a flexible in-memory cache with customizable capacity and eviction policies.

The cache should allow users to define:

Capacity: Specify how much data the cache can hold based on memory resources and data size.
Eviction Policy: Choose strategies for removing items when the cache is full, such as Least Recently Used (LRU) or Lowest Priority.
This flexibility ensures the cache can be tailored to meet specific requirements, balancing resource usage and performance.

(Reported follow-on: once the low-level design was agreed, extend it to many nodes in a distributed setup — the challenges, hot keys in a write-heavy setup, and some Redis internals.)"""),
}
MERGED_AWAY = {'hosthealth': 'metrics'}    # InterviewDB question folded into another card
