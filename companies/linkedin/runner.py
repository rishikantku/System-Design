#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local code runner + static server for the practice page.

    python3 companies/linkedin/runner.py
    -> http://localhost:8765/companies/linkedin/07-practice.html

Why this exists: the deployed site can only reach free public executors, and every
free one is stuck on an old C# dialect (Judge0 is Mono/C# 7.0; Piston went
whitelist-only in Feb 2026; Wandbox's .NET image is broken). Locally you have a real
dotnet, so running here gives you the actual compiler, the actual error messages, and
no network round trip.

It serves the repo AND implements /api/run, so the page talks to a relative URL and
works identically here and on Vercel. No CORS, no mixed content, no configuration.

SECURITY: this compiles and runs code that arrives over HTTP. It binds to 127.0.0.1
only, and rejects requests carrying an Origin header from anywhere but itself, so a
web page you visit cannot use it to run code on your machine. Do not expose it.
"""
import os, sys, json, time, shutil, subprocess, tempfile, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PORT = int(os.environ.get('PORT', '8765'))
WORK = os.path.join(tempfile.gettempdir(), 'linkedin-practice-runner')
TIMEOUT = int(os.environ.get('RUN_TIMEOUT', '15'))
TFM = os.environ.get('TFM', 'net10.0')

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>%s</TargetFramework>
    <Nullable>disable</Nullable>
    <AssemblyName>run</AssemblyName>
    <RootNamespace>run</RootNamespace>
    <InvariantGlobalization>true</InvariantGlobalization>
    <GenerateDocumentationFile>false</GenerateDocumentationFile>
    <WarningLevel>0</WarningLevel>
    <NoWarn>CS0168;CS0219;CS8321</NoWarn>
  </PropertyGroup>
</Project>
""" % TFM

_lock = threading.Lock()


def ensure_project():
    """One warm project directory; the first build is ~2 s, later ones are much faster."""
    os.makedirs(WORK, exist_ok=True)
    proj = os.path.join(WORK, 'run.csproj')
    if not os.path.exists(proj) or open(proj).read() != CSPROJ:
        open(proj, 'w').write(CSPROJ)
    return WORK


def run_csharp(program):
    d = ensure_project()
    open(os.path.join(d, 'Program.cs'), 'w', encoding='utf-8').write(program)

    t0 = time.time()
    try:
        b = subprocess.run(['dotnet', 'build', '-v', 'q', '--nologo', '-o', 'out'],
                           cwd=d, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'stage': 'compile', 'compile_output': 'build timed out', 'ms': 0}

    if b.returncode != 0:
        # keep only the lines that name a file/line - MSBuild noise helps nobody
        lines = [l for l in (b.stdout + b.stderr).split('\n')
                 if ('error' in l.lower() or 'warning' in l.lower()) and 'Program.cs' in l]
        return {'ok': False, 'stage': 'compile',
                'compile_output': '\n'.join(lines) or (b.stdout + b.stderr)[-4000:],
                'ms': int((time.time() - t0) * 1000)}

    t1 = time.time()
    try:
        r = subprocess.run(['dotnet', os.path.join('out', 'run.dll')],
                           cwd=d, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'stage': 'run', 'stdout': '', 'timeout': True,
                'stderr': 'Timed out after %d s - probably an infinite loop.' % TIMEOUT,
                'ms': int((time.time() - t0) * 1000)}

    return {'ok': r.returncode == 0, 'stage': 'run',
            'stdout': r.stdout[-200000:], 'stderr': r.stderr[-8000:],
            'exit': r.returncode,
            'compile_ms': int((t1 - t0) * 1000),
            'ms': int((time.time() - t0) * 1000),
            'engine': 'local dotnet %s' % DOTNET_VERSION}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        if '/api/run' in (self.path or ''):
            sys.stderr.write('  run %s\n' % time.strftime('%H:%M:%S'))

    def _reject_foreign_origin(self):
        """A page on another site must not be able to execute code here."""
        origin = self.headers.get('Origin')
        if origin and origin not in ('http://localhost:%d' % PORT,
                                     'http://127.0.0.1:%d' % PORT, 'null'):
            self.send_error(403, 'cross-origin execution refused')
            return True
        return False

    def do_POST(self):
        if self.path.rstrip('/') != '/api/run':
            return self.send_error(404)
        if self._reject_foreign_origin():
            return
        try:
            n = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(n) or b'{}')
        except Exception as e:
            return self._json({'ok': False, 'stage': 'request', 'stderr': str(e)}, 400)

        program = body.get('program') or ''
        if not program.strip():
            return self._json({'ok': False, 'stage': 'request', 'stderr': 'no program'}, 400)

        with _lock:                      # one build directory, so one build at a time
            result = run_csharp(program)
        self._json(result)

    def _json(self, obj, code=200):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def end_headers(self):
        if self.path.endswith(('.html', '.js', '.css')):
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


def main():
    global DOTNET_VERSION
    if not shutil.which('dotnet'):
        sys.exit('dotnet not found - install the .NET SDK, or use the deployed site '
                 '(which runs on Judge0, C# 7.0 only)')
    DOTNET_VERSION = subprocess.run(['dotnet', '--version'], capture_output=True,
                                    text=True).stdout.strip()

    url = 'http://localhost:%d/companies/linkedin/07-practice.html' % PORT
    print('runner   dotnet %s   (warm build dir: %s)' % (DOTNET_VERSION, WORK))
    print('serving  %s' % ROOT)
    print('\n  %s\n' % url)
    print('Ctrl-C to stop.')

    if '--open' in sys.argv:
        subprocess.Popen(['open', url])
    try:
        ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nstopped')


DOTNET_VERSION = ''
if __name__ == '__main__':
    main()
