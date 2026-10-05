# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 1 — real-time spell checker."""
from lib import *

lesson_header('5.1', 'Design a real-time spell checker',
              'Trie &middot; prefix validity &middot; edit distance &middot; client-side budgets',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 15,
              """Chapter five, lesson one: a real-time spell checker. A word processor underlines a word """
              """as you type, and the requirement is precise &mdash; underline it as soon as the """
              """characters entered cannot possibly form a valid word. That word &ldquo;cannot&rdquo; is """
              """doing an enormous amount of work, and noticing it is most of the question.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Highlight &ldquo;as soon as the entered characters cannot form a valid word&rdquo;. Follow-ups: '
  'real-time suggestions, many candidates, candidate ranking'),
 ('Related &mdash; lesson 2.2 typeahead', 'March 2026', 'Senior / Staff',
  'Prefix retrieval with 3 independent reports. <b>Different problem, same structure</b>'),
], """Single source, so medium confidence. But the phrasing is unusually precise: highlight as soon as """
     """the entered characters cannot form a valid word. Not when the word is wrong &mdash; when no """
     """completion of it could ever be right.""",
 ["""And the follow-ups push into suggestions and ranking, which is where it starts to overlap with the """
  """typeahead lesson from chapter two. Same data structure, genuinely different question &mdash; and """
  """being able to say why they differ is worth more than either answer alone."""],
 caveat='Single source. The trie machinery is shared with typeahead, which has three reports, so this '
        'prepares you either way.',
 narration_caveat="""Single source for this framing. The machinery is shared with typeahead, which has """
                  """three independent reports, so the preparation transfers.""")

sid = beat('Why this is interesting', 'It is a <b>prefix</b> question pretending to be a dictionary question',
           '<div style="font-size:29px;line-height:1.75">'
           'The naive reading: look the word up in a dictionary. Not found &rarr; underline it.<br><br>'
           '<span style="color:#ff9a9a">That is wrong, and it is wrong in a way the user feels.</span> '
           'Type <code>r-e-c-e</code> and a dictionary lookup fails at every single keystroke. The word '
           'would be underlined while you are still correctly typing <i>receive</i>.<br><br>'
           'The requirement is not &ldquo;is this a word&rdquo;. It is:<br><br>'
           '<b>&ldquo;Is this still a prefix of any word?&rdquo;</b><br><br>'
           '&bull; <code>rece</code> &rarr; prefix of <i>receive</i>, <i>recent</i>, <i>recess</i> '
           '&rarr; <span style="color:#a8e6a3">stay silent</span><br>'
           '&bull; <code>recz</code> &rarr; prefix of nothing &rarr; '
           '<span style="color:#ff9a9a">underline now</span><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the data structure follows from the '
           'question you actually have to answer, and the question here is about prefixes, not '
           'membership.</span></div>',
           """Why is this interesting? Because the obvious reading is wrong in a way the user actually """
           """feels. The naive version looks the word up in a dictionary: not found, underline it.""",
           step=0)
seg(sid, 1, """Type r-e-c-e and a dictionary lookup fails at every keystroke. R is not a word. R-e is not """
            """a word. R-e-c is not a word. So the word gets underlined while you are still correctly """
            """typing &ldquo;receive&rdquo;, and the feature is worse than useless &mdash; it is """
            """actively distracting.""")
seg(sid, 2, """The requirement is not &ldquo;is this a word&rdquo;. It is &ldquo;is this still a prefix """
            """of any word&rdquo;. R-e-c-e is a prefix of receive, recent, recess, so stay quiet. """
            """R-e-c-z is a prefix of nothing, so underline it immediately &mdash; and notice you can """
            """underline it at the z, before the user has finished, which is exactly what the """
            """requirement asked for.""")
seg(sid, 3, """That is the staff-level insight here and it generalises: the data structure follows from """
            """the question you actually have to answer. A hash set answers membership. Only a prefix """
            """structure answers &ldquo;could this still become something&rdquo;. Get the question """
            """right and the trie is obvious; get it wrong and no amount of optimisation saves you.""")

think('A user types "recz". You want to underline at the z. What does your data structure have to be able '
      'to tell you that a hash set of 200,000 words cannot?',
      20,
      """Pause. A user types r-e-c-z and you want to underline at the z. What does your data structure """
      """have to be able to tell you, that a hash set of two hundred thousand words simply cannot? Say """
      """it out loud.""",
      """Keep that. The answer is &ldquo;does any word start with this&rdquo;, and only one family of """
      """structures answers it cheaply.""")

clarify('What I would clarify first', [
 ('Does this run on the client or the server?',
  '<b>The single biggest fork.</b> A keystroke cannot afford a network round trip, so the checking '
  'structure almost certainly has to ship to the device. That bounds its size.'),
 ('How big is the dictionary, and how many languages?',
  '200k English words is a few megabytes. Forty languages with inflections is a different product and '
  'a different shipping problem.'),
 ('Do we need suggestions, or only detection?',
  'Detection is a prefix walk. <b>Suggestion is fuzzy matching</b>, which is a far harder structure and '
  'a much bigger budget. Confirm which is in scope.'),
 ('Are there personal dictionaries &mdash; names, jargon, company terms?',
  'Means a per-user overlay on top of the shared dictionary, and a <b>merge</b> at lookup time.'),
 ('What counts as a word &mdash; hyphens, apostrophes, numbers, camelCase?',
  'Tokenisation decides what you even look up. <code>don&rsquo;t</code> and <code>state-of-the-art</code> '
  'break a naive splitter.'),
 ('How often does the dictionary change?',
  'Rarely &rarr; ship it with the app and forget it. Continuously &rarr; you need a distribution and '
  'versioning story, which is the denylist problem from 4.4 again.'),
], [
 """Client or server? This is the biggest fork in the whole design. A keystroke cannot afford a network """
 """round trip, so the checking structure almost certainly has to live on the device &mdash; and that """
 """immediately bounds how big it is allowed to be. Ask this first.""",
 """How big is the dictionary, and how many languages? Two hundred thousand English words is a few """
 """megabytes. Forty languages with full inflection is a different product with a different shipping """
 """problem.""",
 """Do we need suggestions or only detection? Detection is a prefix walk and is genuinely easy. """
 """Suggestion is fuzzy matching, which is a far harder structure and a much larger budget. Confirm """
 """which is in scope before you commit to anything.""",
 """Are there personal dictionaries &mdash; names, jargon, company terms? That means a per-user overlay """
 """on top of the shared dictionary and a merge at lookup time, which is cheap if you plan for it and """
 """awkward if you bolt it on.""",
 """What counts as a word? Hyphens, apostrophes, numbers, camel case. Tokenisation decides what you """
 """even look up, and a naive splitter breaks on don't and state-of-the-art immediately.""",
 """And how often does the dictionary change? Rarely means ship it with the application and forget it. """
 """Continuously means you need distribution and versioning &mdash; which is the denylist problem from """
 """lesson four point four wearing different clothes.""",
])

