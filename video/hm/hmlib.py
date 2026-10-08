# -*- coding: utf-8 -*-
"""LINKEDIN STAFF ENGINEER — HOST MANAGER PLAYBOOK: builds one lesson from
companies/linkedin/src/hostmgr_course.py + hostmgr_bank*.py + hostmgr_data.py, on top of the
system-design course's slide helpers (video/design/lib.py).

Lesson shape: header · objective · concept · (model diagram) · my personal example · interview mode
(QUESTION → YOUR TURN 25 s → MODEL RESPONSE → WHY IT WORKS → FOLLOW-UP → pause → ANSWER) ·
common mistakes · Staff-level signal · key takeaways.

Provenance stays visible on screen: constructed story details show as [PRACTICE STORY · CONFIRM],
unknowns as [YOUR FACTS], numbers as [METRIC TO VERIFY]. Narration never speaks the brackets:
it tells the viewer to confirm, or to use their own facts.
"""
import importlib.util, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'companies', 'linkedin', 'src'))
sys.path.insert(0, os.path.join(REPO, 'video', 'src'))

_spec = importlib.util.spec_from_file_location('dlib', os.path.join(REPO, 'video', 'design', 'lib.py'))
dlib = importlib.util.module_from_spec(_spec); sys.modules['dlib'] = dlib; _spec.loader.exec_module(dlib)
import engine as E
E.BRAND = 'LinkedIn Staff &middot; Host Manager Playbook'

import hostmgr_course as C
import hostmgr_bank as B
import hostmgr_data as D
from hostmgr_bank2 import SCENARIOS
SBY = {h['id']: h for h in SCENARIOS}

QBY = {q['id']: q for q in B.BANK}
esc = E.esc
MARK = re.compile(r'\[((?:STORY|USER INPUT REQUIRED|METRIC TO VERIFY|GENERAL)[^\]]*)\]')


# ---------------------------------------------------------------- text paths
def speak(s):
    s = str(s)
    s = re.sub(r'\[STORY[^\]]*\]', '', s)
    s = re.sub(r'\[METRIC TO VERIFY[^\]]*\]', ' — and here, give your real number, or say plainly that you do not have it — ', s)
    s = re.sub(r'\[USER INPUT REQUIRED[^\]]*\]', ' — and here, use your own facts — ', s)
    s = re.sub(r'\[GENERAL[^\]]*\]', '', s)
    s = re.sub(r'\((RESUME|YOURS|RESUME / YOURS)\)', '', s)
    s = s.replace('**', '').replace('~', 'about ')
    return re.sub(r'\s+', ' ', s).strip(' —')

def screen(s):
    s = esc(str(s)).replace('**', '')
    def tag(m):
        t = m.group(1).upper()
        lab, col = (('PRACTICE STORY · CONFIRM', '#fbbf24') if t.startswith('STORY') else ('METRIC TO VERIFY', '#f472b6') if t.startswith('METRIC')
                    else ('GENERAL', '#94a3b8') if t.startswith('GENERAL') else ('YOUR FACTS', '#f87171'))
        rest = m.group(1).split(':', 1)[1].strip() if ':' in m.group(1) else ''
        return '<span style="color:%s;font-weight:700">[%s]</span>%s' % (col, lab, (' <span style="color:#cbd5e1">%s</span>' % rest) if rest else '')
    return MARK.sub(tag, s)

def has_story(*texts): return any('[STORY' in t for t in texts)
def has_input(*texts): return any('[USER INPUT REQUIRED' in t for t in texts)

