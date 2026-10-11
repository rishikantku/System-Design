# -*- coding: utf-8 -*-
"""LinkedIn system design course: join the per-lesson MP4s into three part-films, by chapter.

    python3 combine.py            -> ../build-design/_upload/

Each part gets chapter markers (one per lesson), a merged .srt and a chapters.txt for a
description. Lessons are concatenated with -c copy (no re-encode); the script refuses if
stream parameters differ. Lessons without an MP4 yet are skipped and listed, so re-running
after they are encoded simply produces longer parts.
"""
import os, re, sys, subprocess, html

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, '..', 'build-design'))
OUT = os.path.join(BUILD, '_upload')
sys.path.insert(0, HERE)
import index as I

PARTS = [
    ('LinkedIn-Design-Part-1-Method-and-Core-Questions', 'Part 1 - Method and the core LinkedIn questions', ['m1', 'm2', 'm3']),
    ('LinkedIn-Design-Part-2-Control-Retrieval-Storage-and-Delivery', 'Part 2 - Distributed control, retrieval, storage and delivery', ['m4', 'm5', 'm6', 'm7']),
    ('LinkedIn-Design-Part-3-Stateful-Intelligence-Patterns-and-Recent', 'Part 3 - Stateful systems, intelligence, patterns and recent reports', ['m8', 'm9', 'm10', 'm11']),
]


def probe(path, entries):
    return subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entries, '-of', 'default=nw=1:nk=1', path],
                          capture_output=True, text=True).stdout.strip()

def duration(p): return float(probe(p, 'format=duration') or 0)

def stamp(sec, srt=False):
    sec = max(0.0, sec); h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return '%02d:%02d:%02d,%03d' % (h, m, int(s), round((s - int(s)) * 1000)) if srt else '%d:%02d:%02d' % (h, m, int(s))

SRT_TIME = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)')

def shift_srt(path, offset, n):
    if not os.path.exists(path): return '', n
    to_s = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    out = []
    for block in re.split(r'\n\s*\n', open(path, encoding='utf-8').read().strip()):
        lines = block.strip().split('\n'); m = SRT_TIME.search(block)
        if len(lines) < 2 or not m: continue
        a = to_s(*m.group(1, 2, 3, 4)) + offset; b = to_s(*m.group(5, 6, 7, 8)) + offset
        text = '\n'.join(lines[2:]) if lines[0].strip().isdigit() else '\n'.join(lines[1:])
        out.append('%d\n%s --> %s\n%s' % (n, stamp(a, True), stamp(b, True), text)); n += 1
    return '\n\n'.join(out), n

def lesson_title(l):
    ch = I.CHAPTERS[l['chapter']]['num']
    num = l['file'].split('-')[2] if l['file'].count('-') >= 2 else str(ch)
    return '%s %s' % (num, html.unescape(re.sub('<[^>]+>', '', l['title'])))


def build_part(name, title, chapters):
    have, missing = [], []
    for l in I.LESSONS:
        if l['chapter'] not in chapters: continue
        mp4 = os.path.join(BUILD, l['id'], l['file'] + '.mp4')
        (have if os.path.exists(mp4) else missing).append((l, mp4))
    for l, _ in missing: print('  skip (no MP4 yet): %s' % lesson_title(l))
    if not have: print('  nothing built for %s' % name); return None

    sigs = {probe(m, 'stream=codec_name,width,height,r_frame_rate,sample_rate,channels') for _, m in have}
    if len(sigs) != 1: sys.exit('stream parameters differ; copy-concat unsafe:\n  ' + '\n  '.join(sigs))

    marks, t = [], 0.0
    for l, mp4 in have:
        d = duration(mp4); marks.append((t, l, d, mp4)); t += d

    lst = os.path.join(OUT, name + '.concat.txt'); meta = os.path.join(OUT, name + '.ffmeta')
    with open(lst, 'w', encoding='utf-8') as f:
        for *_, mp4 in marks: f.write("file '%s'\n" % mp4.replace("'", r"'\''"))
    with open(meta, 'w', encoding='utf-8') as f:
        f.write(';FFMETADATA1\ntitle=LinkedIn System Design - %s\n' % title)
        for s, l, d, _ in marks:
            f.write('[CHAPTER]\nTIMEBASE=1/1000\nSTART=%d\nEND=%d\ntitle=%s\n'
                    % (round(s * 1000), round((s + d) * 1000), lesson_title(l).replace('=', '-').replace(';', ',')))

    out = os.path.join(OUT, name + '.mp4')
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', meta,
                        '-map_metadata', '1', '-c', 'copy', '-movflags', '+faststart', out])
    if r.returncode: sys.exit('ffmpeg failed on ' + name)

    parts, n = [], 1
    for s, l, d, mp4 in marks:
        chunk, n = shift_srt(mp4[:-4] + '.srt', s, n)
        if chunk: parts.append(chunk)
    if parts: open(os.path.join(OUT, name + '.srt'), 'w', encoding='utf-8').write('\n\n'.join(parts) + '\n')
    with open(os.path.join(OUT, name + '-chapters.txt'), 'w', encoding='utf-8') as f:
        f.write('LinkedIn System Design - %s (%s, %d lessons)\n\n' % (title, stamp(t), len(marks)))
        for s, l, *_ in marks: f.write('%s %s\n' % (stamp(s), lesson_title(l)))
    for p in (lst, meta): os.remove(p)

    actual = duration(out)
    print('  %s  %s  %.0f MB  %d chapters  drift %.2fs' % (os.path.basename(out), stamp(actual),
          os.path.getsize(out) / 1e6, len(marks), abs(actual - t)))
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, title, chs in PARTS:
        print(title); build_part(name, title, chs)
