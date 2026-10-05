# -*- coding: utf-8 -*-
"""Chapter 5, Lesson 2 — document indexing with boolean queries (Lynda)."""
from lib import *

lesson_header('5.2', 'Document indexing with boolean queries',
              'Inverted index &middot; postings intersection &middot; NOT &middot; build it in a month',
              dict(reports='InterviewTV list; related to the Staff search report in 3.1',
                   latest='2026', level='Staff',
                   conf='MEDIUM &mdash; the family is HIGH, this framing is single-source',
                   sources='InterviewTV.io + Taro Staff loop'), 18,
              """Chapter five, lesson two. LinkedIn bought Lynda, Lynda has a huge collection of P-D-Fs, """
              """and you need to index them. The example query they give is specific and worth reading """
              """carefully: documents containing red AND green but NOT blue. And then there is a second """
              """question tucked at the end that most candidates skip &mdash; how would you build an """
              """alpha in one month with two engineers? That is not a throwaway. It is the real """
              """question.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Boolean queries named explicitly: <b>red AND green NOT blue</b>. Plus crawling, parsing, '
  'tokenisation, index construction, partitioning, updates, replication. <b>And: an alpha in one '
  'month with two engineers</b>'),
 ('Taro &mdash; Staff loop, India', '12 May 2025', 'Staff Engineer',
  'A distributed search index question, first-hand, with real detail. <b>Lesson 3.1</b>'),
], """Two related sources. The InterviewTV framing is specific about boolean queries, and it names the """
     """full pipeline &mdash; crawling, parsing, tokenisation, construction, partitioning, updates, """
     """replication.""",
 ["""And the search family is independently attested by a first-hand Staff report from a Taro loop, """
  """which is lesson three point one in this course. Watch that one first if you have not &mdash; this """
  """lesson assumes the sharding and scatter-gather machinery and spends its time on what is """
  """different: boolean logic, P-D-F parsing, and the one-month constraint."""],
 caveat='The search family is well attested. This specific Lynda framing is single-source.',
 narration_caveat="""The search family is well attested. This specific Lynda framing is single-source, """
                  """so hold the details loosely and the machinery tightly.""")

sid = beat('Why this is interesting', 'Two questions in one, and the second is the real test',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>Question one:</b> build a search index. Well-trodden &mdash; inverted index, postings, '
           'sharding. You should be fluent, and fluency alone is a Senior answer.<br><br>'
           '<b>Question two:</b> <i>&ldquo;build an alpha in one month with two engineers.&rdquo;</i>'
           '<br><br>'
           'That is a <b>scoping</b> question wearing a systems costume. It is asking:<br>'
           '&bull; Can you tell the difference between the system and the <i>first useful slice</i> of it?<br>'
           '&bull; Do you know what to <b>buy</b> rather than build?<br>'
           '&bull; Will you spend the month on the index, or on the <b>PDF parsing</b> that will '
           'actually eat it?<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the honest one-month answer is '
           '&ldquo;Elasticsearch, and I spend the month on extraction and evaluation.&rdquo; Being '
           'willing to say that &mdash; in a system design interview &mdash; is the signal.</span>'
           '<br><br>'
           '<span style="color:#a8e6a3">Design the real thing to show you can. Then say what you would '
           'actually ship in a month, and why it is different.</span></div>',
           """Why is this interesting? Because it is two questions, and the second one is the real """
           """test.""", step=0)
seg(sid, 1, """Question one is build a search index. Inverted index, postings lists, sharding, """
            """scatter-gather. Well-trodden ground, and you should be fluent &mdash; but fluency alone """
            """is a senior answer, not a staff one.""")
seg(sid, 2, """Question two is build an alpha in one month with two engineers. That is a scoping question """
            """wearing a systems costume. It is asking whether you can tell the difference between the """
            """system and the first useful slice of it. Whether you know what to buy instead of build. """
            """And whether you will spend the month on the index, or on the P-D-F parsing that is """
            """genuinely going to eat it.""")
seg(sid, 3, """The honest one-month answer is: use Elasticsearch, and spend the month on extraction and """
            """evaluation. Being willing to say that out loud in a system design interview is the """
            """signal. A lot of candidates feel they are supposed to build everything from scratch """
            """because that is what the format seems to reward.""")
seg(sid, 4, """So the structure I would use is: design the real thing, to show you can. Then say what you """
            """would actually ship in a month, and explain why those are different. Doing both is """
            """strictly better than doing either, and it directly answers a question they asked.""")

think('You have one month and two engineers. Of crawling PDFs, extracting text, building the index, '
      'serving queries and ranking results &mdash; which one will actually consume the month, and which '
      'would you buy outright?',
      25,
      """Pause. One month, two engineers. Of crawling, extracting text from P-D-Fs, building the index, """
      """serving queries and ranking results &mdash; which one actually consumes the month? And which """
      """would you simply buy? Say it out loud.""",
      """Hold that answer. We will come back to it, and I suspect your instinct about which part is hard """
      """is correct.""")

clarify('What I would clarify first', [
 ('How many documents, and how large?',
  '50,000 course PDFs is a <b>single machine</b> problem. 50 million is a cluster. The answer changes '
  'the architecture completely, and it is a one-sentence question.'),
 ('Boolean only, or ranked relevance too?',
  'Boolean returns a <b>set</b> &mdash; order does not matter and you can stop early. Ranked returns '
  'the <i>best</i> ten, which needs scoring and changes the postings format.'),
 ('Phrase queries &mdash; &ldquo;machine learning&rdquo; as a phrase?',
  'Needs <b>positions</b> in the postings list, which roughly doubles index size. Worth knowing '
  'before you commit to a format.'),
 ('How fresh? A new course uploaded now &mdash; findable when?',
  'Minutes means an incremental path. Nightly batch is far simpler and usually fine for a course '
  'catalogue.'),
 ('Is it just the PDF text, or transcripts, titles and metadata too?',
  'Video transcripts are probably the <b>most valuable</b> field for Lynda, and they come with '
  'timestamps &mdash; which changes what a &ldquo;result&rdquo; even is.'),
 ('Who searches &mdash; the public, or logged-in members?',
  'Decides whether results need <b>permission filtering</b>, which is much harder than it looks at '
  'index time.'),
], [
 """How many documents and how large? Fifty thousand course P-D-Fs is a single-machine problem and you """
 """should say so rather than reflexively sharding. Fifty million is a cluster. One sentence changes """
 """the entire architecture, so ask it before you draw anything.""",
 """Boolean only, or ranked relevance too? Boolean returns a set, so order does not matter and you can """
 """stop early once you have enough. Ranked returns the best ten, which needs scoring and changes what """
 """you store in the postings.""",
 """Phrase queries? Searching for &ldquo;machine learning&rdquo; as a phrase rather than two words """
 """needs positions in the postings list, which roughly doubles the index size. Worth settling before """
 """you commit to a format.""",
 """How fresh? A new course uploaded now &mdash; findable in minutes, or tomorrow? Minutes means an """
 """incremental indexing path. A nightly batch is dramatically simpler and is almost certainly fine for """
 """a course catalogue that gains a few items a day.""",
 """Is it just the P-D-F text, or transcripts, titles and metadata? For Lynda specifically the video """
 """transcripts are probably the most valuable field, and they come with timestamps &mdash; which """
 """changes what a result even is. You might be returning &ldquo;this course, at eleven minutes """
 """in&rdquo;.""",
 """And who searches &mdash; the public or logged-in members? That decides whether results need """
 """permission filtering, which is much harder at index time than people expect.""",
])

capacity('Capacity', [
 ('50k courses &times; ~40 pages &times; 500 words', '50k &times; 20,000 words',
  '&asymp; 1B words total', 'Sounds huge. <b>It is not</b> &mdash; see below'),
 ('Distinct terms (vocabulary)', 'Heaps&rsquo; law: vocab grows &asymp; &radic;(total words)',
  '&asymp; 1&ndash;2M distinct terms', 'The dictionary fits in RAM easily'),
 ('Postings: 1B word occurrences &times; 4 B docId', '1B &times; 4 B', '&asymp; 4 GB raw',
  'Before compression. <b>One machine can hold this</b>'),
 ('Compressed (delta + varint)', '~1 B per posting typical', '&asymp; 1 GB',
  '<b>Fits in memory on a single box.</b> Say this &mdash; it kills the premature cluster'),
 ('With positions (for phrase queries)', '&asymp; 2&ndash;3&times;', '&asymp; 3 GB',
  'Still single-machine. Positions are affordable here'),
 ('PDF text extraction', '50k docs &times; ~2 s / doc &divide; 8 workers', '&asymp; 3.5 hours',
  '<b>The whole corpus indexes in an afternoon.</b> This is the number that sets the project plan'),
], [
 """Numbers, and this is a case where doing them honestly changes the answer. Fifty thousand courses at """
 """forty pages and five hundred words a page is about a billion words in total. That sounds enormous.""",
 """The distinct vocabulary is much smaller. Heaps' law says vocabulary grows roughly with the square """
 """root of total words, so a billion words gives one to two million distinct terms. The term """
 """dictionary fits in memory trivially.""",
 """Postings: a billion word occurrences at four bytes per document I-D is about four gigabytes raw, """
 """before any compression. One machine holds that.""",
 """Compressed with delta encoding and variable-length integers, postings typically come down to around """
 """one byte each, so about a gigabyte. That fits in memory on a single box, and I would say that out """
 """loud, because it kills the premature cluster. A lot of candidates shard this corpus and never """
 """notice it did not need sharding.""",
 """Adding positions for phrase queries roughly doubles or triples it &mdash; three gigabytes. Still """
 """single-machine. So positions are affordable here, which is not true at web scale.""",
 """And the number that actually sets the project plan: fifty thousand documents at two seconds each """
 """across eight workers is about three and a half hours. The entire corpus indexes in an afternoon. """
 """Which means index build time is not a constraint at all, and the month goes somewhere else.""",
])

