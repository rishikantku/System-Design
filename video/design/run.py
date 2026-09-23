# -*- coding: utf-8 -*-
"""Per-lesson pipeline for the LinkedIn coding course.

    python3 run.py plan  [ids]     # build deck.html + plan.json per lesson
    python3 run.py render [ids]    # render frames (parallel browsers)
    python3 run.py encode [ids]    # TTS + encode one mp4 per lesson
    python3 run.py all    [ids]

Each lesson lands in build-design/<id>/ with its own frames, audio, segments
and a single .mp4 plus .srt. Nothing is concatenated across lessons: the point
is that you can watch one pattern in 20 minutes.
"""
import importlib, io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'src')
OUT = os.path.abspath(os.path.join(HERE, '..', 'build-design'))
sys.path.insert(0, HERE); sys.path.insert(0, SRC)

import index as COURSE          # lesson registry


def lesson_ids(argv):
    if len(argv) > 2:
        wanted = argv[2].split(',')
        return [l for l in COURSE.LESSONS if l['id'] in wanted or l['chapter'] in wanted]
    return COURSE.LESSONS


def build_plan(lesson):
    """Fresh engine per lesson, then write deck.html + plan.json into its own folder."""
    for mod in list(sys.modules):
        if mod == 'engine' or mod.startswith('lessons.') or mod == 'lib':
            del sys.modules[mod]
    import engine as E
    importlib.import_module('lib')
    importlib.import_module('lessons.' + lesson['module'])

    out = os.path.join(OUT, lesson['id'])
    os.makedirs(out, exist_ok=True)
    css = io.open(os.path.join(SRC, 'style.css'), encoding='utf-8').read()
    slides = '\n'.join(h for _, h in E.SLIDES)

    plan, prev = [], None
    N = len(E.SEGMENTS)
    for i, s in enumerate(E.SEGMENTS):
        prog = i / max(1, N - 1)
        base = dict(slide=s['slide'], step=s['step'], prog=prog)
        frames = []
        is_new_slide = prev is None or prev['slide'] != s['slide']
        if s['kind'] == 'chapter':
            for k in range(1, 13):
                frames.append(dict(base, f='g%04d_%02d' % (i, k), p=1, black=k / 12))
        elif is_new_slide:
            for k in range(1, 9):
                frames.append(dict(base, f='g%04d_%02d' % (i, k), p=1, fade=k / 8,
                                   prev=prev['slide'] if prev else None,
                                   prevStep=prev['step'] if prev else 0))
        elif s['step'] != (prev['step'] if prev else -1):
            for k in range(1, 8):
                frames.append(dict(base, f='g%04d_%02d' % (i, k), p=k / 7))
        if s['kind'] == 'think':
            secs = s['think']
            for k in range(int(secs * 4) + 1):
                t = k / max(1, secs * 4)
                frames.append(dict(base, f='g%04d_t%03d' % (i, k), p=1, think=t,
                                   cd=max(0, secs - k // 4)))
        if s.get('travel'):
            tr = s['travel']
            pts = tr['points']
            total = tr['frames']
            for k in range(total):
                f = k / max(1, total - 1)
                x, y = _lerp(pts, f)
                frames.append(dict(base, f='g%04d_p%02d' % (i, k), p=1, pkt=[x, y, tr['kind']]))
        hold = dict(base, p=1, f='g%04d_hold' % i)
        if s['kind'] == 'think' and frames: hold = dict(frames[-1], f='g%04d_hold' % i)
        if s.get('travel') and frames: hold['pkt'] = frames[-1]['pkt']
        plan.append(dict(seg=i, frames=frames, hold=hold, kind=s['kind'], think=s['think'],
                         narr=s['narr'], tail=s.get('tail')))
        prev = s

    doc = ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s'
           '<script type="application/json" id="plan">%s</script></body></html>') % (
        css, slides, json.dumps([dict(frames=p['frames'], hold=p['hold']) for p in plan]))
    io.open(os.path.join(out, 'deck.html'), 'w', encoding='utf-8').write(doc)
    io.open(os.path.join(out, 'plan.json'), 'w', encoding='utf-8').write(
        json.dumps(dict(plan=plan, chapters=E.CHAPTERS, fps=E.FPS)))

    words = sum(len(p['narr'].split()) for p in plan)
    frames_n = sum(len(p['frames']) + 1 for p in plan)
    return dict(id=lesson['id'], slides=len(E.SLIDES), segs=N, frames=frames_n, words=words,
                mins=round(words / 165 + sum(p['think'] for p in plan) / 60, 1))


def _lerp(pts, f):
    import math
    segs = list(zip(pts, pts[1:]))
    total = sum(math.dist(a, b) for a, b in segs) or 1
    t = total * f
    for a, b in segs:
        d = math.dist(a, b)
        if t <= d or (a, b) == segs[-1]:
            r = t / d if d else 0
            return [round(a[0] + (b[0] - a[0]) * r), round(a[1] + (b[1] - a[1]) * r)]
        t -= d
    return list(pts[-1])


def render(lesson, force=False):
    out = os.path.join(OUT, lesson['id'])
    frames = os.path.join(out, 'frames')
    os.makedirs(frames, exist_ok=True)
    n = len(json.load(io.open(os.path.join(out, 'plan.json')))['plan'])
    url = 'file://%s/deck.html#from=0&to=%d&out=%s%s' % (out, n, frames, '&force=1' if force else '')
    cmd = ['node', os.path.expanduser('~/.codegpt/skills/browser-automation/browser.mjs'), url,
           '--script', os.path.join(SRC, 'render.mjs'), '--timeout', '3600000']
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = '"shots"' in r.stdout
    return ok, len(os.listdir(frames))


def encode(lesson):
    out = os.path.join(OUT, lesson['id'])
    env = dict(os.environ, BUILD=out, OUTNAME=lesson['file'], TTS='sarvam',
               SARVAM_SPEAKER=os.environ.get('SARVAM_SPEAKER', 'ritu'), JOBS='6')
    r = subprocess.run([sys.executable, os.path.join(SRC, 'encode.py')], env=env,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout.strip().split('\n') or [''])[0], r.stderr[-400:]


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'plan'
    todo = lesson_ids(sys.argv)
    print('%d lesson(s): %s' % (len(todo), ', '.join(l['id'] for l in todo)))
    for l in todo:
        if what in ('plan', 'all'):
            info = build_plan(l)
            print('  plan   %-22s %3d slides %3d segs %5d frames %5d words ~%s min'
                  % (info['id'], info['slides'], info['segs'], info['frames'], info['words'], info['mins']))
        if what in ('render', 'all'):
            ok, n = render(l)
            print('  render %-22s %s (%d frames)' % (l['id'], 'ok' if ok else 'FAILED', n))
        if what in ('encode', 'all'):
            ok, line, err = encode(l)
            print('  encode %-22s %s %s' % (l['id'], 'ok' if ok else 'FAILED', line or err))
