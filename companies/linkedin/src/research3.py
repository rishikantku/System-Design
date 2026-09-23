# -*- coding: utf-8 -*-
"""Research pass 3 (23 Sep 2026) — system design questions only.

Rules, unchanged from pass 2 and applied strictly:

  REPORTED   a candidate described being asked it, or the reader supplied it first-hand
  OFFICIAL   LinkedIn's own recruiter pack said it - the strongest evidence there is
  GENERAL    a topic guides recommend, or a community thread speculates about; NOT evidence
             that anyone was asked

Copies of one original report never count as independent. A "top questions" article is
not a report. Two threads quoting the same candidate are one report.

What this pass added over pass 2:
  - metrics gathering upgraded LOW -> HIGH: a second and third independent first-hand
    report surfaced (Blind, Sep 2025, "they asked me metric aggregator"; and a Blind
    onsite review for Senior SWE on the applications track)
  - the IDI3 / Infrastructure Design Interview round is named explicitly by several
    infra candidates, and is described as lower-stack and concurrency-heavy rather than
    API-heavy. That matters: the reader is interviewing with an infra team.
  - two Blind topic lists (key-value store, top-k in a time window) are recorded as
    GENERAL, not reported: the threads suggest topics, they do not report being asked.
  - one widely-linked thread turned out to be from 2019 and purely speculative, so it
    is excluded rather than counted.
"""

DATE = '23 September 2026'

SOURCES = {
 'pack':       dict(name='LinkedIn recruiter pack — Staff SI Onsite Prep (CWAI)',
                    url='', note='Sent to the reader by the recruiter. Authoritative.'),
 'exp-cand':   dict(name='Exponent — candidate report, Senior SWE',
                    url='https://www.tryexponent.com/questions?company=linkedin&type=system-design'),
 'exp-bank':   dict(name='Exponent — LinkedIn system design question bank',
                    url='https://www.tryexponent.com/questions?company=linkedin&role=swe&type=system-design'),
 'gd-swe':     dict(name='Glassdoor — LinkedIn Senior SWE interview reports',
                    url='https://www.glassdoor.com/Interview/LinkedIn-Senior-Software-Engineer-Interview-Questions-EI_IE34865.0,8_KO9,33.htm'),
 'gd-staff':   dict(name='Glassdoor — LinkedIn Staff SWE interview reports',
                    url='https://www.glassdoor.com/Interview/LinkedIn-Staff-Software-Engineer-Interview-Questions-EI_IE34865.0,8_KO9,32.htm'),
 'blind-infra':dict(name='Blind — LinkedIn Senior SWE Infrastructure interview experience',
                    url='https://www.teamblind.com/post/linkedin-senior-software-engineer-infrastructure-interview-experience-rfq58zbt'),
 'blind-sysinf':dict(name='Blind — LinkedIn System and Infrastructure interview',
                    url='https://www.teamblind.com/post/linkedin-system-and-infrastructure-interview-0pqvh5ts'),
 'blind-onsite':dict(name='Blind — LinkedIn onsite interview, system design review',
                    url='https://www.teamblind.com/post/linkedin-onsite-interview-system-design-review-1buxmbjm'),
 'blind-id3':  dict(name='Blind — LinkedIn System Design (ID3) interview tips',
                    url='https://www.teamblind.com/post/linkedin-system-design-id3-interview-tips-jpcyqods'),
 'taro-india': dict(name='Taro — Staff Engineer, India loop',
                    url='https://www.jointaro.com/'),
 'taro-staff': dict(name='Taro — Staff phone screen summary',
                    url='https://www.jointaro.com/'),
 'lc-staff':   dict(name='LeetCode Discuss — Staff SWE loop',
                    url='https://leetcode.com/discuss/'),
}

