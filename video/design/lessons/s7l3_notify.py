# -*- coding: utf-8 -*-
"""Chapter 7, Lesson 3 — the notification system."""
from lib import *

lesson_header('7.3', 'Design the notification system',
              'Channel fanout &middot; preferences &middot; dedup &middot; provider failure',
              dict(reports='InterviewTV list only', latest='2026', level='Staff',
                   conf='MEDIUM &mdash; single source', sources='InterviewTV.io'), 16,
              """Chapter seven, lesson three: notifications across push, email and in-app. This is the """
              """question where the hardest problem is not technical. Delivering a message is easy. """
              """Deciding whether to send it at all &mdash; given preferences, dedup, batching, """
              """priority and the fact that annoying someone makes them turn you off forever &mdash; is """
              """the real system. The restraint logic is bigger than the delivery logic, and candidates """
              """almost always build only the delivery half.""")

evidence('Where this question comes from', [
 ('InterviewTV.io &mdash; supplied list', '2026', 'Staff',
  'Named: <b>fanout, preferences, deduplication, prioritisation, delivery guarantees, retry, rate '
  'limiting, provider failures, offline users, batching</b>'),
], """Single source, so medium confidence. But read the list of named topics: fanout and delivery """
     """guarantees are there, and so are preferences, deduplication, prioritisation, rate limiting and """
     """batching.""",
 ["""Six of those ten are about <i>not</i> sending something. That is the question telling you where """
  """the difficulty is, and it is unusual &mdash; most design questions are about doing more, and this """
  """one is largely about doing less."""],
 caveat='Single source. The fanout-plus-preferences shape is universal to any notification system, so '
        'it transfers.',
 narration_caveat="""Single source. The fanout-plus-preferences shape is universal to any notification """
                  """system, so the preparation transfers regardless.""")

sid = beat('Why this is interesting', 'Delivery is easy. <b>Restraint</b> is the system.',
           '<div style="font-size:28px;line-height:1.72">'
           'Sending a push notification is an HTTP call to APNs or FCM. '
           '<span style="color:#a8e6a3">That part is a library call.</span><br><br>'
           'The actual system is everything that happens <i>before</i> it:<br><br>'
           '&bull; Does this member want this, on this channel? (<b>preferences</b>)<br>'
           '&bull; Have we already told them? (<b>dedup</b>)<br>'
           '&bull; Should these twelve events be <i>one</i> notification? (<b>batching</b>)<br>'
           '&bull; Have we sent them too many today? (<b>rate limiting</b>)<br>'
           '&bull; Is this worth interrupting them for? (<b>prioritisation</b>)<br><br>'
           '<span style="color:#ff9a9a">The cost of over-notifying is not a bad user experience. It is '
           'permanent: the user turns notifications off, and you never reach them again.</span><br><br>'
           '<span style="color:#ffd483">STAFF-LEVEL INSIGHT: the irreversibility is what makes this '
           'different. A dropped notification costs one impression. An annoying one costs every future '
           'impression &mdash; so the system should be biased toward sending <i>less</i>.</span></div>',
           """Why is this interesting? Because sending a push notification is an H-T-T-P call to A-P-N-s """
           """or F-C-M. That part is a library call. The actual system is everything that happens """
           """before it.""", step=0)
seg(sid, 1, """Does this member want this, on this channel &mdash; preferences. Have we already told them """
            """&mdash; deduplication. Should these twelve events be one notification &mdash; batching. """
            """Have we sent them too many today &mdash; rate limiting. And is this even worth """
            """interrupting them for &mdash; prioritisation.""")
seg(sid, 2, """And here is the thing that makes this question different from every other delivery """
            """problem. The cost of over-notifying is not a bad experience that you can fix next """
            """sprint. It is permanent. The user turns notifications off in their O-S settings, and you """
            """never reach them again. There is no recovery path.""")
seg(sid, 3, """So the staff-level insight is about irreversibility. A dropped notification costs you one """
            """impression. An annoying notification costs you every future impression. Those are not """
            """symmetric, which means the system should be deliberately biased toward sending less """
            """&mdash; and saying that explicitly, early, reframes the whole design.""")