capacity('Capacity &mdash; and why this one barely needs a server', [
 ('Dictionary: 200k English words, avg 8 chars', '200,000 &times; 8 B', '&asymp; 1.6 MB raw',
  'Small. <b>The whole question is whether it fits on the device</b>'),
 ('Naive trie: ~26 pointers per node', '~500k nodes &times; 26 &times; 8 B', '&asymp; 100 MB',
  '<b>Too big to ship.</b> The naive structure is 60&times; the data it holds'),
 ('Compressed trie / radix tree', 'collapse single-child chains', '&asymp; 8&ndash;12 MB',
  'Shippable, but still heavy for a mobile app bundle'),
 ('DAWG (shared suffixes merged)', 'identical subtrees deduplicated', '&asymp; 1&ndash;2 MB',
  '<b>Smaller than the word list itself.</b> This is the answer'),
 ('Lookup per keystroke', 'walk one more node', '&asymp; 1 &micro;s, O(1) per key',
  'Effectively free. <b>No server, no network, no QPS to compute</b>'),
 ('Typing rate', '5 keystrokes / s / user', '5 lookups / s / user',
  'Even a billion users generate <b>zero backend load</b> if the check is local'),
], [
 """The numbers, and this is a question where the arithmetic leads somewhere unusual. Two hundred """
 """thousand English words at eight characters each is about one point six megabytes of raw data. """
 """Small. The entire question is whether it fits on the device.""",
 """A naive trie with twenty-six pointers per node is about five hundred thousand nodes times twenty-six """
 """pointers times eight bytes &mdash; roughly a hundred megabytes. The structure is sixty times larger """
 """than the data it holds, which is a lovely thing to say out loud because it kills the obvious answer """
 """with a number.""",
 """A compressed trie, collapsing chains of single-child nodes, gets you to eight or twelve megabytes. """
 """Shippable, but still heavy for a mobile bundle.""",
 """A D-A-W-G &mdash; a directed acyclic word graph &mdash; merges identical subtrees as well, so every """
 """word ending in -ing shares one tail. That lands at one to two megabytes, which is smaller than the """
 """word list you started with. That is the answer.""",
 """A lookup is walking one more node: about a microsecond, constant time per keystroke. Effectively """
 """free.""",
 """And here is the conclusion the numbers force. At five keystrokes a second per user, even a billion """
 """users generate exactly zero backend load, because the check never leaves the device. Saying """
 """&ldquo;this system does not need a server&rdquo; and defending it with arithmetic is a much """
 """stronger answer than designing a service nobody needed.""",
])

