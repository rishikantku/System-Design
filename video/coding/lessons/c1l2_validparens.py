# -*- coding: utf-8 -*-
"""Chapter 1, Lesson 2 — Valid Parentheses, the warm-up."""
from lib import *

lesson_header('1.2', 'Valid Parentheses — the warm-up, and what they watch', 'Stacks · warm-up discipline',
              'High', 'Your list + the LinkedIn tagged set', '2026', 'High', 12,
              """Chapter one, lesson two. Valid Parentheses is on your own list and on the LinkedIn tagged set, and it is """
              """the easiest question in this entire course. So why is it here? Because an easy question early in a round """
              """is not a test of whether you can solve it — it is a test of how you behave when you already know the """
              """answer. That is a genuinely different skill, most people are bad at it, and it sets the tone for """
              """everything after.""")

sid = beat('Question', 'The problem, as they pose it',
           '<div class="qwrap"><div class="qtext" style="font-size:36px;line-height:1.4">'
           'Given a string containing only the characters <code>( ) [ ] { }</code>, decide whether the brackets are '
           'correctly matched and correctly nested.</div></div>',
           """The question. Given a string of round, square and curly brackets, decide whether they are correctly matched """
           """and correctly nested. You almost certainly know the answer already, so the interesting question is what you """
           """do in the next sixty seconds.""")

sid = compare('Two candidates, same code, different outcomes',
 ('Candidate A', 'deny', 0,
  ['Starts typing immediately',
   'Finishes in 90 seconds, says &ldquo;done&rdquo;',
   'Asked nothing; explained nothing',
   'Interviewer learns: <b>they have seen this before</b> &mdash; and nothing else']),
 ('Candidate B', 'ok', 1,
  ['&ldquo;Only those six characters, or can other text appear?&rdquo;',
   '&ldquo;A stack: push openers, and every closer must match the top.&rdquo;',
   'Codes it, then walks <code>([)]</code> through out loud',
   'Names the edge cases, then offers the extension &mdash; **4 minutes, far more signal**']))
seg(sid, 0, """Candidate A starts typing immediately, finishes in ninety seconds and says done. They asked nothing and """
            """explained nothing. What did the interviewer learn? That this person has seen the question before. That is """
            """all — and it is not much to write on a scorecard.""")
seg(sid, 1, """Candidate B asks whether the string contains only those six characters or can include other text. States the """
            """approach in one sentence before coding. Writes it, then walks a tricky input through out loud. Names the """
            """edge cases, then offers an extension. Four minutes, and the interviewer now has real signal about how this """
            """person works. Same code, completely different round.""")

sid = beat('The approach, in one sentence', 'Say it before you type it',
           '<div class="bigidea">Push every opening bracket. On a closing bracket, the top of the stack must be its '
           'partner &mdash; otherwise the string is invalid. At the end the stack must be <b>empty</b>.</div>'
           '<div style="margin-top:26px;font-size:30px;line-height:1.7">'
           'Why a stack: nesting is <b>last-in, first-out</b> by definition. The most recently opened bracket is the '
           'one that must close first. The data structure <i>is</i> the problem statement.</div>',
           """The approach, in one sentence, said before you type. Push every opening bracket. On a closing bracket, the """
           """top of the stack must be its partner, otherwise the string is invalid. And at the end, the stack must be """
           """empty.""", step=0)
seg(sid, 1, """And the justification, which takes five seconds and is worth saying: nesting is last-in first-out by """
            """definition — the most recently opened bracket is the one that must close first. The data structure is the """
            """problem statement. That sentence turns a memorised answer into a derived one, and an interviewer cannot """
            """tell the difference any other way.""")

D = Diagram('Walking "([)]" &mdash; the input that catches lazy solutions')
D.box('s1', 150, 170, 400, 120, "read '('", 'push &rarr; stack: [ ( ]', kind='ok', step=0)
D.box('s2', 620, 170, 400, 120, "read '['", 'push &rarr; stack: [ ( [ ]', kind='ok', step=1)
D.box('s3', 1090, 170, 620, 120, "read ')'", 'top is &lsquo;[&rsquo;, not &lsquo;(&rsquo; &rarr; **invalid**',
      kind='deny', step=2)
