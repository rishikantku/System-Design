# -*- coding: utf-8 -*-
"""TTS + per-segment encode + concat + chapters + captions."""
import io, json, os, re, subprocess, hashlib, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.abspath(os.path.join(HERE, '..', 'build'))
FR, AU, SG = [os.path.join(B, d) for d in ('frames', 'audio', 'segs')]
for d in (FR, AU, SG): os.makedirs(d, exist_ok=True)
VOICE, RATE = os.environ.get('VOICE', 'Samantha'), os.environ.get('RATE', '172')
OUTNAME = os.environ.get('OUTNAME', 'Isolated-Cloud-Staff-Interview-Course')

SAY = [  # (pattern, spoken) — applied to narration only, never to slides
 (r'\bL2\.5\b', 'L two point five'), (r'\bL0\b', 'L zero'), (r'\bL1\b', 'L one'), (r'\bL2\b', 'L two'), (r'\bL3\b', 'L three'),
 (r'\bGraphQL\b', 'Graph Q L'), (r'\bDataLoader\b', 'Data Loader'), (r'\bNadel\b', 'Nah-dell'),
 (r'\bAWS\b', 'A W S'), (r'\bVPCs\b', 'V P Cs'), (r'\bVPC\b', 'V P C'), (r'\bSLOs?\b', 'S L O'), (r'\bSLA\b', 'S L A'),
 (r'\bSRE\b', 'S R E'), (r'\bAPIs\b', 'A P Is'), (r'\bAPI\b', 'A P I'), (r'\bIPs\b', 'I Ps'), (r'\bIP\b', 'I P'),
 (r'\bAZs\b', 'availability zones'), (r'\bAZ\b', 'availability zone'), (r'\bKMS\b', 'K M S'),
 (r'/20\b', 'slash twenty'), (r'/19\b', 'slash nineteen'), (r'99\.95%', 'ninety-nine point nine five percent'),
 (r'99\.99%', 'ninety-nine point nine nine percent'), (r'\b24h\b', 'twenty-four hour'), (r'(\d)×', r'\1 times'),
 (r'⅓', 'a third'), (r'→', ', then '), (r'·', ', '), (r' = ', ' means '), (r' \+ ', ' plus '), (r'~', 'about '),
 (r'\bPITR\b', 'point in time recovery'), (r'\bTCS\b', 'Tenant Context Service'), (r'\bJSM\b', 'J S M'), (r'\bOU\b', 'O U'),
 (r'\bIDs\b', 'I Ds'), (r'\bID\b', 'I D'),
 (r'\bvs\.?\b', 'versus'), (r'\be\.g\.', 'for example'), (r'—', ', '), (r'–', ' to '), (r'\bUI\b', 'U I'),
]
def spoken(t):
    for p, r in SAY: t = re.sub(p, r, t)
    return t

def dur(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).strip())

TTS = os.environ.get('TTS', 'say')                      # say | sarvam
SARVAM_SPEAKER = os.environ.get('SARVAM_SPEAKER', 'ritu')
SARVAM_MODEL = os.environ.get('SARVAM_MODEL', 'bulbul:v3')

def _chunks(text, limit=2000):
    """Split at sentence boundaries so each request stays under the API's character limit."""
    out, cur = [], ''
    for sent in re.split(r'(?<=[.?!])\s+', text):
        if cur and len(cur) + len(sent) + 1 > limit: out.append(cur); cur = sent
        else: cur = (cur + ' ' + sent).strip()
    return out + ([cur] if cur else [])

def sarvam(text, out):
    import base64, time, urllib.request, urllib.error
    key = os.environ['SARVAM_API_KEY']                  # never written to disk
    parts = []
    for n, chunk in enumerate(_chunks(text)):
        body = json.dumps({'text': chunk, 'language_code': 'en-IN', 'speaker': SARVAM_SPEAKER, 'model': SARVAM_MODEL,
                           'speech_sample_rate': 48000, 'pace': 1.0}).encode()
        for attempt in range(8):
            req = urllib.request.Request('https://api.sarvam.ai/text-to-speech', data=body,
                                         headers={'api-subscription-key': key, 'Content-Type': 'application/json'})
            try:
                r = json.load(urllib.request.urlopen(req, timeout=180)); break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
                code = getattr(e, 'code', None)
                if code in (400, 401, 403): raise RuntimeError(f'Sarvam {code}: {e.read()[:300]}')
                if attempt == 7: raise
                time.sleep(2 * (attempt + 1))
        wav = out + f'.{n}.wav'
        open(wav, 'wb').write(b''.join(base64.b64decode(x) for x in r['audios']))
        parts.append(wav)
    lst = out + '.parts.txt'
    io.open(lst, 'w').write(''.join(f"file '{w}'\n" for w in parts))
    # 0.18 s lead-in silence, matching the say pipeline
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst,
                    '-af', 'adelay=180|180,aresample=48000', '-ac', '1', out], check=True)
    for w in parts: os.remove(w)
    os.remove(lst)

