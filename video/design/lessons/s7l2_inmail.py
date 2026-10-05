# -*- coding: utf-8 -*-
"""Chapter 7, Lesson 2 — LinkedIn InMail."""
from lib import *

lesson_header('7.2', 'Design LinkedIn InMail',
              'Conversation model &middot; per-recipient state &middot; unread counts &middot; abuse',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 16,
              """Chapter seven, lesson two: LinkedIn InMail. A messaging system &mdash; and the """
              """temptation is to treat it as a feed with two people in it. It is not. The read-write """
              """ratio inverts, the data model has a trap in it that most candidates walk into, and """
              """there is a product constraint here that does not exist in ordinary messaging: InMail """
              """is paid, rationed, and sent to strangers. That last fact drives more of the design """
              """than the messaging does.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Named: message creation, <b>conversation/thread, inbox, delivery, read/unread, search, '
  'notifications, spam/abuse, ordering, storage, partitioning, fanout</b>'),
 ('Related &mdash; lesson 7.1 and 7.3', '2026', 'Staff',
  'Shares fanout vocabulary with the feed and delivery with notifications &mdash; but the '
  '<b>guarantees are different</b>'),
], """Single source, so medium confidence. The named topics look like the feed question &mdash; fanout, """
     """ordering, partitioning &mdash; which is exactly the trap.""",
 ["""Because a feed can drop an item and nobody notices, and a message cannot. The vocabulary overlaps """
  """and the guarantees do not, and spotting that early is most of what separates a good answer """
  """here."""],
 caveat='Single source. The conversation model and per-recipient state are universal to any messaging '
        'system, so this transfers.',
 narration_caveat="""Single source for this framing. The conversation model and per-recipient state are """
                  """universal to any messaging system, so the preparation transfers.""")

sid = beat('Why this is interesting', 'A feed may lose a post. A message may not.',
           '<div style="font-size:28px;line-height:1.72">'
           'The feed in 7.1 could drop an item, deliver late, or show a slightly different list on '
           'refresh. <span style="color:#a8e6a3">Nobody notices.</span><br><br>'
           '<span style="color:#ff9a9a">Messaging has none of that slack.</span> A lost message is a '
           'lost business opportunity. A message shown twice looks broken. An unread badge that is '
           'wrong is the most-reported bug in every messaging product ever built.<br><br>'
           '<b>Three things make it genuinely different:</b><br>'
           '&bull; <b>Read/write ratio inverts.</b> A feed is ~1000:1 reads. An inbox is roughly '
           '<b>1:1</b> &mdash; most messages are read about once. <span style="color:#ffd483">So '
           'precomputing buys you much less.</span><br>'
           '&bull; <b>State is per recipient.</b> The message is shared; read/unread, archived and '
           'deleted are not.<br>'
           '&bull; <b>InMail is sent to strangers, and it is paid.</b> That makes abuse control and '
           'quota <i>part of the product</i>, not an afterthought.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the same words &mdash; fanout, ordering, '
           'partitioning &mdash; mean different things once loss is unacceptable. Say which guarantees '
           'you are buying before you draw anything.</span></div>',
           """Why is this interesting? Because the feed in the last lesson could drop an item, deliver """
           """late, or show a slightly different list when you refresh, and nobody notices.""", step=0)
seg(sid, 1, """Messaging has none of that slack. A lost message is a lost business opportunity. A message """
            """shown twice looks broken. And an unread badge that is wrong is, genuinely, the """
            """most-reported bug in every messaging product ever built &mdash; worth remembering, """
            """because it tells you where to spend your design effort.""")
seg(sid, 2, """Three things make it different. First, the read-write ratio inverts. A feed is about a """
            """thousand to one reads. An inbox is roughly one to one &mdash; most messages are read """
            """about once and then never again. So precomputation, which was the whole answer in the """
            """feed lesson, buys you much less here.""")
seg(sid, 3, """Second, state is per recipient. The message body is shared between sender and receiver, """
            """but read, unread, archived and deleted are not. That split is the data model trap and we """
            """will spend a deep dive on it.""")
seg(sid, 4, """And third &mdash; the one specific to InMail rather than messaging in general &mdash; """
            """InMail is sent to strangers and it is paid for. That makes abuse control and quota part """
            """of the product rather than an afterthought. If you design this as WhatsApp you will have """
            """designed the wrong thing.""")
seg(sid, 5, """So the staff-level insight: the same words &mdash; fanout, ordering, partitioning &mdash; """
            """mean different things once loss is unacceptable. Say which guarantees you are buying """
            """before you draw a single box.""")

think('Two people are in a conversation. One of them archives it and marks it read; the other has not '
      'opened it. Where does "read" live &mdash; on the message, on the conversation, or somewhere else? '
      'And what breaks if you put it in the obvious place?',
      25,
      """Pause. Two people are in a conversation. One archives it and marks it read; the other has not """
      """opened it yet. Where does &ldquo;read&rdquo; actually live &mdash; on the message, on the """
      """conversation, or somewhere else? And what breaks if you put it in the obvious place? Say it """
      """out loud.""",
      """Hold that. Putting per-recipient state on a shared object is the single most common data model """
      """error in messaging, and it is not obvious until it is.""")

clarify('What I would clarify first', [
 ('One-to-one only, or group conversations?',
  '<b>Groups change the data model fundamentally.</b> Two participants can be two rows; N participants '
  'needs a membership table and fanout per message.'),
 ('Does InMail have a quota, and is it enforced per sender?',
  'Almost certainly yes &mdash; it is a paid product. That makes this <b>lesson 4.2 embedded inside a '
  'messaging system</b>, and I would reuse that design rather than invent one.'),
 ('Can recipients block, report, or decline?',
  'Sending to strangers means abuse is <b>certain</b>, not hypothetical. The response pipeline is part '
  'of the system, not a later feature.'),
 ('Is delivery required to be ordered, and within what scope?',
  'Per-conversation ordering is required and achievable. <b>Global ordering is neither.</b>'),
 ('How long is history kept, and is search over all of it?',
  'Search over years of messages is a separate index and roughly doubles the storage story.'),
 ('Must the recipient see it in real time, or is a notification enough?',
  'Real-time means a persistent connection tier. A notification means you can be far simpler &mdash; '
  'and most InMail is <b>not</b> read in the moment.'),
], [
 """One-to-one only, or groups? This changes the data model fundamentally. Two participants can be two """
 """rows. N participants needs a membership table and fanout per message, and suddenly you are building """
 """something much larger.""",
 """Does InMail have a quota, enforced per sender? Almost certainly yes, because it is a paid product. """
 """Which means this is lesson four point two &mdash; the A-P-I quota system &mdash; embedded inside a """
 """messaging system, and I would say explicitly that I would reuse that design rather than inventing a """
 """second counter.""",
 """Can recipients block, report or decline? Sending to strangers means abuse is certain rather than """
 """hypothetical. So the reporting and response pipeline is part of this system, not a feature for next """
 """quarter.""",
 """Is delivery ordered, and within what scope? Per-conversation ordering is both required and """
 """achievable. Global ordering across all conversations is neither, and I would say so.""",
 """How long is history kept, and does search cover all of it? Search over years of messages is a """
 """separate index and roughly doubles the storage story, so it is worth pricing separately.""",
 """And must the recipient see it in real time, or is a notification sufficient? Real time means a """
 """persistent connection tier for a hundred million people. A notification means you can be far """
 """simpler &mdash; and the honest observation is that most InMail is not read in the moment anyway.""",
])

capacity('Capacity', [
 ('~50M messages / day sent', '50M &divide; 86,400', '&asymp; 580 messages / s',
  'Peak ~2,300/s. <b>Small</b> &mdash; messaging is not a throughput problem'),
 ('Each message touches 2 inboxes', '580 &times; 2', '&asymp; 1,200 inbox writes / s',
  'Fanout is 2, not 1,000. <b>The feed&rsquo;s central problem does not exist here</b>'),
 ('Message size ~1 KB with metadata', '50M &times; 1 KB', '&asymp; 50 GB / day',
  '~18 TB/year. Trivial compared with photos or logs'),
 ('Inbox reads: 100M DAU &times; 5 opens', '500M reads / day', '&asymp; 5,800 reads / s',
  '<b>Read:write is ~10:1</b>, not 1000:1. Precompute buys far less than in a feed'),
 ('Unread count queries', 'every app open, every screen', '&asymp; 20,000 / s',
  '<b>The hottest query in the system.</b> It must never be a COUNT(*) over messages'),
 ('Search index over 18 TB/year', '&asymp; 1.5&times; raw for a field index', '&asymp; 27 TB',
  'Index selectively. <b>Full-text over all history is the expensive option</b>'),
], [
 """Numbers. Around fifty million messages a day is five hundred and eighty a second, maybe two thousand """
 """three hundred at peak. That is small &mdash; and saying so matters, because it stops you designing """
 """for a throughput problem you do not have.""",
 """Each message touches two inboxes, so about twelve hundred inbox writes a second. Fanout is two, not """
 """a thousand. The feed's central problem simply does not exist here, and I would point that out """
 """rather than importing machinery I do not need.""",
 """Message size around a kilobyte with metadata gives fifty gigabytes a day, about eighteen terabytes """
 """a year. Trivial next to photos or logs.""",
 """Inbox reads: a hundred million daily actives opening five times is five hundred million reads, """
 """about five thousand eight hundred a second. So read-to-write is roughly ten to one, not a thousand """
 """to one. Precomputation buys far less here, which is the arithmetic behind that earlier claim.""",
 """And here is the number that actually matters. Unread count queries happen on every app open and """
 """every screen &mdash; call it twenty thousand a second. That is the hottest query in the entire """
 """system, and it must never be a count over the messages table. Finding the hottest query and """
 """designing for it specifically is the move here.""",
 """Search over eighteen terabytes a year at roughly one and a half times for a field index is about """
 """twenty-seven terabytes. Index selectively; full text over all history is the expensive option.""",
])