A = Arch('Spell check &mdash; the work happens on the device', kicker='Architecture', height=760)

A.zone(540, 130, 700, 480, 'ON THE DEVICE — every keystroke')

A.box('kb',   70, 320, 160, 85, 'Keystroke', '5 / s', kind='neutral', step=0, focus=0, small=True)
A.box('tok',  290, 310, 200, 100, 'Tokeniser', 'word boundaries', kind='ok', step=0, focus=0)
A.arrow('kb', 'tok', step=0, focus=0)

A.box('dawg', 580, 200, 230, 110, 'DAWG', '~1.5 MB, read-only', kind='ok', step=1, focus=[1, 2])
A.arrow('tok', 'dawg', step=1, label='prefix?', focus=1)

A.box('user', 580, 390, 230, 100, 'Personal dict', 'names, jargon', kind='info', step=2, focus=2, small=True)
A.arrow('tok', 'user', step=2, focus=2, dashed=True)

A.box('ui',   900, 290, 220, 105, 'Underline', 'or stay silent', kind='shared', step=3, focus=3)
A.arrow('dawg', 'ui', step=3, focus=3)
A.arrow('user', 'ui', step=3, focus=3, dashed=True)

A.box('sug', 900, 440, 220, 100, 'Suggestions', 'only on demand', kind='neutral', step=4, focus=4, small=True)
A.arrow('ui', 'sug', step=4, focus=4, dashed=True)

A.box('cdn', 1340, 200, 230, 100, 'Dictionary CDN', 'versioned bundles', kind='dp', step=5, focus=5, small=True)
A.arrow('cdn', 'dawg', step=5, focus=5, dashed=True)

A.box('tel', 1340, 390, 230, 100, 'Telemetry', 'unknown words', kind='shared', step=6, focus=6, small=True)
A.arrow('ui', 'tel', step=6, focus=6, dashed=True)

A.note(560, 640, 'There is no request path. The only network calls are a dictionary update and optional telemetry.',
       step=1, kind='info', w=560)

A.narrate(0, """A keystroke arrives and a tokeniser decides where the current word starts and ends. """
             """Boring, and it is where hyphens and apostrophes break naive implementations &mdash; """
             """worth one sentence, not more.""",
          A.flow([(230, 362), (290, 360)]))