A = Arch('Indexing pipeline, and the query path', kicker='Architecture', height=800)

A.zone(60, 130, 700, 290, 'BUILD — offline, runs in an afternoon')
A.zone(60, 470, 1000, 280, 'SERVE — online')

A.box('src',   95, 215, 165, 90, 'PDF store', '50k docs', kind='dp', step=0, focus=0, small=True)
A.box('ext',  300, 205, 200, 105, 'Extractor', 'text + metadata', kind='ok', step=0, focus=[0, 1])
A.arrow('src', 'ext', step=0, focus=0)

A.box('tok',  540, 205, 200, 105, 'Analyser', 'tokenise, fold,<br>stem, stop-words', kind='ok', step=1, focus=1)
A.arrow('ext', 'tok', step=1, focus=1)

A.box('bld',  820, 205, 210, 105, 'Index builder', 'sort by term', kind='info', step=2, focus=2)
A.arrow('tok', 'bld', step=2, focus=2)

A.box('idx', 1110, 195, 230, 120, 'Inverted index', 'term &rarr; postings', kind='ok', step=3, focus=[3, 5])
A.arrow('bld', 'idx', step=3, focus=3)

A.box('q',     95, 555, 165, 90, 'Query', 'red AND green<br>NOT blue', kind='neutral', step=4, focus=4, small=True)
A.box('par',  300, 545, 200, 105, 'Parser', 'boolean tree', kind='ok', step=4, focus=4)
A.arrow('q', 'par', step=4, focus=4)

