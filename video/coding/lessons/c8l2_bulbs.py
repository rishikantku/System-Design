# -*- coding: utf-8 -*-
"""Chapter 8, Lesson 2 — Bulb Switcher."""
from lib import *

lesson_header('8.2', 'Bulb Switcher — when the answer is one line of maths', 'Maths · reasoning out loud',
              'High', 'Your own list', '2026', 'Medium', 13,
              """Chapter eight, lesson two. Bulb Switcher, from your own list. Medium confidence — one report — but I am """
              """including it because it is the only question in this course where the final code is a single line, which """
              """makes it the purest test of something the official pack cares about: can you reason out loud while you do """
              """not yet know the answer? If you go silent on this question, you fail it even if you eventually get there. """
              """So this lesson is about how to think audibly.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:35px;line-height:1.4">'
           'There are <b>n</b> bulbs, all off. You make n passes.<br><br>'
           'On pass 1 you toggle <b>every</b> bulb. On pass 2 you toggle every <b>2nd</b> bulb. On pass 3 every '
           '<b>3rd</b>, and so on until pass n, where you toggle only bulb n.<br><br>'
           'After all n passes, <b>how many bulbs are on?</b></div></div>',
           """The question. There are n bulbs, all off. You make n passes. On the first pass you toggle every bulb. On the """
           """second, every second bulb. On the third, every third, and so on, until the last pass where you toggle only """
           """the final bulb. After all n passes, how many bulbs are on?""")

sid = beat('How to start', 'Say the simulation first &mdash; then say why you are not going to stop there',
           '<div style="font-size:31px;line-height:1.7">'
           '<i>&ldquo;The direct simulation is n passes over up to n bulbs, so O(n&sup2;) time and O(n) space. '
           'That works and I can write it in two minutes. But the structure here looks like it wants a closed form, '
           'so let me look at small cases first &mdash; if I do not find one in a couple of minutes, I will write the '
           'simulation.&rdquo;</i><br><br>'
           'That sentence does three things: it proves you have a working answer, it names what you are looking for, '
           'and it <b>sets a time budget</b> out loud. Now thinking in silence has become a plan.</div>',
           """Here is how to start, and this opening is most of the lesson. Say the simulation first. It is n passes over """
           """up to n bulbs, so quadratic time and linear space, and you can write it in two minutes.""", step=0)
seg(sid, 1, """Then say why you are not going to stop there: the structure looks like it wants a closed form, so you will """
            """look at small cases — and if you do not find one within a couple of minutes, you will write the simulation.""")
seg(sid, 2, """That sentence does three things at once. It proves you already have a working answer, so you are never at """
            """risk of having nothing. It names what you are hunting for. And it sets a time budget out loud, which turns """
            """silent thinking into a visible plan. Interviewers do not penalise thinking; they penalise not knowing what """
            """you are doing.""")

think('Work out n = 1 through 6 by hand. Which bulbs end up on?', 40,
      """Now pause and actually do this by hand, because doing it is the only way the pattern arrives. Work out which """
      """bulbs are on for n equals one through six. Write the toggles down.""",
      """Let us do it together.""")

D = Diagram('Which bulbs survive, for n = 6')
vals = ['1','2','3','4','5','6']
ids = array_row(D, vals, x=280, y=160, cw=180, ch=100, step=0, kind='info')
D.label(280, 280, 'bulb 6 is toggled on passes 1, 2, 3, 6 &rarr; **4 toggles** &rarr; off',
        kind='deny', step=1, w=1500, size='m')
D.label(280, 350, 'bulb 4 is toggled on passes 1, 2, 4 &rarr; **3 toggles** &rarr; **on**',
        kind='ok', step=2, w=1500, size='m')
D.label(280, 430, 'A bulb is toggled once per **divisor**. Odd number of divisors &rarr; ends up on.',
        kind='dp', step=3, w=1600, size='l')
D.label(280, 530, 'Divisors come in **pairs**: d &times; (k/d). 6 &rarr; (1,6) (2,3). Always even&hellip;',
        kind='neutral', step=4, w=1600, size='m')
D.label(280, 610, '&hellip;**unless** d = k/d, i.e. k is a **perfect square**. 4 &rarr; (1,4) and (2,2) &mdash; 2 is '
                  'unpaired.', kind='ok', step=5, w=1600, size='l')
hl_cells(D, [ids[0], ids[3]], x=280, y=160, cw=180, ch=100, marks={0: 6, 3: 6}, kind='ok')
D.label(280, 720, 'So the bulbs left on are exactly **1, 4, 9, 16, &hellip;** &rarr; the answer is '
                  '**&lfloor;&radic;n&rfloor;**.', kind='dp', step=6, w=1600, size='l')
sid = D.build()
seg(sid, 0, """Six bulbs. Rather than tracking all of them, look at individual ones and ask how many times each gets """
            """toggled.""")
seg(sid, 1, """Bulb six is toggled on passes one, two, three and six — four toggles, an even number, so it ends up off.""")
seg(sid, 2, """Bulb four is toggled on passes one, two and four — three toggles, odd, so it ends up on.""")
seg(sid, 3, """And there is the reframing: a bulb is toggled exactly once per divisor of its number. So a bulb ends up on """
            """precisely when it has an odd number of divisors. Notice that we have replaced a simulation question with a """
            """number theory question, and that replacement is the actual insight.""")
seg(sid, 4, """Now, divisors come in pairs — d and k over d. Six pairs up as one and six, two and three. That is always an """
            """even count.""")
seg(sid, 5, """Unless the two members of a pair are the same number, which happens exactly when k is a perfect square. """
            """Four pairs as one and four, and then two with itself — so two is unpaired and the count is odd.""")
seg(sid, 6, """Therefore the bulbs left on are exactly the perfect squares: one, four, nine, sixteen and so on. And the """
            """count of perfect squares up to n is the floor of the square root of n. That is the answer, and it is one """
            """line.""")

CODE = '''// The whole solution.
public int BulbSwitch(int n) => (int)Math.Sqrt(n);

// Worth mentioning: floating-point sqrt on very large n can land one off.
// If they push on it, guard the boundary explicitly:
public int BulbSwitchExact(int n) {
    int r = (int)Math.Sqrt(n);
    while ((long)(r + 1) * (r + 1) <= n) r++;      // step up if sqrt rounded down
    while ((long)r * r > n) r--;                   // step back if it rounded up
    return r;
}'''
code_slide('The C# implementation', CODE, [
 ('1-2', """The whole solution is one line, and if you have explained the reasoning first, that line is satisfying rather """
           """than suspicious. If you write it without the reasoning, it looks like you memorised it — which on this """
           """particular question is the thing they are trying to detect."""),
 ('4-11', """And here is the detail that turns a good answer into a careful one. Floating-point square root on very large """
            """inputs can land one either side of the true value. If the interviewer pushes on correctness at scale, guard """
            """the boundary explicitly with integer arithmetic, using long in the multiplications so the check itself does """
            """not overflow. Volunteering this unprompted is a strong signal, because it shows you distrust floating point """
            """in an integer problem — which is a habit rather than a fact."""),
])

sid = cards('If the pattern does not come &mdash; what to do', [
 (0, 'Say what you are trying', '"I am looking at how many times each bulb is toggled, because that decides its final state."', 'ok'),
 (0, 'Tabulate out loud', 'n = 1..10, marking which are on. A pattern you can see is worth ten minutes of staring at algebra.', 'ok'),
 (1, 'Name the sequence when you see it', '"1, 4, 9 — those are perfect squares. Let me work out why."', 'ok'),
 (1, 'Fall back on schedule', 'You said two minutes. Honour it: write the O(n²) simulation, then keep thinking while it is on the board.', 'shared'),
 (2, 'Never go silent', 'Silence is the only unrecoverable failure on this question. Narrate dead ends too &mdash; "divisor pairs, that feels promising".', 'deny'),
 (2, 'If they hint, take it gracefully', '"Divisors — yes, that is the right lens, thank you." Taking a hint well is a scored behaviour, not a defeat.', 'ok'),
], cols=2)
seg(sid, 0, """Now the important part: what to do if the pattern does not come, because for most people it does not come """
            """instantly. Say what you are trying — I am looking at how many times each bulb is toggled, because that """
            """decides its final state. That sentence alone earns credit whether or not you finish.""")
seg(sid, 1, """Tabulate out loud for n from one to ten, marking which bulbs are on. A pattern you can see beats ten minutes """
            """of staring at algebra. And when you spot it, name it: one, four, nine — those are perfect squares, let me """
            """work out why.""")
seg(sid, 2, """If your budget runs out, honour it. Write the quadratic simulation, get a working answer on the board, and """
            """keep thinking while it sits there. A correct slow answer plus visible reasoning is a pass; nothing on the """
            """board is not.""")
seg(sid, 3, """And never go silent. Silence is the only unrecoverable failure on this question. Narrate the dead ends too. """
            """If they offer a hint, take it gracefully and say so — taking a hint well is a scored behaviour in every """
            """rubric I have seen, not a defeat.""")

sid = beat('Why they ask this', 'It is a proxy for something real',
           '<div style="font-size:30px;line-height:1.7">'
           'A one-line answer is worthless as a coding test. So what is being measured?<br><br>'
           '<b>&bull;</b> Do you produce a <b>working</b> answer before chasing an elegant one?<br>'
           '<b>&bull;</b> Do you <b>reframe</b> &mdash; from "simulate toggles" to "count divisors"?<br>'
           '<b>&bull;</b> Can you be watched while you do not yet know the answer?<br>'
           '<b>&bull;</b> Do you <b>verify</b> the pattern, or just assert it?<br><br>'
           'That last one matters: after you spot perfect squares, <b>check n = 10</b> out loud. Three bulbs on: '
           '1, 4, 9. &lfloor;&radic;10&rfloor; = 3. ✓</div>',
           """Why do they ask a question whose answer is one line? Because as a coding test it is worthless — so something """
           """else is being measured.""", step=0)
seg(sid, 1, """Do you produce a working answer before chasing an elegant one. Do you reframe, from simulating toggles to """
            """counting divisors. Can you be watched while you do not yet know the answer. And do you verify the pattern or """
            """merely assert it.""")
seg(sid, 2, """That last one is worth ten seconds and most candidates skip it. After you spot perfect squares, check n """
            """equals ten out loud: bulbs one, four and nine are on, that is three, and the floor of the square root of ten """
            """is three. Confirmed. A pattern you verified is evidence; a pattern you guessed is a guess, and the """
            """interviewer cannot tell the difference unless you show them.""")

followups(
 ['"Prove the divisor-pairing argument" — pairs (d, k/d) are distinct unless d² = k',
  '"Which bulbs specifically, not how many?" — the perfect squares up to n; generate them in O(√n)',
  '"What if bulbs start on?" — invert: the answer becomes n − ⌊√n⌋'],
 ['"n is 10¹⁸" — the formula is fine, but floating-point sqrt is not; use integer square root and verify the boundary',
  '"Every 2nd pass only, or passes from a given set S" — the pairing argument dies; now it is a parity question over the divisors that lie in S',
  '"Distribute the simulation" — each pass is independent as a set of indices; but since the answer is closed-form, the right call is not to distribute it at all'],
 """Follow-ups. Proving the pairing argument is one sentence: the pair d and k over d are distinct numbers unless d """
 """squared equals k. Asking which bulbs rather than how many gives you the perfect squares, generated in root n time. """
 """And if the bulbs start on, the answer inverts to n minus the floor of the root.""",
 """At staff level, the first follow-up is the one to be ready for: n of ten to the eighteen. The formula is still """
 """correct, but double-precision square root is not reliable there, so you use an integer square root and verify the """
 """boundary — which is exactly the guard we wrote. The second is genuinely harder: if only passes from some arbitrary """
 """set happen, the pairing argument dies, and it becomes a parity question over the divisors that lie in that set, with """
 """no closed form in general. And the third is a small trap worth spotting: yes, the simulation parallelises, but since """
 """there is a closed form, the right engineering answer is not to distribute it at all. Knowing when not to reach for """
 """infrastructure is itself a staff signal.""")

interview_script([
 '"The direct simulation is O(n²) time, O(n) space, and I can write it now if you want a baseline."',
 '"But let me look at small cases for two minutes first — this smells like it has a closed form."',
 '"A bulb is toggled once per divisor of its index, so it ends up on exactly when it has an odd number of divisors."',
 '"Divisors pair up as d and k/d, so the count is even — unless d equals k/d, which means k is a perfect square."',
 '"So the answer is the number of perfect squares up to n, which is ⌊√n⌋. Let me check n = 10: bulbs 1, 4, 9 — three. ✓"',
 '"One caveat: for very large n I would not trust floating-point sqrt; I would use an integer root and verify the boundary."',
], [
 """The script, and notice its shape: baseline, budget, reframe, derive, verify, caveat. That is the shape of every good """
 """answer to a puzzle-flavoured question, and it works even when the puzzle is one you have not seen.""",
 """The reframe line is the one that earns the interview: a bulb is toggled once per divisor. Everything after it is """
 """arithmetic.""",
 """And the last two lines are what most candidates skip. Verify on a concrete case out loud, and name the """
 """floating-point caveat. Together they take fifteen seconds and they are the difference between "got the answer" and """
 """"reasons like an engineer".""",
])

sid = statement('Lesson 8.2', 'A one-line answer is a test of how you think while you do not yet know it.',
                'Baseline first, budget out loud, reframe, verify on a real case. That sequence works even when the trick does not come.',
                kind='ok')
seg(sid, 0, """One line. A one-line answer is not a test of the line — it is a test of how you think while you do not yet """
            """know it.""")
seg(sid, 1, """Baseline first, budget out loud, reframe, verify on a real case. That sequence works even when the trick """
            """never arrives, which is exactly why it is worth rehearsing. Next is the chapter eight recap.""")