A.narrate(1, """The D-A-W-G. One and a half megabytes, read-only, shipped with the application. Each """
             """keystroke walks one node deeper. If the walk falls off the structure, no word starts """
             """with what has been typed, and we underline.""",
          A.flow([(490, 350), (580, 255)]))
A.narrate(2, """A personal dictionary alongside it &mdash; names, jargon, company terms. Small, mutable, """
             """and checked in parallel. A word is only wrong if it is a prefix of nothing in """
             """<i>either</i> structure, and that union is easy to get wrong in the direction of """
             """underlining a colleague's surname every time.""",
          A.flow([(490, 370), (580, 440)]))
A.narrate(3, """The decision reaches the U-I: underline or stay silent. Note what is not on this path """
             """&mdash; there is no network call, no server, no queue. The entire hot path is a pointer """
             """walk.""",
          A.flow([(810, 255), (900, 340)]))
A.narrate(4, """Suggestions hang off to the side and happen only on demand &mdash; when the user right""" 
             """-clicks or long-presses. That separation matters, because suggestions are expensive and """
             """detection is not, and bundling them would make every keystroke pay for a feature used """
             """once a page.""")
A.narrate(5, """Dictionary updates come from a C-D-N as versioned bundles. Rare, in the background, and """
             """exactly the push-with-a-version pattern from the denylist lesson &mdash; the third time """
             """that shape has appeared in this course.""")
A.narrate(6, """And optional telemetry: which unknown words did users type and then keep? That is how the """
             """dictionary learns new words, and it is the one place privacy needs a real answer &mdash; """
             """you are shipping fragments of what people write.""")
A.build()

sid = beat('Deep dive 1', 'Trie, compressed trie, DAWG &mdash; and what each one buys',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>Trie.</b> One node per prefix, a child per letter. Lookup is O(length), independent of '
           'dictionary size. <span style="color:#ff9a9a">~100 MB for 200k words &mdash; the pointers '
           'dwarf the data.</span><br><br>'
           '<b>Compressed trie (radix).</b> Collapse chains with one child: '
           '<code>c&rarr;a&rarr;t</code> becomes a single <code>cat</code> edge. '
           '<span style="color:#a8e6a3">~10&times; smaller</span>, same O(length) lookup.<br><br>'
           '<b>DAWG.</b> Also merge identical <i>suffixes</i>. Every word ending <code>-ing</code> '
           'shares one tail. <span style="color:#a8e6a3">~1&ndash;2 MB. Smaller than the word list.</span>'
           '<br><br>'
           '<b>The cost of the DAWG:</b> it is a graph, not a tree, so a node no longer belongs to one '
           'word. <span style="color:#ff9a9a">You cannot hang per-word data (frequency, language) off '
           'the nodes</span>, and it is awkward to update incrementally &mdash; you rebuild it.<br><br>'
           '<span style="color:#ffd483">So: DAWG for the fixed shared dictionary, a small plain trie '
           'for the mutable personal one. Two structures because they have two lifecycles.</span></div>',
           """Deep dive one: the structures, and what each actually buys you. A trie is one node per """
           """prefix with a child per letter. Lookup is order of word length, completely independent of """
           """dictionary size, which is the property we want. It costs about a hundred megabytes for two """
           """hundred thousand words, because the pointers dwarf the data.""", step=0)
seg(sid, 1, """A compressed trie collapses chains that have only one child, so c-a-t becomes a single """
            """edge labelled &ldquo;cat&rdquo; rather than three nodes. Roughly ten times smaller, with """
            """exactly the same lookup cost. That is close to free and I would do it without """
            """discussion.""")
seg(sid, 2, """A D-A-W-G goes further and merges identical suffixes too. Every word ending in -i-n-g """
            """shares one tail subgraph. That gets you to one or two megabytes &mdash; genuinely smaller """
            """than the raw word list, because you are storing the shared structure once instead of """
            """repeating it.""")
