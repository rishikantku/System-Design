# -*- coding: utf-8 -*-
"""Slide + segment engine for the Isolated Cloud interview course video.
Content modules call the helpers below; build.py turns the result into
deck.html (all slides) and a frame plan the renderer follows."""
import json, html as H, math

W, HGT = 1920, 1080
FPS = 25
KIND = {  # colour per component kind
 'cp':'#a78bfa', 'dp':'#2dd4bf', 'shared':'#fbbf24', 'com':'#94a3b8',
 'deny':'#f87171', 'ok':'#34d399', 'info':'#60a5fa', 'neutral':'#e2e8f0'}

BRAND = 'Isolated Cloud &middot; Staff interview prep'   # courses may override
SLIDES = []      # (id, chapter_label, html)
SEGMENTS = []    # dicts
CHAPTERS = []    # (title, first segment index)
_state = {'chapter': '', 'chapnum': 0, 'n': 0}

def esc(s): return H.escape(s, quote=False)
def rich(s):
    """**bold** and `mono` in short slide strings"""
    out = esc(s)
    import re
    out = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', out)
    out = re.sub(r'`(.+?)`', r'<code>\1</code>', out)
    return out

# ------------------------------------------------------------------ chapters
def chapter(num, title, subtitle, narration):
    _state['chapter'] = title; _state['chapnum'] = num
    sid = new_slide(f'''
      <div class="chapcard">
        <div class="chapnum">{"Chapter %d" % num if num else "Welcome"}</div>
        <div class="chaptitle">{rich(title)}</div>
        <div class="chapsub">{rich(subtitle)}</div>
      </div>''', cls='chapter')
    CHAPTERS.append((("%d. " % num if num else "") + title, len(SEGMENTS)))
    seg(sid, 0, narration, kind='chapter')
    return sid

def new_slide(inner, cls='', title=None, kicker=None):
    _state['n'] += 1
    sid = 's%03d' % _state['n']
    head = ''
    if title:
        k = kicker or _state['chapter']
        head = f'<div class="kicker">{esc(k)}</div><h1>{rich(title)}</h1>'
    foot = f'<div class="foot"><span>{esc(_state["chapter"])}</span><div class="prog"><i></i></div><span class="brand">{BRAND}</span></div>'
    SLIDES.append((sid, f'<section class="slide {cls}" id="{sid}">{head}<div class="stage">{inner}</div>{foot if cls!="chapter" else ""}</section>'))
    return sid

def seg(slide, step, narration, kind='say', travel=None, think=0, tail=None):
    SEGMENTS.append(dict(slide=slide, step=step, narr=narration.strip(), kind=kind,
                         travel=travel, think=think, tail=tail))

# ------------------------------------------------------------------ text layouts
def cards(title, items, cols=2, kicker=None, note=None):
    """items: list of (step, head, body, kind)"""
    cells = []
    for it in items:
        st, head, body = it[0], it[1], it[2]
        kind = it[3] if len(it) > 3 else 'info'
        cells.append(f'<div class="card k-{kind}" data-step="{st}"><div class="ch">{rich(head)}</div>'
                     + (f'<div class="cb">{rich(body)}</div>' if body else '') + '</div>')
    n = f'<div class="note" data-step="{note[0]}">{rich(note[1])}</div>' if note else ''
    return new_slide(f'<div class="cards c{cols}">{"".join(cells)}</div>{n}', title=title, kicker=kicker)

def compare(title, left, right, kicker=None):
    """left/right: (head, kind, step, [lines]) """
    def col(c):
        head, kind, st, lines = c
        li = ''.join(f'<li>{rich(x)}</li>' for x in lines)
        return f'<div class="cmp k-{kind}" data-step="{st}"><div class="cmph">{rich(head)}</div><ul>{li}</ul></div>'
    return new_slide(f'<div class="cmpwrap">{col(left)}{col(right)}</div>', title=title, kicker=kicker)

