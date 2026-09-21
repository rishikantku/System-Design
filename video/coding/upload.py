# -*- coding: utf-8 -*-
"""Upload the coding course to YouTube as a private playlist.

SETUP (once)
  1. console.cloud.google.com -> new project
  2. APIs & Services -> Library -> enable "YouTube Data API v3"
  3. APIs & Services -> OAuth consent screen -> External -> add yourself as a Test user
  4. Credentials -> Create credentials -> OAuth client ID -> Desktop app
     -> Download JSON, save it next to this file as  client_secret.json
  5. pip3 install google-api-python-client google-auth-oauthlib

RUN
    python3 upload.py --limit 4          # one day's worth, then stop
    python3 upload.py --limit 4          # next day: resumes where it left off
    python3 upload.py --dry-run          # show what would happen, call nothing

QUOTA is the reason for --limit. A Google project gets 10,000 units/day by default:
    videos.insert        1600
    captions.insert       400
    playlistItems.insert   50
so ~2,050 units per lesson => 4 lessons/day, or 6 with --no-captions (1,650 each).
34 lessons is therefore about 9 days, unless you request more quota in the console.

State lives in upload-state.json, so re-running never double-uploads. Everything is
uploaded PRIVATE; nothing is published. Flip visibility yourself in YouTube Studio.
"""
import os, sys, json, re, argparse, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.abspath(os.path.join(HERE, '..', 'build-coding'))
YT = os.path.join(BUILD, '_youtube')
STATE = os.path.join(HERE, 'upload-state.json')
SECRET = os.path.join(HERE, 'client_secret.json')
TOKEN = os.path.join(HERE, 'upload-token.json')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube']
PLAYLIST_TITLE = 'LinkedIn Staff Coding Interview Prep'
CATEGORY_EDUCATION = '27'

spec = importlib.util.spec_from_file_location('course_index', os.path.join(HERE, 'index.py'))
IDX = importlib.util.module_from_spec(spec); spec.loader.exec_module(IDX)


# ------------------------------------------------------------------ upload text
def parse_pack(path):
    """The NN-<id>.txt written by youtube.py -> {title, description, tags}."""
    raw = open(path, encoding='utf-8').read()
    out, key = {}, None
    buf = []
    for line in raw.split('\n'):
        if line in ('TITLE', 'DESCRIPTION', 'TAGS', 'FILE', 'SUBTITLES'):
            if key:
                out[key] = '\n'.join(buf).strip()
            key, buf = line.lower(), []
        else:
            buf.append(line)
    if key:
        out[key] = '\n'.join(buf).strip()
    out['tags'] = [t.strip() for t in out.get('tags', '').split(',') if t.strip()]
    return out


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {'playlist_id': None, 'videos': {}}


def save_state(s):
    json.dump(s, open(STATE, 'w'), indent=2)


# ------------------------------------------------------------------ api
def service():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(SECRET):
                sys.exit('missing %s - see the SETUP notes at the top of this file' % SECRET)
            creds = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES).run_local_server(port=0)
        open(TOKEN, 'w').write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)


def ensure_playlist(yt, state, dry):
    if state.get('playlist_id'):
        return state['playlist_id']
    desc = ''
    p = os.path.join(YT, '00-playlist.txt')
    if os.path.exists(p):
        desc = open(p, encoding='utf-8').read()[:4900]
    if dry:
        print('would create private playlist %r' % PLAYLIST_TITLE)
        return 'DRY-PLAYLIST'
    r = yt.playlists().insert(
        part='snippet,status',
        body={'snippet': {'title': PLAYLIST_TITLE, 'description': desc},
              'status': {'privacyStatus': 'private'}}).execute()
    state['playlist_id'] = r['id']
    save_state(state)
    print('created playlist %s (private)' % r['id'])
    return r['id']