seg(sid, 3, """And here is the cost, which is the part worth volunteering. A D-A-W-G is a graph, not a """
            """tree, so a node no longer belongs to exactly one word. You cannot hang per-word data off """
            """the nodes &mdash; no frequency, no language tag, no part of speech &mdash; because many """
            """words share that node. And it is awkward to update incrementally; in practice you rebuild """
            """it offline.""")
seg(sid, 4, """So the answer is two structures: a D-A-W-G for the big fixed shared dictionary, and a """
            """small plain trie for the mutable personal one. Not because one is better, but because """
            """they have different lifecycles &mdash; one is read-only and shipped, the other changes """
            """whenever the user clicks &ldquo;add to dictionary&rdquo;. Choosing structures by """
            """lifecycle rather than by performance is a staff-level move.""")

sid = beat('Deep dive 2', 'Suggestions &mdash; a different problem with a different budget',
           '<div style="font-size:27px;line-height:1.7">'
           'Detection asks <b>&ldquo;is this a prefix?&rdquo;</b> &mdash; a walk. '
           'Suggestion asks <b>&ldquo;what did they mean?&rdquo;</b> &mdash; a search.<br><br>'
           '<b>Candidate generation</b> &mdash; words within edit distance 1 or 2:<br>'
           '&bull; <b>Generate-and-test</b>: build every edit of the typo and check each. '
           '~80 edits at distance 1 for an 8-letter word; <span style="color:#ff9a9a">~25,000 at '
           'distance 2</span>. Fine for d=1, painful for d=2.<br>'
           '&bull; <b>Trie walk with an error budget</b>: descend the trie allowing k mismatches. '
           '<span style="color:#a8e6a3">Prunes early &mdash; scales to d=2 comfortably.</span><br><br>'
           '<b>Ranking</b> &mdash; candidate generation gives you 50 words; the product is the '
           '<i>top three</i>:<br>'
           '&bull; edit distance (1 beats 2) &bull; word frequency in the language<br>'
           '&bull; keyboard adjacency &mdash; <code>recieve</code>&rarr;<code>receive</code> beats '
           '<code>relieve</code> &bull; the user&rsquo;s own history<br><br>'
           '<span style="color:#ffd483">Same shape as typeahead in lesson 2.2: generate candidates '
           'cheaply, then rank. The ranking is the product.</span></div>',
           """Deep dive two: suggestions, which is the follow-up and is genuinely a different problem. """
           """Detection asks &ldquo;is this a prefix&rdquo;, which is a walk. Suggestion asks """
           """&ldquo;what did they mean&rdquo;, which is a search.""", step=0)
seg(sid, 1, """Candidate generation means finding words within edit distance one or two. The first """
            """approach is generate-and-test: build every possible edit of the typo and check each """
            """against the dictionary. For an eight-letter word that is about eighty candidates at """
            """distance one, which is fine. At distance two it is around twenty-five thousand, which """
            """is painful.""")
seg(sid, 2, """The better approach is to walk the trie with an error budget: descend, allowing up to k """
            """mismatches, and prune a branch the moment the budget is exhausted. That prunes """
            """aggressively and scales to distance two comfortably. It also reuses the structure you """
            """already shipped, which is the real argument for it.""")
seg(sid, 3, """Then ranking, and this is where the product actually lives. Candidate generation hands you """
            """fifty plausible words and the user wants three. Edit distance one beats two. Word """
            """frequency in the language matters enormously &mdash; most typos are for common words. """
            """Keyboard adjacency is the signal people forget: r-e-c-i-e-v-e should suggest receive """
            """over relieve, because i and e are adjacent in the typo pattern. And the user's own """
            """history beats all of it.""")
seg(sid, 4, """Notice the shape: generate candidates cheaply, then rank. That is exactly the typeahead """
            """structure from lesson two point two, and exactly the structure of the job """
            """recommendation lesson later in chapter nine. Three completely different products, one """
            """pipeline. When you see &ldquo;return the best few from many&rdquo;, this is the shape.""")