def chunks(text, n):
    sents = [x for x in re.split(r'(?<=[.?!])\s+', text.strip()) if x]
    n = max(1, min(n, len(sents))); per = -(-len(sents) // n)
    return [' '.join(sents[i * per:(i + 1) * per]) for i in range(n) if sents[i * per:(i + 1) * per]]


# ---------------------------------------------------------------- slides
def section(name):
    E._state['chapter'] = name
    E.CHAPTERS.append((name, len(E.SEGMENTS)))

def header(l):
    rows = [('Objective', esc(l['objective'])), ('Format', 'Concept &rarr; my example &rarr; your turn &rarr; model answer &rarr; follow-up'),
            ('Rule', 'Practice-story details: confirm before you say them')]
    meta = ''.join('<div class="lh-k">%s</div><div class="lh-v k-neutral">%s</div>' % (k, v) for k, v in rows)
    sid = E.new_slide('<div class="lhead"><div class="lh-num">HOST MANAGER PLAYBOOK &middot; VIDEO %s</div><h1 class="lh-t">%s</h1>'
                      '<div class="lh-p">LinkedIn Staff Engineer &middot; the Host Leader round</div><div class="lh-meta">%s</div></div>'
                      % (l['num'], esc(l['title']), meta), cls='lesson-head')
    return sid

def bullets(title, items, narration, kicker):
    """A numbered list that reveals with the narration; items may carry provenance markers."""
    lis = ''.join('<li class="k-info" data-step="%d"><span class="sn">%d</span><span>%s</span></li>' % (i, i + 1, screen(t)) for i, t in enumerate(items))
    sid = E.new_slide('<ol class="sl">%s</ol>' % lis, title=dlib._md(title), kicker=kicker)
    parts = chunks(speak(narration), len(items))
    for i, p in enumerate(parts):
        dlib.seg(sid, len(items) - 1 if i == len(parts) - 1 else min(i, len(items) - 1), p)
    return sid

def model_chain(steps, title='The model'):
    boxes = ''.join('<div data-step="%d" style="display:inline-block;margin:10px 6px;padding:30px 34px;border-radius:18px;border:3px solid #60a5fa;'
                    'background:rgba(96,165,250,.10);font:800 40px Inter,sans-serif;color:#fff">%s</div>%s'
                    % (i, esc(s), '<span style="font:800 34px Inter;color:#64748b">&rarr;</span>' if i < len(steps) - 1 else '') for i, s in enumerate(steps))
    sid = E.new_slide('<div style="position:absolute;left:110px;right:110px;top:120px;text-align:center;line-height:1.2">%s</div>' % boxes,
                      title=title, kicker='The model')
    dlib.seg(sid, len(steps) - 1, 'Here is the model, in one line: ' + ', then '.join(s for s in steps if not s.startswith('=')) + '.')

def interview(qid, n, think=25, brief=False, lead=''):
    q = QBY[qid]
    kick = 'Your turn &middot; ' + esc(q['cat'])
    qs = E.new_slide('<div class="qwrap"><div class="qlabel">The Host Manager asks</div><div class="qtext" style="font-size:%dpx">&ldquo;%s&rdquo;</div>'
                     '<div class="think" data-step="1"><div class="thinkl">YOUR TURN &mdash; answer out loud. Pause the video if you need longer.</div>'
                     '<div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>' % (60 if len(q['q']) < 90 else 46, esc(q['q'])), kicker=kick)
    dlib.seg(qs, 0, (lead + ' ' if lead else '') + 'The question: ' + q['q'] + ' Your turn. Answer it out loud.')
    E.seg(qs, 1, '', kind='think', think=think)

    def blk(label, body, kind, st):
        return '<div class="ab k-%s" data-step="%d"><div class="abl">%s</div><div class="abb">%s</div></div>' % (kind, st, label, body)
    rec = '<p style="margin:0 0 10px">&ldquo;%s&rdquo;</p><ul>%s</ul>' % (screen(q['opener']), ''.join('<li>%s</li>' % screen(a) for a in q['anchors']))
    blocks = [blk('Model response &middot; anchor points, not a script', rec, 'ok', 0)]
    if not brief:
        why = ('<p style="margin:0 0 8px"><b>Really asking:</b> %s</p><p style="margin:0 0 6px;color:#fca5a5"><b>Weak:</b> %s</p>'
               '<p style="margin:0 0 6px;color:#cbd5e1"><b>Senior:</b> %s</p><p style="margin:0;color:#86efac"><b>Staff:</b> %s</p>'
               % (screen(q['asking']), screen(q['weak']), screen(q['senior']), screen(q['staff'])))
        blocks.append(blk('Why it works', why, 'dp', 1))
    a = E.new_slide('<div class="qmini">&ldquo;%s&rdquo;</div><div class="ablocks">%s</div>' % (esc(q['q']), ''.join(blocks)), kicker='Model response')
    narr = 'Here is how a strong answer goes. You might open with: ' + speak(q['opener']) + ' Then hit these anchor points. ' + ' '.join(speak(x).rstrip('.') + '.' for x in q['anchors'])
    if q['metrics']: narr += ' The numbers: ' + ', '.join(speak(m) for m in q['metrics']) + '.'
    if q['lesson']: narr += ' And land the lesson: ' + speak(q['lesson'])
    if has_story(q['opener'], *q['anchors']): narr += ' One honest note: parts of this come from a practice story that was constructed for you. Confirm every detail is true before you say it.'
    dlib.seg(a, 0, narr)
    if not brief:
        dlib.seg(a, 1, 'Why this works. What the Host Manager is really asking is: ' + speak(q['asking']) + ' A weak answer sounds like this: ' + speak(q['weak']) +
                 ' A senior answer: ' + speak(q['senior']) + ' And the Staff answer: ' + speak(q['staff']))
    for k, (fq, fa) in enumerate(q['fu'][:1 if brief else 2]):
        f = E.new_slide('<div class="qwrap"><div class="qlabel">Follow-up</div><div class="qtext" style="font-size:50px">&ldquo;%s&rdquo;</div>'
                        '<div class="think" data-step="1"><div class="thinkl">Answer it.</div><div class="thinkbar"><i></i></div><div class="thinkc"></div></div>'
                        '<div class="qsub" data-step="2">%s</div></div>' % (esc(speak(fq)), screen(fa)), kicker='Follow-up')
        dlib.seg(f, 0, ('The likely follow-up: ' if k == 0 else 'And then: ') + speak(fq))
        E.seg(f, 1, '', kind='think', think=12)
        dlib.seg(f, 2, speak(fa) or 'Answer that one with your own facts.')

def scenario(sid_, n, think=30):
    h = SBY[sid_]
    qs = E.new_slide('<div class="qwrap"><div class="qlabel">Hypothetical &middot; %s &middot; %s</div><div class="qtext" style="font-size:48px">%s</div>'
                     '<div class="think" data-step="1"><div class="thinkl">YOUR TURN &mdash; walk it through out loud: considerations, stakeholders, metrics, decision, rollout, rollback.</div>'
                     '<div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>' % ('single candidate report' if h['src'] else 'practice scenario', esc(h['title']), esc(h['scenario'])), kicker='LinkedIn-style hypothetical')
    dlib.seg(qs, 0, ('Scenario %d, from a single candidate report, so treat it as a preparation signal, not a promise. ' if h['src'] else 'Scenario %d, a practice scenario. ') % n + '%s Your turn: what would you consider, who are the stakeholders, which metrics decide it, what do you decide, and how do you roll it out and back?' % h['scenario'])
    E.seg(qs, 1, '', kind='think', think=think)
    def blk(label, body, kind, st):
        return '<div class="ab k-%s" data-step="%d"><div class="abl">%s</div><div class="abb">%s</div></div>' % (kind, st, label, body)
    left = ('<p style="margin:0 0 6px"><b>Consider:</b> %s</p><p style="margin:0 0 6px"><b>Stakeholders:</b> %s</p><p style="margin:0 0 6px"><b>Metrics:</b> %s</p>'
            '<p style="margin:0"><b>Trade-offs:</b> %s</p>' % (esc(' · '.join(h['consider'])), esc(', '.join(h['stakeholders'])), esc(', '.join(h['metrics'])), esc(', '.join(h['tradeoffs']))))
    right = ('<p style="margin:0 0 6px"><b>Decision:</b> %s</p><p style="margin:0 0 6px"><b>Rollout:</b> %s</p><p style="margin:0"><b>Rollback:</b> %s</p>'
             % (esc(h['decision']), esc(h['rollout']), esc(h['rollback'])))
    a = E.new_slide('<div class="qmini">%s</div><div class="ablocks">%s%s</div>' % (esc(h['title']), blk('What to weigh', left, 'dp', 0), blk('What to decide', right, 'ok', 1)),
                    kicker='Model response')
    dlib.seg(a, 0, 'What I would weigh. ' + ' '.join(c.rstrip('?.') + '?' for c in h['consider']) + ' The stakeholders: ' + ', '.join(h['stakeholders']) +
             '. The metrics that decide it: ' + ', '.join(h['metrics']) + '. And the trade-off: ' + ', '.join(h['tradeoffs']) + '.')
    dlib.seg(a, 1, 'The decision. ' + h['decision'] + ' Rollout: ' + h['rollout'] + ' Rollback: ' + h['rollback'])
    if h['fu']:
        fq, fa = h['fu'][0]
        f = E.new_slide('<div class="qwrap"><div class="qlabel">Follow-up</div><div class="qtext" style="font-size:50px">&ldquo;%s&rdquo;</div>'
                        '<div class="think" data-step="1"><div class="thinkl">Answer it.</div><div class="thinkbar"><i></i></div><div class="thinkc"></div></div>'
                        '<div class="qsub" data-step="2">%s</div></div>' % (esc(fq), esc(fa)), kicker='Follow-up')
        dlib.seg(f, 0, 'The follow-up: ' + fq)
        E.seg(f, 1, '', kind='think', think=12)
        dlib.seg(f, 2, fa)


def close(l):
    section('Close')
    if l['mistakes']:
        bullets('Common mistakes', l['mistakes'], 'The common mistakes. ' + ' '.join(m.rstrip('.') + '.' for m in l['mistakes']), 'Avoid')
    if l['signal']:
        sid = dlib.statement('The Staff-level signal', l['signal'], None, kind='ok', kicker='Signal')
        dlib.seg(sid, 0, 'The Staff-level signal in this lesson: ' + l['signal'])
    if l['takeaways']:
        bullets('Key takeaways', l['takeaways'], 'To take away. ' + ' '.join(t.rstrip('.') + '.' for t in l['takeaways']), 'Takeaways')


# ---------------------------------------------------------------- lessons
def build(lesson_id):
    l = [x for x in C.ALL if x['id'] == lesson_id][0]
    if l['id'] == C.REVISION['id']:
        return build_revision(l)
    section('Objective')
    sid = header(l)
    dlib.seg(sid, 0, 'Video %d. %s. %s' % (int(l['num']), l['title'], l['objective']))
    if l['concept']:
        section('Concept')
        for title, items, narr in l['concept']:
            bullets(title, items, narr, 'Concept')
        if l['chain']:
            model_chain(l['chain'])
    if l['example']:
        section('My personal example')
        t, items, narr = l['example']
        bullets('My example · ' + t, items, narr, 'My personal example')
        if has_story(*items) or has_input(*items):
            sid = dlib.statement('Before you use this example', 'Gold = a practice story constructed for you: confirm it is true. Red = only you can supply it.',
                                 None, kind='shared', kicker='Honesty')
            dlib.seg(sid, 0, 'A quick honesty check on that example. Anything marked as a practice story was constructed to help you rehearse, and you did not supply it. '
                              'Confirm it is true before you say it, or replace it with what really happened. Anything marked as your facts, only you can fill in.')
    if l['questions']:
        section('Interview mode')
        mock = l['id'].endswith('full-mock')
        leads = ['', 'Following up on that,', 'They keep drilling:', 'Next,', 'Then,', 'And then,'] if mock else ['']
        for i, qid in enumerate(l['questions']):
            if qid.startswith('scn:'):
                scenario(qid[4:], i + 1)
            else:
                interview(qid, i + 1, think=25, brief=mock, lead=leads[min(i, len(leads) - 1)] if mock and i else '')
    close(l)


def build_revision(l):
    section('Revision')
    sid = header(l)
    dlib.seg(sid, 0, 'This is the final revision. Watch it the evening before and the morning of. We go through who you are as a Staff engineer, your stories, and every high-priority question, '
                      'with a short pause to say your first sentence.')
    P = D.POSITIONING
    sid = dlib.statement('Your positioning', P['one_line'], P['archetype'][0], kind='ok', kicker='Who you are')
    dlib.seg(sid, 0, 'Your positioning, in one line. ' + P['one_line'] + ' Archetype: ' + P['archetype'][0] + '.')
    bullets('Tell me about yourself · 90 seconds', D.TMAY['90 seconds'], ' '.join(D.TMAY['90 seconds']), 'Opening')
    bullets('Address these before they become doubts', [r[0] for r in D.RISKS],
            'Five things a Host Manager will notice in your resume. ' + ' '.join('%s. %s' % (r[0], r[1]) for r in D.RISKS) +
            ' Have one calm, precise sentence ready for each, in your own words.', 'Risks')
    bullets('The core stories', [s['title'] for s in D.STORIES[:8]],
            'Your core stories. ' + '. '.join(s['title'] for s in D.STORIES[:8]) + '. Remember: the stories marked as practice stories need confirming, '
            'and the failure and mentoring stories still need your real examples.', 'Story bank')
    section('Top questions')
    for i, qid in enumerate(l['questions']):
        q = QBY[qid]
        s = E.new_slide('<div class="qwrap"><div class="qlabel">%d / %d &middot; %s</div><div class="qtext" style="font-size:50px">&ldquo;%s&rdquo;</div>'
                        '<div class="think" data-step="1"><div class="thinkl">Say your first sentence.</div><div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>'
                        % (i + 1, len(l['questions']), esc(q['cat']), esc(q['q'])), kicker='Final revision')
        dlib.seg(s, 0, 'Question %d. %s' % (i + 1, q['q']))
        E.seg(s, 1, '', kind='think', think=10)
        body = ('<div class="ab k-ok" data-step="0"><div class="abl">Open with</div><div class="abb"><p style="margin:0 0 8px">&ldquo;%s&rdquo;</p><ul>%s</ul></div></div>'
                '<div class="ab k-dp" data-step="1"><div class="abl">The Staff answer</div><div class="abb">%s</div></div>'
                % (screen(q['opener']), ''.join('<li>%s</li>' % screen(a) for a in q['anchors']), screen(q['staff'])))
        a = E.new_slide('<div class="qmini">&ldquo;%s&rdquo;</div><div class="ablocks">%s</div>' % (esc(q['q']), body), kicker='Final revision')
        dlib.seg(a, 0, 'Open with: ' + speak(q['opener']) + ' Anchors: ' + ' '.join(speak(x).rstrip('.') + '.' for x in q['anchors']))
        dlib.seg(a, 1, 'The Staff answer: ' + speak(q['staff']))
        if q['fu']:
            fq, fa = q['fu'][0]
            f = E.new_slide('<div class="qwrap"><div class="qlabel">Likely follow-up</div><div class="qtext" style="font-size:46px">&ldquo;%s&rdquo;</div>'
                            '<div class="qsub" data-step="1">%s</div></div>' % (esc(speak(fq)), screen(fa)), kicker='Final revision')
            dlib.seg(f, 0, 'Likely follow-up: ' + speak(fq))
            dlib.seg(f, 1, speak(fa) or 'Answer that one with your own facts.')
    section('Close')
    rows = [(a, b) for a, b in D.RED_FLAGS[:6]]
    dlib.cheatsheet('What not to say, and what to say instead', rows,
                    ['What not to say. ' + ' '.join('Instead of %s, say %s.' % (speak(a), speak(b)) for a, b in rows)])
    bullets('Questions to ask the Host Manager', [a for a, b in D.ASK_HM[:5]],
            'Your questions for them. ' + ' '.join(a for a, b in D.ASK_HM[:5]) + ' And when they answer, connect it to your experience in one sentence.', 'Your questions')
    bullets('Final checklist', D.CHECKLIST[:9], 'The final checklist. ' + ' '.join(D.CHECKLIST[:9]), 'Checklist')
    bullets('Final checklist, continued', D.CHECKLIST[9:], ' '.join(D.CHECKLIST[9:]) +
            ' The question underneath all of it: why should this Host Manager trust you to operate as a Staff engineer? You have the evidence. Say it plainly. Good luck.', 'Checklist')
