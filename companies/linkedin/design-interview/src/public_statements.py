# -*- coding: utf-8 -*-
"""Public versions of the InterviewDB questions — rewritten in my own words.

The InterviewDB wording is paid content: it stays only in src/statements.json, which is git-excluded and
used for the local build. Everything committed (and deployed) uses these rewrites. Same requirements and
numbers, different words. LeetCode Discuss questions (metrics, scheduler, cache) are public posts and keep
their reported wording.
"""

PUBLIC = {
 'coderpad': ('Design CoderPad', '8.1',
  'Design the collaborative coding tool LinkedIn uses for interviews. The candidate writes code and the interviewer watches it '
  'change live (assume only the candidate edits). There is also a drawing canvas that both people see in real time. The interviewer '
  'can invite more people to a pad by email. Finally, any interview can be replayed later, showing what happened at each moment.'),
 'denylist': ('Malicious IP denylist', '4.4',
  'A small share of LinkedIn\'s traffic is malicious. Given a function that tells you whether a request is malicious, design a system '
  'that builds a list of bad IP addresses and keeps every one of LinkedIn\'s many web servers up to date with it.'),
 'lynda': ('Lynda document indexing', '5.2',
  'LinkedIn has just acquired a learning company with an enormous library of PDF documents. You and one other engineer have a month '
  'to ship a first version that lets members search it. Design the indexing system so it can answer queries such as "documents '
  'containing red and green but not blue" quickly. How are the word indexes computed and stored?'),
 'jobrec': ('Job recommendations', '9.1',
  'Design the "top job picks for you" feature on LinkedIn\'s jobs page. Recommend the best 3 jobs out of millions, with low latency, '
  'based on each member\'s profile. Only recommend jobs the member is basically qualified for (no senior executive roles for students, '
  'no backend roles for designers). Personalise accurately; optionally use recent activity such as pages visited and posts liked. '
  'Scale: about 1 billion members, 100 million daily active.'),
 'photos': ('Photo storage and delivery', '6.2',
  'Design a system where members upload photos from desktop or mobile, and the photos are processed, stored, catalogued, searched and '
  'served. Cover upload, processing, storage and delivery. Follow-ups: handle 50 million uploads a day; process a photo within about '
  '2 seconds; add video support; show an upload progress bar.'),
 'logistics': ('Package logistics', '8.2',
  'Design the system a shipping company uses to move packages from senders to recipients through its hubs — tracking every package '
  'and routing it. Follow-ups: where do you optimise and where is it not worth it, what are you optimising for, and how do you handle '
  'security, reliability and ease of use?'),
 'spell': ('Real-time spell checker', '5.1',
  'Design the spell checking in a word processor: a word is highlighted as soon as the user finishes typing something that is not a '
  'real word. Follow-ups: offer live suggestions instead of only highlighting, and complete half-typed words — and choose which of '
  'many candidates to show.'),
 'topn': ('Top-N in the last 24 hours', '4.3',
  'A service runs on several hundred machines. Design a way to answer "which N items were requested most in the previous 24 hours" '
  '(a fixed day, not an arbitrary window) — for example the most searched strings of a search service, or the most requested keys '
  'of a distributed key-value store.'),
 'typeahead': ('Typeahead for LinkedIn search', '2.2 + 5.3',
  'Design autocomplete for LinkedIn\'s search bar: as the member types a few letters, suggest matching people, companies and more '
  '(for example "Ry" suggests a connection named Ryan). Follow-ups: scale the index to a billion members, and compute and return the '
  'top K results with low latency.'),
 'quota': ('API quota system', '4.2',
  'LinkedIn\'s public APIs give each company and each user a daily call allowance. Design the system that enforces these quotas and '
  'records API usage.'),
 'calendar': ('Calendar system', '8.3',
  'Design a calendar: users create events, invite others, accept or decline, and see their events on their calendar.'),
 'geoviz': ('Live map of new sign-ups', '9.3',
  'Design a live map that shows where newly registered LinkedIn members are signing up from.'),
 'notify': ('Notification delivery', '7.3',
  'Design how LinkedIn delivers notifications to members over push, email and in-app.'),
 'logging': ('Distributed logging', '6.3',
  'Design a distributed logging system that serves an analytics service.'),
 'kvstore': ('Key-value store on files', '6.1',
  'Design a key-value store on top of a minimal file API: you can create a file, append bytes to it, and read bytes from an offset. '
  'Keys fit in memory; values do not and must be read from disk.'),
 'mq': ('Message queue', '3.3', 'Design a distributed message queue.'),
 'inmail': ('InMail messaging', '7.2', 'Design the messaging system behind LinkedIn InMail.'),
 'feed': ('News feed', '7.1', 'Design LinkedIn\'s news feed.'),
 'svcauthz': ('Service-to-service permissions', '9.4',
  'A company runs many services that call each other. Design a permission system that decides which services may call which.'),
 'ratelimit': ('Rate limiter', '4.1', 'Design a distributed rate limiter.'),
 'hosthealth': ('Host health monitoring', '9.2',
  'LinkedIn runs hundreds of thousands of hosts across three data centres. Design a system that tracks each host\'s health now and over '
  'time, with a UI engineers use for troubleshooting — start with the overall picture, then go deep on parts.'),
}
