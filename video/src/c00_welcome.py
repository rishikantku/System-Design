# -*- coding: utf-8 -*-
from engine import *

chapter(0, "Atlassian Isolated Cloud", "A Staff-level design retrospective course. One project, taught properly.",
 """Welcome. This course is your interview preparation for the LinkedIn Staff Engineer design retrospective, built entirely from your Isolated Cloud prep document. Think of me as the mentor sitting next to you before the interview. I'm not going to read the document to you. I'm going to teach you how to think about this system, how to explain it out loud, and what the interviewer is really listening for.""")

sid = cards("How this course works", [
 (0, "Understand, then practise", "Project → problem → architecture → why → trade-offs → failures → operations → migration → ownership → impact", 'dp'),
 (1, "Diagrams build step by step", "Each box appears when it matters. Watch the highlighted part.", 'cp'),
 (2, "Questions pause for you", "When the timer runs, answer out loud before I do.", 'shared'),
 (3, "Revise fast at the end", "Rapid revision, then a full mock interview.", 'ok'),
], cols=2)
seg(sid, 0, """Here's how the course is structured. The first half is understanding. We start with what the project is and the problem it solved, then the architecture, then why it's shaped the way it is, the trade-offs, the failure modes, operations at scale, the migration, and finally your personal ownership and the business impact.""")
seg(sid, 1, """The architecture diagrams build one step at a time. Don't try to absorb the whole picture at once. Watch the part that's highlighted, because that's what I'm explaining in that moment. By the end of each diagram, you should be able to redraw it yourself.""")
seg(sid, 2, """The second half is practice. When you see a question with a timer, that's your turn. Answer out loud, as if the interviewer just asked you. It feels awkward the first time. It's also the single most useful thing you can do, because saying it is a different skill from knowing it.""")
seg(sid, 3, """And at the end there's a rapid revision section for the morning of the interview, followed by a full mock interview. If you only have fifteen minutes before the call, skip straight to rapid revision.""")

sid = statement("The one rule for this interview", "Tell the same story, the same way, every time.",
 "Interviewers cross-check. The same incident, the same numbers and the same people must come out identically however they ask.", kind='shared')
seg(sid, 0, """Before we start, one rule that matters more than anything else in a retrospective. Tell the story the same way every time.""")
seg(sid, 1, """A retrospective interviewer will come at the same event from different angles. They'll ask about migration, then about conflict, then about production issues, and they're quietly checking that the details line up. The same incident, the same numbers, the same people. So as we go, notice the specific figures. Two days down to five hours for provisioning. Ninety-nine point nine five percent per environment. About ten minutes for the worst cutover. Those numbers need to be automatic, and they need to match everywhere.""")
