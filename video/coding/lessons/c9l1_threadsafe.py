# -*- coding: utf-8 -*-
"""Chapter 9, Lesson 1 — "Now make it thread-safe"."""
from lib import *

lesson_header('9.1', '"Now make it thread-safe" — the pivot that decides the round', 'Concurrency · locking strategy',
              'Highest', 'Glassdoor phone screen (Mar 2026) + repeated as a follow-up', '2026', 'High', 18,
              """Chapter nine, lesson one, and this is the most important lesson in the second half of the course. It is """
              """not a question — it is a pivot. A candidate reported a string-manipulation phone screen in March twenty """
              """twenty-six that turned into a concurrency discussion, and thread-safety shows up repeatedly as a follow-up """
              """on the data structure questions in chapter four. So the scenario to rehearse is this: you have just """
              """finished a correct solution, there are fifteen minutes left, and the interviewer says "now make it """
              """thread-safe". What you say in the next sixty seconds decides the round.""")

sid = beat('The scenario', 'What actually happens in the room',
           '<div class="qwrap"><div class="qtext" style="font-size:34px;line-height:1.4">'
           'You have just finished your LFU cache, or your All O`one, or your word-distance index.<br><br>'
           'The interviewer says: <i>&ldquo;Good. Now suppose this is called from many threads. Make it '
           'thread-safe.&rdquo;</i></div></div>',
           """The scenario. You have just finished your LFU cache, or your All O-one, or your word-distance index. The """
           """interviewer says: good, now suppose this is called from many threads — make it thread-safe.""")

sid = compare('The two ways candidates answer this',
 ('The reflex answer', 'deny', 0,
  ['&ldquo;I&rsquo;ll use a ConcurrentDictionary.&rdquo;',
   'Wrong, and confidently wrong &mdash; per-operation atomicity does not make a **multi-structure** update atomic',
   'Sprinkles `lock` inside methods without saying what the unit of atomicity is',
   'Never mentions what the lock is protecting']),
 ('The answer that gets the level', 'ok', 1,
  ['&ldquo;First: what is the <b>invariant</b> that must hold across the whole operation?&rdquo;',
   'Then: one lock, correct and simple &mdash; **state the throughput cost**',
   'Then: where the contention actually is, and what you would measure',
   'Then: striping or read-write locks, <b>with the risk named</b>']))
seg(sid, 0, """Here is how most candidates answer, and it is the trap. "I will use a concurrent dictionary." That is """
            """confidently wrong, and it is wrong in an interesting way: a concurrent dictionary makes each individual """
            """operation atomic, but your LFU cache updates a dictionary, a linked list and an integer together. """
            """Per-operation atomicity does not make a multi-structure update atomic. Sprinkling locks inside methods """
            """without saying what the unit of atomicity is has the same problem.""")
seg(sid, 1, """And here is the answer that gets the level. Start by asking what invariant must hold across the whole """
            """operation. Then give one lock — correct and simple — and state its throughput cost out loud. Then say where """
            """the contention actually is and what you would measure. And only then offer striping or a read-write lock, """
            """with the risk named. Notice the order: correctness, then cost, then measurement, then optimisation. That is """
            """the order a staff engineer uses in a design review.""")

sid = beat('Step 1', 'Name the invariant. It is always bigger than one line.',
           '<div style="font-size:30px;line-height:1.7">'
           'For the LFU cache, one <code>Get</code> does <b>four</b> things:<br>'
           '&bull; read the node from the dictionary<br>'
           '&bull; unlink it from its frequency bucket<br>'
           '&bull; possibly advance <code>minFreq</code><br>'
           '&bull; push it onto the next bucket<br><br>'
           '<b>A reader must never observe the state between those steps</b> &mdash; a node in no bucket, or a '
           '<code>minFreq</code> pointing at an empty one. So the unit of atomicity is <b>the whole operation</b>, '
           'not the dictionary access.<br><br>'
           '<i>Say that sentence and you have already beaten most candidates.</i></div>',
           """Step one: name the invariant, and notice that it is always bigger than one line of code. Take the LFU cache. """
           """A single Get does four things.""", step=0)
seg(sid, 1, """It reads the node from the dictionary, unlinks it from its frequency bucket, possibly advances the minimum """
            """frequency, and pushes it onto the next bucket.""")
seg(sid, 2, """And the requirement is that no other thread may ever observe the state between those steps — a node that is """
            """in no bucket at all, or a minimum frequency pointing at a bucket that is momentarily empty. So the unit of """
            """atomicity is the whole operation, not the dictionary access.""")