A = Arch('InMail &mdash; shared message, per-recipient state', kicker='Architecture', height=800)

A.box('snd',   60, 180, 150, 90, 'Sender', '', kind='neutral', step=0, focus=0, small=True)
A.box('api',  250, 170, 195, 110, 'Message API', 'quota check first', kind='ok', step=0, focus=[0, 1])
A.arrow('snd', 'api', step=0, focus=0)

A.box('quota', 250, 350, 195, 100, 'InMail quota', 'reuse lesson 4.2', kind='info', step=1, focus=1, small=True)
A.arrow('api', 'quota', step=1, focus=1, dashed=True)

A.box('abuse', 250, 500, 195, 100, 'Abuse checks', 'rate, reputation', kind='shared', step=1, focus=1, small=True)
A.arrow('api', 'abuse', step=1, focus=1, dashed=True)

A.box('msg',  540, 170, 220, 115, 'Messages', 'immutable bodies<br>by conversation', kind='ok', step=2,
      focus=[2, 4])
A.arrow('api', 'msg', step=2, label='write once', focus=2)

A.box('conv', 540, 340, 220, 105, 'Conversations', 'participants, last msg', kind='dp', step=2, focus=2, small=True)
A.arrow('api', 'conv', step=2, focus=2, dashed=True)