A.box('exe',  540, 545, 200, 105, 'Executor', 'intersect postings', kind='info', step=5, focus=5)
A.arrow('par', 'exe', step=5, focus=5)
A.arrow('idx', 'exe', step=5, focus=5, dashed=True)

A.box('res',  820, 555, 210, 95, 'Results', 'doc IDs', kind='shared', step=6, focus=6, small=True)
A.arrow('exe', 'res', step=6, focus=6)

A.box('doc', 1110, 545, 230, 105, 'Document store', 'titles, snippets', kind='dp', step=6, focus=6, small=True)
A.arrow('res', 'doc', step=6, focus=6, dashed=True)

A.note(1400, 400, 'The index holds doc IDs only. Fetching titles and snippets is a separate lookup — keep the index small and hot.',
       step=6, kind='info', w=440)

A.narrate(0, """The build side first, and note the zone label: this runs offline and finishes in an """
             """afternoon. P-D-Fs come out of storage and an extractor pulls text and metadata. That """
             """extractor is the part that will actually hurt, and we will come back to it.""",
          A.flow([(260, 260), (300, 257)]))
A.narrate(1, """An analyser tokenises the text, lower-cases it, applies stemming so that """
             """&ldquo;running&rdquo; and &ldquo;runs&rdquo; match, and drops stop words. This stage """
             """decides what is findable, and it has to be applied identically at query time &mdash; """
             """a mismatch here is the classic silent search bug.""",
          A.flow([(500, 257), (540, 257)]))
