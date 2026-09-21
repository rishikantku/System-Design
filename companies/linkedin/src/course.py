# -*- coding: utf-8 -*-
"""06-coding-course.html — index for the video coding course.

Reads the lesson registry straight out of video/coding/index.py so the page can never
drift from what has actually been built. A lesson shows as READY once its MP4 exists.
"""
import os, sys, importlib.util, datetime
import lib
from lib import esc, rich, card, sec, note, table, grid, acc, titled

VIDEO = os.path.abspath(os.path.join(lib.OUT, '..', '..', 'video', 'coding'))
BUILD = os.path.abspath(os.path.join(lib.OUT, '..', '..', 'video', 'build-coding'))


def _registry():
    spec = importlib.util.spec_from_file_location('course_index', os.path.join(VIDEO, 'index.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _video(lesson):
    """(href, size_mb, minutes) for a built lesson, or None."""
    d = os.path.join(BUILD, lesson['id'])
    mp4 = os.path.join(d, lesson['file'] + '.mp4')
    if not os.path.exists(mp4):
        return None
    rel = os.path.relpath(mp4, lib.OUT).replace(os.sep, '/')
    srt = lesson['file'] + '.srt'
    has_srt = os.path.exists(os.path.join(d, srt))
    return dict(href=rel, mb=round(os.path.getsize(mp4) / 1e6),
                srt=os.path.relpath(os.path.join(d, srt), lib.OUT).replace(os.sep, '/') if has_srt else None)


def _rawtable(headers, rows, cls=''):
    """lib.table() escapes cell HTML through rich(); these cells are already markup."""
    th = ''.join('<th>%s</th>' % esc(x) for x in headers)
    tr = ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>' for r in rows)
    return ('<div class="tw"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (cls, th, tr))


def build():
    reg = _registry()
    lessons, chapters, planned = reg.LESSONS, reg.CHAPTERS, reg.PLANNED

    ready = [l for l in lessons if _video(l)]
    total_mins = sum(l['mins'] for l in lessons)

    # ------------------------------------------------------------------ how to use
    body = [sec('how', 'How to use this course',
        card(rich(
          'Every lesson is **its own video**, twelve to eighteen minutes. That is deliberate: a pattern you are shaky on '
          'should cost you one lesson to revise, not a scrub bar through a five-hour file.\n\n'
          'Each lesson runs the same eighteen beats — the question as an interviewer poses it, the interview context, how to '
          'think about it, the naive answer, why the naive answer is not good enough, the key observation, the optimal '
          'approach, why it works, a visual walkthrough, a worked example, edge cases, the C# code, a line-by-line walk of '
          'that code, time, space, follow-ups, how the interviewer may modify the question, and how to respond.\n\n'
          'There are **pause-and-think points** in every lesson. Use them. The video waits; an interviewer does not, and the '
          'only way to build the reflex is to do the thinking before you hear the answer.') ) +
        note(rich('**Chapter order is driven by the research, not by a textbook.** Trees come before graphs because trees are '
                  'the biggest reported cluster. Nothing here claims a question is guaranteed to appear — the relevance '
                  'header on each lesson tells you exactly what the evidence is.'), kind='warn', label='Read this first'),
        kicker='Video course',
        why='Short, single-pattern videos you can revise from the night before.')]

    # ------------------------------------------------------------------ chapters
    for cid, ch in chapters.items():
        rows = []
        for l in [x for x in lessons if x['chapter'] == cid]:
            v = _video(l)
            if v:
                link = '<a href="%s">▶ Watch</a>' % v['href']
                if v['srt']:
                    link += ' &nbsp;<a href="%s" class="dim">SRT</a>' % v['srt']
                link += ' <span class="dim">%d MB</span>' % v['mb']
            else:
                link = '<span class="dim">not built yet</span>'
            rel = l['relevance']
            relc = {'Highest': 'hi', 'High': 'hi', 'Medium': 'med', 'Lower': 'low'}.get(rel, '')
            rows.append([
                '<b>%s</b><br><span class="dim">%s</span>' % (esc(l['title']), esc(l['pattern'])),
                '%s min' % l['mins'],
                (lib.tag(relc, rel) if relc else esc(rel)) +
                '<br><span class="dim">%s</span>' % esc(l['reports']),
                esc(l['confidence']),
                link,
            ])
        body.append(sec('ch%d' % ch['num'], 'Chapter %d · %s' % (ch['num'], ch['title']),
            note(rich(ch['why']), kind='', label='Why this chapter is here') +
            _rawtable(['Lesson', 'Runtime', 'LinkedIn relevance · evidence', 'Confidence', 'Video'],
                      rows, cls='t-course'),
            kicker='%d lessons' % len([x for x in lessons if x['chapter'] == cid])))

    # ------------------------------------------------------------------ what is coming
    prows = [['<b>Chapter %s · %s</b>' % (c.replace('c', ''), esc(t)), rich(w)] for c, t, w in planned]
    body.append(sec('planned', 'Chapters 4–10 — written next',
        _rawtable(['Chapter', 'Questions it covers'], prows, cls='t-planned') +
        note(rich('These follow the same eighteen-beat shape. Chapter 10 is the rapid revision pass plus a **full '
                  '50-minute mock**, timed, with the grading rubric supplied afterwards.'), kind=''),
        kicker='Backlog'))

    # ------------------------------------------------------------------ cross links
    body.append(sec('alongside', 'What to pair each lesson with',
        grid([
          card(rich('**Before a lesson** — read the matching item on <a href="01-coding.html">01 Staff Coding</a> and try the '
                    'problem cold for ten minutes. A lesson you have already struggled with teaches four times as much.'),
               title='The tracker'),
          card(rich('**After a lesson** — mark the item on 01 Staff Coding: solved, needs revision, slow, or needed a hint. '
                    'The dashboard readiness bar reads those marks, so the course and the tracker stay one system.'),
               title='Mark it'),
          card(rich('**For the evidence behind a relevance header** — <a href="05-research.html">05 Recent interview '
                    'research</a> has the source, the date and the role for every reported question, plus the ones that are '
                    'general preparation rather than reported.'), title='The research'),
        ], cols='g3'),
        kicker='Loop'))

    return lib.page('06-coding-course.html', 'Video coding course',
        '%d lessons across chapters 1–3 · about %d minutes · one video per pattern, narrated, C# throughout.' % (len(lessons), total_mins),
        ''.join(body), crumb_tail='Video coding course',
        hero_chips=[('done', '%d lessons built' % len(ready)),
                    ('', '%d lessons written' % len(lessons)),
                    ('', 'Chapters 1–3 of 10'),
                    ('', '~%d min' % total_mins)])
