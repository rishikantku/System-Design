# -*- coding: utf-8 -*-
"""Builds the question data, merged and ranked.

    python3 src/build.py

  assets/questions.json        PUBLIC (committed, deployed): InterviewDB questions rewritten in my own words
  assets/questions.local.json  LOCAL ONLY (git-excluded): the verbatim InterviewDB wording, built only when
                               src/statements.json (also git-excluded) is present
The page and the local server prefer the .local file when it exists."""
import io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from guides import G
from guides2 import G2, ADD
from reports import REPORTS, ORDER, NEW, MERGED_AWAY, UNPLACED, RECENT
from extra13 import X
from detail import D
from paths import P
from public_statements import PUBLIC
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', 'video', 'design', 'lessons'))
from top10_data import TOP10, STAFF, MODEL

def design_for(qid):
    t = next((d for d in TOP10 if d['id'] == qid), None)
    d = dict(t, staff=STAFF[qid], model=MODEL[qid]) if t else X[qid]
    opts, chosen, flip = d['trade']
    out = dict(fr=d['fr'], nfr=d['nfr'], rows=d['rows'], arrows=d['arrows'], cap=d['cap'], model=d['model'],
               trade=dict(options=[dict(name=n, kind=k, pros=p, cons=c) for n, k, p, c in opts], chosen=chosen, flip=flip),
               fail=d['fail'], staff=d['staff'])
    ids = {b[0] for row in d['rows'] for b in row}
    assert all(a in ids and b in ids for a, b in d['arrows']), (qid, 'arrow to unknown box')
    assert all(len(r) == 4 for r in d['cap']) and all(len(r) == 4 for r in d['model']) and all(len(r) == 3 for r in d['fail']), qid
    return out

FIELDS = ['gist', 'clarify', 'numbers', 'api', 'parts', 'deep', 'followups', 'mistakes', 'say']
# "Earlier research" lines stand for several reports; this is how many each one stands for.
EARLY_COUNT = {'metrics': 3, 'topn': 2, 'typeahead': 3, 'mq': 2, 'scheduler': 1, 'ratelimit': 1, 'feed': 1, 'calendar': 1, 'logging': 1}

def build(idb):
  out = []
  for rank, qid in enumerate(ORDER, 1):
      if qid in NEW:
          base = dict(id=qid, title=NEW[qid]['title'], lesson=NEW[qid]['lesson'], statement=NEW[qid]['statement'], idb=False)
      else:
          q = idb[qid]; base = dict(id=qid, title=q['title'], lesson=q['lesson'], statement=q['statement'], idb=True)
      g = dict(G2[qid]) if qid in G2 else dict(G[qid])
      for k, extra in ADD.get(qid, {}).items():
          g[k] = list(g[k]) + extra
      missing = [f for f in FIELDS if not g.get(f)]
      assert not missing, (qid, missing)
      reps = REPORTS.get(qid, [('InterviewDB', 'In your InterviewDB list.', '')])
      count = sum(1 for r in reps if r[0] != 'Earlier research' and not r[0].endswith('not counted')) + EARLY_COUNT.get(qid, 0)
      variants = [dict(source=s, text=t, note=n) for s, t, n in reps]
      for gone, into in MERGED_AWAY.items():
          if into == qid:
              variants.append(dict(source='InterviewDB (merged into this question)', text=idb[gone]['statement'], note=''))
      base.update(n=rank, rank=rank, recent=qid in RECENT, reports=count, variants=variants, guide={f: g[f] for f in FIELDS}, design=design_for(qid))
      dd = D[qid]
      ids = {b[0] for row in dd['rows'] for b in row}
      assert len(dd['rows']) <= 3 and all(len(r) <= 4 for r in dd['rows']), (qid, 'detail layout too big')
      assert all(a in ids and b in ids for a, b, _ in dd['arrows']), (qid, 'detail arrow to unknown box')
      assert all(len(st) == 4 for st in dd['steps']), qid
      base['detail'] = dict(rows=dd['rows'], arrows=[list(x) for x in dd['arrows']], steps=dd['steps'])
      pp = P[qid]
      for kind in ('write', 'read'):
          bad = [b for b, _ in pp[kind][1] if b not in ids]
          assert not bad, (qid, kind, 'path names unknown boxes', bad)
      base['detail']['paths'] = {k: dict(title=pp[k][0], steps=[list(x) for x in pp[k][1]]) for k in ('write', 'read')}
      out.append(base)

  ids = [q['id'] for q in out]
  assert len(ids) == len(set(ids))
  assert set(idb) - set(ids) == set(MERGED_AWAY), set(idb) - set(ids)

  return out

PUB = {k: dict(title=v[0], lesson=v[1], statement=v[2]) for k, v in PUBLIC.items()}
public = build(PUB)
io.open(os.path.join(HERE, '..', 'assets', 'questions.json'), 'w', encoding='utf-8').write(json.dumps(public, ensure_ascii=False))
SRC = os.path.join(HERE, 'statements.json')
if os.path.exists(SRC):
    verbatim = {q['id']: q for q in json.load(io.open(SRC, encoding='utf-8'))}
    assert len(verbatim) == 21
    # The public file must not carry any InterviewDB sentence verbatim.
    pub_text = json.dumps(public, ensure_ascii=False)
    for q in verbatim.values():
        for sent in [x.strip() for x in q['statement'].replace('\n', ' ').split('.') if len(x.strip()) > 60]:
            assert sent not in pub_text, ('verbatim InterviewDB text in the public build', q['id'], sent[:80])
    io.open(os.path.join(HERE, '..', 'assets', 'questions.local.json'), 'w', encoding='utf-8').write(json.dumps(build(verbatim), ensure_ascii=False))
    print('local verbatim build -> assets/questions.local.json')
io.open(os.path.join(HERE, '..', 'assets', 'meta.json'), 'w', encoding='utf-8').write(json.dumps(dict(unplaced=UNPLACED, updated='26 Oct 2026'), ensure_ascii=False))
for q in public: print('%2d %-10s %d report(s)%s' % (q['rank'], q['id'], q['reports'], '' if q['idb'] else '  NEW'))
print(len(public), 'questions (public build -> assets/questions.json)')
