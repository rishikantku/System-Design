# -*- coding: utf-8 -*-
"""Chapter 6, Lesson 1 — a disk-based key-value store."""
from lib import *

lesson_header('6.1', 'Design a disk-based key-value store',
              'Append-only log &middot; in-memory index &middot; compaction &middot; crash recovery',
              dict(reports='InterviewTV list only', latest='2026', level='Staff, Infrastructure',
                   conf='MEDIUM &mdash; single source, and a classic infra question',
                   sources='InterviewTV.io'), 18,
              """Chapter six, lesson one: a disk-based key-value store. And read the constraints """
              """carefully, because they are unusually specific. You can append to a file, read bytes """
              """from an offset, and create a file. Keys are eight bytes and all keys fit in memory. """
              """Values do not fit in memory and must be read from disk. Those constraints are not """
              """flavour text &mdash; they are describing a particular design, and your job is to """
              """notice which one.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff, Infrastructure',
  'Primitives given: <b>append to a file, read bytes at an offset, create a file</b>. Keys 8 B and '
  'fit in memory; values do not. Deep dives named: in-memory index, file layout, offsets, compaction, '
  'crash recovery, checksums, concurrency, disk I/O, write amplification'),
], """Single source, so medium confidence &mdash; but this is a classic infrastructure question and the """
     """framing here is unusually precise. The primitives you are given are append, read-at-offset, and """
     """create. That is it. No seek-and-overwrite, no delete.""",
 ["""And the named deep dives &mdash; in-memory index, offsets, compaction, crash recovery, checksums, """
  """write amplification &mdash; are the syllabus of a log-structured store. The question has told you """
  """what it wants; the skill is hearing it."""],
 caveat='Single source. But the structure here is the basis of Bitcask, LevelDB, RocksDB and Kafka, so '
        'it is worth knowing regardless.',
 narration_caveat="""Single source for this exact framing. The structure underlies Bitcask, LevelDB, """
                  """RocksDB and Kafka's own storage, so it is worth knowing whatever gets asked.""")

sid = beat('Why this is interesting', 'The constraints are the answer, if you read them',
           '<div style="font-size:28px;line-height:1.72">'
           '<b>&ldquo;You can append to a file.&rdquo;</b> Not overwrite. Not seek-and-write. '
           '<span style="color:#a8e6a3">Append-only is being handed to you.</span><br><br>'
           '<b>&ldquo;Keys fit in memory. Values do not.&rdquo;</b> So the index lives in RAM and the '
           'data lives on disk. <span style="color:#a8e6a3">The split is specified, not chosen.</span>'
           '<br><br>'
           '<b>&ldquo;Read bytes from an offset.&rdquo;</b> So the index must map key &rarr; '
           '<i>offset</i>. <span style="color:#a8e6a3">The index entry format is specified too.</span>'
           '<br><br>'
           'Put those together and you have:<br>'
           '<b>a hash map in memory from key to (file, offset, length), over an append-only log on '
           'disk.</b><br><br>'
           'That is <b>Bitcask</b>. The question described it; you just have to recognise it.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: when a question specifies primitives this '
           'precisely, the primitives <i>are</i> the hint. Spend thirty seconds reading them back before '
           'designing anything.</span></div>',
           """Why is this interesting? Because the constraints are the answer, if you actually read """
           """them rather than skimming to get to the architecture.""", step=0)
seg(sid, 1, """You can append to a file. Not overwrite, not seek-and-write. Append-only storage is being """
            """handed to you, which is a big architectural decision made for free.""")
seg(sid, 2, """Keys fit in memory, values do not. So the index lives in RAM and the data lives on disk. """
            """That split is specified rather than chosen. And read bytes from an offset tells you the """
            """index must map a key to an offset &mdash; so even the index entry format is """
            """specified.""")
seg(sid, 3, """Put those three together and you have a hash map in memory from key to file, offset and """
            """length, sitting over an append-only log on disk. That is Bitcask, the storage engine """
            """behind Riak. The question described it; your job is to recognise it and then defend """
            """it.""")
seg(sid, 4, """And the staff-level habit worth taking from this: when a question specifies primitives """
            """this precisely, the primitives are the hint. Spend thirty seconds reading them back """
            """before designing anything. In a lot of infrastructure questions the constraints have """
            """already eliminated most of the design space, and candidates who start drawing """
            """immediately end up arguing for something the question ruled out in its second """
            """sentence.""")

think('Every write appends to the end of a file and nothing is ever overwritten. So what happens to the '
      'old value when you update a key twice &mdash; and what does that mean for the size of the file '
      'after a year of updates?',
      25,
      """Pause. Every write appends to the end of a file, and nothing is ever overwritten. So what """
      """happens to the old value when you update the same key twice? And what does that mean for the """
      """size of your file after a year of updates? Say it out loud.""",
      """Hold that. Dead data accumulating is the price of append-only, and reclaiming it is the """
      """hardest part of this design.""")

clarify('What I would clarify first', [
 ('Single process, or concurrent readers and writers?',
  '<b>Single writer transforms this problem.</b> Append-only plus one writer means almost no locking, '
  'because readers never see a partial record.'),
 ('How many keys, and how big are values?',
  '10M keys &times; 8 B is trivial. 10B keys does not fit in memory, and then the whole premise of the '
  'question changes.'),
 ('Durability &mdash; must a write survive power loss the instant it returns?',
  '<code>fsync</code> per write is ~1 ms and caps you at ~1,000 writes/s. Batched fsync is 100&times; '
  'faster and risks the last few milliseconds. <b>Ask, because it sets the throughput ceiling.</b>'),
 ('Do we need range scans, or only point lookups?',
  '<b>The biggest fork after durability.</b> Point lookups &rarr; hash index, which is what the '
  'question implies. Ranges &rarr; sorted structure, and you are building an LSM tree instead.'),
 ('Deletes?',
  'Append-only cannot remove anything, so a delete is a <b>tombstone record</b>. That matters for '
  'compaction and for crash recovery.'),
 ('How much disk, and is space reclamation required?',
  'If disk is effectively free, you can defer compaction a long time. If not, compaction is on the '
  'critical path from day one.'),
], [
 """Single process, or concurrent readers and writers? A single writer transforms this problem """
 """&mdash; append-only plus one writer means almost no locking is needed, because a reader can never """
 """observe a half-written record. Establish that early; it removes a whole section of difficulty.""",
 """How many keys and how big are the values? Ten million keys at eight bytes is trivial. Ten billion """
 """keys does not fit in memory, and then the premise of the question has changed and you should say """
 """so.""",
 """Durability &mdash; must a write survive power loss the moment it returns? An fsync per write is """
 """about a millisecond, which caps you near a thousand writes a second. Batched fsync is a hundred """
 """times faster and risks the last few milliseconds of writes. Ask, because that single answer sets """
 """your throughput ceiling.""",
 """Do we need range scans or only point lookups? This is the biggest fork after durability. Point """
 """lookups means a hash index, which is what the question implies by giving you keys in memory. Range """
 """scans mean a sorted structure, and you are building an L-S-M tree instead of a Bitcask.""",
 """Deletes? Append-only cannot remove anything, so a delete has to be a tombstone record appended like """
 """any other write. That matters for compaction and for crash recovery.""",
 """And how much disk, and is space reclamation required? If disk is effectively free you can defer """
 """compaction for a long time. If not, compaction is on the critical path from day one.""",
])

capacity('Capacity', [
 ('10M keys &times; (8 B key + 16 B offset/len/file)', '10M &times; 24 B',
  '&asymp; 240 MB index', '<b>Fits in RAM comfortably.</b> This is why the design works'),
 ('100M keys', '100M &times; 24 B', '&asymp; 2.4 GB index',
  'Still fits on a server. <b>~1B keys is where this design dies</b>'),
 ('Values: 10M &times; 10 KB avg', '10M &times; 10 KB', '&asymp; 100 GB on disk',
  'Never in memory. Every read is a disk seek'),
 ('Read: 1 index lookup + 1 disk seek', 'RAM ~100 ns + NVMe ~100 &micro;s',
  '&asymp; 100 &micro;s per read', '<b>Exactly one seek per read</b> &mdash; the design&rsquo;s main '
  'guarantee'),
 ('Write with fsync per record', '~1 ms per fsync', '&asymp; 1,000 writes / s',
  'Durability is the bottleneck, not the disk&rsquo;s bandwidth'),
 ('Write with batched fsync (every 10 ms)', 'amortise across the batch', '&asymp; 100,000 writes / s',
  '<b>100&times; throughput, risking 10 ms of writes.</b> Name the trade explicitly'),
], [
 """Numbers. Ten million keys, each with an eight byte key plus about sixteen bytes of file I-D, offset """
 """and length, is about two hundred and forty megabytes of index. That fits in RAM comfortably, and """
 """that is the entire reason this design is allowed to exist.""",
 """A hundred million keys is two point four gigabytes &mdash; still fine on a server. Around a billion """
 """keys is where this design dies, because the index stops fitting, and then you need an L-S-M tree """
 """where the index itself is on disk. Knowing where your design breaks is worth saying unprompted.""",
 """Values at ten million times ten kilobytes is a hundred gigabytes on disk. Never in memory, so every """
 """read is a disk seek.""",
 """A read is one index lookup in RAM, about a hundred nanoseconds, plus one disk seek, about a hundred """
 """microseconds on N-V-M-e. So roughly a hundred microseconds per read &mdash; and crucially, exactly """
 """one seek. That is the main guarantee this design offers and it is what distinguishes it from a """
 """B-tree, which may need several.""",
 """Writes with an fsync per record are capped around a thousand a second. Note that the bottleneck is """
 """durability, not the disk's bandwidth &mdash; the disk could take far more, you are waiting for the """
 """flush.""",
 """Batching fsync every ten milliseconds amortises it across the whole batch and gets you to around a """
 """hundred thousand writes a second. A hundred times the throughput, risking ten milliseconds of """
 """writes on power loss. Name that trade explicitly rather than quietly picking one.""",
])

A = Arch('Append-only log with an in-memory index', kicker='Architecture', height=800)

A.box('w',    60, 180, 150, 85, 'Write', 'put(k,v)', kind='neutral', step=0, focus=0, small=True)
A.box('r',    60, 430, 150, 85, 'Read', 'get(k)', kind='neutral', step=3, focus=3, small=True)

A.box('idx',  280, 290, 240, 125, 'In-memory index', 'key &rarr; file, offset, len', kind='ok', step=0,
      focus=[0, 1, 3])
A.arrow('w', 'idx', step=0, focus=0)

A.zone(580, 140, 740, 330, 'ON DISK — append-only segments')
A.box('act',  620, 200, 240, 110, 'Active segment', 'append here only', kind='ok', step=1, focus=[1, 2])
A.arrow('idx', 'act', step=1, label='append', focus=1)

A.box('old1', 620, 340, 240, 95, 'Sealed segment', 'read-only', kind='dp', step=2, focus=2, small=True)
A.box('old2', 910, 340, 240, 95, 'Sealed segment', 'read-only', kind='dp', step=2, focus=2, small=True)
A.box('old3', 910, 200, 240, 95, 'Sealed segment', 'read-only', kind='dp', step=2, focus=2, small=True)

A.arrow('r', 'idx', step=3, focus=3)
A.arrow('idx', 'old1', step=3, label='read at offset', focus=3, dashed=True)

A.box('comp', 620, 560, 250, 110, 'Compactor', 'live records only', kind='info', step=4, focus=[4, 5])
A.arrow('old1', 'comp', step=4, focus=4, dashed=True)
A.arrow('old2', 'comp', step=4, focus=4, dashed=True)

A.box('new',  960, 560, 240, 110, 'Merged segment', '+ hint file', kind='shared', step=5, focus=5)
A.arrow('comp', 'new', step=5, focus=5)
A.arrow('new', 'idx', step=5, label='swap', focus=5, dashed=True)

A.note(1370, 200, 'One seek per read, always. The index knows exactly where the value is — no tree to descend.',
       step=3, kind='info', w=430)
A.note(1270, 580, 'Hint files make restart fast: rebuild the index without reading the values.',
       step=5, kind='info', w=420)

A.narrate(0, """A write arrives. It updates the in-memory index and appends to disk &mdash; and the """
             """order matters, which we will come back to in the crash-recovery dive.""",
          A.flow([(210, 222), (280, 300)]))
A.narrate(1, """There is exactly one active segment and writes only ever go to the end of it. That is the """
             """whole write path: no seeking, no in-place update, so the disk is doing pure sequential """
             """I-O, which even on N-V-M-e is meaningfully faster than random.""",
          A.flow([(520, 330), (620, 255)]))
A.narrate(2, """When the active segment reaches a size limit, it is sealed and a new one is opened. """
             """Sealed segments are immutable and read-only forever. Immutability is what makes """
             """everything else &mdash; concurrency, compaction, recovery &mdash; tractable.""")
A.narrate(3, """A read looks the key up in the in-memory index, which gives a file, an offset and a """
             """length, then reads exactly those bytes. One seek. Always one. No tree to descend, no """
             """variable number of hops &mdash; which means predictable tail latency, and that """
             """predictability is often worth more than the average.""",
          A.flow([(210, 472), (280, 400), (620, 387)]))
A.narrate(4, """The compactor reads sealed segments and keeps only the records that are still live """
             """&mdash; the ones the index still points at. Everything superseded or tombstoned is """
             """dropped.""",
          A.flow([(860, 387), (745, 560)]))
A.narrate(5, """It writes a merged segment plus a hint file, then atomically swaps the index entries over """
             """and deletes the old segments. The hint file holds just the keys and offsets, so on """
             """restart you rebuild the index by reading hints rather than scanning a hundred gigabytes """
             """of values. That one file turns a ten-minute startup into a few seconds.""",
          A.flow([(870, 615), (960, 615)]))
A.build()

sid = beat('Deep dive 1', 'Crash recovery, and the order of two writes',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The question:</b> the process dies mid-write. What state is the store in?<br><br>'
           '<b>Order matters, and only one order is safe:</b><br>'
           '&bull; <span style="color:#a8e6a3">Append to disk, fsync, <i>then</i> update the index.</span> '
           'A crash before the index update loses the write &mdash; but the store is '
           '<b>consistent</b>, and the caller never got an acknowledgement.<br>'
           '&bull; <span style="color:#ff9a9a">Index first, then disk</span> &rarr; the index points at '
           'an offset that does not exist. <b>Reads return garbage.</b> Never do this.<br><br>'
           '<b>Torn writes.</b> A partially-written record at the tail is normal after a crash. '
           'Every record carries a <b>CRC</b>; on recovery, scan from the last known-good point and '
           'stop at the first bad checksum. <span style="color:#a8e6a3">Truncate there.</span><br><br>'
           '<b>Recovery itself:</b> load hint files for sealed segments (fast), then scan only the '
           '<i>active</i> segment record by record. Bounded by segment size, not by total data.<br><br>'
           '<span style="color:#ffd483">This is why segments are size-capped: the cap is a bound on '
           'recovery time. The size limit is a <i>recovery</i> decision, not a storage one.</span></div>',
           """Deep dive one: crash recovery, and it starts with a question about the order of two """
           """operations. The process dies mid-write. What state is the store in?""", step=0)
seg(sid, 1, """Only one order is safe. Append to disk, fsync, and then update the in-memory index. If """
            """you crash before the index update, you have lost that write &mdash; but the store is """
            """consistent, and the caller never received an acknowledgement, so nobody was lied to.""")
seg(sid, 2, """Do it the other way round &mdash; index first, then disk &mdash; and after a crash the """
            """index points at an offset that does not exist. Reads return garbage, or crash, and """
            """the store is corrupt rather than merely behind. Never do this, and say why rather than """
            """just asserting the order.""")
seg(sid, 3, """Torn writes. A partially-written record at the tail of the file is completely normal after """
            """a power loss. So every record carries a C-R-C, and recovery scans forward from the last """
            """known-good point and stops at the first bad checksum, then truncates there. The checksum """
            """is not there to detect disk rot &mdash; it is there to find the end of valid data.""")
seg(sid, 4, """Recovery itself: load hint files for the sealed segments, which is fast because hints are """
            """tiny, then scan only the active segment record by record. So recovery time is bounded by """
            """segment size, not by how much total data you have.""")
seg(sid, 5, """Which gives the point I would most want to make here: segments are size-capped because """
            """the cap is a bound on recovery time. The segment size limit is a recovery decision """
            """dressed as a storage decision. Noticing which requirement a parameter actually serves is """
            """a very staff-level thing to say.""")

sid = beat('Deep dive 2', 'Compaction, and the write amplification it buys',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The problem:</b> update a key 100 times and the file holds 100 copies, 99 of them dead. '
           'Disk grows with <i>writes</i>, not with <i>data</i>.<br><br>'
           '<b>Compaction:</b> read sealed segments, keep only records the index still points at, write '
           'a new segment, swap, delete the old ones.<br><br>'
           '<b>The cost is write amplification.</b> Every byte you wrote once gets rewritten by every '
           'compaction that touches it. <span style="color:#ffd483">Amplification &asymp; number of '
           'times a record is rewritten before it dies.</span><br><br>'
           '<b>When to compact &mdash; and this is the real question:</b><br>'
           '&bull; Track <b>dead bytes per segment</b> (you know this: an index update means the old '
           'record just died)<br>'
           '&bull; Compact a segment when dead &gt; ~40%, not on a timer<br>'
           '&bull; Compact <b>one segment at a time</b>, throttled &mdash; a compaction storm will '
           'starve live traffic of I/O<br><br>'
           '<span style="color:#a8e6a3">Never compact the active segment. It is being appended to; '
           'immutability is what makes compaction safe to run concurrently with reads.</span></div>',
           """Deep dive two: compaction, which is the answer to what I asked you to pause on. Update a """
           """key a hundred times and the file holds a hundred copies, ninety-nine of them dead. Disk """
           """grows with the number of writes, not with the amount of data you actually hold.""", step=0)
seg(sid, 1, """Compaction reads sealed segments, keeps only the records the index still points at, writes """
            """a fresh segment, swaps it in and deletes the old ones. Conceptually simple.""")
seg(sid, 2, """The cost is write amplification. Every byte you wrote once gets rewritten by every """
            """compaction that touches it, so your disk does several times the write traffic your """
            """application actually generated. On S-S-Ds that matters for endurance as well as """
            """throughput, and it is the number a storage interviewer will want you to name.""")
seg(sid, 3, """When to compact is the real question. Track dead bytes per segment &mdash; and you already """
            """know this for free, because every index update tells you the record it replaced just """
            """died. Compact a segment when it is more than about forty percent dead, rather than on a """
            """timer. A timer compacts segments that did not need it and ignores ones that did.""")
seg(sid, 4, """Compact one segment at a time and throttle it. A compaction storm will starve live traffic """
            """of I-O, and the classic production incident with log-structured stores is exactly that """
            """&mdash; latency spikes caused by your own background maintenance, not by load.""")
seg(sid, 5, """And never compact the active segment, because it is being appended to. Immutability of """
            """sealed segments is what makes compaction safe to run concurrently with reads without any """
            """locking at all &mdash; readers are reading files that nobody can change.""")

tradeoff('Hash index vs sorted structure (LSM)', [
 ('Hash index over an append-only log', 'ok',
  ['<b>Exactly one disk seek per read</b>', 'Trivially simple to reason about',
   'Writes are pure sequential appends'],
  ['<b>All keys must fit in memory</b>', 'No range scans at all',
   'Restart needs an index rebuild (mitigated by hint files)']),
 ('LSM tree (sorted memtable + SSTables)', 'info',
  ['Keys need not fit in memory', 'Range scans work', 'Still sequential writes'],
  ['A read may touch several levels &mdash; <b>more seeks</b>, needs bloom filters',
   'Much more machinery: levels, merges, bloom filters',
   'Compaction is far more complex']),
 ('B-tree (update in place)', 'shared',
  ['Range scans', 'No compaction needed', 'Mature and well understood'],
  ['<b>Random writes</b> &mdash; and the question only gave us append',
   'Write amplification at page granularity', 'Needs a WAL for crash safety anyway']),
], 'The hash index over an append-only log &mdash; it is what the stated primitives describe, and it '
   'gives exactly one seek per read.',
 'If keys stopped fitting in memory, or range scans were required, I would move to an LSM tree. Both '
 'are plausible next requirements, and both break this design in the same place: the in-memory index.',
 [
 """Trade-off: hash index over a log, versus a sorted structure. The hash index gives exactly one disk """
 """seek per read, is trivially simple to reason about, and writes are pure sequential appends. The """
 """cost is that all keys must fit in memory, there are no range scans at all, and restart needs an """
 """index rebuild &mdash; which hint files mitigate.""",
 """An L-S-M tree removes the memory constraint and gives you range scans, and still writes """
 """sequentially. The cost is that a read may touch several levels, so more seeks, which is why L-S-M """
 """trees need bloom filters to avoid pointless disk reads. And there is a great deal more machinery: """
 """levels, merge policies, bloom filters, far more complex compaction.""",
 """A B-tree gives range scans and needs no compaction, and it requires random writes in place &mdash; """
 """which the question did not give us. We were given append, read-at-offset and create, and that is """
 """it. So the primitives rule it out, and pointing that out is better than arguing about """
 """performance.""",
 """I would take the hash index over the append-only log, because it is precisely what the stated """
 """primitives describe and it gives the one-seek guarantee.""",
 """What would flip it: keys no longer fitting in memory, or range scans being required. Both are """
 """plausible next requirements, and notice they break the design in the same place &mdash; the """
 """in-memory index. Knowing the single point where your design fails is more useful than knowing ten """
 """things it does well.""",
])

failures('What happens when each piece dies', [
 ('Process crashes mid-append', 'Last write lost, never acknowledged',
  'CRC per record; recovery scans to the first bad checksum and truncates. <b>Consistent, just behind</b>'),
 ('Power loss with batched fsync', 'Up to one batch interval of writes lost',
  '<b>A deliberate, stated trade</b> for 100&times; throughput. If unacceptable, fsync per write and '
  'accept ~1,000 writes/s'),
 ('Disk full', 'Writes fail; compaction cannot run either',
  '<b>The nastiest failure</b> &mdash; compaction needs free space to write the merged segment before '
  'deleting the old. Reserve headroom and alert well before full'),
 ('Compaction crashes halfway', 'Nothing &mdash; old segments still intact',
  'Write to a temp file and <b>rename atomically</b>. Never delete a source segment until the merged '
  'one is fsynced and swapped'),
 ('Bit rot in a sealed segment', 'One key returns corrupt data',
  'The per-record CRC catches it on read. Return an error rather than bad bytes &mdash; '
  '<b>silent corruption is worse than a visible failure</b>'),
 ('Index and disk disagree after a bug', 'Reads return wrong or missing values',
  'The log is the source of truth; the index is derived. <b>Rebuild the index from the log</b> &mdash; '
  'that recoverability is the main benefit of keeping the log authoritative'),
], [
 """Failures. Process crashes mid-append: the last write is lost and was never acknowledged. C-R-C per """
 """record, recovery scans to the first bad checksum and truncates. The store is consistent, just """
 """slightly behind, which is the correct outcome.""",
 """Power loss with batched fsync loses up to one batch interval. That is a deliberate, stated trade """
 """for a hundred times the throughput. If it is unacceptable, fsync per write and accept a thousand """
 """writes a second &mdash; and let the interviewer choose, because it is their requirement, not """
 """yours.""",
 """Disk full is the nastiest failure here and it is worth volunteering. Writes fail, which is expected. """
 """But compaction cannot run either, because compaction needs free space to write the merged segment """
 """before it can delete the originals. So the one mechanism that would free space requires space. """
 """Reserve headroom and alert long before full.""",
 """Compaction crashing halfway does nothing, because the old segments are still intact. Write to a """
 """temp file, fsync, rename atomically, and only then delete the sources. Never delete a source until """
 """the merged segment is durable and swapped.""",
 """Bit rot in a sealed segment makes one key return corrupt data. The per-record C-R-C catches it on """
 """read, and you return an error rather than the bad bytes. Silent corruption is far worse than a """
 """visible failure, because it propagates into everything downstream before anyone notices.""",
 """And if the index and disk ever disagree after a bug, the log is the source of truth and the index """
 """is derived, so you rebuild the index from the log. That recoverability is the main benefit of """
 """keeping the log authoritative, and it is the same inversion as the quota counters in lesson four """
 """point two.""",
])

say('What I should actually say in the room', [
 'Let me read the constraints back, because I think they describe a specific design. Append only, read '
 'at an offset, keys in memory, values on disk &mdash; that is a hash index over an append-only log. '
 'Bitcask, essentially.',
 'The index maps key to file, offset and length. 10 million keys is about 240 MB of index, so it fits '
 'comfortably &mdash; and around a billion keys is where this design stops working.',
 'One active segment, appended to; sealed segments are immutable. A read is one index lookup plus '
 'exactly one disk seek, always one, which gives predictable tail latency.',
 'Write ordering matters: append and fsync first, then update the index. The other order leaves the '
 'index pointing at bytes that do not exist.',
 'Every record carries a CRC, so recovery scans to the first bad checksum and truncates. Segments are '
 'size-capped specifically so recovery time is bounded.',
 'Updates leave dead records behind, so compaction rewrites live records only. I would trigger it on '
 'dead-byte ratio rather than a timer, and throttle it &mdash; a compaction storm starving live traffic '
 'of I/O is the classic incident with these stores.',
 'And I would reserve disk headroom, because compaction needs free space to run, so a full disk takes '
 'away the very mechanism that would free space.',
], [
 """The sentences. Open by reading the constraints back and naming the design they describe. That takes """
 """twenty seconds and immediately establishes that you understood the question rather than """
 """pattern-matching it to &ldquo;design a database&rdquo;.""",
 """Then the index arithmetic including where it breaks, the one-seek guarantee, and the write """
 """ordering with its failure. Then C-R-Cs and the recovery bound.""",
 """Then compaction with the trigger and the throttle, and finish on the disk-full interaction, which """
 """is the detail that sounds like operational experience rather than theory.""",
])

followups([
 'How is the in-memory index structured?',
 'What is the file layout?',
 'How do you find a value from an offset?',
 'How does compaction work?',
 'How do you recover from a crash?',
 'How do checksums fit in?',
 'How do you handle concurrency?',
 'What about write amplification?',
], [
 'Now the keys do not fit in memory. What do you build instead?',
 'Add range scans. What changes?',
 'How would you replicate this across three machines?',
 'How do you support transactions across two keys?',
 'What does this cost in SSD endurance, and does that change your compaction policy?',
],
 """The reported follow-ups are the full syllabus of this design and we have covered all of them. On """
 """concurrency specifically: a single writer appending, with many readers reading immutable sealed """
 """segments, needs almost no locking &mdash; the only shared mutable structure is the in-memory index, """
 """which wants a concurrent map or a read-write lock, and that is the whole concurrency story.""",
 """The staff-level follow-ups all push on the same weak point. Keys not fitting in memory means an """
 """L-S-M tree. Range scans means the same. Replication means shipping the log itself, which is lovely, """
 """because an append-only log is already a replication stream &mdash; that is exactly what Kafka is. """
 """Transactions across two keys need a write-ahead batch with a commit record, so recovery either """
 """sees the whole batch or none of it. And S-S-D endurance is a genuinely good question: write """
 """amplification burns write cycles, so on consumer drives you compact less aggressively and accept """
 """more wasted space, which is a cost decision rather than a performance one.""")

cheatsheet('Disk KV store &mdash; the one-page card', [
 ('Requirements', 'get/put over append-only files; keys in memory, values on disk; survive crashes'),
 ('Scale', '10M keys &rarr; 240 MB index; 100 GB of values; ~100 &micro;s reads; 1k&ndash;100k writes/s '
           'depending on fsync policy'),
 ('Core architecture', 'In-memory hash: key &rarr; (file, offset, len). One active segment appended to; '
                       'sealed segments immutable; background compactor'),
 ('Data store', 'The append-only log <b>is</b> the store. The index is derived and rebuildable'),
 ('Partition key', 'Single node by assumption. To scale out, hash the key across nodes &mdash; each '
                   'runs this design independently'),
 ('Cache', 'OS page cache does the work. <b>Do not build your own</b> unless you can prove it beats it'),
 ('Queue', 'None. The log is the queue, which is why this structure also underlies Kafka'),
 ('Consistency', 'Single writer &rarr; linearizable per key. Durability set by the fsync policy'),
 ('Failure handling', 'CRC per record; scan-and-truncate on recovery; hint files for fast restart; '
                      'atomic rename for compaction'),
 ('Key deep dives', 'Write ordering and recovery &middot; compaction and write amplification'),
 ('Biggest trade-off', 'Simplicity and one-seek reads, bought with <b>an in-memory index and write '
                       'amplification</b>'),
], [
 """The card. Requirements and scale &mdash; and the two numbers to remember are two hundred and forty """
 """megabytes of index for ten million keys, and around a hundred microseconds per read.""",
 """Architecture in one line. Note the data store row: the log is the store and the index is derived """
 """and rebuildable, which is the sentence that makes recovery tractable. And the cache row &mdash; the """
 """O-S page cache does the work, and building your own is a thing to justify, not to assume.""",
 """Consistency is linearizable per key given a single writer. Failure handling is C-R-Cs and atomic """
 """renames. And the biggest trade-off: simplicity and one-seek reads, paid for with an in-memory index """
 """and write amplification. Both of those costs are where the follow-ups will come from.""",
])

say('The 60-second answer', [
 'The constraints describe the design, so let me read them back: append only, read at an offset, keys '
 'fit in memory, values do not. That is a hash index over an append-only log &mdash; Bitcask.',
 'The in-memory index maps each key to a file, an offset and a length. Ten million keys is about 240 MB, '
 'which fits easily; around a billion is where this approach stops working and I would move to an LSM '
 'tree.',
 'Writes append to a single active segment and nothing is ever overwritten, so the disk only ever does '
 'sequential I/O. A read is one index lookup plus exactly one seek &mdash; always one, which gives very '
 'predictable tail latency.',
 'Ordering matters: append and fsync, then update the index. The reverse leaves the index pointing at '
 'bytes that do not exist after a crash.',
 'Every record carries a CRC, so recovery scans to the first bad checksum and truncates; segments are '
 'size-capped precisely so that recovery time is bounded.',
 'Updates leave dead records behind, so a background compactor rewrites only live records. I trigger it '
 'on dead-byte ratio rather than a timer, throttle it so it cannot starve live reads, and keep disk '
 'headroom &mdash; because compaction needs free space to reclaim free space.',
], [
 """The sixty-second answer. The opening move &mdash; reading the constraints back and naming the """
 """design they imply &mdash; is the strongest thing you can do on this question, and it takes fifteen """
 """seconds.""",
 """Say it once out loud. The last clause is the one worth landing cleanly: compaction needs free space """
 """to reclaim free space. It is memorable, it is true, and it is the kind of detail that only comes """
 """from having thought about running the thing.""",
], kicker='60-second interview answer')