A.narrate(2, """The index builder sorts every term-document pair by term. That sort is the whole """
             """construction algorithm &mdash; group by term and you have your postings lists.""",
          A.flow([(740, 257), (820, 257)]))
A.narrate(3, """Which gives the inverted index: term, pointing to the sorted list of documents """
             """containing it.""",
          A.flow([(1030, 257), (1110, 255)]))
A.narrate(4, """Now the serve side. A query arrives &mdash; red AND green NOT blue &mdash; and a parser """
             """turns it into a boolean tree rather than treating it as a bag of words.""",
          A.flow([(260, 600), (300, 597)]))
A.narrate(5, """The executor walks that tree against the postings lists, intersecting and subtracting. """
             """That is the next deep dive, because how you do it decides whether this is fast or """
             """merely correct.""",
          A.flow([(500, 597), (540, 597)]))
A.narrate(6, """Results come back as document I-Ds, and a separate lookup fetches titles and snippets """
             """from a document store. Worth drawing as two steps: the index holds I-Ds only, which """
             """keeps it small enough to stay in memory. Putting document text in the index is a """
             """common and expensive mistake.""",
          A.flow([(740, 597), (820, 600), (1110, 597)]))
A.build()

sid = beat('Deep dive 1', 'Executing <b>red AND green NOT blue</b>',
           '<div style="font-size:27px;line-height:1.7">'
           'Postings lists are <b>sorted by document ID</b>. That single property is what makes all '
           'three operators cheap.<br><br>'
           '<b>AND</b> &mdash; walk both lists together, advance the smaller ID. O(n+m), no allocation. '
           '<span style="color:#a8e6a3">Always intersect the <i>shortest</i> list first</span>: '
           '<code>green</code> has 2,000 docs, <code>red</code> has 40,000 &mdash; start from green and '
           'you do 2,000 steps, not 40,000.<br><br>'
           '<b>NOT</b> &mdash; never materialise it. <code>NOT blue</code> alone is &ldquo;every '
           'document except these&rdquo;, which is the whole corpus. <span style="color:#a8e6a3">Apply '
           'it as a <i>filter</i> on an existing candidate set</span>, never as a standalone set.<br><br>'
           '<b>OR</b> &mdash; merge both lists, which can only grow the result. Do it <b>last</b>.<br><br>'
           '<b>Skip pointers:</b> store every &radic;n-th entry so intersection can jump ahead instead '
           'of stepping. Turns O(n+m) into something closer to O(m log n) when one list is tiny.<br><br>'
           '<span style="color:#ffd483">Query planning = reorder the tree so the cheapest, most '
           'selective operation runs first. Same instinct as a SQL optimiser.</span></div>',
           """Deep dive one: actually executing red AND green NOT blue, because the interviewer named """
           """that query and will expect you to run it.""", step=0)
seg(sid, 1, """Everything rests on one property: postings lists are sorted by document I-D. That is what """
            """makes all three operators cheap, and it is why you sort at build time rather than at """
            """query time.""")
seg(sid, 2, """AND is a merge walk. Step through both lists together, always advancing whichever has the """
            """smaller document I-D, and emit when they match. Linear in the two lists, no allocation. """
            """And the optimisation that matters: always start with the shortest list. If green appears """
            """in two thousand documents and red in forty thousand, driving from green means two """
            """thousand steps instead of forty thousand. Term frequency is in your index, so you know """
            """the lengths before you start.""")
