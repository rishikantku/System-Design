# -*- coding: utf-8 -*-
import io, json, os, sys, importlib, subprocess, re, math
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'build')
sys.path.insert(0, HERE)
import engine as E

MODULES = sys.argv[1].split(',') if len(sys.argv) > 1 else None

def load_content():
    import content_index
    for m in (MODULES or content_index.ORDER):
        importlib.import_module(m)

def main():
    load_content()
    os.makedirs(OUT, exist_ok=True)
    css = io.open(os.path.join(HERE, 'style.css'), encoding='utf-8').read()
    slides = '\n'.join(h for _, h in E.SLIDES)
    # frame plan -----------------------------------------------------------
    plan = []
    N = len(E.SEGMENTS)
    prev = None
    for i, s in enumerate(E.SEGMENTS):
        prog = i / max(1, N - 1)
        base = dict(slide=s['slide'], step=s['step'], prog=prog)
        frames = []
        new_slide = prev is None or prev['slide'] != s['slide']
        if s['kind'] == 'chapter':
            for k in range(1, 13):
                frames.append(dict(base, p=1, black=k / 12))
        elif new_slide:
            for k in range(1, 9):
                frames.append(dict(base, p=1, prev=prev['slide'], prevStep=prev['step'], fade=k / 8))
        elif s['step'] != prev['step'] and s['kind'] != 'think':
            for k in range(1, 8):
                frames.append(dict(base, p=k / 7))
        tr = s.get('travel')
        if tr:
            pts = tr['points']; segs = list(zip(pts, pts[1:])); L = sum(math.dist(a, b) for a, b in segs)
            for k in range(1, tr['frames'] + 1):
                d = L * (k / tr['frames']); t = d
                for a, b in segs:
                    l = math.dist(a, b)
                    if t <= l or (a, b) == segs[-1]:
                        f = t / l if l else 0; x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f; break
                    t -= l
                frames.append(dict(base, p=1, pkt=[round(x), round(y), tr['kind']]))
        think = s['kind'] == 'think'
        if think:
            n = int(s['think'] * 4)
            for k in range(n + 1):
                frames.append(dict(base, p=1, think=k / n, cd=max(0, math.ceil(s['think'] - k / 4))))
        hold = dict(base, p=1)
        if tr: hold['pkt'] = frames[-1]['pkt']
        if think: hold = frames[-1]
        for j, f in enumerate(frames): f['f'] = 'g%04d_%03d' % (i, j)
        hold = dict(hold); hold['f'] = 'g%04d_hold' % i
        plan.append(dict(seg=i, frames=frames, hold=hold, kind=s['kind'], think=s['think'], narr=s['narr'],
                         tail=s['tail'], travel=bool(tr)))
        prev = s
    deck = f'''<!doctype html><html><head><meta charset="utf-8"><title>Isolated Cloud course deck</title>
<style>{css}</style></head><body>
{slides}
<script type="application/json" id="plan">{json.dumps([dict(frames=p['frames'], hold=p['hold']) for p in plan])}</script>
</body></html>'''
    io.open(os.path.join(OUT, 'deck.html'), 'w', encoding='utf-8').write(deck)
    json.dump(dict(plan=plan, chapters=E.CHAPTERS, fps=E.FPS), io.open(os.path.join(OUT, 'plan.json'), 'w', encoding='utf-8'))
    words = sum(len(p['narr'].split()) for p in plan)
    frames = sum(len(p['frames']) + 1 for p in plan)
    print(f"slides {len(E.SLIDES)} | segments {N} | frames {frames} | narration words {words} (~{words/170:.0f} min) | chapters {len(E.CHAPTERS)}")

if __name__ == '__main__':
    main()