A.box('state', 540, 500, 220, 115, 'Per-recipient state', 'read, archived,<br>unread count', kind='info',
      step=3, focus=[3, 5])
A.arrow('api', 'state', step=3, label='2 rows', focus=3)

A.box('rd',   860, 340, 200, 105, 'Inbox read', 'conv list + state', kind='ok', step=4, focus=4, small=True)
A.arrow('conv', 'rd', step=4, focus=4)
A.arrow('state', 'rd', step=4, focus=4, dashed=True)
A.arrow('msg', 'rd', step=4, focus=4, dashed=True)

A.box('cnt',  860, 500, 200, 105, 'Unread counter', '20k/s &mdash; hottest', kind='shared', step=5, focus=5, small=True)
A.arrow('state', 'cnt', step=5, focus=5)

A.box('notif', 860, 170, 200, 105, 'Notifications', 'see 7.3', kind='neutral', step=6, focus=6, small=True)
A.arrow('msg', 'notif', step=6, focus=6, dashed=True)

A.box('srch', 1130, 340, 200, 105, 'Search index', 'per recipient', kind='neutral', step=6, focus=6, small=True)
A.arrow('msg', 'srch', step=6, focus=6, dashed=True)

A.note(1130, 500, 'Unread is a maintained counter, never a COUNT over messages. It is the hottest read in the system.',
       step=5, kind='info', w=440)