tradeoff('Where the dictionary lives', [
 ('Server-side API per keystroke', 'info',
  ['One dictionary to update', 'Works on a thin client', 'Full ranking signals available server-side'],
  ['<b>A network round trip per keystroke</b> &mdash; 50&ndash;200 ms',
   'Useless offline', 'Every keystroke is a request: enormous QPS for a trivial answer',
   'You are shipping what the user types to a server &mdash; a privacy question']),
 ('Ship the whole dictionary to the device', 'ok',
  ['Zero latency, zero backend', 'Works offline', '<b>Nothing the user types leaves the device</b>'],
  ['1&ndash;2 MB in the bundle', 'Updates need a distribution story', 'Per-language bundles multiply it']),
 ('Hybrid: local detection, server suggestions', 'shared',
  ['Fast underline, rich ranking when asked', 'Suggestion traffic is tiny &mdash; on demand only'],
  ['Two code paths', 'Suggestions unavailable offline', 'Still a privacy question for the typo sent up']),
], 'Ship a DAWG to the device for detection. That is the hot path, and it should never touch a network.',
 'If the product were a shared web editor on a managed network, or the dictionary were enormous '
 '(CJK, or a 40-language bundle), I would move suggestions server-side and keep only detection local.',
 [
 """Trade-off: where does the dictionary live? Server-side per keystroke gives you one dictionary to """
 """update and works on a thin client, and costs a network round trip per keystroke &mdash; fifty to """
 """two hundred milliseconds on a feature that must feel instant. It is useless offline, it generates """
 """enormous query volume for a trivial answer, and it means everything the user types goes to a """
 """server, which is a privacy conversation you will have to have.""",
 """Shipping the dictionary to the device gives zero latency and zero backend, works offline, and """
 """nothing the user types ever leaves the machine. It costs one to two megabytes in the bundle and """
 """needs an update story, and per-language bundles multiply it.""",
 """The hybrid keeps detection local and sends only suggestion requests &mdash; which are on demand, so """
 """the traffic is tiny.""",
 """I would ship the D-A-W-G to the device for detection. The hot path is a keystroke, and a keystroke """
 """should never touch a network. That is the whole argument and it is enough.""",
 """What would flip it: a shared web editor on a managed network, or a genuinely enormous dictionary """
 """&mdash; C-J-K languages, or a forty-language bundle. Then I would move suggestions server-side and """
 """keep only detection local, because the bundle size argument has inverted.""",
])

failures('What happens when each piece dies', [
 ('Dictionary bundle fails to download', 'Spell check silently stops working',
  'Ship a <b>baseline dictionary with the app</b> so there is always one. Updates improve it; they are '
  'never required for the feature to function'),
 ('Dictionary file is corrupt', 'Crash, or every word underlined',
  'Checksum the bundle and <b>fall back to the previous version</b>. A spell checker that underlines '
  'everything is worse than one that is switched off'),
 ('Personal dictionary lost (reinstall, cache wipe)', 'Colleagues&rsquo; names underlined again',
  'Sync it &mdash; it is tiny, a few kilobytes. <b>The most user-visible failure in the system</b>, and '
  'the cheapest to prevent'),
 ('A word is in the dictionary but wrong in context', '<i>&ldquo;Their going to the store&rdquo;</i> passes',
  '<b>Out of scope and say so.</b> This needs a language model, not a dictionary. Naming the boundary '
  'is better than pretending it is covered'),
 ('Suggestion service unavailable (hybrid)', 'Underlines still work; no suggestions on right-click',
  '<b>Graceful degradation by design</b> &mdash; the valuable half is local and keeps working'),
 ('Telemetry uploads what people typed', 'A privacy incident, not an outage',
  'Only upload words the user <b>explicitly added</b> to their dictionary, hashed and aggregated with '
  'k-anonymity. Default to collecting nothing'),
], [
 """Failures. The dictionary bundle fails to download and spell check silently stops working. The fix """
 """is to ship a baseline dictionary with the application, so there is always one present. Updates """
 """improve it, they are never required for it to function. That is a general principle for anything """
 """shipped to a device.""",
 """A corrupt dictionary either crashes or underlines every word. Checksum the bundle and fall back to """
 """the previous version. A spell checker that underlines everything is worse than one that is turned """
 """off, because the user cannot tell it is broken, they just think your product is stupid.""",
 """Personal dictionary lost on reinstall, and every colleague's name is underlined again. Sync it """
 """&mdash; it is a few kilobytes. I would call this the most user-visible failure in the whole system """
 """and also the cheapest to prevent, which is usually a sign it is worth doing first.""",
 """A word that is in the dictionary but wrong in context &mdash; &ldquo;their going to the store&rdquo; """
 """&mdash; passes cleanly. That is out of scope and I would say so plainly: it needs a language model, """
 """not a dictionary. Naming the boundary of what you built is better than pretending it is covered.""",
 """Suggestion service down in the hybrid: underlines still work, suggestions do not. Graceful """
 """degradation by design, because the valuable half is the local half.""",
 """And telemetry uploading what people typed is a privacy incident rather than an outage. Only upload """
 """words the user explicitly added to their own dictionary, hashed and aggregated with k-anonymity, """
 """and default to collecting nothing. On a system that watches everything a person writes, that """
 """default is the whole ethical question.""",
])