seg(sid, 3, """NOT is the one people get wrong. Never materialise it. &ldquo;NOT blue&rdquo; on its own """
            """means every document in the corpus except a few thousand, which is a set the size of your """
            """whole collection. Instead apply it as a filter on a candidate set you already have: """
            """compute red AND green first, then remove anything in blue's list. Same answer, a """
            """thousand times cheaper.""")
seg(sid, 4, """OR merges rather than intersects, so it can only make the result bigger. Do it last, """
            """after the selective operations have cut the candidate set down.""")
seg(sid, 5, """Skip pointers are the refinement: store every square-root-of-n-th entry so an intersection """
            """can jump forward rather than stepping one at a time. When one list is tiny and the other """
            """is huge, that turns a linear walk into something much closer to logarithmic.""")
seg(sid, 6, """And the framing to say out loud: this is query planning. You are reordering the boolean """
            """tree so the cheapest and most selective operation runs first. It is exactly what a S-Q-L """
            """optimiser does with joins, and naming that connection shows you understand why the """
            """optimisation exists rather than just that it does.""")

sid = beat('Deep dive 2', 'One month, two engineers &mdash; what you actually ship',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>What eats the month (and it is not the index):</b><br>'
           '&bull; <b>PDF extraction.</b> Scanned pages with no text layer. Two-column layouts that '
           'interleave. Tables. Slides where text is an image. <span style="color:#ff9a9a">This is '
           'where the month goes, and candidates always underestimate it.</span><br>'
           '&bull; <b>Knowing whether results are any good.</b> With no evaluation set you cannot tell '
           'improvement from regression.<br><br>'
           '<b>The plan I would give:</b><br>'
           '<b>Week 1</b> &mdash; extraction on 500 sample PDFs. Measure what fails. Decide the OCR '
           'question with data, not opinion.<br>'
           '<b>Week 2</b> &mdash; <span style="color:#a8e6a3">Elasticsearch, off the shelf.</span> '
           'Boolean queries work on day one. Index the corpus overnight.<br>'
           '<b>Week 3</b> &mdash; a 50-query evaluation set with human-judged answers. <b>This is the '
           'highest-value week</b> and the one teams skip.<br>'
           '<b>Week 4</b> &mdash; a thin search UI, and iterate on the analyser against the eval set.'
           '<br><br>'
           '<span style="color:#ffd483">&ldquo;I would not build the index. I would buy it, and spend '
           'the month on extraction quality and on being able to tell whether search is working.&rdquo;'
           '</span></div>',
           """Deep dive two, and this is the half of the question most candidates skip. One month, two """
           """engineers &mdash; what do you actually ship?""", step=0)
seg(sid, 1, """First, what eats the month, and it is not the index. It is P-D-F extraction. Scanned pages """
            """with no text layer at all. Two-column layouts where naive extraction interleaves the """
            """columns into nonsense. Tables. Slide decks where the text is an image. If Lynda's """
            """collection is anything like a real one, a meaningful fraction of those documents will """
            """not give up their text easily, and that is where your two engineers will actually """
            """spend their time.""")
seg(sid, 2, """Second, knowing whether the results are any good. Without an evaluation set you cannot """
            """tell an improvement from a regression, so every tuning decision is guesswork dressed up """
            """as engineering.""")
seg(sid, 3, """So here is the plan. Week one: run extraction over five hundred sample P-D-Fs and measure """
            """what fails. Decide the O-C-R question with data rather than opinion &mdash; you may find """
            """two percent need it, or forty percent, and those are different projects.""")
seg(sid, 4, """Week two: Elasticsearch, off the shelf. Boolean queries work on day one, it does postings """
            """compression and skip lists better than you will in a month, and the whole corpus indexes """
            """overnight. Buying this is not a compromise, it is the correct engineering decision at """
            """this scale.""")
seg(sid, 5, """Week three: build a fifty-query evaluation set with human-judged correct answers. I would """
            """argue this is the highest-value week in the month, and it is the one teams always skip """
            """because it does not feel like building. Without it, week four is blind.""")
seg(sid, 6, """Week four: a thin search U-I, and iterate on the analyser against the eval set. And the """
            """sentence I would actually say: I would not build the index, I would buy it, and spend """
            """the month on extraction quality and on being able to tell whether search is working. """
            """Saying that confidently in a system design interview takes a bit of nerve, and it is """
            """exactly what the question was testing.""")

