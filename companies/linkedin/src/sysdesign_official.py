# -*- coding: utf-8 -*-
"""The design question printed in LinkedIn's own Staff SI onsite prep pack."""

OFFICIAL_DESIGNS = [
 dict(id='bitly', title='Bit.ly — the official example question', topic='Official example · Storage · Serving', prio='p0',
  why='**This is the example question in LinkedIn\'s own prep pack**, with four named sub-questions: how you allocate the '
      'shorthand URLs, how you store the mapping, how you implement the redirect servers, and how you keep and store click stats. '
      'Treat those four as the actual agenda of the hour — the pack is telling you where the interview goes.',
  ask=['Scale: how many new URLs per day, and what read-to-write ratio? (Read-heavy by orders of magnitude.)',
       'Custom/vanity aliases, or system-generated only?',
       'Expiry and deletion — do links live forever?',
       'Stats: real-time counters, or analytics that can lag minutes?',
       'Global audience? (Redirect latency is the product, so edge presence matters.)',
       'Guessability: must short codes be unpredictable (security) or is sequential fine?'],
  fr=['Create a short code for a long URL, optionally with a custom alias',
      'Redirect a short code to the original URL',
      'Count clicks and expose stats per link',
      'Delete or expire a link'],
  nfr=['Redirect p99 in tens of milliseconds, globally — this is the whole user experience',
       'Very high availability on the read path; the write path can be less available',
       'No collisions, ever: a code must map to exactly one URL, permanently',
       'Stats may be eventually consistent; the mapping may not'],
  scale='Assume 100 million new links per day and a 100:1 read-to-write ratio → ~1,200 writes/s and ~120,000 redirects/s. '
        'Storage: 100M/day × ~500 bytes ≈ 50 GB/day, ~18 TB/year including indexes. At 7 base-62 characters the key space is '
        '3.5 × 10¹² — decades of headroom; at 6 characters it is 57 billion, which you would exhaust in under two years at this rate. '
        'That arithmetic is the answer to "how long should the code be?"',
  api='`POST /links {longUrl, alias?, ttl?}` → `{shortCode, shortUrl}`; `GET /{shortCode}` → 301/302 redirect; '
      '`GET /links/{shortCode}/stats?from=&to=&groupBy=` → click counts. Creation is idempotent on (longUrl, owner) if you want '
      'to deduplicate; say whether you do, because it changes the storage model.',
  data='Mapping: `shortCode → {longUrl, ownerId, createdAt, expiresAt}` in a key-value store partitioned by hash of shortCode. '
       'Stats: raw click events in a log, rolled up into `(shortCode, timeBucket) → count` aggregates. Keep the two apart: the '
       'mapping is small, hot and must be correct; the stats are large, append-only and tolerant of lag.',
  arch='Write path: API → allocate code → persist mapping → populate cache.\n\n'
       'Read path: DNS/anycast → edge → redirect service (stateless) → cache → key-value store on a miss → emit a click event.\n\n'
       'Stats path: click events → a partitioned log (this is Kafka\'s home ground) → stream aggregation (Samza-style) → '
       'time-bucketed rollups in an analytics store (Pinot-style) for queries, with raw events landing in cold storage for '
       'reprocessing.\n\n'
       'Saying "the mapping is a KV problem, the stats are a streaming problem, and they should not share a store" is the '
       'structural insight the sub-questions are fishing for.',
  deep=['**Sub-question 1 — allocating short codes.** Three options, and pick with reasons. (a) **Hash the URL** (MD5 → base62, '
        'first 7 chars): deduplicates identical URLs, but needs collision handling on write. (b) **Random 7 chars**: '
        'unguessable, but needs a uniqueness check, and birthday collisions start mattering as the table fills. (c) **Counter + '
        'base62**, with each host leasing a range (say a block of 100k) from a coordination service: no collisions by construction, '
        'no read-before-write, and ranges survive host restarts — you just lose the tail of a leased block. I would take (c), and '
        'scramble the counter (Feistel or base-62 with a keyed permutation) so codes are not sequentially guessable.',
        '**Sub-question 2 — storing the mapping.** A key-value store partitioned by hash of the short code, replicated, with the '
        'row being immutable after creation. Immutability is the gift here: caches never need invalidation for the common case, '
        'only for deletes and expiry. Cache in front (LRU plus a bloom filter for known-missing codes to stop cache-miss stampedes '
        'on garbage traffic).',
        '**Sub-question 3 — redirect servers.** Stateless, horizontally scaled, close to users, holding a large local cache; the '
        'hot set is tiny (a few percent of links get most traffic). **301 versus 302 is the trade-off to name**: 301 is cached by '
        'browsers and CDNs, which makes redirects nearly free but destroys your click stats and your ability to change or revoke a '
        'link; 302 keeps every click visible and costs a request every time. Most link shorteners choose 302 for exactly that reason.',
        '**Sub-question 4 — click stats.** Do not write to a database per click at 120k/s. Emit an event to a partitioned log, '
        'partitioned by short code so per-link counts land in one place, then aggregate in a stream processor into minute and '
        'hour buckets. Keep raw events for reprocessing; serve queries from the rollups. Hot links create a hot partition — '
        'pre-aggregate on the producer side (batch counts per second per host) so the fan-in is bounded.',
        '**Expiry and deletion.** TTL in the row plus a lazy check on read, with a background sweeper for storage reclamation. '
        'Deletion must invalidate caches and edge entries, which is the second reason to prefer 302.'],
  fails=['Key-value store unavailable → serve from cache; unknown codes fail with a clean 404 rather than a hang.',
         'Cache cold after a deploy → a thundering herd on the store; stagger restarts and pre-warm from the hot-set list.',
         'Coordination service for counter ranges down → hosts keep issuing from their current lease; only new leases block, '
         'which is a graceful degradation rather than an outage.',
         'Stats pipeline lagging → redirects are unaffected (the paths are separate); stats catch up, and you can say so to the '
         'customer honestly.',
         'Abuse: someone shortens malicious URLs → a denylist check on create and a re-check on read, plus rate limits per account.'],
  scaling=['Read path scales by adding stateless redirect nodes and cache capacity; nothing coordinates.',
           'Write path scales by leasing wider counter ranges — no shared hot row.',
           'Stats scale by log partitions; hot links are handled by producer-side pre-aggregation.',
           'Geo: replicate the mapping read-only to each region; creation can stay in one region if 1,200 writes/s is fine there.'],
  obs=['Redirect p99 by region, and cache hit rate (the two numbers that define the product)',
       'Unknown-code rate — a spike means either a bug or a scanning attack',
       'Stats pipeline lag', 'Counter-range utilisation, so you never discover exhaustion at 3 a.m.'],
  sec=['Unguessable codes if links may be private; sequential codes leak volume and allow enumeration.',
       'Malware/phishing denylist on create and on read.',
       'Open-redirect abuse: you are a redirector by definition, so rate-limit and attribute every link to an owner.'],
  cost='The read path dominates: cache memory and bandwidth. Stats storage grows forever unless you tier — keep minute buckets '
       'for days, hour buckets for months, and raw events in cold storage. Quote it: 100M links/day of raw click events at ~100 '
       'bytes is ~10 GB/day per 100M clicks, which is cheap in object storage and expensive in a hot analytics store.',
  trade=[('301 vs 302', 'Free, browser-cached redirects versus visible click stats and revocability — the defining trade of this design'),
         ('Counter ranges vs hashing', 'No collisions and no read-before-write, at the cost of a coordination dependency and non-dedup'),
         ('Stats freshness', 'Real-time counters cost a hot path; minute-level rollups are usually enough and far cheaper'),
         ('Code length', '6 characters is compact and runs out; 7 gives decades of headroom for one extra character')],
  evolve='Phase 1: single region, counter ranges, KV plus cache, 302 redirects, click events to a log with hourly rollups. '
         'Phase 2: multi-region read replicas and edge caching. Phase 3: minute-level stats, custom aliases, abuse detection. '
         'The seam that makes phase 3 cheap is keeping stats out of the mapping store from day one.',
  senior='"Hash the URL, store it in a database with a cache, redirect with 301, and increment a counter per click."',
  staff='"The redirect is trivial; the interesting decisions are code allocation without coordination on the hot path, 301 versus '
        '302 as a stats-versus-cost trade, and keeping click stats entirely off the mapping store — a log plus stream aggregation, '
        'because a write per click at a hundred thousand per second is the thing that actually falls over. I would also size the '
        'code length from the arithmetic rather than picking seven by convention."'),
]