seg(sid, 3, """Say that sentence out loud and you have already beaten most candidates, because you have shown that you know """
            """what thread-safety means here rather than which class name sounds concurrent.""")

D = Diagram('Why a concurrent dictionary does not save you')
D.box('t1', 130, 160, 760, 240, 'Thread A: Get("x")', '1. reads node from the map ✓ (atomic)\n'
      '2. unlinks it from bucket 3\n&nbsp;&nbsp;&nbsp;&nbsp;&mdash; **pauses here** &mdash;\n'
      '3. pushes onto bucket 4', kind='info', step=0)
D.box('t2', 990, 160, 780, 240, 'Thread B: Put(&hellip;), cache full', '1. reads minFreq = 3\n'
      '2. takes the tail of bucket 3 to evict\n3. **bucket 3 is mid-surgery**\n'
      '&rarr; evicts a node that is being moved, or reads a dangling pointer',
      kind='deny', step=1)
D.label(130, 450, 'Every individual structure was &ldquo;thread-safe&rdquo;. The **operation** was not.',
        kind='deny', step=2, w=1700, size='l')
D.label(130, 550, 'This class of bug does not throw. It corrupts the structure and surfaces minutes later, '
                  'somewhere else, under load.', kind='deny', step=3, w=1700, size='m')
D.label(130, 650, 'Which is exactly why the boring answer &mdash; **one lock around the whole operation** &mdash; is the '
                  'right first answer.', kind='ok', step=4, w=1700, size='l')
sid = D.build()
seg(sid, 0, """Let me show you the failure concretely, because it is worth being able to narrate. Thread A calls Get. It """
            """reads the node from the map, which is atomic, then unlinks it from bucket three — and pauses there, """
            """mid-operation.""")
seg(sid, 1, """Thread B calls Put on a full cache. It reads the minimum frequency as three, goes to evict the tail of """
            """bucket three, and finds bucket three in the middle of surgery. It evicts a node that is being moved, or """
            """follows a pointer that is about to change.""")
seg(sid, 2, """Every individual structure involved was thread-safe. The operation was not.""")
seg(sid, 3, """And notice the character of this bug: it does not throw. It corrupts the structure and surfaces minutes """
            """later, somewhere else, under load. That is the sentence to say, because it explains why you are being """
            """conservative rather than clever.""")
seg(sid, 4, """Which is exactly why the boring answer — one lock around the whole operation — is the right first answer.""")

CODE = '''// STEP 1: correct, simple, and honest about its cost.
public sealed class LockedLfuCache {
    private readonly LFUCache _inner;
    private readonly object _gate = new();

    public int Get(int key)            { lock (_gate) return _inner.Get(key); }
    public void Put(int key, int value) { lock (_gate) _inner.Put(key, value); }
}

// Why a lock and not Concurrent* types:
//   - the invariant spans the dictionary AND the bucket lists AND minFreq
//   - ConcurrentDictionary makes each ACCESS atomic, not each OPERATION
//   - a correct coarse lock beats a subtly wrong fine-grained one, every time

// Cost, stated out loud: every operation serialises. Throughput is 1 / (time per op),
// regardless of core count. For a cache doing 100 ns of work, that is ~10M ops/sec -
// usually fine. If it is not fine, the next step is to MEASURE, not to guess.'''
code_slide('Step 1 &mdash; the answer to give first', CODE, [
 ('1-8', """Wrap the whole structure and take one lock for the duration of each public operation. Six lines, obviously """
           """correct, and the separation into a wrapper class is deliberate — it keeps the single-threaded logic testable """
           """and it makes the locking policy one readable thing rather than scattered statements."""),
 ('10-13', """Then say why, in these three bullets. The invariant spans three structures; a concurrent dictionary gives """
             """you atomic accesses, not atomic operations; and a correct coarse lock beats a subtly wrong fine-grained """
             """one every time. That third line is a judgement statement, and it is the one that sounds like experience."""),
 ('15-17', """And then price it, out loud, with a number. Every operation serialises, so throughput is one over the time """
             """per operation regardless of how many cores you have. For a cache doing a hundred nanoseconds of work that """
             """is about ten million operations a second, which is usually fine. Giving a number turns "it might be slow" """
             """into engineering."""),
])