think('A member is tagged in a post. Twelve people then comment on that post over the next four minutes. '
      'How many notifications should they receive &mdash; and what does your system need to remember in '
      'order to get that right?',
      25,
      """Pause. A member is tagged in a post, and then twelve people comment on it over the next four """
      """minutes. How many notifications should they get? And what does your system need to remember in """
      """order to get that right? Say it out loud.""",
      """Hold that. The answer is almost certainly two, not thirteen &mdash; and what it needs to """
      """remember is the key to the whole design.""")

clarify('What I would clarify first', [
 ('Which channels, and who chooses &mdash; us or the member?',
  'Push, email and in-app have <b>completely different latency and cost profiles</b>. In-app is free '
  'and instant; email is cheap and slow; push is the one you can lose forever.'),
 ('Is any notification <i>transactional</i> &mdash; security alerts, password resets?',
  '<b>The most important question.</b> Transactional notifications bypass preferences, batching and '
  'rate limits. Mixing them with marketing in one pipeline is a serious design error.'),
 ('What latency does each type need?',
  'A security alert is seconds. &ldquo;Someone viewed your profile&rdquo; can wait hours and is '
  '<i>better</i> batched. <b>One pipeline, several urgency classes.</b>'),
 ('Delivery guarantee &mdash; at-least-once or at-most-once?',
  'At-least-once means duplicates, which for notifications are very visible. <b>At-most-once means '
  'silently losing a security alert.</b> Usually: at-least-once plus dedup.'),
 ('Do we need read receipts / in-app state?',
  'An in-app notification centre is a <b>stored inbox</b>, which is lesson 7.2 again &mdash; '
  'per-recipient state and an unread count.'),
 ('What is the volume, and is there a daily cap per member?',
  'If there is no cap, there should be. <b>Ask who owns that number</b>, because every product team '
  'will want an exception.'),
], [
 """Which channels, and who chooses &mdash; us or the member? Push, email and in-app have completely """
 """different latency and cost profiles. In-app is free and instant. Email is cheap and slow. Push is """
 """the one you can lose permission for forever, so it deserves the most restraint.""",
 """Is any notification transactional &mdash; security alerts, password resets? This is the most """
 """important question on this slide. Transactional notifications must bypass preferences, batching and """
 """rate limits, and mixing them with marketing in a single undifferentiated pipeline is a serious """
 """design error that gets people locked out of their accounts.""",
 """What latency does each type need? A security alert is seconds. &ldquo;Someone viewed your """
 """profile&rdquo; can wait hours and is genuinely better batched. So: one pipeline, several urgency """
 """classes.""",
 """Delivery guarantee &mdash; at-least-once or at-most-once? At-least-once means duplicates, which for """
 """notifications are highly visible and annoying. At-most-once means occasionally losing a security """
 """alert, which is worse. The usual answer is at-least-once plus deduplication, and you should say """
 """that rather than picking one.""",
 """Do we need an in-app notification centre with read state? If so that is a stored inbox, which is """
 """lesson seven point two again &mdash; per-recipient state and an unread count, same machinery.""",
 """And what is the volume, with a daily cap per member? If there is no cap there should be. And I """
 """would ask who owns that number, because every product team will want an exception to it and """
 """somebody has to be allowed to say no.""",
])