tradeoff('Build the index, or buy it', [
 ('Build the inverted index yourself', 'info',
  ['Full control of the postings format', 'Nothing you do not understand',
   'Shows you know how search works'],
  ['<b>Months of work</b> for compression, skip lists, merging, recovery',
   'You will reimplement Lucene, worse', 'Zero product value delivered while you do it']),
 ('Elasticsearch / OpenSearch', 'ok',
  ['Boolean queries on day one', 'Battle-tested compression, ranking and sharding',
   'Operational tooling already exists'],
  ['A cluster to operate', 'Opinionated &mdash; fighting it is painful',
   'You must still understand what it does, or you cannot debug it']),
 ('SQLite FTS5 / a single-node library', 'shared',
  ['<b>Zero ops</b>', 'Genuinely sufficient for 50k documents', 'Trivially embeddable in the alpha'],
  ['Single node, so no horizontal scale', 'Weaker ranking', 'A migration later if it grows']),
], 'For an alpha in a month: <b>Elasticsearch</b>, or even SQLite FTS5 if 50k documents is really the '
   'ceiling. Spend the engineering on extraction and evaluation.',
 'I would build the index myself if the ranking had to do something no engine supports &mdash; a '
 'domain-specific scoring model &mdash; or if the corpus were large enough that the licence and '
 'hardware cost of an engine exceeded the cost of the engineers.',
 [
 """Trade-off: build the index or buy it. Building it yourself gives full control and proves you """
 """understand search, and costs months of work on compression, skip lists, segment merging and crash """
 """recovery. You will reimplement Lucene, worse, and deliver no product value while you do.""",
 """Elasticsearch gives you boolean queries on day one with battle-tested compression, ranking and """
 """sharding. The cost is a cluster to operate and an opinionated system that is painful to fight """
 """&mdash; and the real cost, which is that you must still understand what it does internally or you """
 """cannot debug it when it misbehaves.""",
 """And the option people forget: SQLite F-T-S five, or a single-node library. Zero operations, """
 """genuinely sufficient for fifty thousand documents, and trivially embeddable. For an alpha that may """
 """be the right answer, and offering it shows you are sizing the solution to the problem.""",
 """For an alpha in a month I would take Elasticsearch, or even SQLite if fifty thousand documents is """
 """really the ceiling, and spend the engineering on extraction and evaluation.""",
 """What would flip it: if ranking had to do something no engine supports &mdash; a domain-specific """
 """scoring model &mdash; or if the corpus were large enough that licence and hardware cost exceeded """
 """the cost of the engineers. Both are real, and neither applies to fifty thousand P-D-Fs.""",
])