A.narrate(0, """A sender hits the message A-P-I. And the first thing that happens is not storage &mdash; """
             """it is permission.""",
          A.flow([(210, 222), (250, 222)]))
A.narrate(1, """Quota check, because InMail is rationed and paid for, and abuse checks, because this is """
             """being sent to a stranger. I would reuse the quota design from lesson four point two """
             """wholesale rather than inventing a second counter &mdash; and saying that out loud is """
             """better than silently rebuilding it.""",
          A.flow([(345, 280), (345, 350)]))
A.narrate(2, """Then storage, and notice it is three separate things. Messages are immutable bodies, """
             """stored by conversation. Conversations hold participants and a pointer to the last """
             """message. Those two are shared between both people.""",
          A.flow([(445, 225), (540, 227)]))
A.narrate(3, """And per-recipient state is separate: read, archived, deleted, unread count. Two rows per """
             """message, one for each participant. This is the split that the whole data model turns """
             """on, and it is the next deep dive.""",
          A.flow([(445, 280), (540, 557)]))
A.narrate(4, """An inbox read fetches the conversation list, joins the per-recipient state, and pulls """
             """message bodies for whichever conversation is opened. Three lookups, all by the same """
             """partition key.""",
          A.flow([(760, 392), (860, 392)]))
A.narrate(5, """The unread counter is maintained incrementally &mdash; incremented on receive, """
             """decremented on read &mdash; never computed by counting messages. At twenty thousand """
             """queries a second, a count over a table would dominate the entire system's load.""",
          A.flow([(760, 557), (860, 552)]))
A.narrate(6, """And two things hang off the message store: notifications, which is the next lesson, and a """
             """per-recipient search index. Both are asynchronous, because neither should be able to """
             """delay a message being delivered.""")
A.build()

sid = beat('Deep dive 1', 'Where read/unread lives &mdash; and the obvious wrong answer',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The obvious answer:</b> put <code>read: true</code> on the message row. '
           '<span style="color:#ff9a9a">Wrong, and it fails immediately.</span> A message has two '
           'participants with different states &mdash; the sender has effectively read it, the '
           'recipient has not. One boolean cannot hold both.<br><br>'
           '<b>The fix: a per-(recipient, message) row.</b><br>'
           '<code>(userId, conversationId, messageId) &rarr; read, archived, deleted</code><br><br>'
           '&bull; <b>Deletion is per recipient too.</b> If I delete a conversation, you still have it. '
           '<span style="color:#a8e6a3">A &ldquo;deleted&rdquo; message is still stored &mdash; only '
           '<i>my</i> view of it is gone.</span><br>'
           '&bull; This is also why <b>GDPR deletion is hard</b>: erasing my data must not erase your '
           'copy of a conversation we both had.<br><br>'
           '<b>The unread count: never a COUNT(*).</b> Maintain it:<br>'
           '&bull; +1 when a message is written to a recipient &bull; &minus;1 when marked read<br>'
           '&bull; Single row per user, incremented atomically &mdash; <b>at 20k reads/s it has to be '
           'O(1)</b><br>'
           '&bull; <span style="color:#ffd483">Drift is inevitable (retries, bugs). Recompute it '
           'nightly from the state table and reconcile.</span></div>',
           """Deep dive one: where read and unread actually live, and this is the question I asked you """
           """to pause on. The obvious answer is to put a read flag on the message row.""", step=0)
seg(sid, 1, """That is wrong and it fails immediately. A message has two participants with different """
            """states &mdash; the sender has effectively read it, the recipient has not. One boolean """
            """cannot hold two people's state, and as soon as you add group conversations it cannot """
            """hold N.""")
seg(sid, 2, """The fix is a row per recipient per message: user, conversation, message, pointing at """
            """read, archived and deleted. State belongs to the pair, not to the object.""")
seg(sid, 3, """And notice deletion falls out of the same insight. If I delete a conversation, you still """
            """have it &mdash; so a deleted message is still stored, and only my view of it is gone. """
            """That is also precisely why G-D-P-R deletion is genuinely hard in messaging: erasing my """
            """data must not erase your copy of a conversation we both participated in. Raising that """
            """unprompted is a strong signal.""")