capacity('Capacity', [
 ('~500M notification events / day', '500M &divide; 86,400', '&asymp; 5,800 events / s',
  'Peak ~25,000/s. <b>Events, not sends</b> &mdash; the difference is the whole point'),
 ('After preferences + dedup + batching', 'typically 70&ndash;90% suppressed',
  '&asymp; 50&ndash;150M actual sends / day', '<b>The filter is the system.</b> Most events never '
  'become notifications'),
 ('Fanout: 1 event &rarr; up to 3 channels', '100M sends &times; ~1.5 channels', '&asymp; 150M deliveries / day',
  '&asymp; 1,700 / s. Modest &mdash; <b>provider rate limits bind before our capacity does</b>'),
 ('Preference lookups', 'one per event, before anything else', '&asymp; 25,000 / s peak',
  '<b>The hottest read.</b> Must be cached; a DB lookup per event would dominate everything'),
 ('Dedup window: 24 h of keys', '500M &times; ~40 B', '&asymp; 20 GB',
  'Fits in Redis with a TTL. <b>Dedup is cheap &mdash; there is no excuse for duplicates</b>'),
 ('Email cost at &pound;0.0001 each', '50M emails / day', '&asymp; &pound;5,000 / day',
  '<b>Suppression saves real money</b>, not just goodwill'),
], [
 """Numbers. About five hundred million notification events a day is roughly five thousand eight """
 """hundred a second, maybe twenty-five thousand at peak. And note the word events &mdash; not sends. """
 """That distinction is the whole point of this system.""",
 """After preferences, deduplication and batching, typically seventy to ninety percent are suppressed, """
 """leaving fifty to a hundred and fifty million actual sends. So most events never become """
 """notifications at all. The filter is the system, and that number is the one I would put on the """
 """board first.""",
 """Fanout across up to three channels gives maybe a hundred and fifty million deliveries a day, about """
 """seventeen hundred a second. Modest &mdash; and the useful observation is that provider rate limits """
 """will bind before our own capacity does, so the constraint is external.""",
 """Preference lookups happen once per event, before anything else, so twenty-five thousand a second at """
 """peak. That is the hottest read in the system and it must be cached &mdash; a database lookup per """
 """event would dominate everything else you do.""",
 """A twenty-four hour dedup window at five hundred million keys times forty bytes is about twenty """
 """gigabytes, which fits in Redis with a T-T-L. Deduplication is cheap, which means there is no excuse """
 """for duplicates, and I would say that plainly.""",
 """And email at a hundredth of a penny each, at fifty million a day, is around five thousand pounds a """
 """day. So suppression saves real money, not just goodwill &mdash; which is a useful argument when a """
 """product team wants an exemption from the cap.""",
])

A = Arch('Notifications &mdash; a filter pipeline with a delivery tail', kicker='Architecture', height=800)

A.box('src',   60, 320, 155, 95, 'Event sources', 'likes, messages,<br>jobs, security', kind='neutral',
      step=0, focus=0, small=True)
A.box('ing',  250, 310, 185, 110, 'Ingest', 'normalise', kind='ok', step=0, focus=0)
A.arrow('src', 'ing', step=0, focus=0)

A.zone(500, 130, 560, 520, 'THE FILTER — where most events die')

A.box('pri',  540, 180, 200, 95, 'Classify', 'transactional?', kind='info', step=1, focus=1, small=True)
A.arrow('ing', 'pri', step=1, focus=1)

A.box('pref', 540, 310, 200, 95, 'Preferences', 'cached, 25k/s', kind='ok', step=2, focus=2, small=True)
A.arrow('pri', 'pref', step=2, focus=2)

A.box('dedup',540, 440, 200, 95, 'Dedup', '24 h keys', kind='ok', step=3, focus=3, small=True)
A.arrow('pref', 'dedup', step=3, focus=3)

A.box('batch',820, 310, 200, 95, 'Batcher', 'collapse + delay', kind='shared', step=4, focus=4, small=True)
A.arrow('dedup', 'batch', step=4, focus=4)

A.box('cap',  820, 440, 200, 95, 'Per-user cap', 'daily budget', kind='shared', step=4, focus=4, small=True)
A.arrow('batch', 'cap', step=4, focus=4)

A.box('q',   1110, 310, 190, 105, 'Send queue', 'per channel', kind='info', step=5, focus=5)
A.arrow('cap', 'q', step=5, focus=5)
A.arrow('pri', 'q', step=5, label='transactional bypass', focus=5, dashed=True)

A.box('push',1370, 180, 190, 95, 'APNs / FCM', '', kind='dp', step=6, focus=6, small=True)
A.box('mail',1370, 310, 190, 95, 'Email provider', '', kind='dp', step=6, focus=6, small=True)
A.box('app', 1370, 440, 190, 95, 'In-app store', 'read state', kind='dp', step=6, focus=6, small=True)
A.arrow('q', 'push', step=6, focus=6)
A.arrow('q', 'mail', step=6, focus=6)
A.arrow('q', 'app', step=6, focus=6)

A.note(500, 690, '70–90% of events are suppressed here. The filter is the system; delivery is a library call.',
       step=4, kind='info', w=560)