say('What I should actually say in the room', [
 'The requirement says highlight as soon as the characters <i>cannot</i> form a valid word &mdash; so '
 'the question is not &ldquo;is this a word&rdquo;, it is &ldquo;is this still a prefix of any '
 'word&rdquo;. A hash set cannot answer that; a trie can.',
 'A keystroke cannot afford a network round trip, so the structure has to live on the device, which '
 'bounds how big it is allowed to be.',
 'A naive trie is ~100 MB for 200,000 words &mdash; the pointers dwarf the data. A DAWG, sharing '
 'suffixes as well as prefixes, is 1&ndash;2 MB, smaller than the word list itself.',
 'So: DAWG for the shared read-only dictionary, plus a small mutable trie for the personal one. Two '
 'structures because they have two different lifecycles.',
 'At five keystrokes a second this generates zero backend load, because the check never leaves the '
 'device. This system does not need a server for its main feature.',
 'Suggestions are a separate, much more expensive problem &mdash; a trie walk with an error budget to '
 'generate candidates, then ranking on frequency, keyboard adjacency and personal history. I would run '
 'it on demand, not per keystroke.',
], [
 """The sentences. Lead with the restatement of the requirement, because that one move &mdash; prefix """
 """rather than membership &mdash; is the entire question and it takes ten seconds to say.""",
 """Then the latency constraint that forces it onto the device, then the two memory numbers that kill """
 """the naive structure and justify the D-A-W-G. Then the two-structures-two-lifecycles point.""",
 """Then the conclusion most candidates never reach: this feature does not need a backend. And finally """
 """separate suggestions out explicitly, so the interviewer can choose whether to spend time there.""",
])

followups([
 'How do you give real-time suggestions as well?',
 'There are many possible completions &mdash; how do you narrow them?',
 'How do you rank the candidates?',
 'How much memory does the dictionary take?',
 'How do you handle personal dictionaries?',
 'How do dictionary updates get distributed?',
], [
 'Now do it for a language with no spaces between words, like Chinese or Thai.',
 'How would you detect a word that is spelled correctly but wrong in context?',
 'The dictionary is 40 languages. What changes?',
 'How would you measure whether the suggestions are actually any good?',
 'What is the privacy story for a feature that sees everything the user writes?',
],
 """The reported follow-ups are suggestions, narrowing many candidates, ranking, memory, personal """
 """dictionaries and distribution &mdash; and we have covered every one. Ranking is the one to go deep """
 """on if they let you, because it is where the product lives.""",
 """The staff-level follow-ups are harder and more interesting. A language with no spaces, like Chinese """
 """or Thai, breaks tokenisation entirely &mdash; you cannot find word boundaries before you look words """
 """up, so segmentation and checking become one problem rather than two. Context errors need a language """
 """model. Forty languages multiplies the bundle, which pushes you toward downloading per language on """
 """demand. Measuring suggestion quality is genuinely hard and the honest answer is acceptance rate. """
 """And privacy &mdash; for a feature that sees everything the user writes, the right default is that """
 """nothing leaves the device, and you should say that before you are asked.""")

