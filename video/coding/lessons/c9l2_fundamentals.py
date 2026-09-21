# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 2 — OS and networking fundamentals."""
from lib import *

lesson_header('9.2', 'OS and networking fundamentals they actually ask', 'Systems fundamentals',
              'High', 'Taro Senior Infra report (Oct 2025)', '2025', 'High', 17,
              """Chapter nine, lesson two. A Senior Infrastructure candidate reported an October twenty twenty-five loop """
              """that included straight fundamentals — TCP versus UDP, paging, and similar — alongside the coding. This """
              """is not a coding lesson, and it is deliberately not a textbook chapter either. It is the eight answers I """
              """would want in your mouth, each in the form an interviewer actually wants: short, correct, with the """
              """trade-off named, and with one real consequence attached.""")

sid = beat('How to answer a fundamentals question', 'The shape matters more than the content',
           '<div style="font-size:31px;line-height:1.7">'
           'Every good answer to &ldquo;explain X&rdquo; has three parts, in this order:<br><br>'
           '<b>1. What it is</b>, in one sentence, no preamble.<br>'
           '<b>2. The trade-off</b> &mdash; what it buys and what it costs.<br>'
           '<b>3. One consequence you have actually seen</b> or would design around.<br><br>'
           'Thirty to sixty seconds. Then <b>stop</b>. A fundamentals question is a prompt for a conversation, and '
           'candidates who lecture for four minutes prevent the follow-up that would have shown depth.</div>',
           """Before the content, the shape — because on fundamentals the shape matters more than the facts. Every good """
           """answer to "explain X" has three parts in this order.""", step=0)
seg(sid, 1, """One: what it is, in one sentence, with no preamble. Two: the trade-off — what it buys and what it costs. """
            """Three: one consequence you have actually seen, or would design around.""")
seg(sid, 2, """Thirty to sixty seconds, and then stop. A fundamentals question is a prompt for a conversation, not a request """
            """for a lecture, and candidates who talk for four minutes prevent the follow-up question that would have """
            """shown their depth. Stopping is a skill.""")

sid = beat('1. TCP vs UDP', 'The one that was reported by name',
           '<div style="font-size:29px;line-height:1.65">'
           '<b>What:</b> TCP is a connection-oriented, ordered, reliable byte stream with flow and congestion control. '
           'UDP is unordered, unreliable datagrams with almost no machinery.<br><br>'
           '<b>The trade:</b> TCP buys reliability and pays in <b>latency</b> &mdash; a handshake before any data, and '
           '<b>head-of-line blocking</b>: one lost packet stalls everything behind it, even data that already arrived.'
           '<br><br>'
           '<b>Consequence:</b> that is why live video and game state prefer UDP &mdash; a stale frame retransmitted '
           '200 ms late is worse than a dropped one. And it is why <b>QUIC exists</b>: HTTP/3 runs reliable, ordered '
           'streams <i>on top of</i> UDP, so one lost packet stalls only its own stream.</div>',
           """One: TCP versus UDP, which was reported by name. What it is: TCP is a connection-oriented, ordered, reliable """
           """byte stream with flow control and congestion control. UDP is unordered, unreliable datagrams with almost no """
           """machinery around them.""", step=0)
seg(sid, 1, """The trade: TCP buys reliability and pays in latency. There is a handshake before any data flows, and there """
            """is head-of-line blocking — one lost packet stalls everything queued behind it, including data that has """
            """already physically arrived.""")
seg(sid, 2, """And the consequence, which is the part that shows you understand rather than recall. That head-of-line """
            """behaviour is why live video and game state prefer UDP: a frame retransmitted two hundred milliseconds late """
            """is worse than a frame that was simply dropped. It is also why QUIC exists — HTTP three runs reliable, """
            """ordered streams on top of UDP, so a lost packet stalls only its own stream rather than the whole """
            """connection. If you can land the QUIC sentence, you have answered a level above the question.""")