A.narrate(0, """Event sources &mdash; likes, messages, job matches, security alerts &mdash; land in an """
             """ingest service that normalises them into one shape. Worth doing, because otherwise """
             """every product team invents its own notification format and the filter has to """
             """understand all of them.""",
          A.flow([(215, 367), (250, 365)]))
A.narrate(1, """First, classify. Is this transactional &mdash; a security alert, a password reset &mdash; """
             """or is it engagement? That single branch decides whether the rest of the filter applies """
             """at all, which is why it comes first.""",
          A.flow([(435, 340), (540, 227)]))
A.narrate(2, """Preferences. Does this member want this type, on this channel? Cached, because at """
             """twenty-five thousand lookups a second a database read here would dominate the system.""",
          A.flow([(640, 275), (640, 310)]))
A.narrate(3, """Deduplication against a twenty-four hour window of keys. Have we already told them this? """
             """Twenty gigabytes in Redis with a T-T-L.""",
          A.flow([(640, 405), (640, 440)]))
A.narrate(4, """Then batching, which collapses twelve comments into one notification and may deliberately """
             """delay delivery to let more events arrive. And a per-user daily cap, which is the last """
             """line of defence against a product team shipping something enthusiastic. Between them, """
             """seventy to ninety percent of events die in this zone &mdash; which is the system """
             """working, not failing.""",
          A.flow([(740, 357), (820, 357), (820, 440)]))
A.narrate(5, """What survives goes to per-channel send queues. And note the dashed line: transactional """
             """notifications bypass the entire filter and go straight to the queue. A security alert """
             """must not be rate limited, batched or suppressed by a preference.""",
          A.flow([(1020, 487), (1110, 362)]))
A.narrate(6, """Then the actual delivery &mdash; A-P-N-s, F-C-M, an email provider, and the in-app store """
             """which keeps read state. Three channels, three failure modes, and the in-app one is """
             """really the inbox from the previous lesson.""",
          A.flow([(1300, 362), (1370, 227)]))
A.build()

sid = beat('Deep dive 1', 'Dedup and batching &mdash; turning thirteen events into two',
           '<div style="font-size:27px;line-height:1.7">'
           '<b>The scenario:</b> tagged in a post, then 12 comments in 4 minutes. Naive: 13 '
           'notifications. <span style="color:#ff9a9a">That is how you lose a user permanently.</span>'
           '<br><br>'
           '<b>Deduplication</b> &mdash; the same notification, twice:<br>'
           'Key on <code>(userId, type, objectId)</code> with a TTL. A retry, a duplicate event, or '
           'two services both reacting to the same thing all collapse to one send.<br><br>'
           '<b>Batching</b> &mdash; <i>different</i> notifications that should be one:<br>'
           '&bull; Key on <code>(userId, type, objectId)</code> again, but now <b>accumulate</b> rather '
           'than suppress<br>'
           '&bull; Hold a short window &mdash; 2&ndash;5 minutes for engagement events<br>'
           '&bull; Collapse into one message: <i>&ldquo;12 people commented on your post&rdquo;</i><br>'
           '&bull; <span style="color:#a8e6a3">The window is the trade: longer window, fewer and better '
           'notifications, but staler.</span><br><br>'
           '<b>The subtlety:</b> batching requires <b>deliberately delaying</b> delivery. You are '
           'choosing to be slower in order to be less annoying.<br><br>'
           '<span style="color:#ffd483">Which is why transactional notifications must never enter this '
           'path &mdash; delaying a security alert by five minutes to batch it is indefensible.</span>'
           '</div>',
           """Deep dive one: deduplication and batching, which answers what I asked you to pause on. """
           """Tagged in a post, then twelve comments in four minutes. The naive system sends thirteen """
           """notifications, and that is how you lose a user permanently.""", step=0)
seg(sid, 1, """Deduplication handles the same notification arriving twice. Key on user, type and object """
            """I-D with a T-T-L. A retry, a duplicate event, or two different services both reacting to """
            """the same thing all collapse to a single send.""")
seg(sid, 2, """Batching is different &mdash; it handles genuinely distinct notifications that ought to be """
            """one. Same key, but now you accumulate rather than suppress. Hold a short window, two to """
            """five minutes for engagement events, and collapse them into one message: twelve people """
            """commented on your post.""")
