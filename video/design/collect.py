# -*- coding: utf-8 -*-
"""Gather every finished design video into one folder, ready to upload.

Hardlinks rather than copies: same filesystem, so a 23-video set costs no extra disk.
Numbering follows the course order in index.py, so an alphabetical sort in Finder or a
YouTube bulk upload lands them in the order they should be watched.

    python3 collect.py
"""
import io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'build-design'))
DEST = os.path.join(OUT, '_upload')
sys.path.insert(0, HERE)
import index as COURSE


def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', path], capture_output=True, text=True)
    try:
        return float(json.loads(r.stdout)['format']['duration'])
    except Exception:
        return 0.0


def link(src, dst):
    """Hardlink, falling back to a copy across filesystems."""
    if os.path.exists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        import shutil
        shutil.copy2(src, dst)


def main():
    os.makedirs(DEST, exist_ok=True)
    rows, missing, total = [], [], 0.0

    for n, lesson in enumerate(COURSE.LESSONS, 1):
        d = os.path.join(OUT, lesson['id'])
        mp4 = os.path.join(d, lesson['file'] + '.mp4')
        srt = os.path.join(d, lesson['file'] + '.srt')

        if not os.path.exists(mp4):
            missing.append((n, lesson))
            continue

        base = '%02d-%s' % (n, lesson['file'])
        link(mp4, os.path.join(DEST, base + '.mp4'))
        if os.path.exists(srt):
            link(srt, os.path.join(DEST, base + '.srt'))

        secs = duration(mp4)
        total += secs
        rows.append((n, base, secs, os.path.getsize(mp4), lesson))

    # a manifest so the upload order and titles are obvious without opening anything
    man = ['LinkedIn system design course — upload order', '']
    chap = None
    for n, base, secs, size, lesson in rows:
        if lesson['chapter'] != chap:
            chap = lesson['chapter']
            c = COURSE.CHAPTERS[chap]
            man.append('')
            man.append('Chapter %d — %s' % (c['num'], c['title'].replace('&mdash;', '—')))
        man.append('  %-52s %5.1f min  %5.1f MB' % (base + '.mp4', secs / 60, size / 1e6))
        man.append('      %s' % lesson['title'].replace('&mdash;', '—'))

    if missing:
        man.append('')
        man.append('NOT YET ENCODED (rendered, waiting on TTS credits):')
        for n, lesson in missing:
            man.append('  %02d  %-46s %s' % (n, lesson['file'], lesson['title'].replace('&mdash;', '—')))

    man.append('')
    man.append('%d videos · %.1f hours total' % (len(rows), total / 3600))
    io.open(os.path.join(DEST, '00-ORDER.txt'), 'w', encoding='utf-8').write('\n'.join(man) + '\n')

    print('\n'.join(man))
    print('\n-> %s' % DEST)


if __name__ == '__main__':
    main()