cheatsheet('Spell checker &mdash; the one-page card', [
 ('Requirements', 'Underline as soon as the typed characters cannot <b>prefix</b> any valid word'),
 ('Scale', '200k words, 1.6 MB raw. Naive trie 100 MB, compressed 10 MB, <b>DAWG 1&ndash;2 MB</b>'),
 ('Core architecture', 'Keystroke &rarr; tokeniser &rarr; DAWG walk (+ personal trie) &rarr; underline. '
                       'All on device'),
 ('Data store', 'Read-only DAWG shipped in the app bundle; small mutable trie for personal words'),
 ('Partition key', '<b>None.</b> The dictionary is small enough to replicate whole onto every device'),
 ('Cache', 'The structure <i>is</i> the cache. No eviction, no TTL, no invalidation'),
 ('Queue', 'None. Dictionary updates arrive as versioned bundles from a CDN'),
 ('Consistency', 'Irrelevant on the hot path. Dictionary freshness is eventual and measured in weeks'),
 ('Failure handling', 'Baseline dictionary always present; checksum and roll back; sync the personal '
                      'dictionary'),
 ('Key deep dives', 'Prefix vs membership &middot; trie/radix/DAWG &middot; suggestion ranking'),
 ('Biggest trade-off', 'Bundle size vs latency &mdash; and the latency requirement wins so decisively '
                       'that the server disappears from the design'),
], [
 """The card. The requirement line is the one to memorise: prefix, not membership. Scale is four """
 """numbers and the D-A-W-G is the punchline.""",
 """Architecture is one line and it is entirely on-device. Note the partition key row says none, """
 """because the dictionary replicates whole &mdash; the second time in this course that the right """
 """answer to partitioning is &ldquo;you do not need to&rdquo;.""",
 """Consistency is irrelevant on the hot path, which is a luxury almost nothing else in this course """
 """has. And the biggest trade-off: bundle size versus latency, where latency wins so decisively that """
 """the server disappears from the design altogether.""",
])

say('The 60-second answer', [
 'The key sentence in the requirement is &ldquo;cannot form a valid word&rdquo;. That is not a '
 'membership question, it is a prefix question &mdash; is this still the start of anything? A hash set '
 'cannot answer it; a trie answers it in one node walk per keystroke.',
 'A keystroke has no latency budget for a network call, so the structure ships to the device, and that '
 'caps its size.',
 'A naive trie is about 100 MB for 200,000 words because the pointers dwarf the data. Compressing '
 'single-child chains gets to ~10 MB; a DAWG that also shares suffixes gets to 1&ndash;2 MB &mdash; '
 'smaller than the word list.',
 'So I ship a DAWG for the shared dictionary and keep a small plain trie for personal words, because '
 'one is read-only and the other is mutable.',
 'The consequence is that this feature generates no backend load at all: detection never leaves the '
 'device, which also means nothing the user types is sent anywhere.',
 'Suggestions are a separate and much costlier problem &mdash; a trie walk with an error budget for '
 'candidates, then ranking on frequency, keyboard adjacency and personal history &mdash; and I would '
 'run that on demand rather than on every keystroke.',
], [
 """The sixty-second answer. It opens by reinterpreting the requirement, which is the move that makes """
 """everything else obvious, and it carries real numbers for the structures.""",
 """The fifth sentence is the one that distinguishes it &mdash; concluding that the system needs no """
 """backend, and noticing that this is also the privacy answer. Say it out loud once; a confident """
 """&ldquo;this does not need a server&rdquo; is memorable in a round where everyone else is drawing """
 """load balancers.""",
], kicker='60-second interview answer')
