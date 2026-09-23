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
]

CHAPTERS = {
 'm1': dict(num=1, title='System design methodology',
            why='The method is worth more than any single answer. It is what carries you '
                'through a question you have never seen, which is the likeliest case.'),
 'm2': dict(num=2, title='The reported LinkedIn questions',
            why='The three with the strongest evidence: the question LinkedIn published '
                'itself, and the two with three independent candidate reports each.'),
}

# Built after the pilot is reviewed, in research-priority order.
PLANNED = [
 ('Distributed inverted index / search', 'HIGH · Staff report, May 2025'),
 ('Job scheduler', 'HIGH · Senior Infra report, Sep 2025'),
 ('Kafka-like message queue', 'HIGH · 2 reports · the house speciality'),
 ('News feed', 'MEDIUM · recurring via aggregators'),
 ('Rate limiter', 'MEDIUM · recent single report'),
 ('In-memory cache with configurable eviction', 'MEDIUM · straddles the coding round'),
 ('Calendar (low-level design)', 'MEDIUM · very recent'),
 ('Malicious request interception', 'LOW · shares machinery with rate limiting'),
 ('Staff-level deep dives', 'Cross-cutting: multi-region, cost, consistency, evolution'),
 ('Mocks and rapid revision', 'Full timed mocks plus the revision cards'),
]