seg(sid, 4, """Then the unread count, which is the hottest query in the system. Never a count over """
            """messages. Maintain it: plus one when a message is written to a recipient, minus one when """
            """it is marked read, as a single row per user incremented atomically. At twenty thousand """
            """reads a second it has to be constant time.""")
seg(sid, 5, """And here is the part that comes from having operated one of these. The counter will """
            """drift. Retries double-increment, bugs decrement twice, a crash loses an update. So """
            """recompute it nightly from the state table and reconcile. Every messaging product does """
            """this, because the alternative is a badge that says three when the inbox is empty &mdash; """
            """which users report as a bug forever.""")

sid = beat('Deep dive 2', 'Abuse, because InMail goes to strangers',
           '<div style="font-size:27px;line-height:1.7">'
           'Ordinary messaging is between people who already know each other. <b>InMail is not.</b> '
           'That single fact makes abuse control a core subsystem rather than a feature.<br><br>'
           '<b>Three layers, in order of cost:</b><br>'
           '&bull; <b>Quota</b> &mdash; InMail is rationed and paid for, which is itself the first '
           'abuse control. <span style="color:#a8e6a3">Rate limiting someone who pays per message is '
           'the cheapest filter there is.</span><br>'
           '&bull; <b>Reputation</b> &mdash; a sender whose messages are reported or ignored gets '
           'throttled. Signals: report rate, reply rate, block rate, account age.<br>'
           '&bull; <b>Content</b> &mdash; classifiers on the message body. Expensive, so run it '
           '<i>asynchronously</i> and retract rather than blocking the send path.<br><br>'
           '<b>The response pipeline, which people forget to design:</b><br>'
           'report &rarr; the message is already delivered &rarr; so you need <b>retraction</b> '
           '(hide for the recipient), sender penalty, and a feedback loop into reputation.<br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: do not put an ML classifier on the '
           'synchronous send path. It adds latency, it fails, and it is the wrong place &mdash; '
           'deliver, then scan, then retract.</span></div>',
           """Deep dive two: abuse, which matters here because InMail goes to strangers. Ordinary """
           """messaging is between people who already know each other; InMail is not, and that single """
           """fact makes abuse control a core subsystem rather than a feature.""", step=0)
seg(sid, 1, """Three layers, in order of cost. First, quota. InMail is rationed and paid for, and that """
            """is itself the first abuse control &mdash; rate limiting someone who pays per message is """
            """the cheapest filter you will ever deploy. Worth saying that the business model is doing """
            """security work for you.""")
seg(sid, 2, """Second, reputation. A sender whose messages are repeatedly reported or ignored gets """
            """throttled. Useful signals are report rate, reply rate, block rate and account age. This """
            """is cheap because it uses data you already have.""")
seg(sid, 3, """Third, content classifiers on the message body. Expensive, so run them asynchronously and """
            """retract if needed, rather than blocking the send path.""")
seg(sid, 4, """And then the piece people forget to design at all: the response pipeline. A report arrives """
            """after the message is already delivered. So you need retraction &mdash; hiding it for the """
            """recipient &mdash; a penalty applied to the sender, and a feedback loop back into """
            """reputation so the next message from them is scored differently.""")
seg(sid, 5, """The staff-level point: do not put a machine learning classifier on the synchronous send """
            """path. It adds latency to every message, it fails occasionally, and it is simply the """
            """wrong place. Deliver, then scan, then retract. That ordering is the same instinct as """
            """lazy expiry in the cache lesson &mdash; do the expensive work where it does not block """
            """anybody.""")