seg(sid, 3, """And the window is the trade. A longer window means fewer and better notifications, and """
            """staler ones. That is a product decision, and the right move is to make it a """
            """configurable per type rather than a constant in the code.""")
seg(sid, 4, """Here is the subtlety that makes batching architecturally interesting: it requires """
            """deliberately delaying delivery. You are choosing to be slower in order to be less """
            """annoying. Almost every other system in this course is trying to be faster; this one """
            """buys quality with latency on purpose.""")
seg(sid, 5, """Which is exactly why transactional notifications must never enter this path. Delaying a """
            """security alert by five minutes so it can be batched with something else is indefensible, """
            """and it is the kind of thing that happens when one pipeline is used for everything """
            """without a bypass.""")

sid = beat('Deep dive 2', 'Provider failure, and the retry that must not duplicate',
           '<div style="font-size:27px;line-height:1.7">'
           'You depend on <b>third parties you do not control</b> &mdash; APNs, FCM, an email provider. '
           'They will be slow, rate-limit you, and occasionally be down.<br><br>'
           '<b>Per-channel isolation.</b> Separate queues and separate worker pools per channel. '
           '<span style="color:#a8e6a3">Email being down must not block push.</span> This is the '
           'bulkhead pattern, and the cost of skipping it is one provider taking out all notifications.'
           '<br><br>'
           '<b>Retry, carefully:</b><br>'
           '&bull; Exponential backoff <b>with jitter</b> &mdash; without jitter, every worker retries '
           'in lockstep and you re-create the outage<br>'
           '&bull; <b>Circuit breaker</b> per provider: stop hammering something that is down<br>'
           '&bull; Distinguish <b>retryable</b> (5xx, timeout, 429) from <b>permanent</b> (invalid '
           'token, unsubscribed) &mdash; retrying a dead token forever is a common and expensive bug'
           '<br><br>'
           '<b>The duplicate problem:</b> you sent it, the response timed out. Did it arrive?<br>'
           '&bull; Most providers accept a <b>client-supplied idempotency / collapse key</b> &mdash; '
           'use it<br>'
           '&bull; Otherwise record <code>(userId, notificationId)</code> as sent <i>before</i> the '
           'call, and accept that a crash mid-call may lose one<br>'
           '&bull; <span style="color:#ffd483">For notifications, losing one is better than sending it '
           'twice &mdash; which is the opposite of the choice you make for messages.</span></div>',
           """Deep dive two: provider failure. You depend on third parties you do not control &mdash; """
           """A-P-N-s, F-C-M, an email provider. They will be slow, they will rate limit you, and """
           """occasionally they will be down.""", step=0)
seg(sid, 1, """So: per-channel isolation. Separate queues and separate worker pools for each channel, so """
            """email being down cannot block push. That is the bulkhead pattern, and the cost of """
            """skipping it is that one provider's outage takes out every notification you send.""")
seg(sid, 2, """Retry carefully. Exponential backoff with jitter &mdash; and the jitter matters, because """
            """without it every worker retries in lockstep and you recreate the thundering herd that """
            """caused the problem.""")
seg(sid, 3, """A circuit breaker per provider, so you stop hammering something that is already down. And """
            """distinguish retryable failures &mdash; five-hundreds, timeouts, four-two-nines &mdash; """
            """from permanent ones like an invalid device token or an unsubscribed address. Retrying a """
            """dead token forever is a common bug and it costs real money at email provider """
            """rates.""")
seg(sid, 4, """Then the duplicate problem. You sent it, and the response timed out. Did it arrive? Most """
            """providers accept a client-supplied idempotency or collapse key &mdash; use it, because """
            """it is free and it solves the problem properly.""")
seg(sid, 5, """Otherwise record the notification as sent before you make the call, and accept that a """
            """crash mid-call may lose one. And here is the judgement worth stating: for notifications, """
            """losing one is better than sending it twice. That is the opposite of the choice you make """
            """for messages in the previous lesson, and the reason is the asymmetry we opened with """
            """&mdash; a duplicate notification costs you permission, a missing one costs you an """
            """impression.""")

