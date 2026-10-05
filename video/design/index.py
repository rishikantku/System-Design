# -*- coding: utf-8 -*-
"""Lesson registry for the LinkedIn system design course.

Question order comes from companies/linkedin/src/research3.py: ranked by recency,
number of independent reports, Staff relevance, follow-up depth and fit to LinkedIn's
domain. The three questions in the pilot are the three with the strongest evidence -
the one LinkedIn itself put in writing, and the two with three independent reports each.

Nothing here claims a question will be asked. `evidence` on each lesson says exactly
what is known and how confident it is, and that is what the lesson states on screen.
"""

LESSONS = [

 # ---------------- chapter 1: methodology ----------------
 dict(id='s1l1-method', chapter='m1', module='s1l1_method',
      title='How to approach a Staff-level system design interview',
      file='LinkedIn-Design-1.1-Methodology', mins=30,
      pattern='The twenty steps, and what to say at each one',
      evidence=None),

 dict(id='s1l2-capacity', chapter='m1', module='s1l2_capacity',
      title='Capacity estimation masterclass',
      file='LinkedIn-Design-1.2-Capacity-Estimation', mins=32,
      pattern='Assumption &rarr; calculation &rarr; result &rarr; architectural implication',
      evidence=None),

 # ---------------- chapter 2: the reported questions ----------------
 dict(id='s2l1-bitly', chapter='m2', module='s2l1_bitly',
      title='Design a URL shortener (Bit.ly)',
      file='LinkedIn-Design-2.1-URL-Shortener', mins=34,
      pattern='Read-heavy KV &middot; unique id generation &middot; analytics',
      evidence=dict(reports="LinkedIn's own recruiter pack, with four named sub-questions",
                    latest='September 2026', level='Staff, Systems &amp; Infrastructure',
                    conf='HIGHEST &mdash; official', sources='Staff SI Onsite Prep pack')),

 dict(id='s2l2-typeahead', chapter='m2', module='s2l2_typeahead',
      title='Design typeahead / autosuggest',
      file='LinkedIn-Design-2.2-Typeahead', mins=34,
      pattern='Prefix retrieval &middot; ranking &middot; tight latency budget',
      evidence=dict(reports='3 independent candidate reports',
                    latest='March 2026', level='Senior SWE / L5',
                    conf='HIGH &mdash; recurring', sources='Exponent &times;2, Glassdoor')),

 dict(id='s2l3-metrics', chapter='m2', module='s2l3_metrics',
      title='Design a metrics gathering and aggregation system',
      file='LinkedIn-Design-2.3-Metrics-Platform', mins=34,
      pattern='High-cardinality ingestion &middot; time series &middot; alerting',
      evidence=dict(reports='3 independent candidate reports',
                    latest='September 2025', level='Senior SWE and unspecified',
                    conf='HIGH &mdash; upgraded in research pass 3',
                    sources='Blind &times;2, Glassdoor')),

 # ---------------- chapter 3: distributed infrastructure ----------------
 dict(id='s3l1-search', chapter='m3', module='s3l1_search',
      title='Design a distributed search index',
      file='LinkedIn-Design-3.1-Distributed-Search', mins=30,
      pattern='Inverted index &middot; sharding &middot; scatter-gather &middot; near-real-time',
      evidence=dict(reports='1 first-hand report, with real detail',
                    latest='12 May 2025', level='Staff Engineer',
                    conf='HIGH', sources='Taro &mdash; Staff loop, India')),

 dict(id='s3l2-scheduler', chapter='m3', module='s3l2_scheduler',
      title='Design a distributed job scheduler',
      file='LinkedIn-Design-3.2-Job-Scheduler', mins=30,
      pattern='Time-ordered work &middot; exactly-once &middot; leases &middot; clock skew',
      evidence=dict(reports='1 first-hand report from an Infrastructure loop',
                    latest='30 Sep 2025', level='Senior SWE, Infrastructure',
                    conf='HIGH', sources='Blind &mdash; Infrastructure interview')),

 dict(id='s3l3-queue', chapter='m3', module='s3l3_queue',
      title='Design a Kafka-like distributed message queue',
      file='LinkedIn-Design-3.3-Message-Queue', mins=32,
      pattern='Partitioned log &middot; replication &middot; consumer groups &middot; delivery semantics',
      evidence=dict(reports='2 independent reports',
                    latest='June 2025', level='Staff SWE',
                    conf='HIGH &mdash; and LinkedIn wrote Kafka',
                    sources='LeetCode Discuss, Blind ID3 thread')),

 # ================= chapter 4: distributed control =================
 # Counting something across a fleet, deciding on it, and getting the answer everywhere.

 dict(id='s4l1-ratelimit', chapter='m4', module='s4l1_ratelimit',
      title='Design a distributed rate limiter',
      file='LinkedIn-Design-4.1-Rate-Limiter', mins=18,
      pattern='Token bucket &middot; distributed counters &middot; fail-open vs fail-closed',
      evidence=dict(reports='InterviewTV list, and 1 independent recent report',
                    latest='2026', level='Staff / Senior',
                    conf='MEDIUM-HIGH &mdash; corroborated',
                    sources='InterviewTV.io + research pass 3')),

 dict(id='s4l2-quota', chapter='m4', module='s4l2_quota',
      title='Design the LinkedIn API quota system',
      file='LinkedIn-Design-4.2-API-Quota', mins=17,
      pattern='Per-tenant counters &middot; atomicity &middot; daily reset &middot; multi-region',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source, but shares machinery with 4.1',
                    sources='InterviewTV.io')),

 dict(id='s4l3-topn', chapter='m4', module='s4l3_topn',
      title='Top-N requests over the last 24 hours',
      file='LinkedIn-Design-4.3-Top-N', mins=16,
      pattern='Heavy hitters &middot; count-min sketch &middot; fixed windows &middot; exact vs approximate',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s4l4-denylist', chapter='m4', module='s4l4_denylist',
      title='Design a malicious-IP denylist',
      file='LinkedIn-Design-4.4-IP-Denylist', mins=18,
      pattern='Control plane &middot; propagation to a fleet &middot; staleness budget',
      evidence=dict(reports='InterviewTV list, and 1 report in research pass 3',
                    latest='2026', level='Staff',
                    conf='MEDIUM &mdash; corroborated, thin detail',
                    sources='InterviewTV.io + research pass 3')),

 # ================= chapter 5: text retrieval =================

 dict(id='s5l1-spell', chapter='m5', module='s5l1_spell',
      title='Design a real-time spell checker',
      file='LinkedIn-Design-5.1-Spell-Checker', mins=16,
      pattern='Trie &middot; prefix validity &middot; edit distance &middot; client-side budgets',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s5l2-docindex', chapter='m5', module='s5l2_docindex',
      title='Document indexing with boolean queries (Lynda)',
      file='LinkedIn-Design-5.2-Document-Indexing', mins=17,
      pattern='Inverted index &middot; postings intersection &middot; NOT &middot; build it in a month',
      evidence=dict(reports='InterviewTV list; related to the Staff search report in 3.1',
                    latest='2026', level='Staff',
                    conf='MEDIUM &mdash; the family is HIGH, this framing is single-source',
                    sources='InterviewTV.io + Taro Staff loop')),

 dict(id='s5l3-typeahead2', chapter='m5', module='s5l3_typeahead2',
      title='Typeahead, part two: personalisation and freshness',
      file='LinkedIn-Design-5.3-Typeahead-Part-2', mins=16,
      pattern='Mixed entity types &middot; per-member signals &middot; seconds-fresh index',
      evidence=dict(reports='3 independent reports (see lesson 2.2), plus the InterviewTV follow-ups',
                    latest='March 2026', level='Senior / Staff',
                    conf='HIGH &mdash; strongest in the set',
                    sources='Exponent &times;2, Glassdoor, InterviewTV.io')),

 # ================= chapter 6: storage and media =================

 dict(id='s6l1-kvstore', chapter='m6', module='s6l1_kvstore',
      title='Design a disk-based key-value store',
      file='LinkedIn-Design-6.1-Disk-KV-Store', mins=17,
      pattern='Append-only log &middot; in-memory index &middot; compaction &middot; crash recovery',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff, Infrastructure',
                    conf='MEDIUM &mdash; single source, and a classic infra question',
                    sources='InterviewTV.io')),

 dict(id='s6l2-photos', chapter='m6', module='s6l2_photos',
      title='Photo storage, processing and delivery',
      file='LinkedIn-Design-6.2-Photo-Platform', mins=16,
      pattern='Object store + metadata DB &middot; async pipeline &middot; CDN &middot; resumable upload',
      evidence=dict(reports='InterviewTV list only, with six follow-ups',
                    latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s6l3-logging', chapter='m6', module='s6l3_logging',
      title='Design a distributed logging system',
      file='LinkedIn-Design-6.3-Distributed-Logging', mins=16,
      pattern='Agents &middot; the log as a buffer &middot; retention tiers &middot; backpressure',
      evidence=dict(reports='InterviewTV list; overlaps the metrics question in 2.3',
                    latest='2026', level='Staff, Infrastructure',
                    conf='MEDIUM-HIGH &mdash; the family is well attested',
                    sources='InterviewTV.io + research pass 3')),

 # ================= chapter 7: fanout and delivery =================

 dict(id='s7l1-feed', chapter='m7', module='s7l1_feed',
      title='Design the LinkedIn news feed',
      file='LinkedIn-Design-7.1-News-Feed', mins=17,
      pattern='Fanout on write vs read &middot; the hybrid &middot; the celebrity problem',
      evidence=dict(reports='InterviewTV list, and recurring via aggregators',
                    latest='2026', level='Staff',
                    conf='MEDIUM-HIGH &mdash; corroborated',
                    sources='InterviewTV.io + research pass 3')),

 dict(id='s7l2-inmail', chapter='m7', module='s7l2_inmail',
      title='Design LinkedIn InMail',
      file='LinkedIn-Design-7.2-InMail', mins=17,
      pattern='Conversation model &middot; per-recipient state &middot; unread counts &middot; abuse',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s7l3-notify', chapter='m7', module='s7l3_notify',
      title='Design the notification system',
      file='LinkedIn-Design-7.3-Notifications', mins=16,
      pattern='Channel fanout &middot; preferences &middot; dedup &middot; provider failure',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 # ================= chapter 8: stateful sessions and event-sourced work ====

 dict(id='s8l1-coderpad', chapter='m8', module='s8l1_coderpad',
      title='Design CoderPad &mdash; collaborative editing and replay',
      file='LinkedIn-Design-8.1-CoderPad', mins=17,
      pattern='WebSockets &middot; session affinity &middot; ordered event log &middot; replay',
      evidence=dict(reports='InterviewTV list &mdash; and LinkedIn interviews run on this tool',
                    latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source, high plausibility',
                    sources='InterviewTV.io')),

 dict(id='s8l2-logistics', chapter='m8', module='s8l2_logistics',
      title='Design a package logistics and routing system',
      file='LinkedIn-Design-8.2-Logistics', mins=17,
      pattern='State machine &middot; scan events &middot; idempotency &middot; what you do NOT optimise',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s8l3-calendar', chapter='m8', module='s8l3_calendar',
      title='Design a calendar system',
      file='LinkedIn-Design-8.3-Calendar', mins=16,
      pattern='Recurrence expansion &middot; time zones &middot; invitation state &middot; conflicts',
      evidence=dict(reports='InterviewTV list, and 1 very recent report',
                    latest='2026', level='Staff',
                    conf='MEDIUM-HIGH &mdash; corroborated',
                    sources='InterviewTV.io + research pass 3')),

 # ================= chapter 9: intelligence, geo and trust =================

 dict(id='s9l1-jobrec', chapter='m9', module='s9l1_jobrec',
      title='Design LinkedIn job recommendations',
      file='LinkedIn-Design-9.1-Job-Recommendations', mins=17,
      pattern='Candidate generation &rarr; filter &rarr; rank &middot; offline vs online &middot; feature store',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source, and squarely LinkedIn-shaped',
                    sources='InterviewTV.io')),

 dict(id='s9l2-hosthealth', chapter='m9', module='s9l2_hosthealth',
      title='Design host health monitoring across three data centres',
      file='LinkedIn-Design-9.2-Host-Health', mins=16,
      pattern='Agent push &middot; time series &middot; current state vs history &middot; the engineer UI',
      evidence=dict(reports='InterviewTV list; the metrics family has 3 reports (lesson 2.3)',
                    latest='September 2025', level='Staff, Infrastructure',
                    conf='MEDIUM-HIGH &mdash; family corroborated',
                    sources='InterviewTV.io + Blind &times;2, Glassdoor')),

 dict(id='s9l3-geoviz', chapter='m9', module='s9l3_geoviz',
      title='Design a live map of new member sign-ups',
      file='LinkedIn-Design-9.3-Geo-Visualisation', mins=16,
      pattern='Geo aggregation &middot; tiles &middot; k-anonymity &middot; real-time vs batch',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 dict(id='s9l4-svcauthz', chapter='m9', module='s9l4_svcauthz',
      title='Design service-to-service permissions',
      file='LinkedIn-Design-9.4-Service-Permissions', mins=17,
      pattern='Workload identity &middot; policy distribution &middot; evaluate locally &middot; revocation',
      evidence=dict(reports='InterviewTV list only', latest='2026', level='Staff, Infrastructure',
                    conf='MEDIUM &mdash; single source',
                    sources='InterviewTV.io')),

 # ================= chapter 10: the revision finale =================

 dict(id='s10l1-patterns', chapter='m10', module='s10l1_patterns',
      title='Patterns you should recognise &mdash; and how to spot them in a new question',
      file='LinkedIn-Design-10.1-Patterns', mins=15,
      pattern='Seven reusable shapes, and the tell that identifies each one',
      evidence=None),
]


CHAPTERS = {
 'm1': dict(num=1, title='System design methodology',
            why='The method is worth more than any single answer. It is what carries you '
                'through a question you have never seen, which is the likeliest case.'),
 'm2': dict(num=2, title='The reported LinkedIn questions',
            why='The three with the strongest evidence: the question LinkedIn published '
                'itself, and the two with three independent candidate reports each.'),
 
 'm4': dict(num=4, title='Distributed control: counting, limiting, propagating',
            why='Four questions that look unrelated and are the same problem: count something '
                'across a fleet, decide on it, and get the decision everywhere before it goes '
                'stale. Learn the counter once and all four fall out.'),
 'm5': dict(num=5, title='Text retrieval',
            why='A clean progression from the simplest index to the hardest. A trie that answers '
                '"is this still a word", an inverted index that answers boolean queries, and then '
                'ranked prefix retrieval with personalisation on top.'),
 'm6': dict(num=6, title='Storage engines and media pipelines',
            why='What actually happens to bytes. An append-only store you build yourself, an '
                'object store you buy, and a log pipeline that moves them &mdash; so you can '
                'argue about durability from first principles rather than by naming products.'),
 'm7': dict(num=7, title='Fanout and delivery',
            why='Three questions with one axis running through them: do you do the work when the '
                'content is written, or when it is read? Feed, inbox and notifications answer it '
                'differently, and the reason is the read/write ratio each one faces.'),
 'm8': dict(num=8, title='Stateful sessions and event-sourced workflows',
            why='Systems where the state <i>is</i> the sequence of events. CoderPad replays it, '
                'logistics is a state machine over scans, and a calendar is invitation state plus '
                'recurrence. All three need ordering and idempotency for the same reason.'),
 'm9': dict(num=9, title='Intelligence, geo and trust',
            why='The four that need something other than a database: a ranking pipeline, a '
                'time-series store, a geospatial aggregate, and a policy engine. Each one is a '
                'different answer to &ldquo;where does the answer actually get computed?&rdquo;'),
 'm10': dict(num=10, title='Revision: the patterns',
             why='Not a summary. The seven shapes that recur across all twenty-one questions, '
                 'and the tell that lets you recognise each one in a question you have never seen.'),
 'm3': dict(num=3, title='Distributed infrastructure',
            why='The three remaining HIGH-confidence questions, and the ones closest to the '
                'Infrastructure round: search, scheduling and the log. All three are lower-stack '
                'than the product questions, which is what infra candidates report facing.'),
}

PLANNED = [
 ('News feed', 'MEDIUM · recurring via aggregators'),
 ('Rate limiter', 'MEDIUM · recent single report'),
 ('In-memory cache with configurable eviction', 'MEDIUM · straddles the coding round'),
 ('Calendar (low-level design)', 'MEDIUM · very recent'),
 ('Malicious request interception', 'LOW · shares machinery with rate limiting'),
 ('Staff-level deep dives', 'Cross-cutting: multi-region, cost, consistency, evolution'),
 ('Mocks and rapid revision', 'Full timed mocks plus the revision cards'),
]
