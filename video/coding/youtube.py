# -*- coding: utf-8 -*-
"""Generate the YouTube upload pack for the coding course.

Everything here is derived from the build output, never written by hand:
  - runtime and chapter timestamps come from the encoded segment durations (ffprobe)
  - chapter titles come from the slide headings in each lesson's deck.html
  - relevance/evidence lines come from index.py

    python3 youtube.py            -> writes ../build-coding/_youtube/
"""
import os, re, json, subprocess, html, importlib.util, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, '..', 'build-coding'))
OUT = os.path.join(BUILD, '_youtube')

spec = importlib.util.spec_from_file_location('course_index', os.path.join(HERE, 'index.py'))
IDX = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDX)

COURSE = 'LinkedIn Staff Coding Interview Prep'
BASE_TAGS = ['linkedin interview', 'staff engineer interview', 'coding interview',
             'system design prep', 'data structures and algorithms', 'c# interview',
             'leetcode linkedin', 'technical interview preparation']


def ffdur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def slide_titles(deck_path):
    """slide id -> heading text, from the rendered deck."""
    h = open(deck_path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'<section class="slide[^"]*" id="(s\d+)"(.*?)(?=<section class="slide|\Z)', h, re.S):
        sid, body = m.group(1), m.group(2)
        t = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.S)
        if not t:
            t = re.search(r'<div class="(?:chaptitle|lh-t|stbig|qlabel)"[^>]*>(.*?)</div>', body, re.S)
        if t:
            txt = re.sub(r'<[^>]+>', '', t.group(1))
            for _ in range(3):                       # rich() escapes '&', so entities arrive doubled
                un = html.unescape(txt)
                if un == txt:
                    break
                txt = un
            txt = txt.replace('*', '').replace('\u2014', '-').strip(' .')
            out[sid] = re.sub(r'\s+', ' ', txt)
    return out


def stamp(sec):
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return ('%d:%02d:%02d' % (h, m, s)) if h else ('%d:%02d' % (m, s))


def chapters_for(lesson):
    """[(seconds, title)] — one entry per slide whose heading changes, ≥10 s apart."""
    d = os.path.join(BUILD, lesson['id'])
    plan = json.load(open(os.path.join(d, 'plan.json')))['plan']
    titles = slide_titles(os.path.join(d, 'deck.html'))
    concat = os.path.join(d, 'concat.txt')          # authoritative order; segs/ keeps stale hashes
    segs = [re.match(r"file '(.+)'", l).group(1)
            for l in open(concat, encoding='utf-8') if l.startswith('file ')]
    if len(segs) != len(plan):
        return [], 0.0

    marks, t, last = [], 0.0, None
    for i, entry in enumerate(plan):
        sid = entry['frames'][0]['slide'] if entry['frames'] else None
        title = titles.get(sid)
        if title in ('Interviewer', 'The interviewer asks'):
            title = 'Pause and think'
        elif title and re.fullmatch(r'Lesson [\d.R]+', title):
            title = 'Takeaway'
        if title and title != last:
            marks.append([t, title])
            last = title
        t += ffdur(segs[i])

    # YouTube: first chapter at 0:00, each at least 10 s long
    merged = []
    for m in marks:
        if merged and m[0] - merged[-1][0] < 10:
            continue
        merged.append(m)
    if merged:
        merged[0][0] = 0.0
    return merged, t


def describe(lesson, chapters, runtime):
    ch = IDX.CHAPTERS[lesson['chapter']]
    ev = lesson['reports']
    lines = []
    num = re.search(r'LinkedIn-Coding-([\d.R]+)-', lesson['file'])
    num = num.group(1) if num else ''
    lines.append('Lesson %s of the %s course.' % (num, COURSE))
    lines.append('')
    if lesson['relevance'] not in ('—', ''):
        lines.append('LinkedIn relevance: %s  ·  Evidence: %s  ·  Latest report: %s  ·  Confidence: %s'
                     % (lesson['relevance'], ev, lesson['latest'], lesson['confidence']))
        lines.append('')
    lines.append('Pattern: %s' % lesson['pattern'])
    lines.append('Runtime: %s  ·  All code in C#' % stamp(runtime))
    lines.append('')
    lines.append('This lesson follows the same structure as every other one: the question as an interviewer poses it, '
                 'how to think about it, the naive answer and why it is not enough, the key observation, the optimal '
                 'approach and why it works, a visual walkthrough, edge cases, the C# code line by line, complexity, '
                 'and the follow-ups — reported ones kept separate from likely staff-level ones.')
    lines.append('')
    lines.append('There are pause-and-think points. Use them — the reasoning is the point, not the solution.')
    lines.append('')
    lines.append('CHAPTERS')
    for t, title in chapters:
        lines.append('%s %s' % (stamp(t), title))
    lines.append('')
    lines.append('ABOUT THIS CHAPTER')
    lines.append(re.sub(r'\s+', ' ', ch['why']))
    lines.append('')
    lines.append('A note on evidence: questions are marked by what is actually reported by candidates or supplied '
                 'first-hand, separately from general preparation topics. Nothing here claims any question is '
                 'guaranteed to appear in your interview.')
    return '\n'.join(lines)