tradeoff('How the inbox is stored', [
 ('One shared conversation, join state at read', 'info',
  ['Message stored once &mdash; no duplication', 'Easy to add participants later',
   'Edits and deletes are naturally consistent'],
  ['Every read is a join across two or three tables',
   '<b>Cross-shard if the two users live on different shards</b>',
   'Unread count needs its own maintained structure anyway']),
 ('Per-recipient inbox copy (fanout on write)', 'shared',
  ['Inbox read is a single-shard scan', 'Per-recipient state is naturally local',
   'Same shape as the feed in 7.1'],
  ['Message body duplicated per participant', 'Edits and deletes must touch every copy',
   '<b>Fanout is only 2 &mdash; so the benefit is small and the cost is real</b>']),
 ('Hybrid: shared bodies, per-recipient index rows', 'ok',
  ['Body stored once; <b>index row per recipient</b>', 'Inbox listing is a single-shard read',
   'Per-recipient state lives with the index row'],
  ['Two stores to keep consistent', 'Opening a conversation fetches bodies separately']),
], 'Shared immutable message bodies, plus a per-recipient index row carrying state. Partition '
   '<b>everything by userId</b>, so one person&rsquo;s entire inbox lives on one shard.',
 'If group conversations became large &mdash; hundreds of participants &mdash; the per-recipient index '
 'row stops being cheap, and I would move back toward a shared conversation with state joined at read '
 'time.',
 [
 """Trade-off: how the inbox is stored. One shared conversation with state joined at read means the """
 """message is stored once, it is easy to add participants, and edits and deletes are naturally """
 """consistent. The cost is that every read is a join across two or three tables, and if the two users """
 """live on different shards that join crosses shards &mdash; which is the thing you most want to """
 """avoid on a hot read path.""",
 """A per-recipient inbox copy makes the inbox read a single-shard scan and keeps per-recipient state """
 """local. It duplicates the message body per participant, and edits and deletes must touch every copy. """
 """And the key observation: fanout here is only two, so the benefit of copying is small while the cost """
 """is real. That is the opposite of the feed, where fanout was a thousand.""",
 """The hybrid stores the body once and writes a per-recipient index row carrying the state. The inbox """
 """listing is a single-shard read, state lives with the index row, and opening a conversation fetches """
 """bodies separately.""",
 """That is what I would build, and the critical decision alongside it is to partition everything by """
 """user I-D, so one person's entire inbox &mdash; index rows, state, unread counter &mdash; lives on """
 """one shard. Every hot read becomes single-shard.""",
 """What would flip it: if group conversations became large, hundreds of participants, the """
 """per-recipient index row stops being cheap and I would move back toward a shared conversation with """
 """state joined at read time. The right answer depends on the fanout, and the fanout depends on the """
 """product.""",
])

failures('What happens when each piece dies', [
 ('Message written, recipient index row fails', '<b>A message nobody can find</b>',
  'Write the message, then index rows, with the index write <b>retried from a durable queue</b>. The '
  'message store is truth; index rows are rebuildable from it'),
 ('Unread counter drifts', 'Badge says 3, inbox is empty &mdash; the classic bug',
  '<b>Recompute nightly</b> from the per-recipient state table and reconcile. Drift is inevitable; '
  'design the repair, not just the increment'),
 ('Duplicate delivery on retry', 'The same message appears twice',
  'Idempotency key per <code>(sender, clientMessageId)</code>. <b>The client generates it</b>, so a '
  'retry is recognisably the same message'),
 ('Notification sent, message write fails', 'A notification for a message that does not exist',
  'Notify <b>after</b> the message is durable, never before. Ordering of side effects matters more '
  'than it looks'),
 ('Abuse classifier is down', 'Unscreened messages delivered',
  '<b>Fail open and queue for rescanning.</b> Blocking all InMail because a classifier is down is a '
  'worse outcome than a delay in screening'),
 ('One user receives 10,000 messages in an hour', 'Their shard is hot; inbox read slows',
  'Per-sender quota already limits this. Also cap per-recipient write rate and <b>spill to a '
  'secondary partition</b> if a single inbox goes pathological'),
], [
 """Failures. Message written but the recipient index row fails, and you have a message nobody can """
 """find. Write the message first, then the index rows, with the index write retried from a durable """
 """queue. The message store is truth and index rows are rebuildable from it &mdash; the same """
 """derived-data principle as the feed.""",
 """Unread counter drifts and the badge says three when the inbox is empty. Recompute nightly from the """
 """state table and reconcile. The point worth making is that drift is inevitable, so you design the """
 """repair, not just the increment. Any maintained aggregate needs a reconciliation path.""",
 """Duplicate delivery on retry shows the same message twice. Idempotency key on sender plus a """
 """client-generated message I-D &mdash; and it has to be client-generated, so that a retry is """
 """recognisably the same message rather than a new one. That is the same lesson as the ad billing """
 """impression I-D.""",
 """Notification sent but the message write failed gives a notification for a message that does not """
 """exist. Notify after the message is durable, never before. The ordering of side effects matters more """
 """than people expect.""",
 """Abuse classifier down: fail open and queue for rescanning. Blocking all InMail because a classifier """
 """is unavailable is a worse outcome than a delay in screening, and that is a judgement call worth """
 """stating rather than assuming.""",
 """And one user receiving ten thousand messages in an hour makes their shard hot. Per-sender quota """
 """already limits this, which is the quota earning its keep twice. Beyond that, cap the per-recipient """
 """write rate and spill to a secondary partition if a single inbox goes pathological.""",
])