sid = beat('Step 2', 'Only now, talk about making it faster &mdash; and say what you would measure',
           '<div style="font-size:30px;line-height:1.7">'
           '<b>&ldquo;Before optimising the lock, I would measure: lock wait time, hold time, and the read/write '
           'ratio.&rdquo;</b><br><br>'
           'Then the options, each with its cost:<br><br>'
           '<b>&bull; Read-write lock</b> &mdash; helps only if reads dominate <i>and</i> reads are truly read-only. '
           'In an LFU cache <b>a read mutates</b> (it bumps a frequency), so this <b>does not apply</b> &mdash; naming '
           'that is a strong signal.<br>'
           '<b>&bull; Striping</b> &mdash; shard by key hash into N independent caches, each with its own lock. '
           'Contention drops N-fold. <b>Cost:</b> eviction becomes per-shard, so the global LFU property is lost.<br>'
           '<b>&bull; Lock-free</b> &mdash; possible for simple structures, very hard for this one. I would not attempt '
           'it in an interview, and I would say why.</div>',
           """Step two, and only now do you talk about speed. Before optimising a lock, I would measure three things: lock """
           """wait time, lock hold time, and the read-to-write ratio.""", step=0)
seg(sid, 1, """Then the options, each with its cost attached. A read-write lock helps only if reads dominate and reads are """
            """genuinely read-only — and in an LFU cache a read mutates, because it bumps a frequency. So a read-write """
            """lock does not apply here at all, and noticing that is one of the strongest signals available in this """
            """conversation, because it shows you are thinking about your structure rather than reciting concurrency """
            """primitives.""")
seg(sid, 2, """Striping: shard by key hash into N independent caches, each with its own lock, and contention drops roughly """
            """N-fold. But name the cost — eviction becomes per-shard, so you no longer have a global least-frequently-used """
            """policy. You have N local ones, which is usually an acceptable approximation, and saying "this changes the """
            """semantics, is that acceptable?" is the right way to offer it.""")
seg(sid, 3, """And lock-free: possible for simple structures, genuinely hard for this one, and I would not attempt it in an """
            """interview. Saying that you know it exists and that you would not reach for it here is better than """
            """attempting it badly.""")

sid = cards('Concurrency vocabulary you should be able to use precisely', [
 (0, 'Race condition', 'The result depends on timing. Not the same as a data race &mdash; you can have a race with perfectly locked primitives.', 'shared'),
 (0, 'Atomicity vs visibility', 'A lock gives both. <code>volatile</code> gives visibility only. Interlocked gives atomicity for one variable.', 'shared'),
 (1, 'Deadlock', 'Two locks taken in different orders. The fix is a global ordering &mdash; or, better, one lock.', 'deny'),
 (1, 'Lock granularity', 'Coarse = simple and slow under contention. Fine = fast and easy to get wrong. Name the trade, do not just pick.', 'ok'),
 (2, 'Check-then-act', 'The classic bug: <code>if (!map.Contains(k)) map.Add(k, v)</code> is <b>not</b> safe even on a concurrent map.', 'deny'),
 (2, 'Reentrancy', 'C# <code>lock</code> is reentrant on the same thread. Useful, and a trap if a callback re-enters your structure.', 'shared'),
], cols=2)
seg(sid, 0, """Some vocabulary you should be able to use precisely, because imprecision here is very audible. A race """
            """condition means the result depends on timing, and it is not the same as a data race — you can have a race """
            """condition while using perfectly thread-safe primitives, which is exactly the LFU failure we just walked """
            """through. Atomicity and visibility are different guarantees: a lock gives both, volatile gives visibility """
            """only, and an interlocked operation gives atomicity for one variable.""")
seg(sid, 1, """Deadlock comes from taking two locks in different orders, and the fix is a global lock ordering — or, better """
            """in an interview, having only one lock. Lock granularity is a trade, so name it rather than silently """
            """picking a side.""")
seg(sid, 2, """Check-then-act is the classic bug and the one most likely to appear in your own code under pressure: """
            """checking whether a map contains a key and then adding it is not safe even on a concurrent map, because """
            """another thread can act between the two calls. And C sharp locks are reentrant on the same thread, which is """
            """convenient and is a trap if a callback re-enters your structure.""")