failures('What happens when each piece dies', [
 ('A PDF cannot be parsed', 'That course is invisible in search',
  '<b>The most common real failure, and it is silent.</b> Track extraction coverage as a first-class '
  'metric; alert when it drops. A document missing from an index looks exactly like a document that '
  'does not match'),
 ('Analyser changes (new stemmer, new stop-words)', 'Old documents stop matching new queries',
  'Index and query analysers <b>must be the same version</b>. Changing one means a full reindex &mdash; '
  'version the analyser and store it with the index'),
 ('Index shard unavailable', 'Partial results, silently',
  'Return results <b>with a flag saying they are incomplete</b>. Silently returning 80% of matches as '
  'though complete is the worst option &mdash; the user cannot tell'),
 ('Index build fails halfway', 'Half-updated index, inconsistent results',
  'Build into a <b>new index and swap an alias atomically</b>. Never mutate the live index in place '
  '&mdash; this is why Elasticsearch aliases exist'),
 ('A query matches 2 million documents', 'Slow query, memory spike',
  'Cap the candidate set and <b>paginate with a cursor</b>, not an offset. Deep offsets re-scan from '
  'the start every time'),
 ('Document deleted but still in the index', 'Search returns a 404 link',
  'Tombstone on delete and filter at query time; purge at the next merge. <b>Deletion in an inverted '
  'index is always deferred</b> &mdash; say so'),
], [
 """Failures. A P-D-F that cannot be parsed makes that course invisible. I would call this the most """
 """common real failure in any search system, and the dangerous part is that it is silent &mdash; a """
 """document missing from the index looks exactly like a document that did not match the query. So """
 """track extraction coverage as a first-class metric and alert when it drops.""",
 """Analyser changes: if you upgrade the stemmer or the stop-word list, old documents stop matching new """
 """queries, because they were indexed under different rules. The index analyser and the query analyser """
 """must be the same version. Changing one means a full reindex, so version the analyser and store that """
 """version with the index.""",
 """Index shard unavailable gives partial results. Return them with a flag saying they are incomplete. """
 """Silently returning eighty percent of the matches as though that were all of them is the worst """
 """available option, because the user has no way to know.""",
 """Index build fails halfway and leaves a half-updated index. Build into a new index and swap an alias """
 """atomically. Never mutate the live index in place &mdash; that is precisely why Elasticsearch """
 """aliases exist, and knowing why a feature exists is worth more than knowing it does.""",
 """A query that matches two million documents is slow and spikes memory. Cap the candidate set and """
 """paginate with a cursor rather than an offset, because deep offsets re-scan from the beginning every """
 """time.""",
 """And a document deleted but still in the index returns a dead link. Tombstone it on delete, filter """
 """at query time, and purge at the next segment merge. Deletion in an inverted index is always """
 """deferred, and saying that plainly shows you know how these engines actually work.""",
])

say('What I should actually say in the room', [
 'Before I design: how many documents? If it is 50,000 courses, this is a single-machine problem and I '
 'want to avoid building a cluster nobody needs.',
 'Running the numbers &mdash; about a billion words, 1&ndash;2 million distinct terms, and roughly 1 GB '
 'of compressed postings. That fits in memory on one box.',
 'The structure is an inverted index: term to a list of document IDs, sorted by ID. Sorted is what '
 'makes the boolean operators cheap.',
 'For <i>red AND green NOT blue</i> &mdash; intersect starting from the shortest list, and never '
 'materialise the NOT. Apply it as a filter on the candidates you already have.',
 'I would keep document text out of the index. The index returns IDs; a separate store returns titles '
 'and snippets. That keeps the hot structure small.',
 'On your one-month question: I would not build the index. Elasticsearch gives boolean queries on day '
 'one, and the month goes on PDF extraction, which is what will actually hurt, and on an evaluation '
 'set so we can tell whether search is working.',
 'The failure I would watch hardest is a PDF that silently fails to extract &mdash; it is '
 'indistinguishable from a document that does not match, so extraction coverage has to be a metric.',
], [
 """The sentences. Open with the corpus-size question, because answering it honestly may save you from """
 """designing a cluster nobody needs &mdash; and resisting unnecessary scale is a staff signal.""",
 """Then the numbers that justify a single machine, the structure, and the boolean execution with its """
 """two specific optimisations. Then the IDs-not-text point.""",
 """Then answer the one-month question directly and without hedging, and finish on the silent failure """
 """mode, which shows you have thought about operating it rather than only building it.""",
])

followups([
 'How do you crawl and parse the documents?',
 'How do you tokenise?',
 'How do you build the index?',
 'How do you partition it?',
 'How do you execute boolean queries?',
 'How do you handle updates and deletes?',
 'How do you replicate it?',
 'How would you build an alpha in one month with two engineers?',
], [
 'Now add relevance ranking. What changes in the postings?',
 'Results must respect per-member permissions. How?',
 'The transcripts have timestamps &mdash; can you return &ldquo;this course at 11:42&rdquo;?',
 'How would you support search across 20 languages?',
 'How do you know your search is getting better and not worse?',
],
 """The reported follow-ups walk the whole pipeline &mdash; crawling, tokenising, building, """
 """partitioning, boolean execution, updates, deletes, replication, and the one-month alpha. On """
 """partitioning, the answer at this scale is that you probably do not need to, and if you do, shard by """
 """document I-D rather than by term, so every shard can answer any query independently and you """
 """scatter-gather. Sharding by term sounds appealing and creates a query that must visit several """
 """shards and join.""",
 """The staff-level follow-ups go where the product goes. Adding relevance ranking means storing term """
 """frequencies in the postings, which grows them. Permission filtering is genuinely hard and the """
 """honest answer is to filter after retrieval and over-fetch to compensate, because indexing """
 """permissions makes every permission change a reindex. Transcript timestamps turn a result from a """
 """document into a moment, which is a lovely feature and changes your postings to carry offsets. """
 """Twenty languages means per-language analysers and probably per-language indexes. And the last one """
 """&mdash; how do you know search is getting better &mdash; is the evaluation set again, which is why """
 """I would build it in week three rather than never.""")