BLOCKED = [
 'Blind and Glassdoor block direct fetching; both were read through search summaries, '
 'which is weaker than reading the thread. Graded down accordingly.',
 '1point3acres is referenced by one Blind poster as holding a fuller list, but it is '
 'behind a login and could not be verified. Not counted as evidence.',
]


def Q(**kw):
    kw.setdefault('variation', '')
    kw.setdefault('follows', [])
    kw.setdefault('deep', [])
    kw.setdefault('loc', '—')
    kw.setdefault('idate', '')
    kw.setdefault('kind', 'reported')
    return kw


# ---------------------------------------------------------------- the database
DESIGN = [

 Q(q='Design a URL shortener (Bit.ly)', kind='official',
   variation='The pack names four sub-questions: the core service, how you scale reads, '
             'how you guarantee unique short codes, and analytics on click traffic.',
   date='Sep 2026 (recruiter pack)', level='Staff, Systems & Infrastructure',
   rnd='Systems and Infrastructure Design', src=['pack'], reports=1, rec='official',
   conf='HIGHEST',
   follows=['Read scaling and cache strategy', 'Unique-code generation without coordination',
            'Click analytics pipeline', 'Custom aliases and expiry'],
   deep=['Key generation: counter vs hash vs pre-minted pool', 'Cache-aside vs read-through',
         'Redirect latency budget', 'Analytics write amplification'],
   why='This is the only question LinkedIn itself put in writing. Whatever else appears, '
       'the method it rewards is the method the pack describes: completeness, quality of '
       'decisions, and reasoning about scale, reliability and extensibility.'),

 Q(q='Design the backend for autosuggest / typeahead',
   variation='Also reported as "typeahead for person search" and as autocomplete with '
             'ranking of suggestions.',
   date='≈ Mar 2026, plus ≈2025', level='Senior SWE / L5', rnd='System design',
   src=['exp-cand', 'exp-bank', 'gd-swe'], reports=3, rec='recurring', conf='HIGH',
   follows=['Ranking and personalisation', 'Index build and refresh cadence',
            'Latency budget end to end', 'Typo tolerance'],
   deep=['Trie vs FST vs prefix-keyed KV', 'Where personalisation is applied',
         'Cache design for head prefixes', 'Index freshness vs query latency'],
   why='The most-reported design question, across three independent sources, and the most '
       'LinkedIn-shaped: prefix retrieval over a people graph with personalised ranking.'),

 Q(q='Design a metrics gathering / aggregation system',
   variation='Reported as "metric aggregator" and as collection + time-series storage + '
             'rendering with monitoring and alerting on top.',
   date='Sep 2025 (Blind) · 2025–2026 (Glassdoor) · Blind onsite review',
   idate='≈2024 for the Blind report ("last year")',
   level='Senior SWE (applications track) and unspecified', rnd='System design',
   src=['blind-sysinf', 'blind-onsite', 'gd-swe'], reports=3, rec='recurring', conf='HIGH',
   follows=['Ingestion rate and metric cardinality', 'Downsampling and retention tiers',
            'Alert evaluation at scale', 'Query path for dashboards'],
   deep=['Push vs pull collection', 'Time-series storage layout and compaction',
         'Cardinality explosion as the dominant failure', 'Rollups and pre-aggregation'],
   why='Upgraded from LOW to HIGH in this pass: three independent first-hand reports, and '
       'one poster states plainly that they were asked it. Described as a normal question '
       'for both SWE and Infrastructure candidates.'),

 Q(q='Design a distributed inverted index / search system (Elasticsearch-like)',
   date='12 May 2025', level='Staff Engineer', loc='India', rnd='System design',
   src=['taro-india'], reports=1, rec='single', conf='HIGH',
   follows=['Index sharding and replication', 'Near-real-time indexing',
            'Query fan-out and result merge', 'Ranking'],
   deep=['Segment-based indexing and merges', 'Scatter-gather latency and stragglers',
         'Index vs query trade-off on refresh interval', 'Replica placement'],
   why='A first-hand Staff-level report with real detail. Search and retrieval is core '
       'LinkedIn engineering, and it shares most of its machinery with typeahead.'),

 Q(q='Design a job scheduler',
   date='30 Sep 2025', level='Senior SWE, Infrastructure', rnd='System design',
   src=['blind-infra'], reports=1, rec='single', conf='HIGH',
   follows=['Exactly-once vs at-least-once execution', 'Missed and overdue jobs',
            'Leader election and partitioning', 'Back-pressure'],
   deep=['Timing wheel vs sorted store vs queue-per-bucket', 'Idempotency of execution',
         'Clock skew and the meaning of "on time"', 'Tenant fairness'],
   why='First-hand, recent, and from an Infrastructure loop — the same org the reader is '
       'interviewing with. Exactly-once is the trap the follow-ups walk into.'),

 Q(q='Design a Kafka-like distributed message queue',
   date='Jun 2025', level='Staff SWE', rnd='System design',
   src=['lc-staff', 'blind-id3'], reports=2, rec='recurring', conf='HIGH',
   follows=['Partitioning and ordering guarantees', 'Replication and in-sync replicas',
            'Consumer groups and rebalancing', 'Exactly-once semantics'],
   deep=['Log storage and segment retention', 'Leader/follower replication and ISR',
         'Consumer offset management', 'Hot partitions'],
   why='LinkedIn wrote Kafka. A candidate being asked to design it is being asked about '
       'the house speciality, and the bar for depth is correspondingly higher.'),

 Q(q='Design LinkedIn\'s news feed',
   date='2025–2026 (aggregated; also an older first-hand report)',
   level='Staff / SWE', rnd='System design', src=['gd-staff', 'exp-bank'],
   reports=2, rec='recurring', conf='MEDIUM',
   follows=['Fan-out on write vs on read', 'Ranking', 'Freshness vs cost'],
   deep=['Hybrid fan-out for high-degree members', 'Feed store and pagination',
         'Ranking pipeline and feature freshness'],
   why='Recurring but largely through aggregators, and the strongest first-hand report is '
       'older. Prepare it, but it is not the top priority the guides imply.'),

 Q(q='Design a rate limiter',
   date='≈ Aug 2026 ("asked a month ago")', level='SWE', rnd='System design',
   src=['exp-bank'], reports=1, rec='single', conf='MEDIUM',
   follows=['Distributed counters', 'Per-member vs per-key limits',
            'Behaviour when the shared store is down', 'Fairness and bursts'],
   deep=['Token bucket vs sliding window log vs sliding window counter',
         'Where the limiter lives: edge, gateway, or service',
         'Failing open vs failing closed'],
   why='Recent and specific, but a single report. Cheap to prepare and it recurs as a '
       'sub-question inside abuse prevention and API design.'),

 Q(q='Design a flexible in-memory cache with configurable capacity and eviction',
   date='2025', level='Staff', rnd='System design / design-flavoured coding',
   src=['taro-staff', 'exp-bank'], reports=2, rec='recurring', conf='MEDIUM',
   follows=['TTL', 'Ranked eviction', 'Concurrency and thread safety'],
   deep=['Eviction policy as a strategy interface', 'Sharded locks vs one lock',
         'Memory accounting and sizing'],
   why='Sits on the boundary between the coding round and the design round, which is why '
       'it recurs. The coding course already covers LFU; here it is an API design question.'),

 Q(q='Design a calendar (low-level design)',
   date='≈ Aug/Sep 2026 ("asked 22 days ago")', level='SWE', rnd='Design / LLD',
   src=['exp-bank'], reports=1, rec='single', conf='MEDIUM',
   follows=['Recurring events', 'Time zones and DST', 'Conflict detection'],
   deep=['Recurrence rule storage vs expansion', 'Free/busy query performance',
         'Invite state machine'],
   why='Very recent. It is object modelling rather than distributed systems, so it tests a '
       'different muscle: clean interfaces and extensibility.'),

 Q(q='Design a system that intercepts and blocks malicious requests',
   date='undated', level='SWE', rnd='System design', src=['gd-swe'],
   reports=1, rec='single', conf='LOW',
   follows=['Signal collection', 'Real-time vs batch scoring', 'False positives',
            'Updating rules without a redeploy'],
   deep=['Where enforcement sits in the request path', 'Rule engine vs model',
         'Feedback loop and labelling'],
   why='Undated and single-sourced, so low confidence. Included because abuse prevention '
       'shares its machinery with rate limiting, which is better attested.'),
]


