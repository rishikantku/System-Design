# -*- coding: utf-8 -*-
"""Join every built lesson into one film, with chapters and a merged subtitle track.

    python3 combine.py              -> ../build-coding/_full/

Every lesson came out of the same encoder, so the streams are byte-compatible and this
concatenates with -c copy: no re-encode, no generation loss, minutes rather than hours.
The script refuses to run if the parameters ever stop matching, because a copy-concat
across mismatched streams produces a file that plays for a while and then falls apart.

Outputs:
    LinkedIn-Staff-Coding-Full-Course.mp4   one file, chapter markers embedded
    LinkedIn-Staff-Coding-Full-Course.srt   all subtitles, timestamps shifted
    chapters.txt                            timestamps to paste into a description
"""
import os, re, subprocess, importlib.util, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, '..', 'build-coding'))
OUT = os.path.join(BUILD, '_full')
NAME = 'LinkedIn-Staff-Coding-Full-Course'

spec = importlib.util.spec_from_file_location('course_index', os.path.join(HERE, 'index.py'))
IDX = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDX)


def probe(path, entries):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entries,
                        '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True)
    return r.stdout.strip()


def duration(path):
    return float(probe(path, 'format=duration') or 0)


def signature(path):
    """The stream parameters that must match for a copy-concat to be safe."""
    return probe(path, 'stream=codec_name,width,height,r_frame_rate,sample_rate,channels')


def stamp(sec, srt=False):
    sec = max(0.0, sec)
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    if srt:
        return '%02d:%02d:%02d,%03d' % (h, m, int(s), round((s - int(s)) * 1000))
    return '%d:%02d:%02d' % (h, m, int(s))


SRT_TIME = re.compile(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)')


def shift_srt(path, offset, start_index):
    """Re-time one lesson's subtitles into the combined timeline."""
    if not os.path.exists(path):
        return '', start_index
    def to_s(h, m, s, ms):
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    blocks, n = [], start_index
    raw = open(path, encoding='utf-8').read().strip()
    for block in re.split(r'\n\s*\n', raw):
        lines = block.strip().split('\n')
        if len(lines) < 2:
            continue
        m = SRT_TIME.search(block)
        if not m:
            continue
        a = to_s(*m.group(1, 2, 3, 4)) + offset
        b = to_s(*m.group(5, 6, 7, 8)) + offset
        text = '\n'.join(lines[2:]) if lines[0].strip().isdigit() else '\n'.join(lines[1:])
        blocks.append('%d\n%s --> %s\n%s' % (n, stamp(a, True), stamp(b, True), text))
        n += 1
    return '\n\n'.join(blocks), n


def main():
    lessons = []
    for pos, l in enumerate(IDX.LESSONS, 1):
        mp4 = os.path.join(BUILD, l['id'], l['file'] + '.mp4')
        if os.path.exists(mp4):
            lessons.append((pos, l, mp4))
        else:
            print('skip (not built): %s' % l['title'])

    if not lessons:
        sys.exit('nothing built yet')

    sigs = {signature(m) for _, _, m in lessons}
    if len(sigs) != 1:
        sys.exit('stream parameters differ across lessons, so a copy-concat is unsafe:\n  '
                 + '\n  '.join(sigs))
    print('%d lessons, all %s' % (len(lessons), sigs.pop().replace('\n', ' ')))

    os.makedirs(OUT, exist_ok=True)

    # cumulative start times, and the chapter list
    marks, t = [], 0.0
    for pos, l, mp4 in lessons:
        marks.append((t, l, duration(mp4)))
        t += marks[-1][2]
    total = t

    # ---- concat list
    listfile = os.path.join(OUT, 'concat.txt')
    with open(listfile, 'w', encoding='utf-8') as f:
        for _, _, mp4 in lessons:
            f.write("file '%s'\n" % mp4.replace("'", r"'\''"))

    # ---- chapter metadata, embedded so players show a chapter menu
    meta = os.path.join(OUT, 'chapters.ffmeta')
    with open(meta, 'w', encoding='utf-8') as f:
        f.write(';FFMETADATA1\ntitle=LinkedIn Staff Coding Interview Prep\n')
        for start, l, dur in marks:
            f.write('[CHAPTER]\nTIMEBASE=1/1000\nSTART=%d\nEND=%d\ntitle=%s\n'
                    % (round(start * 1000), round((start + dur) * 1000),
                       l['title'].replace('=', '-').replace(';', ',')))

    out_mp4 = os.path.join(OUT, NAME + '.mp4')
    print('joining -> %s' % out_mp4)
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-stats',
                        '-f', 'concat', '-safe', '0', '-i', listfile,
                        '-i', meta, '-map_metadata', '1',
                        '-c', 'copy', '-movflags', '+faststart', out_mp4])
    if r.returncode != 0:
        sys.exit('ffmpeg failed')

    # ---- merged subtitles
    parts, n = [], 1
    for (start, l, _), (_, _, mp4) in zip(marks, lessons):
        srt = mp4[:-4] + '.srt'
        chunk, n = shift_srt(srt, start, n)
        if chunk:
            parts.append(chunk)
    if parts:
        with open(os.path.join(OUT, NAME + '.srt'), 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(parts) + '\n')

    # ---- timestamps for a description
    with open(os.path.join(OUT, 'chapters.txt'), 'w', encoding='utf-8') as f:
        f.write('LinkedIn Staff Coding Interview Prep - %s, %d lessons\n\n' % (stamp(total), len(marks)))
        for start, l, _ in marks:
            f.write('%s %s\n' % (stamp(start), l['title']))

    actual = duration(out_mp4)
    size = os.path.getsize(out_mp4) / 1e9
    print('\n%s' % out_mp4)
    print('  %s  %.2f GB  %d chapters' % (stamp(actual), size, len(marks)))
    drift = abs(actual - total)
    print('  expected %s, drift %.2f s %s' % (stamp(total), drift,
          '(fine)' if drift < 2 else '(CHECK THIS)'))


if __name__ == '__main__':
    main()