cheatsheet('Document indexing &mdash; the one-page card', [
 ('Requirements', 'Index 50k PDFs; boolean queries including NOT; alpha in one month, two engineers'),
 ('Scale', '~1B words, 1&ndash;2M terms, ~1 GB compressed postings, ~3.5 h to index the corpus'),
 ('Core architecture', 'Extract &rarr; analyse &rarr; sort by term &rarr; inverted index. Query: parse '
                       '&rarr; plan &rarr; intersect postings &rarr; fetch docs'),
 ('Data store', 'Inverted index (IDs only) in memory; separate document store for titles and snippets'),
 ('Partition key', '<b>Document ID</b>, so every shard answers any query independently. Not term '
                   '&mdash; that forces a cross-shard join. And at 50k docs, probably no shard at all'),
 ('Cache', 'Hot postings lists; whole-query result cache for repeated queries'),
 ('Queue', 'Only for incremental updates; the initial build is a batch job'),
 ('Consistency', 'Eventual. Build into a new index and swap an alias atomically'),
 ('Failure handling', 'Track extraction coverage; flag partial results; tombstone deletes and purge '
                      'on merge'),
 ('Key deep dives', 'Boolean execution and query planning &middot; the one-month plan'),
 ('Biggest trade-off', 'Build vs buy. <b>At this scale, buy &mdash; and spend the time on extraction '
                       'quality and evaluation</b>'),
], [
 """The card. Requirements include the one-month constraint, because it is half the question. Scale """
 """&mdash; and the three and a half hours is the number that tells you index build is not the hard """
 """part.""",
 """Architecture in two lines, build and serve. Partition by document I-D, not by term, so every shard """
 """can answer independently &mdash; and at fifty thousand documents, probably not at all.""",
 """Consistency is eventual via an atomic alias swap. Failure handling leads with extraction coverage. """
 """And the biggest trade-off is build versus buy, where at this scale the answer is buy, and spend the """
 """time on the parts nobody can sell you.""",
])

say('The 60-second answer', [
 'First I would ask how many documents, because 50,000 course PDFs is a single-machine problem and I '
 'do not want to build a cluster nobody needs.',
 'At that size it is about a billion words, one to two million distinct terms, and roughly a gigabyte '
 'of compressed postings &mdash; which fits in memory on one box.',
 'The structure is a standard inverted index, term to document IDs sorted by ID, and that sort order '
 'is what makes the boolean operators cheap.',
 'For red AND green NOT blue I intersect starting from the shortest postings list, and I never '
 'materialise the NOT &mdash; it is applied as a filter on an existing candidate set, because on its '
 'own it means the entire corpus.',
 'The index stores document IDs only; titles and snippets come from a separate store, which keeps the '
 'hot structure small enough to stay in memory.',
 'And on building an alpha in a month with two engineers: I would not build the index at all. '
 'Elasticsearch gives boolean queries on day one. The month goes on PDF extraction &mdash; scanned '
 'pages and two-column layouts are what will actually hurt &mdash; and on a 50-query evaluation set, '
 'so we can tell whether search is improving or regressing.',
], [
 """The sixty-second answer. Notice it spends its last and longest sentence on the one-month question, """
 """because that is the half of the problem most candidates drop entirely.""",
 """Say it once from memory. The phrase to land cleanly is &ldquo;I would not build the index at """
 """all&rdquo; &mdash; delivered without apology, immediately followed by what you would do instead and """
 """why. That combination is what makes it sound like judgement rather than laziness.""",
], kicker='60-second interview answer')