sid = cards('2&ndash;3. The two that follow it almost every time', [
 (0, 'The TCP handshake, and why it costs', 'SYN, SYN-ACK, ACK &mdash; one round trip before any data. With TLS on top, two or three more. On a 100 ms link that is 300 ms before a byte moves, which is why <b>connection reuse and keep-alive matter so much</b>.', 'info'),
 (0, 'What a socket actually is', 'A file descriptor plus a 4-tuple: source IP, source port, destination IP, destination port. That tuple is why one server port can hold a million connections &mdash; each is a different tuple.', 'info'),
 (1, 'TIME_WAIT', 'A closed connection lingers ~60 s so late packets cannot be mistaken for a new connection on the same tuple. It is why a busy client can exhaust ephemeral ports &mdash; a real production failure, not trivia.', 'shared'),
 (1, 'Nagle vs delayed ACK', 'Buffering small writes plus delayed acknowledgements can interact to add ~40 ms. <code>TCP_NODELAY</code> is the fix for latency-sensitive RPC.', 'shared'),
], cols=2)
seg(sid, 0, """Two and three, which follow almost every time. The handshake: SYN, SYN-ACK, ACK — one round trip before any """
            """data, and with TLS on top, two or three more. On a hundred-millisecond link that is three hundred """
            """milliseconds before a single byte moves, which is exactly why connection reuse and keep-alive matter so """
            """much in service-to-service traffic. And what a socket actually is: a file descriptor plus a four-tuple of """
            """source and destination addresses and ports. That tuple is the answer to "how can one port hold a million """
            """connections" — each connection is a different tuple.""")
seg(sid, 1, """Then two details that mark you as someone who has operated systems rather than only read about them. """
            """TIME_WAIT: a closed connection lingers for around a minute so that late packets cannot be mistaken for a new """
            """connection on the same tuple — and it is why a busy client can exhaust ephemeral ports, which is a real """
            """production failure. And the Nagle algorithm interacting with delayed acknowledgements to add about forty """
            """milliseconds to small writes, with TCP_NODELAY as the fix for latency-sensitive RPC.""")

sid = beat('4. Paging and virtual memory', 'The other one reported by name',
           '<div style="font-size:29px;line-height:1.65">'
           '<b>What:</b> every process sees its own virtual address space. The MMU translates virtual pages to physical '
           'frames via page tables, cached in the <b>TLB</b>. A reference to a page that is not resident raises a '
           '<b>page fault</b>, and the OS loads it.<br><br>'
           '<b>The trade:</b> you buy isolation, over-commit and simple allocation. You pay with a translation on every '
           'access (hidden by the TLB) and with <b>enormous variance</b> &mdash; a TLB hit is ~1 ns, a page fault to SSD '
           'is ~100 &micro;s. Five orders of magnitude, on the same instruction.<br><br>'
           '<b>Consequence:</b> this is why <b>thrashing</b> collapses a service rather than degrading it, and why a '
           'memory-mapped file feels like RAM until the working set stops fitting, at which point it does not.</div>',
           """Four: paging and virtual memory, the other topic reported by name. What it is: every process sees its own """
           """virtual address space; the memory management unit translates virtual pages into physical frames using page """
           """tables, cached in the translation lookaside buffer; and a reference to a page that is not resident raises a """
           """page fault, which the operating system services by loading it.""", step=0)
seg(sid, 1, """The trade: you buy isolation between processes, the ability to over-commit memory, and simple allocation. """
            """You pay with a translation on every single memory access, mostly hidden by the TLB, and with enormous """
            """variance — a TLB hit is about a nanosecond, and a page fault that reaches an SSD is about a hundred """
            """microseconds. Five orders of magnitude, for the same instruction, depending on state you cannot see.""")
seg(sid, 2, """And the consequence: that variance is why thrashing collapses a service rather than gracefully degrading it, """
            """and why a memory-mapped file feels exactly like memory right up until the working set stops fitting, at """
            """which point it very much does not. If you have ever watched a service fall off a cliff when its cache grew """
            """past available RAM, that is the story to tell here.""")