tradeoff('How much to suppress', [
 ('Send everything; let preferences do the work', 'info',
  ['Simple &mdash; no batching or capping logic', 'No notification is ever delayed',
   'Members control it themselves'],
  ['<b>Users turn notifications off entirely</b> &mdash; irreversible',
   'Email costs scale with every event', 'A single enthusiastic product team can ruin the channel']),
 ('Aggressive suppression and batching', 'shared',
  ['High signal per notification', 'Low cost', 'Protects the channel long-term'],
  ['Important things can be delayed or dropped', 'Hard to debug &ldquo;why did I not get this?&rdquo;',
   'Product teams fight the cap constantly']),
 ('Tiered: transactional bypass, engagement filtered', 'ok',
  ['Security and account events are never delayed', 'Engagement noise is aggressively collapsed',
   '<b>One pipeline, explicit classes</b>'],
  ['Someone must classify every notification type', 'The classification will be gamed &mdash; every '
   'team wants &ldquo;transactional&rdquo;']),
], 'Tiered, with a hard bypass for transactional and aggressive batching and capping for engagement.',
 'If engagement were the <b>only</b> type &mdash; a pure marketing system &mdash; I would drop the '
 'bypass entirely and batch everything, because then nothing is urgent and the only risk is annoyance.',
 [
 """Trade-off: how much to suppress. Sending everything and letting preferences do the work is simple, """
 """nothing is ever delayed, and members control it themselves. The cost is that users turn """
 """notifications off entirely, which is irreversible, and email costs scale with every event. And one """
 """enthusiastic product team can ruin the channel for everyone.""",
 """Aggressive suppression and batching gives high signal per notification, low cost, and protects the """
 """channel long term. The cost is that important things can be delayed or dropped, it is genuinely """
 """hard to debug why someone did not receive something, and product teams will fight the cap """
 """constantly.""",
 """Tiered is the answer: a hard bypass for transactional, aggressive filtering for engagement. One """
 """pipeline with explicit classes.""",
 """And I want to name the real cost of that choice honestly, because it is organisational rather than """
 """technical: somebody must classify every notification type, and the classification will be gamed. """
 """Every team will want their notification to be transactional. So the classification needs an owner """
 """and a review, or within a year everything is transactional and you have no filter at all.""",
 """What would flip it: if engagement were the only type &mdash; a pure marketing system &mdash; I """
 """would drop the bypass entirely and batch everything, because then nothing is urgent and the only """
 """risk is annoyance.""",
])

failures('What happens when each piece dies', [
 ('Push provider (APNs/FCM) is down', 'No push; email and in-app unaffected',
  '<b>Per-channel queues and circuit breakers.</b> Queue push and drain on recovery &mdash; but '
  '<b>expire stale ones</b>: a 6-hour-old &ldquo;someone liked your post&rdquo; is noise'),
 ('Preference service is down', 'Cannot tell who wants what',
  '<b>Fail closed for engagement, open for transactional.</b> Sending to someone who opted out is '
  'worse than a delay &mdash; and may be a legal problem'),
 ('Dedup store is unavailable', 'Duplicates get through',
  '<b>Fail closed on dedup</b> for engagement &mdash; skip rather than risk a duplicate. For '
  'transactional, send anyway and accept the duplicate'),
 ('Batching worker crashes with events held', 'Batched notifications never sent',
  'Hold pending batches <b>durably</b>, not in memory. A crash loses nothing; it only delays the '
  'flush'),
 ('A bug sends 10M notifications in an hour', 'Mass unsubscribes &mdash; irreversible',
  '<b>Global kill switch</b> and a per-type circuit breaker on send volume. This is the incident that '
  'actually happens, and the one worth designing for explicitly'),
 ('Device token is invalid', 'Permanent failures retried forever',
  'Treat invalid-token as <b>permanent</b>: stop retrying and purge the token. Each retry costs money '
  'and provider reputation'),
], [
 """Failures. Push provider down: no push, while email and in-app continue. Per-channel queues and """
 """circuit breakers. Queue the push notifications and drain on recovery &mdash; but expire stale ones, """
 """because a six-hour-old &ldquo;someone liked your post&rdquo; is pure noise and sending it is worse """
 """than dropping it.""",
 """Preference service down means you cannot tell who wants what. Fail closed for engagement and open """
 """for transactional. Sending to someone who explicitly opted out is worse than a delay, and depending """
 """on jurisdiction it may be a legal problem rather than just a rude one.""",
 """Dedup store unavailable means duplicates get through. Fail closed on dedup for engagement &mdash; """
 """skip the send rather than risk a duplicate. For transactional, send anyway and accept the """
 """duplicate, because a repeated security alert is annoying and a missing one is dangerous.""",
 """Batching worker crashes with events held in memory and those notifications never go out. Hold """
 """pending batches durably rather than in memory, so a crash only delays the flush.""",
 """A bug sends ten million notifications in an hour, causing mass unsubscribes &mdash; irreversible. """
 """You need a global kill switch and a per-type circuit breaker on send volume. I would call this the """
 """incident that actually happens, and designing for it explicitly is worth more than any amount of """
 """throughput work.""",
 """And invalid device tokens retried forever. Treat invalid-token as permanent, stop retrying and """
 """purge the token, because each retry costs money and damages your sender reputation with the """
 """provider.""",
])

