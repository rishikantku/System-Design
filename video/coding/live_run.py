# -*- coding: utf-8 -*-
"""Compile and run every step of lesson 11.2 and record the real console output.

    python3 live_run.py            # all runs
    python3 live_run.py L1 R3b     # some

One small project per run under ../build-coding/c11l2-live/cs/<id>/ (git-ignored). Output goes to
lessons/live_out.json, which the lesson reads — so the video never shows a console that was not produced.
"""
import io, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'lessons'))
import live_cs as L

ROOT = os.path.join(HERE, '..', 'build-coding', 'c11l2-live', 'cs')
OUT = os.path.join(HERE, 'lessons', 'live_out.json')
CSPROJ = '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>
  <Nullable>disable</Nullable><ImplicitUsings>enable</ImplicitUsings><InvariantGlobalization>true</InvariantGlobalization>
  <TreatWarningsAsErrors>false</TreatWarningsAsErrors><NoWarn>CS0168;CS0219;CS0414;CS0169;CS0649</NoWarn></PropertyGroup>
</Project>'''

def files_for(run):
    tests = 'static class Tests {\n    public static void Run() {\n%s\n    }\n}\n%s\n' % (
        '\n'.join('        ' + l if l.strip() else '' for l in run['tests'].strip('\n').split('\n')),
        '\n'.join(run.get('types', [])))
    f = {'Models.cs': L.MODELS.strip() + '\n', 'Harness.cs': L.HARNESS.strip() + '\n',
         'Code.cs': run['code'].strip() + '\n', 'Tests.cs': tests}
    if run.get('extra'): f['LoggerTests.cs'] = run['extra'].strip() + '\n'
    if run.get('code2'): f['AsyncLogger.cs'] = run['code2'].strip() + '\n'
    return f

def verdict(out, built):
    if not built: return 'build'
    if 'Unhandled exception.' in out: return 'crash'
    m = re.search(r'(\d+) passed, (\d+) failed', out)
    return 'pass' if m and m.group(2) == '0' else 'fail'

def run_one(rid):
    d = os.path.join(ROOT, rid); os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'live.csproj'), 'w').write(CSPROJ)
    for name in os.listdir(d):
        if name.endswith('.cs'): os.remove(os.path.join(d, name))
    for name, text in files_for(L.RUNS[rid]).items():
        io.open(os.path.join(d, name), 'w', encoding='utf-8').write(text)
    b = subprocess.run(['dotnet', 'build', '-c', 'Release', '-nologo', '-v', 'q', '-clp:NoSummary'],
                       cwd=d, capture_output=True, text=True, timeout=300)
    if b.returncode != 0:
        errs = []
        for line in (b.stdout + b.stderr).splitlines():
            m = re.search(r'([\w.]+\.cs)\((\d+),(\d+)\): error (CS\d+): (.*?)(?: \[.*\])?$', line)
            if m:
                e = '%s(%s,%s): error %s: %s' % m.groups()
                if e not in errs: errs.append(e)
        return dict(out='\n'.join(errs) or b.stdout[-800:], verdict='build')
    try:
        r = subprocess.run(['dotnet', os.path.join('bin', 'Release', 'net10.0', 'live.dll')], cwd=d,
                           capture_output=True, text=True, timeout=60)
        out = (r.stdout + r.stderr).strip('\n')
    except subprocess.TimeoutExpired:
        out = '(timed out after 60 s)'
    return dict(out=out, verdict=verdict(out, True))

if __name__ == '__main__':
    ids = sys.argv[1:] or list(L.RUNS)
    res = json.load(io.open(OUT)) if os.path.exists(OUT) else {}
    bad = 0
    for rid in ids:
        r = run_one(rid)
        res[rid] = r
        ok = r['verdict'] == L.EXPECT[rid]
        bad += not ok
        print('%s %-4s %-5s (want %-5s) %s' % ('ok  ' if ok else 'BAD ', rid, r['verdict'], L.EXPECT[rid],
                                              r['out'].replace('\n', ' | ')[:150]))
    io.open(OUT, 'w', encoding='utf-8').write(json.dumps(res, indent=1, ensure_ascii=False))
    print('%d runs, %d not as expected' % (len(ids), bad))
    sys.exit(1 if bad else 0)