def table(title, headers, rows, widths=None, kicker=None):
    """rows: (step, [cells], rowkind or None)"""
    ws = widths or [100 // len(headers)] * len(headers)
    th = ''.join(f'<th style="width:{w}%">{rich(h)}</th>' for h, w in zip(headers, ws))
    trs = []
    for r in rows:
        st, cells = r[0], r[1]
        kinds = r[2] if len(r) > 2 and r[2] else [None] * len(cells)
        tds = ''.join(f'<td class="{("k-"+k) if k else ""}">{rich(c)}</td>' for c, k in zip(cells, kinds))
        trs.append(f'<tr data-step="{st}">{tds}</tr>')
    return new_slide(f'<table class="t"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>', title=title, kicker=kicker)

def statement(title, big, small=None, kind='info', kicker=None, steps=None):
    s2 = f'<div class="stsmall" data-step="{steps or 1}">{rich(small)}</div>' if small else ''
    return new_slide(f'<div class="statement k-{kind}"><div class="stbig">{rich(big)}</div>{s2}</div>', title=title, kicker=kicker)

def steps_list(title, items, kicker=None, numbered=True):
    """items: (step, text, kind)"""
    lis = []
    for i, it in enumerate(items, 1):
        st, text = it[0], it[1]; kind = it[2] if len(it) > 2 else 'info'
        num = f'<span class="sn">{i}</span>' if numbered else '<span class="sn dot"></span>'
        lis.append(f'<li class="k-{kind}" data-step="{st}">{num}<span>{rich(text)}</span></li>')
    return new_slide(f'<ol class="sl">{"".join(lis)}</ol>', title=title, kicker=kicker)

def quote_slide(label, text, kicker=None, sub=None):
    s = f'<div class="qsub" data-step="1">{rich(sub)}</div>' if sub else ''
    return new_slide(f'<div class="qwrap"><div class="qlabel">{esc(label)}</div><div class="qtext">&ldquo;{rich(text)}&rdquo;</div>{s}</div>', kicker=kicker, title=None)

# ------------------------------------------------------------------ interview question block
def question(q, think_secs, answer_short, why_strong, testing, followups, answer_long=None,
             deep=None, narr_q=None, narr=None, kicker=None):
    """Builds: question slide -> think pause -> answer slide revealed in parts.
    narr: dict keys short, long, deep, strong, testing, follow (spoken text)"""
    qs = new_slide(f'''<div class="qwrap"><div class="qlabel">The interviewer asks</div>
        <div class="qtext">&ldquo;{rich(q)}&rdquo;</div>
        <div class="think" data-step="1"><div class="thinkl">Pause the video or think it through</div>
        <div class="thinkbar"><i></i></div><div class="thinkc"></div></div></div>''', kicker=kicker)
    seg(qs, 0, narr_q or f"Here's the question. {q}")
    seg(qs, 1, '', kind='think', think=think_secs)
    blocks = []
    st = 0
    def blk(label, body, kind):
        nonlocal st
        blocks.append(f'<div class="ab k-{kind}" data-step="{st}"><div class="abl">{esc(label)}</div><div class="abb">{body}</div></div>')
        st += 1
    blk('30-second answer', rich(answer_short), 'ok')
    if answer_long: blk('60–90 second answer adds', rich(answer_long), 'info')
    if deep: blk('If they want the deep version', rich(deep), 'cp')
    blk('Why it lands', rich(why_strong), 'shared')
    blk('What they are really testing', rich(testing), 'dp')
    fl = ''.join(f'<li>{rich(f)}</li>' for f in followups)
    blk('Expect next', f'<ul>{fl}</ul>', 'deny')
    asl = new_slide(f'<div class="qmini">&ldquo;{rich(q)}&rdquo;</div><div class="ablocks">{"".join(blocks)}</div>', kicker=kicker or _state['chapter'])
    i = 0
    seg(asl, i, narr['short']); i += 1
    if answer_long: seg(asl, i, narr['long']); i += 1
    if deep: seg(asl, i, narr['deep']); i += 1
    seg(asl, i, narr['strong']); i += 1
    seg(asl, i, narr['testing']); i += 1
    seg(asl, i, narr['follow']); i += 1

# ------------------------------------------------------------------ diagrams
class Diagram:
    def __init__(self, title, kicker=None, height=860, top=0):
        self.title, self.kicker, self.hgt, self.top = title, kicker, height, top
        self.boxes, self.parts, self.arrows, self.paths = {}, [], [], {}
    def zone(self, x, y, w, h, label, kind='dp', step=0, dashed=True, hide=None):
        hs = f' data-hide="{hide}"' if hide is not None else ''
        self.parts.append(f'<div class="zone k-{kind}{" dashed" if dashed else ""}" data-step="{step}"{hs} style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><span class="zl">{rich(label)}</span></div>')
    def box(self, id, x, y, w, h, title, sub='', kind='dp', step=0, hl=None, dim=None, hide=None, small=False):
        self.boxes[id] = (x, y, w, h)
        a = f' data-hl="{hl}"' if hl is not None else ''
        a += f' data-dim="{dim}"' if dim is not None else ''
        a += f' data-hide="{hide}"' if hide is not None else ''
        self.parts.append(f'<div class="box k-{kind}{" small" if small else ""}" id="b-{id}" data-step="{step}"{a} style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
                          f'<div class="bt">{rich(title)}</div>' + (f'<div class="bs">{rich(sub).replace(chr(10), "<br>")}</div>' if sub else '') + '</div>')
    def label(self, x, y, text, kind='neutral', step=0, w=420, hide=None, size='m', align='left', hl=None):
        a = f' data-hide="{hide}"' if hide is not None else ''
        a += f' data-hl="{hl}"' if hl is not None else ''
        self.parts.append(f'<div class="dl k-{kind} sz-{size}" data-step="{step}"{a} style="left:{x}px;top:{y}px;width:{w}px;text-align:{align}">{rich(text).replace(chr(10), "<br>")}</div>')
    def anchor(self, id, side, off=0.5):
        x, y, w, h = self.boxes[id]
        return {'l': (x, y + h * off), 'r': (x + w, y + h * off), 't': (x + w * off, y), 'b': (x + w * off, y + h)}[side]
    def arrow(self, a, b, step=0, kind='neutral', label='', fs='r', ts='l', via=None, dashed=False, hl=None,
              hide=None, name=None, lpos=0.5, loff=(0, -16), fo=0.5, to=0.5):
        p1 = self.anchor(a, fs, fo) if isinstance(a, str) else a
        p2 = self.anchor(b, ts, to) if isinstance(b, str) else b
        pts = [p1] + (via or []) + [p2]
        if name: self.paths[name] = pts
        self.arrows.append((pts, step, kind, label, dashed, hl, hide, lpos, loff))
    def path_points(self, name): return self.paths[name]
    def build(self):
        svg = []
        for i, (pts, step, kind, label, dashed, hl, hide, lpos, loff) in enumerate(self.arrows):
            d = 'M ' + ' L '.join(f'{x:.0f} {y:.0f}' for x, y in pts)
            col = KIND[kind]
            a = f' data-hl="{hl}"' if hl is not None else ''
            a += f' data-hide="{hide}"' if hide is not None else ''
            dash = ' stroke-dasharray="12 10"' if dashed else ''
            g = f'<g class="arr" data-step="{step}"{a} style="--c:{col}"><path d="{d}" stroke="{col}" stroke-width="4" fill="none"{dash} marker-end="url(#ah-{kind})" stroke-linejoin="round"/>'
            if label:
                # label at fraction lpos along polyline length
                segs = list(zip(pts, pts[1:])); L = sum(math.dist(p, q) for p, q in segs); t = L * lpos
                for p, q in segs:
                    l = math.dist(p, q)
                    if t <= l or (p, q) == segs[-1]:
                        f = t / l if l else 0
                        mx, my = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f; break
                    t -= l
                g += f'<text x="{mx + loff[0]:.0f}" y="{my + loff[1]:.0f}" class="al" fill="{col}" text-anchor="middle">{esc(label)}</text>'
            svg.append(g + '</g>')
        markers = ''.join(f'<marker id="ah-{k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for k, c in KIND.items())
        inner = (f'<div class="diag" style="height:{self.hgt}px;margin-top:{self.top}px">'
                 f'<svg class="arrows" width="{W}" height="{self.hgt}"><defs>{markers}</defs>{"".join(svg)}</svg>'
                 + ''.join(self.parts) + '<div class="pkt"></div></div>')
        return new_slide(inner, title=self.title, kicker=self.kicker, cls='diagram')

# ------------------------------------------------------------------ travel helper
def travel(points, kind='shared', frames=22):
    """points in diagram coordinates; renderer offsets by the diagram's position"""
    return dict(points=points, kind=kind, frames=frames)