sid = cards('5&ndash;6. Processes, threads, and what a context switch costs', [
 (0, 'Process vs thread', 'Processes have separate address spaces; threads share one. Sharing is why threads are cheap to communicate between and dangerous to get wrong &mdash; which is exactly lesson 9.1.', 'info'),
 (0, 'Context switch cost', 'Direct cost ~1&ndash;5 &micro;s. The <b>real</b> cost is the cold cache and TLB afterwards, which can be far larger and does not show up in the switch count.', 'shared'),
 (1, 'Why async beats thread-per-request at scale', '10,000 threads means 10,000 stacks (~8 MB each by default) and a scheduler doing constant switching. An event loop keeps one stack per core and switches by returning to a loop.', 'ok'),
 (1, 'Blocking I/O vs epoll/kqueue', 'A blocking read parks the thread. Readiness notification lets one thread watch thousands of sockets. This is the whole reason C10K stopped being hard.', 'ok'),
], cols=2)
seg(sid, 0, """Five and six. Process versus thread: separate address spaces versus a shared one — and the sharing is exactly """
            """why threads are cheap to communicate between and dangerous to get wrong, which links straight back to the """
            """previous lesson. Context switch cost: the direct cost is a few microseconds, but the real cost is the cold """
            """cache and TLB afterwards, which can dominate and which does not appear in any switch counter.""")
seg(sid, 1, """Then the pair that matters for service design. Why async beats thread-per-request at scale: ten thousand """
            """threads means ten thousand stacks, eight megabytes each by default, and a scheduler switching constantly. """
            """An event loop keeps one stack per core and switches by returning to a loop. And the underlying mechanism """
            """is readiness notification — epoll or kqueue — which lets one thread watch thousands of sockets instead of """
            """parking a thread per connection. That is the entire reason handling ten thousand concurrent connections """
            """stopped being a research problem.""")

sid = beat('7. The latency numbers worth knowing', 'Approximate, current, and enough to reason with',
           '<div style="font-size:29px;line-height:1.7">'
           '<b>&bull;</b> L1 cache reference &mdash; ~1 ns<br>'
           '<b>&bull;</b> Main memory reference &mdash; ~100 ns<br>'
           '<b>&bull;</b> NVMe SSD random read &mdash; ~50&ndash;100 &micro;s<br>'
           '<b>&bull;</b> Same-datacentre round trip &mdash; ~0.5 ms<br>'
           '<b>&bull;</b> Cross-continent round trip &mdash; ~70&ndash;150 ms (bounded by the speed of light)<br>'
           '<b>&bull;</b> Disk seek on spinning rust &mdash; ~10 ms<br><br>'
           '<i>You do not need precision. You need the <b>ratios</b>: memory is ~100&times; cache, SSD is ~1000&times; '
           'memory, a cross-continent hop is ~1000&times; a local one. Ratios are what let you say &ldquo;that design '
           'spends 90% of its time waiting on the network&rdquo; without a benchmark.</i></div>',
           """Seven: the latency numbers. And the point of these is not precision, it is the ability to reason without a """
           """benchmark.""", step=0)
seg(sid, 1, """An L1 cache reference is about a nanosecond. Main memory is about a hundred nanoseconds. A random read from """
            """an NVMe SSD is fifty to a hundred microseconds. A round trip inside a datacentre is about half a """
            """millisecond. A cross-continent round trip is seventy to a hundred and fifty milliseconds, and that one is """
            """bounded by physics rather than by engineering. A seek on a spinning disk is about ten milliseconds.""")
seg(sid, 2, """What you actually need is the ratios: memory is roughly a hundred times cache, SSD is roughly a thousand """
            """times memory, and a cross-continent hop is roughly a thousand times a local one. Ratios are what let you """
            """say "that design spends ninety percent of its time waiting on the network" in the middle of a conversation, """
            """which is worth far more than remembering any single figure.""")

sid = cards('8. The questions behind the questions', [
 (0, '"Why is your service slow?"', 'A method, not a guess: is it CPU, memory, I/O or lock contention? Name how you would tell them apart &mdash; profiler, page-fault rate, iostat, lock wait time.', 'ok'),
 (0, '"What happens when I type a URL?"', 'They want to see how deep you go and whether you stop. DNS, TCP, TLS, HTTP, render. Hit the layer they care about and pause for direction.', 'ok'),
 (1, '"How much memory does this structure use?"', 'Object header, reference size, padding, and the load factor of a hash table. An honest estimate beats a confident wrong number.', 'shared'),
 (1, '"What breaks first at 10&times; traffic?"', 'The right answer names a <b>specific</b> resource &mdash; connection pool, file descriptors, GC pause, a single-writer shard &mdash; not "we would scale horizontally".', 'ok'),
], cols=2)
seg(sid, 0, """Eight: the questions behind the questions, which is where fundamentals usually actually get tested. Why is """
            """your service slow — the answer is a method, not a guess: is it CPU, memory, I/O or lock contention, and """
            """here is how I would tell them apart. What happens when you type a URL is a test of how deep you go and """
            """whether you know when to stop; name the layers, then pause and let them pick one.""")