# ---------------------------------------------------------------- not evidence
GENERAL = [
 dict(topic='Design a distributed key-value store (DynamoDB-like)',
      note='Named in Blind threads as a topic candidates should know for the Systems & '
           'Infrastructure round. No first-hand report of it being asked was found.',
      src=['blind-id3']),
 dict(topic='Top-k events in a time window',
      note='Same: listed as a topic to prepare, not reported as asked.', src=['blind-id3']),
 dict(topic='Design LinkedIn messaging',
      note='Appears on guide lists. No first-hand report found in this pass.',
      src=['exp-bank']),
 dict(topic='Design job recommendations in real time',
      note='Appears on guide lists. No first-hand report found in this pass.',
      src=['exp-bank']),
]

INFERENCE = [
 dict(claim='The Systems & Infrastructure design round (called IDI3 / ID3 by candidates) '
            'goes lower down the stack than a product design round: concurrency, storage '
            'internals and distributed-systems mechanics rather than API surface.',
      basis='Several infra candidates describe it that way, and it is consistent with the '
            'recruiter pack\'s wording about reliability, fault tolerance and extensibility.',
      confidence='MEDIUM'),
 dict(claim='Retrieval questions (typeahead and search) and observability questions '
            '(metrics) are the two clusters with the strongest recent evidence.',
      basis='Three independent reports each; nothing else in this pass reached three.',
      confidence='HIGH'),
 dict(claim='One Blind poster claims LinkedIn works from a fixed question set.',
      basis='A single unverified claim. Recorded because it would matter if true, but it '
            'is not corroborated and should not drive preparation.',
      confidence='LOW'),
]