def upload_video(yt, pack, mp4, dry):
    body = {
        'snippet': {
            'title': pack['title'][:100],
            'description': pack['description'][:4900],
            'tags': pack['tags'][:15],
            'categoryId': CATEGORY_EDUCATION,
            'defaultLanguage': 'en',
        },
        'status': {
            'privacyStatus': 'private',          # never public from this script
            'selfDeclaredMadeForKids': False,    # required, or the upload is rejected
            'embeddable': True,
        },
    }
    if dry:
        print('    would upload %.0f MB as PRIVATE' % (os.path.getsize(mp4) / 1e6))
        return 'DRY-VIDEO'

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(mp4, chunksize=8 * 1024 * 1024, resumable=True, mimetype='video/mp4')
    req = yt.videos().insert(part='snippet,status', body=body, media_body=media)
    resp, last = None, -1
    while resp is None:
        status, resp = req.next_chunk()
        if status and int(status.progress() * 100) // 10 > last:
            last = int(status.progress() * 100) // 10
            print('    %d%%' % (status.progress() * 100), end='\r', flush=True)
    return resp['id']


def add_caption(yt, video_id, srt, dry):
    if dry:
        print('    would attach captions')
        return
    from googleapiclient.http import MediaFileUpload
    yt.captions().insert(
        part='snippet',
        body={'snippet': {'videoId': video_id, 'language': 'en',
                          'name': 'English', 'isDraft': False}},
        media_body=MediaFileUpload(srt, mimetype='application/octet-stream')).execute()


def add_to_playlist(yt, playlist_id, video_id, position, dry):
    if dry:
        return
    yt.playlistItems().insert(
        part='snippet',
        body={'snippet': {'playlistId': playlist_id, 'position': position,
                          'resourceId': {'kind': 'youtube#video', 'videoId': video_id}}}).execute()


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=4, help='how many to upload this run (quota)')
    ap.add_argument('--no-captions', action='store_true', help='skip SRTs: 6/day instead of 4')
    ap.add_argument('--dry-run', action='store_true', help='print the plan, call nothing')
    ap.add_argument('--only', help='comma-separated lesson ids, ignoring --limit')
    args = ap.parse_args()

    state = load_state()
    done = state['videos']

    todo = []
    for pos, lesson in enumerate(IDX.LESSONS, 1):
        if lesson['id'] in done:
            continue
        mp4 = os.path.join(BUILD, lesson['id'], lesson['file'] + '.mp4')
        pack = os.path.join(YT, '%02d-%s.txt' % (pos, lesson['id']))
        if not (os.path.exists(mp4) and os.path.exists(pack)):
            print('skip %s (not built)' % lesson['id'])
            continue
        todo.append((pos, lesson, mp4, pack))

    if args.only:
        want = {x.strip() for x in args.only.split(',')}
        todo = [t for t in todo if t[1]['id'] in want]
    else:
        todo = todo[:args.limit]

    if not todo:
        print('nothing to do - %d/%d already uploaded' % (len(done), len(IDX.LESSONS)))
        return

    per = 1650 if args.no_captions else 2050
    print('%d already uploaded, %d queued now (~%d quota units of 10,000/day)'
          % (len(done), len(todo), per * len(todo) + (50 if not state.get('playlist_id') else 0)))

    yt = None if args.dry_run else service()
    playlist_id = ensure_playlist(yt, state, args.dry_run)

    for pos, lesson, mp4, packfile in todo:
        pack = parse_pack(packfile)
        print('[%02d/%d] %s' % (pos, len(IDX.LESSONS), pack['title'][:70]))
        try:
            vid = upload_video(yt, pack, mp4, args.dry_run)
            add_to_playlist(yt, playlist_id, vid, pos - 1, args.dry_run)
            srt = mp4[:-4] + '.srt'
            if not args.no_captions and os.path.exists(srt):
                add_caption(yt, vid, srt, args.dry_run)
            if not args.dry_run:
                done[lesson['id']] = {'video_id': vid, 'position': pos,
                                      'at': time.strftime('%Y-%m-%d %H:%M')}
                save_state(state)
                print('    ok https://youtu.be/%s  (private)' % vid)
        except Exception as e:
            msg = str(e)
            if 'quotaExceeded' in msg or 'uploadLimitExceeded' in msg:
                print('    QUOTA EXHAUSTED - stopping. Re-run tomorrow; progress is saved.')
                break
            print('    FAILED: %s' % msg[:300])
            break

    left = len(IDX.LESSONS) - len(done)
    print('\n%d uploaded, %d remaining%s' % (len(done), left,
          '' if args.dry_run else '  (all private; publish from YouTube Studio)'))


if __name__ == '__main__':
    main()