CODE2 = '''// The check-then-act bug, and the two correct fixes.

// WRONG - even with a ConcurrentDictionary:
if (!_map.ContainsKey(key))          // thread B can insert here
    _map[key] = Compute(key);        // ...and we overwrite it

// RIGHT (1) - one atomic operation:
_map.GetOrAdd(key, k => Compute(k)); // note: Compute may run twice; it must be side-effect free

// RIGHT (2) - when the invariant spans more than the map:
lock (_gate) {
    if (!_map.ContainsKey(key)) {
        var node = Compute(key);
        _map[key] = node;
        _buckets[1].PushFront(node);  // the second structure is WHY the lock is needed
        _minFreq = 1;
    }
}'''
code_slide('Check-then-act &mdash; the bug to be able to spot on sight', CODE2, [
 ('3-6', """The wrong version. Another thread can insert between the check and the write, so you overwrite its value or """
           """duplicate the work. This is not fixed by making the map concurrent, and that is the point — the atomicity """
           """you need spans two calls."""),
 ('8-9', """Fix one, when the map is the only thing involved: a single atomic operation. And note the caveat in the """
           """comment, which interviewers like to probe — the factory can run more than once under contention, so it must """
           """be side-effect free. Knowing that detail about GetOrAdd is a genuine experience signal."""),
 ('11-19', """Fix two, and this is the one that applies to everything in chapter four: when the invariant spans more than """
             """the map — here a bucket list and the minimum frequency too — no concurrent collection can help you, and a """
             """lock around the whole sequence is the answer. The comment on the bucket line is where I would point while """
             """explaining."""),
])

followups(
 ['"Which lock would you use in C#?" — `lock` (Monitor) for short critical sections; SemaphoreSlim if you need async',
  '"What about async code?" — you cannot `lock` across an await; use SemaphoreSlim.WaitAsync',
  '"How would you test it?" — a stress test with N threads and an invariant check, plus a single-threaded reference model to compare against'],
 ['"Now make it distributed" — a lock is no longer possible; you need a single-writer shard, or a CAS loop on a versioned value, and you must decide what happens on partition',
  '"Prove your locking is correct" — state the invariant, show every public method establishes it on exit, and show no method publishes a reference to internal state',
  '"What is your P99 under contention?" — lock wait time grows with queueing; mention that a fair lock trades throughput for tail latency, and that this is usually the right trade for a service'],
 """Follow-ups. Which lock in C sharp: the lock statement for short critical sections, and SemaphoreSlim when you need """
 """async, because you cannot hold a lock across an await — that specific fact gets asked and is worth knowing cold. And """
 """how would you test it: a stress test with many threads plus an invariant check, and — the better half of the answer """
 """— a single-threaded reference model that you compare against, because concurrency bugs are found by differential """
 """testing far more reliably than by staring.""",
 """At staff level, the interesting pivot is distribution. Once the structure spans machines, a lock is not available at """
 """all: you need a single-writer shard, or a compare-and-swap loop on a versioned value, and you must say what happens """
 """during a partition. Proving your locking correct is a three-part argument — state the invariant, show each public """
 """method restores it before returning, and show that no method leaks a reference to internal state, which is the part """
 """people forget. And on tail latency: lock wait time grows with queueing, and a fair lock trades throughput for a """
 """better P99, which for a user-facing service is usually the right trade. That last answer is one an infrastructure """
 """interviewer will remember.""")

interview_script([
 '"Before I add locks — what is the invariant? A Get touches the map, a bucket list and minFreq, and no other thread may see the state in between."',
 '"So the unit of atomicity is the whole operation. A ConcurrentDictionary would not help: it makes each access atomic, not each operation."',
 '"I will start with one lock around each public method. It is obviously correct, and correctness first."',
 '"The cost is that every operation serialises: throughput is 1 over the op time regardless of cores. For ~100 ns of work that is millions per second."',
 '"If that is not enough, I would measure lock wait and hold time before changing anything."',
 '"Then striping by key hash — but that makes eviction per-shard, so the global LFU property becomes approximate. Is that acceptable?"',
 '"A read-write lock would not help here, because in an LFU cache a read mutates the frequency."',
], [
 """The script, and I would rehearse this one until it is automatic, because it is the highest-leverage sixty seconds in """
 """the whole course. Open with the invariant, not with a primitive.""",
 """Then the coarse lock with correctness stated as the reason, then the cost with an actual number, then measurement """
 """before optimisation.""",
 """Then striping with its semantic cost turned into a question for the interviewer. And finish with the read-write lock """
 """observation, because rejecting a plausible-sounding technique for a specific structural reason is the single """
 """clearest signal in this conversation that you understand what you built.""",
])

sid = statement('Lesson 9.1', 'Correct and slow, then measured, then fast. Never the other way round.',
                'And always name the invariant before naming a primitive — that one habit separates the answers.',
                kind='ok')
seg(sid, 0, """One line. Correct and slow, then measured, then fast — never the other way round.""")
seg(sid, 1, """And always name the invariant before you name a primitive. That single habit is what separates the two """
            """answers we compared at the start of this lesson. Next: the OS and networking fundamentals an infra """
            """interviewer asks when the coding finishes early.""")