say('What I should actually say in the room', [
 'The first thing I want to establish is that this is not a feed. A feed can drop an item and nobody '
 'notices; a message cannot, and an unread badge that is wrong is the most-reported bug in every '
 'messaging product.',
 'The numbers are small &mdash; about 580 messages a second and fanout of two &mdash; so the feed&rsquo;s '
 'central problem does not exist here. I would say that rather than importing machinery I do not need.',
 'The hottest query is the unread count, at roughly 20,000 a second. That must be a maintained counter, '
 'never a COUNT over messages &mdash; and it will drift, so I recompute it nightly and reconcile.',
 'The data model split is the key decision: message bodies are shared and immutable; read, archived and '
 'deleted are per recipient. One boolean on the message cannot represent two people&rsquo;s state.',
 'That also explains why deletion is per recipient &mdash; if I delete a conversation you still have it '
 '&mdash; and why GDPR erasure is genuinely hard here.',
 'I partition everything by userId so one person&rsquo;s whole inbox is on one shard, which makes every '
 'hot read single-shard.',
 'And because InMail goes to strangers and is paid for, quota and abuse are part of the product. I '
 'would reuse the quota design from the API quota question, and run content classifiers '
 'asynchronously &mdash; deliver, then scan, then retract &mdash; rather than putting a model on the '
 'send path.',
], [
 """The sentences. Open by distinguishing this from the feed, because the interviewer has just heard """
 """you answer a fanout question and will be listening for whether you apply it blindly.""",
 """Then the arithmetic that says the feed's problem is absent, then the hottest query, then the data """
 """model split with its deletion consequence.""",
 """Then the partition key, and finish on abuse &mdash; naming that you would reuse an earlier design """
 """rather than reinvent it, which is both correct and a signal in itself.""",
])

followups([
 'How do you model conversations and threads?',
 'How is the inbox stored and read?',
 'How does delivery work?',
 'How do you track read/unread?',
 'How do you search messages?',
 'How do notifications fit in?',
 'How do you handle spam and abuse?',
 'How do you guarantee ordering?',
 'How do you partition and fan out?',
], [
 'Now make it group conversations with 500 participants. What breaks?',
 'A user requests deletion of all their data. What exactly can you delete?',
 'How do you support message editing and unsend?',
 'How do you keep two devices in sync for the same user?',
 'How would you detect a coordinated spam campaign rather than one bad sender?',
],
 """The reported follow-ups are the whole lesson. On ordering specifically: per-conversation ordering """
 """by a sequence number assigned at write time, not by client timestamp &mdash; client clocks are """
 """wrong and two devices will disagree. Partition by user I-D for inbox reads, and the conversation """
 """itself can be keyed by a deterministic hash of the participant I-Ds so both sides compute the same """
 """key.""",
 """The staff-level follow-ups are where it gets interesting. Five hundred participants breaks the """
 """per-recipient index row, pushing you back to shared state. Data deletion is genuinely hard because """
 """you cannot erase the other participant's copy, so the honest answer is to erase your identity and """
 """your side of the state and tombstone your messages. Editing and unsend mean message bodies are no """
 """longer immutable, which undoes an assumption the whole design rests on &mdash; the usual fix is """
 """versioned bodies with the latest pointer. Multi-device sync is a per-device read cursor rather than """
 """a per-user one. And detecting a coordinated campaign rather than one bad sender is a graph problem """
 """&mdash; clustering on message similarity and recipient overlap &mdash; which is a different system """
 """and worth saying so.""")

