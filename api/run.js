// Vercel serverless function: POST /api/run  ->  compile and run C#.
//
// The practice page posts to a RELATIVE /api/run, so one page works two ways:
//   - locally, companies/linkedin/runner.py serves it and uses your own dotnet
//   - deployed, this function runs it on a free public compiler service
//
// Engines, in order of preference:
//   1. Compiler Explorer, .NET 10 CoreCLR  -> modern C#, matches the local dotnet
//   2. Judge0 CE, Mono                     -> C# 7.0 only; used if (1) is unavailable
//
// Piston is deliberately absent: its public API became whitelist-only in Feb 2026.
//
// Compiler Explorer is a donation-funded community service. This sends one short
// request per Run and falls back rather than retrying, which keeps usage polite. If
// you ever put this in front of real traffic, self-host instead.
//
// TIMEOUTS: 20 s for the first engine plus 15 s for the fallback fits inside the
// 60 s maxDuration set in vercel.json. A Vercel function that outlives its limit is
// killed mid-request, so the caller would get a bare 504 and the fallback would
// never run - which is why these are not left at their earlier, larger values.

const CE = 'https://godbolt.org/api/compiler/dotnet100csharpcoreclr/compile';
const JUDGE0 = 'https://ce.judge0.com';
const CSHARP_MONO = 51;
const MAX_SOURCE = 200_000;

function text(parts) {
  return (parts || []).map((p) => (p && p.text) || '').join('\n');
}

/* ---- engine 1: Compiler Explorer, .NET 10, modern C# ---- */
async function viaCompilerExplorer(program, started) {
  const r = await fetch(CE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({
      source: program,
      lang: 'csharp',
      allowStoreCodeDebug: false,
      options: {
        userArguments: '',
        executeParameters: { args: [], stdin: '' },
        compilerOptions: { executorRequest: true, skipAsm: true },
        filters: { execute: true },
      },
    }),
    signal: AbortSignal.timeout(20_000),
  });

  if (!r.ok) throw new Error(`compiler explorer ${r.status}`);
  const j = await r.json();
  const ms = Date.now() - started;
  const build = j.buildResult || {};
  const engine = 'Compiler Explorer (.NET 10 CoreCLR)';

  if (build.code !== undefined && build.code !== 0) {
    return {
      ok: false, stage: 'compile', engine, dialect: 'modern', ms,
      compile_output: (text(build.stderr) || text(build.stdout) || 'compilation failed').slice(0, 8000),
    };
  }
  if (j.didExecute === false && j.code !== 0) {
    return {
      ok: false, stage: 'compile', engine, dialect: 'modern', ms,
      compile_output: (text(j.stderr) || 'the program did not run').slice(0, 8000),
    };
  }

  return {
    ok: j.code === 0,
    stage: 'run', engine, dialect: 'modern', ms,
    stdout: text(j.stdout).slice(0, 200_000),
    stderr: text(j.stderr).slice(0, 8000),
    exit: j.code,
  };
}

/* ---- engine 2: Judge0, Mono, C# 7.0 ---- */
async function viaJudge0(program, started) {
  const r = await fetch(
    `${JUDGE0}/submissions?base64_encoded=false&wait=true&fields=stdout,stderr,compile_output,status,time,message`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        language_id: CSHARP_MONO,
        source_code: program,
        cpu_time_limit: 10,
        wall_time_limit: 15,
        memory_limit: 256000,
      }),
      signal: AbortSignal.timeout(15_000),
    }
  );

  if (!r.ok) throw new Error(`judge0 ${r.status}`);
  const j = await r.json();
  const statusId = j.status && j.status.id; // 3 Accepted, 5 TLE, 6 Compile error
  const ms = Date.now() - started;
  const engine = 'Judge0 CE (Mono, C# 7.0)';

  if (statusId === 6) {
    return {
      ok: false, stage: 'compile', engine, dialect: 'csharp7', ms,
      compile_output: (j.compile_output || '').slice(0, 8000),
    };
  }
  return {
    ok: statusId === 3,
    stage: 'run', engine, dialect: 'csharp7', ms,
    stdout: (j.stdout || '').slice(0, 200_000),
    stderr: (j.stderr || j.message || '').slice(0, 8000),
    timeout: statusId === 5,
    status: j.status && j.status.description,
  };
}

module.exports = async (req, res) => {
  if (req.method === 'OPTIONS') {
    res.setHeader('Allow', 'POST');
    return res.status(204).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, stage: 'request', stderr: 'POST only' });
  }

  let program = '';
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    program = body.program || '';
  } catch (e) {
    return res.status(400).json({ ok: false, stage: 'request', stderr: 'bad JSON' });
  }
  if (!program.trim()) {
    return res.status(400).json({ ok: false, stage: 'request', stderr: 'no program' });
  }
  if (program.length > MAX_SOURCE) {
    return res.status(413).json({ ok: false, stage: 'request', stderr: 'program too large' });
  }

  const started = Date.now();
  const failures = [];

  for (const engine of [viaCompilerExplorer, viaJudge0]) {
    try {
      const out = await engine(program, started);
      if (failures.length) out.note = `fell back after: ${failures.join('; ')}`;
      return res.status(200).json(out);
    } catch (e) {
      failures.push(String((e && e.message) || e).slice(0, 120));
    }
  }

  return res.status(504).json({
    ok: false,
    stage: 'engine',
    stderr:
      'No remote compiler responded (' + failures.join('; ') + '). ' +
      'Run locally with: python3 companies/linkedin/runner.py',
  });
};