D.label(150, 340, 'A counter of open brackets would say &ldquo;2 open, 2 closed &mdash; fine&rdquo;. '
                  'It cannot see that the nesting is crossed.', kind='deny', step=3, w=1600, size='m')
D.label(150, 440, 'That is exactly why the interviewer will hand you this string. Walk it **before** they do.',
        kind='ok', step=4, w=1600, size='l')
D.label(150, 550, 'The other two inputs that matter:', kind='neutral', step=5, w=1600, size='m')
D.label(150, 620, '&bull; &ldquo;(&ldquo; &rarr; stack not empty at the end &rarr; invalid\n'
                  '&bull; &ldquo;)&rdquo; &rarr; closer with an **empty** stack &rarr; invalid (and a crash if you pop blindly)',
        kind='deny', step=5, w=1600, size='m')
sid = D.build()
seg(sid, 0, """Let me walk the input that catches lazy solutions. Read an open round bracket, push it.""")
seg(sid, 1, """Read an open square bracket, push it.""")
seg(sid, 2, """Read a closing round bracket. The top of the stack is the square bracket, not the round one, so the string """
            """is invalid.""")
seg(sid, 3, """And notice what this input defeats: a solution that merely counts open and closed brackets would say two """
            """open, two closed, looks fine. It cannot see that the nesting is crossed.""")
seg(sid, 4, """Which is exactly why the interviewer will hand you that string. Walk it yourself before they do — that move """
            """converts a passive correct answer into a demonstration.""")
seg(sid, 5, """The other two inputs that matter are the degenerate ones: a lone opener leaves the stack non-empty at the """
            """end, and a lone closer arrives with an empty stack — which is invalid, and which crashes your code if you """
            """pop without checking.""")

CODE = '''public bool IsValid(string s) {
    if ((s.Length & 1) == 1) return false;                 // odd length can never balance - cheap early exit

    var stack = new Stack<char>(s.Length / 2);             // pre-sized: at most half the input
    foreach (char c in s) {
        switch (c) {
            case '(': case '[': case '{':
                stack.Push(c);
                break;

            case ')':
                if (stack.Count == 0 || stack.Pop() != '(') return false;
                break;
            case ']':
                if (stack.Count == 0 || stack.Pop() != '[') return false;
                break;
            case '}':
                if (stack.Count == 0 || stack.Pop() != '{') return false;
                break;

            default:
                return false;                              // decide this WITH the interviewer
        }
    }
    return stack.Count == 0;                               // leftovers mean unclosed brackets
}'''
code_slide('The C# implementation', CODE, [
 ('2', """An early exit on odd length. It is not required, it is two characters of code, and mentioning why it is valid — """
         """every bracket needs a partner — shows you are thinking about the input rather than just the algorithm."""),
 ('4', """Pre-sizing the stack to half the input length. A small thing, but allocation habits get noticed, especially by """
         """infrastructure interviewers."""),
 ('6-10', """Openers are pushed. The switch makes the six cases explicit rather than hiding them in a lookup table — at """
            """this size, explicit is more readable, and readability is what this round scores."""),
 ('12-19', """Each closer checks two things: that the stack is not empty, and that the top is its partner. Both checks """
             """matter, and the empty check must come first or you throw on the input `)`. That ordering is the one real """
             """bug available in this problem."""),
 ('21-22', """The default case is where you look up at the interviewer. If other characters can appear, do they invalidate """
             """the string or get ignored? Do not guess — the question is ten seconds and the two answers are different """
             """programs."""),
 ('24', """And the final check people forget under time pressure: a non-empty stack at the end means unclosed brackets. """
          """Returning true here is the classic wrong answer on the input open-bracket."""),
])

sid = beat('The extension to offer', 'Because you will finish with time left',
           '<div style="font-size:30px;line-height:1.7">'
           'Offer one of these, unprompted, in a single sentence:<br><br>'
           '<b>&bull; Generalise the pairs</b> &mdash; a <code>Dictionary&lt;char,char&gt;</code> of closer&rarr;opener, '
           'so adding a new bracket type is a config change, not a code change. <i>That is the extensibility the pack '
           'scores.</i><br>'
           '<b>&bull; Report where it broke</b> &mdash; push the index alongside the character; now you can say '
           '&ldquo;unmatched &lsquo;[&rsquo; at position 14&rdquo;, which is what a real parser must do.<br>'
           '<b>&bull; The real-world version</b> &mdash; brackets inside string literals and comments must be ignored. '
           'Now it is a tokeniser, and the stack is still the right structure.</div>',
           """And because you will finish with time left, have an extension ready to offer unprompted. One sentence, any """
           """of these three.""", step=0)