seg(sid, 1, """How much memory does this structure use rewards an honest estimate with object headers, reference sizes, """
            """padding and hash-table load factor, rather than a confident wrong number. And what breaks first at ten """
            """times the traffic wants a specific resource named — the connection pool, file descriptors, a garbage """
            """collection pause, a single-writer shard. "We would scale horizontally" is the answer that gets you the """
            """level below the one you want.""")

followups(
 ['"Explain TCP vs UDP" — reported by name; one sentence each, then head-of-line blocking, then QUIC',
  '"Explain paging" — reported by name; translation, page fault, and the 1 ns vs 100 µs variance',
  '"What is a race condition?" — timing-dependent result; distinguish it from a data race (lesson 9.1)'],
 ['"Design the retry policy for that RPC" — exponential backoff with jitter, a deadline budget, and idempotency; retries without jitter synchronise and cause the outage they were meant to prevent',
  '"Why is P99 latency 10× P50?" — queueing, GC pauses, cold caches, and tail amplification when one request fans out to many services',
  '"How would you find a memory leak in production?" — heap growth over time, allocation profiler, and the question of whether it is a leak or simply a cache without a bound'],
 """The follow-ups here are mostly the questions themselves. TCP versus UDP and paging were reported by name, and the """
 """race-condition question connects directly to the previous lesson.""",
 """The staff-level versions are all operational. Designing a retry policy is a favourite, and the answer has three """
 """parts — exponential backoff with jitter, a deadline budget so retries cannot outlive the caller, and idempotency so """
 """a retry is safe — plus the observation that retries without jitter synchronise across clients and cause exactly the """
 """overload they were meant to survive. Why P99 is ten times P50 wants queueing, garbage collection pauses, cold caches """
 """and tail amplification from fan-out. And finding a memory leak wants a method plus one good question: is it a leak, """
 """or is it a cache that nobody bounded? In my experience it is usually the second, and saying so sounds like someone """
 """who has been paged.""")

interview_script([
 '"TCP is an ordered, reliable byte stream; UDP is unordered datagrams with no delivery guarantee."',
 '"The cost of TCP is latency: a handshake before any data, and head-of-line blocking when a packet is lost."',
 '"That is why real-time media prefers UDP, and why QUIC puts ordered streams on top of UDP so one loss stalls only one stream."',
 '"Paging gives isolation and over-commit, and costs you variance: a TLB hit is a nanosecond, a page fault to SSD is a hundred microseconds."',
 '"Which is why thrashing collapses a service instead of slowing it down gracefully."',
 '"I usually reason with ratios rather than absolutes — memory is ~100× cache, a cross-continent hop is ~1000× a local one."',
], [
 """The script, and notice how short each answer is. One sentence of what, one of trade, one of consequence, then """
 """stop.""",
 """The QUIC line and the thrashing line are the two that do the most work for you, because each shows that you """
 """understand the mechanism well enough to know what it caused in the real world.""",
 """And the last line is a good habit to state explicitly: reasoning in ratios rather than absolutes. It invites the """
 """interviewer to give you a scenario, which is exactly the conversation you want to be having in an infrastructure """
 """round.""",
])

sid = statement('Lesson 9.2', 'One sentence of what, one of trade-off, one of consequence. Then stop.',
                'Fundamentals questions are a prompt for a conversation. The candidate who lectures never gets the follow-up that would have shown depth.',
                kind='ok')
seg(sid, 0, """One line. One sentence of what it is, one of the trade-off, one of a consequence — and then stop.""")
seg(sid, 1, """Fundamentals questions are a prompt for a conversation, and the candidate who lectures for four minutes never """
            """gets the follow-up that would have shown their depth. Next is chapter ten: the rapid revision pass, and """
            """then a full fifty-minute mock run in real time.""")