def tts(i, text):
    if TTS == 'sarvam':
        h = hashlib.sha1((SARVAM_MODEL + SARVAM_SPEAKER + spoken(text)).encode()).hexdigest()[:10]
        out = os.path.join(AU, f's{i:04d}_{h}.wav')
        if not os.path.exists(out): sarvam(spoken(text), out)
        return out
    h = hashlib.sha1((VOICE + RATE + spoken(text)).encode()).hexdigest()[:10]
    out = os.path.join(AU, f'a{i:04d}_{h}.aiff')
    if not os.path.exists(out):
        txt = out + '.txt'; io.open(txt, 'w', encoding='utf-8').write('[[slnc 180]] ' + spoken(text))
        subprocess.run(['say', '-v', VOICE, '-r', RATE, '-f', txt, '-o', out], check=True)
    return out

def encode(p, fps):
    i = p['seg']
    frames = p['frames']
    per = [0.25 if p['kind'] == 'think' else 1 / fps for _ in frames]
    trans = sum(per)
    if p['kind'] == 'think':
        total, audio = trans + 0.6, None
    else:
        audio = tts(i, p['narr']) if p['narr'] else None
        ad = dur(audio) if audio else 0
        tail = p['tail'] if p['tail'] is not None else (1.2 if p['kind'] == 'chapter' else 0.6)
        total = max(trans + 0.4, ad + tail)
    hold = max(0.2, total - trans)
    key = hashlib.sha1(json.dumps([p['frames'], p['hold'], total, audio]).encode()).hexdigest()[:10]
    out = os.path.join(SG, f's{i:04d}_{key}.mp4')
    if os.path.exists(out): return out, total
    lst = out + '.txt'
    L = []
    for f, d in zip(frames, per): L += [f"file '{FR}/{f['f']}.jpg'", f'duration {d:.4f}']
    L += [f"file '{FR}/{p['hold']['f']}.jpg'", f'duration {hold:.4f}', f"file '{FR}/{p['hold']['f']}.jpg'"]
    io.open(lst, 'w').write('\n'.join(L) + '\n')
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst]
    if audio: cmd += ['-i', audio]
    else: cmd += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
    cmd += ['-t', f'{total:.3f}', '-vf', f'fps={fps},format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage',
            '-crf', '20', '-r', str(fps), '-video_track_timescale', '25000',
            '-af', 'aresample=48000,apad', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2', out]
    subprocess.run(cmd, check=True)
    return out, total

def ts(t, srt=False):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    if srt: return f'{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}'
    return f'{h}:{m:02d}:{int(s):02d}' if h else f'{m:02d}:{int(s):02d}'

def main():
    P = json.load(open(os.path.join(B, 'plan.json')))
    plan, fps = P['plan'], P['fps']
    only = os.environ.get('ONLY')
    if only:
        a, b = map(int, only.split(':')); plan = plan[a:b]
    with ThreadPoolExecutor(max_workers=int(os.environ.get('JOBS', '6'))) as ex:
        res = list(ex.map(lambda p: encode(p, fps), plan))
    t = 0; starts = []; srt = []; n = 1
    for p, (f, d) in zip(plan, res):
        starts.append(t)
        if p['narr'] and p['kind'] != 'think':
            sents = [s for s in re.split(r'(?<=[.?!])\s+', p['narr']) if s.strip()]
            span = max(0.5, d - 0.8); tot = sum(len(s) for s in sents) or 1; c = t + 0.18
            for s in sents:
                dd = span * len(s) / tot
                srt.append(f'{n}\n{ts(c, True)} --> {ts(c + dd, True)}\n{s}\n'); n += 1; c += dd
        t += d
    concat = os.path.join(B, 'concat.txt')
    io.open(concat, 'w').write(''.join(f"file '{f}'\n" for f, _ in res))
    chapters = [(title, idx) for title, idx in P['chapters']]
    first = plan[0]['seg']
    meta = [';FFMETADATA1']
    yt = []
    for k, (title, idx) in enumerate(chapters):
        if idx < first or idx >= first + len(plan): continue
        st = starts[idx - first]
        nxt = [starts[j - first] for _, j in chapters[k + 1:] if first <= j < first + len(plan)]
        en = nxt[0] if nxt else t
        meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={int(st*1000)}', f'END={int(en*1000)}', f'title={title}']
        yt.append(f'{ts(st)} {title}')
    io.open(os.path.join(B, 'chapters.ffmeta'), 'w').write('\n'.join(meta) + '\n')
    name = OUTNAME + (f'-part-{only.replace(":", "-")}' if only else '')
    final = os.path.join(B, name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concat, '-i', os.path.join(B, 'chapters.ffmeta'),
                    '-map', '0', '-map_metadata', '1', '-c', 'copy', '-movflags', '+faststart', final], check=True)
    io.open(os.path.join(B, name + '.srt'), 'w', encoding='utf-8').write('\n'.join(srt))
    io.open(os.path.join(B, name + '-youtube-chapters.txt'), 'w').write('\n'.join(yt) + '\n')
    print(f'{final}  {ts(t)}  ({t/60:.1f} min)')
    print('\n'.join(yt))

if __name__ == '__main__':
    main()