seg(sid, 1, """Generalise the pairs into a dictionary from closer to opener, so that adding a new bracket type is a """
            """configuration change rather than a code change. That is precisely the extensibility the official pack says """
            """this module scores, and it applies to a fifteen-line function just as much as to a large one.""")
seg(sid, 2, """Or report where it broke: push the index alongside the character, so you can say "unmatched square bracket """
            """at position fourteen" — which is what any real parser has to do, and it costs three characters.""")
seg(sid, 3, """Or the real-world version: brackets inside string literals and comments must be ignored, at which point you """
            """have a tokeniser, and the stack is still the right structure underneath. Any one of these turns ninety """
            """seconds of typing into a conversation about design.""")

followups(
 ['"What if other characters can appear?" — ask; ignore them or reject, and the two answers are different programs',
  '"Report the position of the first error" — push (char, index) pairs',
  '"Support a new bracket type" — a closer→opener dictionary, so it becomes configuration'],
 ['"A 2 GB file of source code" — stream it; the stack depth is the nesting depth, not the file size, which is a nice thing to notice out loud',
  '"Deeply nested input, 10⁶ levels" — an explicit stack is already fine; a recursive solution would blow the call stack',
  '"Validate as the user types" — incremental: keep the stack between keystrokes, and handle a backspace by undoing the last operation'],
 """Follow-ups. What if other characters appear — ask, because ignoring and rejecting are different programs. Reporting """
 """the first error position means pushing character-index pairs. And supporting a new bracket type is the dictionary """
 """change.""",
 """The staff-level ones are worth having ready because they are cheap to answer well. A two-gigabyte source file streams """
 """fine, and the point to make is that your memory is the nesting depth rather than the file size — that observation """
 """lands well. A million levels of nesting is fine with an explicit stack and would blow the call stack if you had """
 """written it recursively, which is a good reason to prefer the iterative form. And validating as the user types is a """
 """genuinely nice design question: you keep the stack between keystrokes and handle backspace by undoing the last """
 """operation, which is how an editor actually does it.""")

interview_script([
 '"Can the string contain characters other than those six? And should they be ignored or treated as invalid?"',
 '"Nesting is last-in-first-out, so a stack: push openers, and each closer must match the top."',
 '"Two checks per closer — the stack must not be empty, and the top must be the matching opener."',
 '"At the end the stack must be empty, otherwise something was never closed."',
 '"Let me walk ([)] through: push, push, then the closer does not match the top, so false."',
 '"O(n) time, O(n) space in the worst case — all openers."',
 '"If you want it extensible, I would put the pairs in a dictionary so a new bracket type is configuration, not code."',
], [
 """The script, and the whole point of this lesson is that it exists at all for a question this easy. Open with the """
 """clarifying question, then justify the stack in one clause rather than just naming it.""",
 """State the two checks per closer and the end condition, because those are the two places the bug lives, and saying """
 """them out loud is how you show you know that.""",
 """Then walk the crossed-nesting input yourself, give the complexity, and offer the extensibility change. Seven """
 """sentences, about four minutes including the code — and the interviewer has learned more about you than from any """
 """ninety-second silent solve.""",
])

sid = statement('Lesson 1.2', 'An easy question is a test of how you behave when you already know the answer.',
                'Clarify, justify, walk an example, name the edges, offer the extension. Same code — completely different round.',
                kind='ok')
seg(sid, 0, """One line. An easy question is not a test of whether you can solve it. It is a test of how you behave when """
            """you already know the answer.""")
seg(sid, 1, """Clarify, justify, walk an example, name the edges, offer the extension. Same code, completely different """
            """round — and it sets the tone for everything that comes after it in the loop. Next is chapter two, where the """
            """reported questions start in earnest.""")
