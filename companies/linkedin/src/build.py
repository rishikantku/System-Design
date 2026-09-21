# -*- coding: utf-8 -*-
import importlib, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib, research as R

MODULES = ['coding', 'aicoding', 'sysdesign', 'hm', 'researchpage', 'course', 'practice', 'dash', 'companies']   # dash last: it reads nothing, but keep order stable
built = []
for m in MODULES:
    try:
        mod = importlib.import_module(m)
    except ModuleNotFoundError as e:
        print('skip', m, '(%s)' % e); continue
    built.append(mod.build())
summary = dict(date=R.DATE, sources=len(R.SOURCES), questions=len(R.Q))
size = lib.write_manifest(summary)
print('built:', ', '.join(built))
print('manifest %d bytes, %d rounds' % (size, len(lib.MANIFEST['rounds'])))
for rid, r in lib.MANIFEST['rounds'].items():
    print('  %-7s %3d items' % (rid, len(r['items'])))
