# -*- coding: utf-8 -*-
"""Gather every built lesson into one flat, upload-ordered folder.

    python3 collect.py            -> ../build-coding/_upload/
    python3 collect.py <dir>      -> somewhere else (e.g. ~/Desktop/linkedin-course)

Files are HARD-LINKED, not copied, so the folder costs no extra disk and always holds
the same bytes as the build. Re-run it after any encode; it replaces stale links.

Names are prefixed with the upload position (01..34) because plain lesson numbers sort
wrongly - "10.1" lands between "1.1" and "2.1" in every file browser.
"""
import os, re, sys, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, '..', 'build-coding'))

spec = importlib.util.spec_from_file_location('course_index', os.path.join(HERE, 'index.py'))
IDX = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDX)


def link(src, dst):
    """Hard-link, falling back to a copy across filesystems."""
    if os.path.exists(dst):
        if os.path.samefile(src, dst):
            return 'kept'
        os.remove(dst)
    try:
        os.link(src, dst)
        return 'linked'
    except OSError:
        shutil.copy2(src, dst)
        return 'copied'


def main():
    out = os.path.abspath(os.path.expanduser(sys.argv[1])) if len(sys.argv) > 1 \
        else os.path.join(BUILD, '_upload')
    os.makedirs(out, exist_ok=True)

    yt = os.path.join(BUILD, '_youtube')
    done, missing, n_files = [], [], 0

    for pos, lesson in enumerate(IDX.LESSONS, 1):
        d = os.path.join(BUILD, lesson['id'])
        mp4 = os.path.join(d, lesson['file'] + '.mp4')
        srt = os.path.join(d, lesson['file'] + '.srt')
        if not os.path.exists(mp4):
            missing.append('%02d  %s' % (pos, lesson['title']))
            continue

        stem = '%02d - %s' % (pos, lesson['file'])
        link(mp4, os.path.join(out, stem + '.mp4')); n_files += 1
        if os.path.exists(srt):
            link(srt, os.path.join(out, stem + '.srt')); n_files += 1

        # the matching title/description/chapters/tags, named so it sorts beside the video
        pack = os.path.join(yt, '%02d-%s.txt' % (pos, lesson['id']))
        if os.path.exists(pack):
            link(pack, os.path.join(out, stem + ' - UPLOAD TEXT.txt')); n_files += 1

        done.append((pos, lesson, os.path.getsize(mp4)))

    for extra in ('00-playlist.txt', '00-upload-order.txt'):
        p = os.path.join(yt, extra)
        if os.path.exists(p):
            link(p, os.path.join(out, extra)); n_files += 1

    # drop anything left over from an earlier run (renamed lessons, removed files)
    valid = {f for f in os.listdir(out)}
    expected = set()
    for pos, lesson, _ in done:
        stem = '%02d - %s' % (pos, lesson['file'])
        expected |= {stem + '.mp4', stem + '.srt', stem + ' - UPLOAD TEXT.txt'}
    expected |= {'00-playlist.txt', '00-upload-order.txt', 'READ ME FIRST.txt'}
    for stale in sorted(valid - expected):
        os.remove(os.path.join(out, stale))
        print('removed stale', stale)

    total_gb = sum(s for _, _, s in done) / 1e9
    readme = [
        'LinkedIn Staff Coding Interview Prep - upload folder',
        '',
        '%d videos, %.1f GB. Files are numbered in upload order.' % (len(done), total_gb),
        '',
        'For each video there are three files with the same prefix:',
        '  NN - <name>.mp4                 the video',
        '  NN - <name>.srt                 subtitles (upload as English)',
        '  NN - <name> - UPLOAD TEXT.txt   title, description with chapter timestamps, tags',
        '',
        '00-playlist.txt      the playlist description',
        '00-upload-order.txt  the full list with runtimes',
        '',
        'The chapter timestamps in each UPLOAD TEXT file are measured from the encoded',
        'audio, so they paste straight into the YouTube description box and will be',
        'picked up as chapters automatically.',
        '',
        'These are hard links to ../<lesson-id>/ - deleting them does not delete the build,',
        'and re-running collect.py refreshes anything that was re-encoded.',
    ]
    if missing:
        readme += ['', 'NOT YET BUILT:'] + ['  ' + m for m in missing]
    with open(os.path.join(out, 'READ ME FIRST.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(readme) + '\n')

    print('%s\n  %d videos, %d files, %.1f GB (hard-linked, no extra disk used)'
          % (out, len(done), n_files, total_gb))
    if missing:
        print('  not yet built: %s' % ', '.join(m.split('  ')[0] for m in missing))


if __name__ == '__main__':
    main()