cheatsheet('InMail &mdash; the one-page card', [
 ('Requirements', 'Send, thread, deliver, read/unread, search, notify, resist abuse &mdash; with '
                  '<b>no loss and no duplicates</b>'),
 ('Scale', '~580 msg/s, fanout of 2, ~50 GB/day, ~5,800 inbox reads/s, <b>~20,000 unread-count '
           'queries/s</b>'),
 ('Core architecture', 'API (quota + abuse) &rarr; immutable message store + conversation row + '
                       'per-recipient index rows &rarr; inbox read joins them'),
 ('Data store', 'Messages immutable and shared; <b>state per (recipient, message)</b>; unread as a '
                'maintained counter'),
 ('Partition key', '<code>userId</code> &mdash; one person&rsquo;s entire inbox on one shard, so every '
                   'hot read is single-shard'),
 ('Cache', 'Unread counts and the recent conversation list. Message bodies barely benefit &mdash; '
           'read:write is only ~10:1'),
 ('Queue', 'Index writes, notifications, search indexing, async abuse scanning &mdash; all off the '
           'send path'),
 ('Consistency', 'Per-conversation ordering by server-assigned sequence. <b>Idempotent on a '
                 'client-generated message ID</b>'),
 ('Failure handling', 'Message store is truth, index rows rebuildable; nightly unread reconciliation; '
                      'abuse classifier fails open'),
 ('Key deep dives', 'Per-recipient state and the unread counter &middot; abuse as a core subsystem'),
 ('Biggest trade-off', 'Shared bodies vs per-recipient copies &mdash; and with a fanout of 2, '
                       '<b>copying buys almost nothing</b>'),
], [
 """The card. Requirements end with the guarantees, because that is what separates this from a feed. """
 """Scale &mdash; and the bolded number is the one to remember, twenty thousand unread-count queries a """
 """second.""",
 """Architecture in one line. Data store row carries the central insight: messages shared, state per """
 """recipient-message pair. Partition by user I-D so every hot read is single-shard.""",
 """Cache barely helps on bodies because read-to-write is only ten to one. Consistency is """
 """per-conversation ordering with client-generated idempotency keys. And the biggest trade-off: shared """
 """bodies versus per-recipient copies, where a fanout of two means copying buys almost nothing.""",
])

say('The 60-second answer', [
 'The first thing I want to say is that this is not a feed. A feed can drop an item and nobody notices; '
 'a message cannot, and a wrong unread badge is the most-reported bug in every messaging product.',
 'The volumes are modest &mdash; around 580 messages a second with a fanout of two &mdash; so the '
 'celebrity-fanout problem simply does not exist here, and I would not import that machinery.',
 'The hottest query by far is the unread count at roughly 20,000 a second, so that is a maintained '
 'counter incremented on receive and decremented on read &mdash; never a COUNT over messages. It will '
 'drift, so I recompute and reconcile nightly.',
 'The data model turns on one split: message bodies are shared and immutable, while read, archived and '
 'deleted are per recipient. A single flag on the message cannot represent two people, which is also '
 'why deletion is per recipient and why GDPR erasure is hard here.',
 'I partition everything by userId so one member&rsquo;s whole inbox &mdash; index rows, state and '
 'counter &mdash; sits on one shard and every hot read is single-shard.',
 'And because InMail is paid and goes to strangers, quota and abuse are part of the product: I reuse '
 'the quota design from the API quota question, and I run content classifiers asynchronously &mdash; '
 'deliver, scan, then retract &mdash; rather than putting a model on the send path.',
], [
 """The sixty-second answer. The opening line does a lot of work: it distinguishes this from the """
 """question you were probably just asked, and it names the guarantee rather than the """
 """components.""",
 """The fourth sentence is the technical heart &mdash; the shared-body, per-recipient-state split """
 """&mdash; and the GDPR observation at the end of it is the kind of detail that makes an interviewer """
 """think you have shipped one of these. Practise those two until they are fluent.""",
], kicker='60-second interview answer')