# ---------------------------------------------------------------- priority
def priority():
    """Ranked by: recency, independent reports, Staff relevance, complexity, follow-up
    depth, distributed-systems weight, and fit to LinkedIn's domain. Evidence-based
    preparation order - not a prediction of what will be asked."""
    order = [
        ('Design a URL shortener (Bit.ly)', 'LinkedIn put it in writing. Start here.'),
        ('Design the backend for autosuggest / typeahead', '3 reports, recurring, most LinkedIn-shaped.'),
        ('Design a metrics gathering / aggregation system', '3 reports; upgraded this pass.'),
        ('Design a distributed inverted index / search system (Elasticsearch-like)',
         'First-hand Staff report; shares machinery with typeahead.'),
        ('Design a job scheduler', 'First-hand, recent, from an Infrastructure loop.'),
        ('Design a Kafka-like distributed message queue', 'The house speciality; the depth bar is higher.'),
        ('Design LinkedIn\'s news feed', 'Recurring, but mostly via aggregators.'),
        ('Design a rate limiter', 'Cheap to prepare; recurs as a sub-question.'),
        ('Design a flexible in-memory cache with configurable capacity and eviction',
         'Straddles the coding round.'),
        ('Design a calendar (low-level design)', 'Very recent; tests modelling, not scale.'),
        ('Design a system that intercepts and blocks malicious requests', 'Low confidence; shares machinery with rate limiting.'),
    ]
    by_q = {q['q']: q for q in DESIGN}
    return [(i + 1, by_q[name], reason) for i, (name, reason) in enumerate(order)]