def tags_for(lesson):
    t = list(BASE_TAGS)
    for word in re.split(r'[·,]', lesson['pattern']):
        word = word.strip().lower()
        if word:
            t.append(word)
    t.append(lesson['title'].split('—')[0].strip().lower())
    seen, out = set(), []
    for x in t:
        if x not in seen and len(x) <= 30:
            seen.add(x); out.append(x)
    return out[:15]


def main():
    os.makedirs(OUT, exist_ok=True)
    built, total = [], 0.0
    index_lines = ['# %s — upload order\n' % COURSE]

    for n, lesson in enumerate(IDX.LESSONS, 1):
        d = os.path.join(BUILD, lesson['id'])
        mp4 = os.path.join(d, lesson['file'] + '.mp4')
        if not os.path.exists(mp4):
            index_lines.append('%2d. [NOT BUILT] %s' % (n, lesson['title']))
            continue

        chapters, runtime = chapters_for(lesson)
        total += runtime
        title = '%s | %s' % (lesson['title'], COURSE)
        if len(title) > 100:
            title = lesson['title'][:100]

        body = ['TITLE', title, '', 'DESCRIPTION', describe(lesson, chapters, runtime), '',
                'TAGS', ', '.join(tags_for(lesson)), '',
                'FILE', mp4, '',
                'SUBTITLES', os.path.join(d, lesson['file'] + '.srt')]
        with open(os.path.join(OUT, '%02d-%s.txt' % (n, lesson['id'])), 'w', encoding='utf-8') as f:
            f.write('\n'.join(body) + '\n')

        built.append((n, lesson, runtime, len(chapters)))
        index_lines.append('%2d. %-52s %6s  %2d chapters  %s'
                           % (n, lesson['title'][:52], stamp(runtime), len(chapters), lesson['file'] + '.mp4'))

    # playlist description
    by_ch = {}
    for n, lesson, runtime, _ in built:
        by_ch.setdefault(lesson['chapter'], []).append((n, lesson, runtime))

    p = []
    p.append('%s — %d lessons, %s total.' % (COURSE, len(built), stamp(total)))
    p.append('')
    p.append('A complete coding-round course built from what LinkedIn candidates have actually reported being asked, '
             'plus the official Staff onsite preparation pack. One short video per pattern, so a topic you are shaky '
             'on costs you fifteen minutes, not an afternoon. Every solution is in C#.')
    p.append('')
    p.append('Each lesson runs the same structure: the question as posed, how to think about it, the naive answer and '
             'why it falls short, the key observation, the optimal approach, a visual walkthrough, edge cases, the '
             'code line by line, complexity, and the follow-ups — with reported follow-ups kept separate from likely '
             'staff-level ones. Every chapter ends with a recap: pattern summary, recognition checklist, common '
             'mistakes, C# templates, the reported questions ranked, a five-minute revision and a mini mock.')
    p.append('')
    p.append('CONTENTS')
    for cid, ch in IDX.CHAPTERS.items():
        rows = by_ch.get(cid, [])
        if not rows:
            continue
        p.append('')
        p.append('Chapter %d — %s (%s)' % (ch['num'], ch['title'], stamp(sum(r[2] for r in rows))))
        for n, lesson, runtime in rows:
            p.append('  %2d. %s (%s)' % (n, lesson['title'], stamp(runtime)))
    p.append('')
    p.append('ON EVIDENCE')
    p.append('Each lesson header states how strong the evidence is that LinkedIn asks that question: whether it was '
             'reported first-hand, how recently, and how confident that makes it. General preparation topics are '
             'labelled as such. No question is ever presented as guaranteed to appear.')
    with open(os.path.join(OUT, '00-playlist.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(p) + '\n')

    with open(os.path.join(OUT, '00-upload-order.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(index_lines) + '\n\nTotal: %s across %d videos\n' % (stamp(total), len(built)))

    print('wrote %d lesson packs + playlist to %s' % (len(built), OUT))
    print('total runtime %s' % stamp(total))


if __name__ == '__main__':
    main()