say('What I should actually say in the room', [
 'Delivering a notification is an HTTP call to a provider. The system is everything that decides '
 'whether to send it at all, so I am going to spend most of my time there.',
 'The reason is asymmetry: a dropped notification costs one impression, but an annoying one makes the '
 'user turn notifications off, and you never reach them again. So the design is biased toward sending '
 'less.',
 'About 500M events a day, and after preferences, dedup, batching and capping, maybe 10&ndash;30% '
 'actually get sent. The filter is the system.',
 'The first branch is transactional versus engagement. Security alerts bypass preferences, batching and '
 'rate limits entirely &mdash; mixing those in one undifferentiated pipeline is how people miss '
 'password resets.',
 'Preference lookups are the hottest read at ~25,000 a second, so they are cached. Dedup is a 24-hour '
 'key window in Redis &mdash; about 20 GB, so there is no excuse for duplicates.',
 'Batching is the interesting one, because it means deliberately delaying delivery to be less annoying. '
 'Twelve comments become one notification. That is a product decision I would make configurable per '
 'type.',
 'Per channel I would use separate queues, worker pools and circuit breakers, so email being down '
 'cannot block push. And I would build a global kill switch, because the incident that actually happens '
 'is a bug sending ten million notifications in an hour.',
], [
 """The sentences. Open by relocating the problem &mdash; the delivery is trivial, the decision is the """
 """system &mdash; and justify it with the asymmetry, which is the single most useful framing in this """
 """question.""",
 """Then the suppression ratio, the transactional branch, and the two hot structures with their """
 """numbers.""",
 """Then batching with its counter-intuitive property of being deliberately slower. And finish on """
 """isolation and the kill switch, which is the sentence that sounds like someone who has watched this """
 """go wrong.""",
])

followups([
 'How do you fan out across push, email and in-app?',
 'How do preferences work?',
 'How do you deduplicate?',
 'How do you prioritise?',
 'What delivery guarantees do you offer?',
 'How do you retry?',
 'How do you rate limit?',
 'What happens when a provider fails?',
 'What about offline users?',
 'How do you batch?',
], [
 'A product team wants to bypass the daily cap. What do you tell them, and what do you build?',
 'How do you measure whether notifications are <i>working</i> rather than just being sent?',
 'How would you run an experiment on notification frequency safely?',
 'A member says they got a notification they had opted out of. How do you investigate?',
 'How does this change for a regulated channel like SMS or marketing email?',
],
 """The reported follow-ups are the lesson, and offline users is one worth answering crisply: push """
 """providers queue for a limited time, so for a device that is off, you let the provider hold it """
 """briefly, expire anything stale, and rely on the in-app notification centre as the durable record. """
 """The in-app store is what guarantees nothing is permanently lost &mdash; push is best-effort by """
 """nature.""",
 """The staff-level follow-ups are mostly organisational, which is appropriate for this system. A """
 """product team wanting to bypass the cap is a governance question &mdash; you build a borrowing """
 """mechanism with an owner and an expiry rather than a permanent exemption. Measuring whether """
 """notifications work means tracking open rate, downstream action, and crucially the """
 """<i>unsubscribe</i> rate, because that is the cost. Experimenting on frequency safely means holding """
 """out a control group permanently so you can see long-term disengagement, not just this week's """
 """clicks. Investigating a wrongly-sent notification needs an audit log of every suppression decision, """
 """which is worth building up front. And regulated channels add consent records, time-of-day rules and """
 """mandatory unsubscribe handling &mdash; a different compliance surface on the same pipeline.""")

