# -*- coding: utf-8 -*-
"""Designs added to close gaps found in research pass 2:
a metrics/alerting platform (reported, aggregated) and a calendar LLD
(reported ~Sep 2026 on the Exponent bank — the most recent design signal found)."""

GAP_DESIGNS = [
 dict(id='metrics', title='Design a metrics and alerting platform', topic='Observability platform', prio='p1',
  why='Reported as a LinkedIn design question in aggregated Glassdoor summaries: collect metrics, store them in a time-series '
      'database, put monitoring and alerting on top. It is also the platform every other system on this page depends on, which '
      'makes it a fair question for a Systems & Infrastructure role.',
  ask=['Who are the users — engineers debugging, automated alerting, or both?',
       'Cardinality: how many distinct series, and who controls the label keys?',
       'Retention: full resolution for how long, then what?',
       'Is a lost data point acceptable? (For metrics usually yes; for billing counters no.)',
       'Push or pull collection? It changes discovery, firewalls and failure semantics.'],
  fr=['Ingest counters, gauges and histograms from every service',
      'Query by metric name, labels and time range',
      'Evaluate alert rules continuously and notify',
      'Dashboards over aggregates'],
  nfr=['Ingest must never back-pressure the applications being measured',
       'Dashboard queries in a second or two',
       'Alerting must survive partial failure of the platform — silent monitoring is the worst outcome',
       'Predictable cost per series, because cardinality grows without limit unless you bound it'],
  scale='10,000 hosts × 200 series each = 2 million active series; at 10-second resolution that is 200k samples per second. '
        'Each sample compresses to roughly 1–2 bytes with delta-of-delta timestamps and XOR-encoded values, so a year is a few '
        'hundred GB. The number that actually decides the design is cardinality, not volume.',
  api='`POST /ingest` (batched); `GET /query?expr=&start=&end=&step=`; alert rules as versioned config with an evaluation '
      'interval and a for-duration. Rules are code: reviewed, versioned, deployed.',
  data='Series key = metric name plus its sorted label set, hashed to a series id. Storage is immutable blocks per time window: '
       'timestamps delta-of-delta encoded, values XOR encoded, plus an inverted index from label pairs to series ids.',
  arch='Agents or scrapers → ingestion tier (validate, enforce cardinality budgets, shard by series id) → write-ahead log → '
       'in-memory head block → compacted immutable blocks on disk and object storage → query tier fanning out and merging → '
       'rule evaluator using the same query path → notifier with grouping, inhibition and silences.\n\n'
       'Two independence rules are worth saying out loud: **ingest must never be blocked by query load**, and **alerting must '
       'not depend on the dashboard tier**.',
  deep=['**Cardinality is the whole problem.** One engineer adding a user id as a label turns 200 series into 20 million. '
        'Enforce per-team series budgets at ingest, reject with an actionable error naming the offending label, and expose the '
        'top offenders. This is the answer that shows you have operated one of these.',
        '**Downsampling and retention tiers.** Raw for days, one-minute rollups for weeks, five-minute for a year. Rollups are '
        'computed once at compaction, never per query.',
        '**Alert evaluation at scale.** Thousands of rules, each a query. Shard rules across evaluators by hash; make evaluation '
        'idempotent so a restart cannot double-fire; the `for` duration needs state, which is what makes evaluators stateful.',
        '**Push versus pull.** Pull gives discovery and a free liveness signal — a target that cannot be scraped is down. Push '
        'works through NAT and for short-lived jobs. Most platforms run both, with a gateway for batch jobs.',
        '**Histograms.** Percentiles cannot be averaged across hosts. Either store buckets and compute quantiles at query time, '
        'or use a mergeable sketch such as t-digest or DDSketch. Saying this unprompted is a strong signal.'],
  fails=['Ingest saturated → shed by tenant priority, keep the write-ahead log, never block the application.',
         'One expensive dashboard → per-query cost limits, and a separate pool for rule evaluation.',
         'Storage unavailable → the head block accepts for a bounded window, then sheds loudly.',
         'The platform itself down → a small independent watchdog on different infrastructure must alert on it. A monitoring '
         'system that cannot report its own death is the classic failure.'],
  scaling=['Shard by series id for write and query; series ids are stable, so shards are stable.',
           'Replicate head blocks for durability; blocks in object storage need no replication of their own.',
           'Separate hot (recent, in memory) from cold (object storage, slower queries).'],
  obs=['Active series per team — the leading indicator of both cost and collapse',
       'Ingest lag and shed rate', 'Rule evaluation duration and skipped evaluations',
       'Query cost distribution', 'Notification latency'],
  sec=['Per-tenant isolation enforced in the ingest and query tiers, not by convention.',
       'Labels leak topology and sometimes personal data — treat label values as untrusted, and redact by policy.'],
  cost='Memory for the index and head blocks dominates, and it scales with cardinality rather than samples. The most effective '
       'lever is a per-team series budget: a social control implemented technically.',
  trade=[('Resolution vs cost', 'Ten-second resolution costs four times forty-second, for insight you may never use'),
         ('Push vs pull', 'Discovery and liveness versus firewall friendliness'),
         ('Sketches vs buckets', 'Mergeable percentiles versus exact ones'),
         ('Series budgets', 'Protects the platform, annoys teams — and you will still need them')],
  evolve='Phase 1: pull collection, local blocks, threshold alerts. Phase 2: sharded ingest, object-storage blocks, '
         'downsampling, rule sharding. Phase 3: multi-tenant budgets and an independent watchdog. Put cardinality limits in at '
         'phase 1 — retrofitting them is a political project, not a technical one.',
  senior='"Agents push metrics into a time-series database and a dashboard queries it, with alerts on top."',
  staff='"The design question is cardinality control and the independence of the alerting path. Per-team series budgets enforced '
        'at ingest with actionable rejections, rollups computed at compaction rather than per query, rule evaluation sharded '
        'separately from dashboards, and a small watchdog on separate infrastructure — because a monitoring platform that cannot '
        'alert on its own failure is worse than none."'),

 dict(id='calendar', title='Design a calendar (low-level design)', topic='LLD · Modelling', prio='p1',
  why='Logged on the Exponent question bank as asked about three weeks ago (≈September 2026) — the most recent design signal '
      'found in either research pass. It is graded on modelling rather than scale, so it doubles as craftsmanship practice.',
  ask=['Single user, or shared calendars with attendees and permissions?',
       'Recurrence: simple daily and weekly, or full RRULE with exceptions?',
       'Time zones: if the organiser moves zone, does the meeting move? (Usually no — it is a wall-clock commitment.)',
       'Do we need free/busy search and conflict detection, or only storage?',
       'Is this one service or one process? For an LLD it is usually the latter — confirm before designing for scale.'],
  fr=['Create, update and delete events, including a single occurrence of a recurring series',
      'Expand a recurrence into occurrences for a date range',
      'Detect conflicts across a set of attendees',
      'Invite attendees and track responses',
      'Find a free slot of length L for a group'],
  nfr=['Correct across time zones and daylight-saving transitions — this is the actual difficulty',
       'Expansion must always be bounded; an infinite series must never be materialised',
       'Clean extension points for new recurrence rules and external calendar providers'],
  scale='Scale is secondary here, but one number shapes the model: a daily event running since 2015 is about 4,000 occurrences. '
        'So you store the rule, not the occurrences, and expand lazily for the requested window.',
  api='`CreateEvent(spec)`, `UpdateEvent(id, scope)`, `DeleteEvent(id, scope)` where `scope` is single, this-and-following or '
      'all; `Expand(calendarId, from, to)`; `FindFreeSlot(attendees, duration, window)`; `Respond(eventId, attendee, status)`. '
      'The scope parameter is the heart of the design, and most candidates never introduce it.',
  data='`Event { Id, OrganiserId, Title, LocalStart, Duration, TimeZoneId, RecurrenceRule?, Attendees[] }` plus '
       '`RecurrenceException { SeriesId, OriginalStart, Action (cancelled or moved), Override? }`. Store **local wall-clock time '
       'plus the zone id**, not a UTC instant, for recurring events — otherwise a daylight-saving change silently shifts every '
       'future occurrence by an hour.',
  arch='Three collaborating pieces, and the seams between them are what is being graded:\n\n'
       '1. **Model** — events, series, exceptions, attendees; immutable value objects where possible.\n'
       '2. **Recurrence engine** — `IRecurrenceRule.Occurrences(from, to)`, implemented per rule type (daily, weekly-by-day, '
       'monthly-by-position), lazy and bounded by the window.\n'
       '3. **Services** — conflict detection and free-slot search, built on interval logic over expanded occurrences.\n\n'
       'Expansion is always: rule occurrences within the window, minus cancellations, plus moved overrides.',
  deep=['**Recurrence with exceptions.** A series plus a sparse exception list beats materialising occurrences. Editing this '
        'occurrence writes an override; this-and-following splits the series at a date; all edits the rule. That three-way scope '
        'is the question behind the question.',
        '**Time zones and DST.** A weekly 09:00 London meeting stays at 09:00 local across the DST boundary, so it moves in UTC. '
        'Store wall clock plus zone and convert at expansion. A meeting starting at 01:30 on a spring-forward night either '
        'shifts or is skipped — pick a rule, document it, and test it.',
        '**Conflict detection.** Expand both sides into half-open intervals and sweep. Half-open means back-to-back meetings do '
        'not conflict, which is what users expect.',
        '**Free-slot search.** Merge every attendee\'s busy intervals, invert within working hours, filter by duration — the '
        'merge-intervals problem wearing a suit.',
        '**Extensibility.** A new recurrence type must not touch the services; an external feed plugs in behind a read '
        'interface. Name both seams out loud; this is the craftsmanship signal.'],
  fails=['An unbounded recurrence expanded without a window → memory blow-up. The API must require a range.',
         'A time-zone database update changes historical offsets → expansions shift; pin the zone data version per stored event.',
         'Concurrent edits to one series → optimistic concurrency with a version; last-writer-wins is wrong for a split.',
         'An attendee in an unconsidered zone → always render in the viewer\'s zone, never the organiser\'s.'],
  scaling=['Cache expanded windows per calendar with a short TTL, invalidated on any write to the series.',
           'Precompute the next N occurrences for reminder scheduling instead of scanning at fire time.',
           'Shard by calendar id if this ever becomes a service.'],
  obs=['Expansion time per query window', 'Cache hit rate on expanded windows',
       'Conflict-detection latency for large groups', 'Reminder accuracy: scheduled versus actual fire time'],
  sec=['Titles and attendee lists are sensitive: free/busy must be answerable without exposing details.',
       'Permissions: organiser, editor, viewer, free/busy-only — enforced in the service, never in the UI.'],
  cost='Not a cost question. If pressed, the levers are caching expansions and bounding recurrence windows, both of which also '
       'fix latency.',
  trade=[('Store the rule vs store occurrences', 'Compact and correct versus trivially queryable — a cache gives you both'),
         ('Wall clock plus zone vs UTC instant', 'Correct across DST for recurring events versus simpler arithmetic for one-offs'),
         ('Expressive recurrence', 'Covers what users actually do versus a much larger surface to test'),
         ('Three edit scopes', 'More code, and the only behaviour users expect')],
  evolve='Phase 1: single events, conflict detection, half-open intervals. Phase 2: simple recurrence with the three edit scopes '
         'and exceptions. Phase 3: full RRULE, free-slot search, external feeds. Get the time-zone model right in phase 1; it is '
         'the one decision that is expensive to change later.',
  senior='"An Event table with start and end times and a recurrence field."',
  staff='"The decision that matters is storing wall-clock time plus a zone id for recurring events, because a UTC instant '
        'silently shifts every future occurrence across a DST boundary. Recurrence is then a rule plus a sparse exception list, '
        'and editing needs three scopes: this occurrence, this and following, or the series. Conflict detection and free-slot '
        'search fall out of half-open interval merging."'),
]