cheatsheet('Notifications &mdash; the one-page card', [
 ('Requirements', 'Push, email, in-app; respect preferences; dedup; batch; prioritise; survive '
                  'provider failure'),
 ('Scale', '~500M events/day (25k/s peak) &rarr; only 10&ndash;30% sent. 25k preference lookups/s; '
           '20 GB dedup window'),
 ('Core architecture', 'Ingest &rarr; classify &rarr; preferences &rarr; dedup &rarr; batch &rarr; cap '
                       '&rarr; per-channel queues &rarr; providers. <b>Transactional bypasses the '
                       'filter</b>'),
 ('Data store', 'Preferences (cached), dedup keys in Redis with TTL, durable pending batches, in-app '
                'notification store'),
 ('Partition key', '<code>userId</code> &mdash; preferences, dedup keys, batches and caps are all '
                   'per-member, so everything co-locates'),
 ('Cache', 'Preferences. It is the hottest read and a DB lookup per event would dominate the system'),
 ('Queue', 'One per channel, with its own workers and circuit breaker &mdash; <b>bulkheads</b>'),
 ('Consistency', 'At-least-once delivery plus dedup. <b>For notifications, losing one beats sending '
                 'it twice</b> &mdash; the opposite of messaging'),
 ('Failure handling', 'Fail closed on preferences and dedup for engagement, open for transactional; '
                      'expire stale queued notifications; <b>global kill switch</b>'),
 ('Key deep dives', 'Dedup vs batching &middot; provider failure and permanent-vs-retryable errors'),
 ('Biggest trade-off', 'Reach vs annoyance &mdash; and the asymmetry is permanent, so bias toward '
                       'sending <b>less</b>'),
], [
 """The card. Requirements, and scale &mdash; where the number to remember is that only ten to thirty """
 """percent of events become notifications.""",
 """Architecture in one line, with the transactional bypass called out because it is the branch that """
 """matters. Partition by user I-D, which co-locates preferences, dedup keys, batches and caps """
 """&mdash; one key for everything.""",
 """Consistency is the interesting row: at-least-once plus dedup, and losing one beats sending twice, """
 """which is explicitly the opposite of the messaging lesson. Failure handling has the kill switch. And """
 """the biggest trade-off is reach versus annoyance, where the asymmetry is permanent &mdash; so bias """
 """toward less.""",
])

say('The 60-second answer', [
 'Delivering a notification is an HTTP call to APNs or an email provider &mdash; that part is a library '
 'call. The system is everything that decides whether to send it at all, so that is where I would spend '
 'the design.',
 'The reason is an asymmetry: a dropped notification costs one impression, but an annoying one makes '
 'someone disable notifications permanently and you never reach them again. So the whole system is '
 'biased toward sending less.',
 'About 500 million events a day, and after preferences, deduplication, batching and a per-member daily '
 'cap, only 10 to 30 percent are actually sent. The filter is the system.',
 'The first branch is transactional versus engagement. Security alerts and password resets bypass '
 'preferences, batching and rate limits entirely &mdash; mixing those into one undifferentiated '
 'pipeline is how people miss account alerts.',
 'Preferences are the hottest read at around 25,000 a second so they are cached; dedup is a 24-hour key '
 'window in Redis, roughly 20 GB, so duplicates are inexcusable. Batching collapses twelve comments '
 'into one notification, which means deliberately delaying delivery to be less annoying.',
 'Per channel I run separate queues, workers and circuit breakers so email being down cannot block '
 'push, I treat invalid tokens as permanent rather than retrying forever, and I build a global kill '
 'switch &mdash; because the incident that actually happens is a bug sending ten million notifications '
 'in an hour.',
], [
 """The sixty-second answer. The first two sentences do the heavy lifting by relocating the problem and """
 """then justifying the relocation with the asymmetry.""",
 """The last clause is the one to land &mdash; naming the incident that actually happens, rather than """
 """the one that theoretically might. Practise it until it comes out as a statement of fact rather """
 """than a worry.""",
], kicker='60-second interview answer')
