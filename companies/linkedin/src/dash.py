# -*- coding: utf-8 -*-
from lib import *
import research as R

def build():
    ROUND_CARDS = [
        ('coding', '01 · 60 MIN', 'Staff Coding', '01-coding.html',
         'Modularity, extensibility, and finding and fixing bugs — the pack\'s own framing. No AI in this module.',
         'Official example: Firefighting Strategy · bug-fix and extensibility drills · patterns in C#'),
        ('ai', '02 · 60 MIN', 'Coding with AI (CWAI)', '02-ai-coding.html',
         'CoderPad AI Assist. You are expected to use AI, and to own every line it produces.',
         'Fundamentals + intentional AI use · validation · iteration · communication'),
        ('design', '03 · 60 MIN', 'Systems & Infrastructure Design', '03-system-design.html',
         'Whiteboard design of infrastructure systems, scored on completeness, decisions and reasoning.',
         'Official example: Bit.ly · rate limiter · scheduler · index · queue · autosuggest'),
        ('hm', '04 · 60 MIN', 'Host Leader', '04-hiring-manager.html',
         'Deep dive on your background and leadership: communication, culture, influence, mentorship, conflict.',
         'Story bank from your own material · two gaps flagged honestly'),
    ]
    cards = []
    for rid, num, name, f, desc, topics in ROUND_CARDS:
        cards.append(
            '<a class="card round" href="%s" data-progress-round="%s">'
            '<div style="display:flex;gap:14px;align-items:flex-start">'
            '<div style="flex:1"><div class="num">%s</div><div class="rt">%s</div>'
            '<div class="rd">%s</div></div><div class="ring"><span>0%%</span></div></div>'
            '<div class="bar"><i></i></div>'
            '<div class="pmeta"><span data-done>0 / 0</span><span data-topics>—</span></div>'
            '<div class="pmeta" style="margin-top:6px"><span>Mocks: <b data-mocks>0</b></span>'
            '<span>Last: <b data-last>never</b></span></div>'
            '<div class="pmeta" style="margin-top:6px"><span>Weakest: <b data-weak>—</b></span></div>'
            '<div class="meta" style="margin-top:8px">%s</div></a>' % (f, rid, num, name, desc, topics))

    status = card(
        '<div class="tags">%s %s</div>'
        '<p style="margin-top:10px">You cleared the design retrospective / screening round. Four rounds remain. '
        'This workspace holds the preparation for all four, plus everything recent candidates have publicly reported '
        'about the LinkedIn loop.</p>'
        '<div class="tw"><table><thead><tr><th>Stage</th><th>Status</th></tr></thead><tbody>'
        '<tr><td><b>Design retrospective / screening</b></td><td>✓ <b style="color:var(--green)">Cleared</b></td></tr>'
        '<tr><td>01 · Coding</td><td>Next</td></tr><tr><td>02 · AI Coding</td><td>Next</td></tr>'
        '<tr><td>03 · System Design</td><td>Next</td></tr><tr><td>04 · Hiring Manager</td><td>Next</td></tr>'
        '</tbody></table></div>' % (tag('hi', 'Retrospective cleared'), tag('lv', 'Full loop ahead')),
        title='Where you are')

    loop_rows = [[n, d, '[%s](%s)' % (R.SOURCES[s]['name'].split('—')[0].strip(), R.SOURCES[s]['url'])] for n, d, s in R.LOOP['rounds']]
    loop = card(
        rich(R.LOOP['summary']) +
        table(['Round', 'What is reported', 'Source'], loop_rows) +
        '<ul>%s</ul>' % ''.join('<li>%s</li>' % rich(n) for n in R.LOOP['notes']),
        title='The loop as recent candidates describe it (community reports)')

    # ---------------- research intelligence ----------------
    counts = {}
    for q in R.Q:
        counts[q['r']] = counts.get(q['r'], 0) + 1
    high = [q for q in R.Q if q['rec'] == 'high']
    a_conf = [q for q in R.Q if q['conf'] == 'A']
    kpis = grid([
        '<div class="kpi"><div class="n">%s</div><div class="l">Research last updated</div></div>' % R.DATE,
        '<div class="kpi"><div class="n">%d</div><div class="l">Sources analysed</div></div>' % len(R.SOURCES),
        '<div class="kpi"><div class="n">%d</div><div class="l">Reported questions catalogued</div></div>' % len(R.Q),
        '<div class="kpi"><div class="n">%d</div><div class="l">High-recurrence patterns</div></div>' % len(high),
        '<div class="kpi"><div class="n">%d</div><div class="l">First-hand (confidence A)</div></div>' % len(a_conf),
        '<div class="kpi"><div class="n">%d / %d / %d / %d</div><div class="l">Coding / AI / Design / HM</div></div>'
        % (counts.get('coding', 0), counts.get('ai', 0), counts.get('design', 0), counts.get('hm', 0)),
    ], 'g3')

    conf_key = note(
        '<b>A</b> — first-hand report with specifics, 2025–2026. &nbsp; '
        '<b>B</b> — aggregator or guide summarising candidate reports, or a thin first-hand report. &nbsp; '
        '<b>C</b> — single source, undated or older, or a category inferred from guides. '
        'Nothing here is confirmed by LinkedIn. Recent candidates reported these; that makes them preparation signals, not predictions.',
        'warn', 'How to read confidence')

    new_patterns = card(
        '<ul>'
        '<li><b>The AI-enabled coding round is real and now well documented.</b> Two platforms reported: CoderPad with a model picker, '
        'and HackerRank with a built-in assistant. [Hello Interview, Feb 2026; Exponent candidate, ≈Mar 2026]</li>'
        '<li><b>Rate limiter is the most recent design prompt found</b> — logged as asked about a month ago. [Exponent question bank]</li>'
        '<li><b>Platform-migration influence questions</b> ("5,000 teams, how do you get them to migrate, what about holdouts?") '
        'appear in the manager/communication round. [Exponent candidate, ≈Mar 2026]</li>'
        '<li><b>A separate craftsmanship round</b> shows up in the India Staff loop: code quality, testing, CI/CD, metrics. [Taro, May 2025]</li>'
        '<li><b>Two interviewers per round</b>, one leading and one shadowing, in the most recent report. [Exponent, ≈Mar 2026]</li>'
        '</ul>', title='New or newly-confirmed patterns since the last pass')

    recurring = card(
        '<ul>' + ''.join('<li><b>%s</b> — %s <span class="src">(%s)</span></li>' % (
            q['q'], q['pat'], ', '.join(R.SOURCES[s]['name'].split('—')[0].strip() for s in q['src']))
            for q in high) + '</ul>',
        title='Recurring across independent reports (high recurrence)')

    # ---------------- question database ----------------
    rows = ''
    for i, q in enumerate(R.Q):
        yr = '2026' if '2026' in q['d'] else ('2025' if '2025' in q['d'] else 'older')
        loc = 'india' if 'India' in q['loc'] else ('us' if 'United States' in q['loc'] or 'US' in q['loc'] else 'other')
        srcs = ' · '.join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (R.SOURCES[s]['url'], R.SOURCES[s]['name'].split('—')[0].strip()) for s in q['src'])
        fu = '<ul style="margin:4px 0 0 16px">%s</ul>' % ''.join('<li>%s</li>' % esc(f) for f in q['fu'])
        rows += (
            '<tr data-id="qdb-%d" data-round="%s" data-year="%s" data-rec="%s" data-conf="%s" data-loc="%s" data-prep="no">'
            '<td><b>%s</b></td>'
            '<td><b>%s</b><div class="src" style="margin-top:4px">%s</div>'
            '<details class="acc" style="margin:8px 0 0"><summary><span class="sq">Follow-ups &amp; what to practise</span></summary>'
            '<div class="body">%s<p style="margin-top:8px"><b>Pattern:</b> %s<br><b>Practise:</b> %s</p></div></details></td>'
            '<td>%s</td><td>%s<div class="src">%s</div></td><td>%s</td><td>%s</td>'
            '<td><button class="sbtn qprep" data-qid="qdb-%d">Mark practised</button></td></tr>'
        ) % (i, q['r'], yr, q['rec'], q['conf'], loc,
             dict(coding='Coding', ai='AI Coding', design='System Design', hm='Hiring Manager')[q['r']],
             esc(q['q']), srcs, fu, esc(q['pat']), esc(q['prep']),
             esc(q['d']), esc(q['role']), esc(q['loc']),
             tag({'high': 'hi', 'medium': 'med', 'one-off': 'low'}[q['rec']], q['rec']),
             tag({'A': 'hi', 'B': 'med', 'C': 'low'}[q['conf']], 'conf ' + q['conf']), i)

    filters = (
        '<div class="filters" data-filter-scope="#qdb tbody tr">'
        '<input class="search" placeholder="Search the question database…">'
        + ''.join('<button class="fchip" data-fk="round" data-fv="%s">%s</button>' % (k, v)
                  for k, v in [('coding', 'Coding'), ('ai', 'AI Coding'), ('design', 'System Design'), ('hm', 'Hiring Manager')])
        + ''.join('<button class="fchip" data-fk="year" data-fv="%s">%s</button>' % (k, v)
                  for k, v in [('2026', '2026'), ('2025', '2025')])
        + '<button class="fchip" data-fk="loc" data-fv="india">India</button>'
        + '<button class="fchip" data-fk="rec" data-fv="high">High recurrence</button>'
        + '<button class="fchip" data-fk="conf" data-fv="A">First-hand (A)</button>'
        + '<button class="fchip" data-fk="conf" data-fv="C">Low confidence (C)</button>'
        + '<button class="fchip" data-fk="prep" data-fv="no">Not practised</button>'
        + '<span class="count"></span></div>')

    qdb = filters + ('<div class="tw" id="qdb"><table><thead><tr>'
                     '<th>Round</th><th>Question</th><th>Reported</th><th>Role / location</th>'
                     '<th>Recurrence</th><th>Confidence</th><th>Prep</th></tr></thead><tbody>%s</tbody></table></div>' % rows)

    # ---------------- what interviews are telling us ----------------
    tell = ''
    for rid, name in [('coding', '1 · Coding'), ('ai', '2 · AI Coding'), ('design', '3 · System Design'), ('hm', '4 · Hiring Manager')]:
        t = R.THEMES[rid]
        tell += card(
            '<p>%s</p>'
            '<h4>Most common themes</h4><ul>%s</ul>'
            '<h4>Common follow-ups</h4><p>%s</p>'
            '<h4>What looks staff-level</h4><p>%s</p>'
            '<h4>What to practise</h4><ul>%s</ul>'
            '<div class="src">Confidence: %s</div>' % (
                rich(t['summary']),
                ''.join('<li>%s</li>' % rich(x) for x in t['themes']),
                rich(t['follow']), rich(t['staff']),
                ''.join('<li>%s</li>' % rich(x) for x in t['practice']),
                rich(t['conf'])),
            title=name)

    # ---------------- research-driven plan ----------------
    drive = card(
        table(['What the reports show', 'How this workspace changed'], [
            ['Rate limiter asked ~a month ago; scheduler, queue and index in 2025 reports',
             '**System design P0 list** leads with rate limiter, job scheduler, Kafka-like queue and distributed index'],
            ['AI round pivots to concurrency and "productionise it" every time',
             '**Every AI exercise ends with a concurrency + production hardening stage**, and the coding page has a concurrency section in C#'],
            ['Debug-then-extend reported as the AI round arc',
             '**Progressive implementation exercises** (LRU → LFU → rank → thread-safe) and a debug-first drill'],
            ['Topological sort, nested-structure DFS, rolling hash in 2025–2026 reports',
             '**Graphs and nested-tree patterns are P0** in the coding page, with those exact variants'],
            ['"5,000 teams, get them to migrate" and career-progression questions',
             '**Migration-at-scale and career-arc answers are the first two stories** in the hiring-manager story bank'],
            ['Separate craftsmanship round in the India Staff loop',
             '**A craftsmanship section** covering code review, testing, CI/CD and metrics sits in the hiring-manager page'],
            ['Down-levelling attributed to leadership signal',
             '**Every round page carries a senior-versus-staff contrast** so the scope signal is explicit'],
        ]) +
        note('Reports are signals, not predictions. Nobody can tell you what you will be asked — the point of the list is '
             'coverage of what LinkedIn interviewers have recently probed, weighted by how often independent candidates mention it.',
             'warn', 'Do not overfit'),
        title='How the research changed the plan')

    sources = card(table(['Source', 'Date', 'Role / location', 'Kind'], [
        ['[%s](%s)' % (s['name'], s['url']), s['date'], '%s · %s' % (s['role'], s['loc']), s['kind']]
        for s in R.SOURCES.values()]) +
        note('Refreshing this later: re-run the research pass, add entries to `scratchpad/lp/research.py` (each with source, date, '
             'recurrence and confidence), and rebuild. Older entries stay in the file so you can compare passes — nothing here is '
             'treated as permanent truth.', '', 'Keeping it current'),
        title='Sources')

    how = card(
        '<ul>'
        '<li><b>Progress is yours, stored in this browser.</b> Every problem, pattern, design and story has a status and a confidence '
        'rating. The rings above are computed from them, not from a guess.</li>'
        '<li><b>Reveal, do not read.</b> Problems and designs open one stage at a time: question → think → approach → edge cases → '
        'code → complexity → follow-up. Try before you open the next stage.</li>'
        '<li><b>Mock mode hands off to chat.</b> Each mock question has a timer and a notes box, then a <b>Grade this with Claude</b> '
        'button that copies a prompt. Paste it to me and I score it (SCORE / STRONG / MISSING / STAFF SIGNAL / IMPROVE / FOLLOW-UP) '
        'and ask the follow-up.</li>'
        '<li><b>Personal material is tagged.</b> %s means it comes from your own Isolated Cloud retrospective and is yours to claim; '
        '%s means it is general interview knowledge.</li>'
        '</ul>' % (tag('exp', 'Your experience'), tag('gen', 'General knowledge')),
        title='How to use this workspace')

    mod_cards = []
    for m in R.OFFICIAL_MODULES:
        page_for = {'design': '03-system-design.html', 'hm': '04-hiring-manager.html',
                    'ai': '02-ai-coding.html', 'coding': '01-coding.html'}[m['id']]
        ex = ''
        if m['example']:
            ex = '<div class="note good" style="margin-top:10px"><span class="lbl">Example in the pack</span><b>%s</b></div>' % esc(m['example']['title'])
        mod_cards.append(
            '<a class="card round" href="%s"><div class="num">%d MINUTES%s</div><div class="rt">%s</div>'
            '<div class="rd">%s</div>%s<div class="meta" style="margin-top:10px">Scored on: %s</div></a>' % (
                page_for, m['mins'], ' · AI ASSISTED' if m['ai'] else '', esc(m['name']),
                esc(m['what'][:205] + ('…' if len(m['what']) > 205 else '')), ex,
                esc(', '.join(x.replace('**', '') .split(' — ')[0] for x in m['evaluated'][:4]))))

    role = R.OFFICIAL_ROLE
    official = (
        note('Your recruiter sent <b>"Staff SI Onsite Prep — CWAI"</b> (LinkedIn Interview Preparation, Staff Virtual Onsite, '
             'Systems and Infrastructure). Everything in this section comes from that pack and is authoritative. The community '
             'research further down is a complement, not a substitute — where they disagree, the pack wins.', 'good',
             'Official source · %s' % R.OFFICIAL_DATE) +
        grid(mod_cards, 'g2') +
        grid([
            card('<p>%s</p><p><b>They want:</b> %s</p><div class="tags">%s</div>%s' % (
                 rich(role['what']), rich(role['wants']),
                 ''.join('<span class="tag gen">%s</span>' % esc(o) for o in role['oss']),
                 note(role['note'], '')),
                 title='The role: %s' % role['title']),
            card(table(['', 'From the pack'], [[a, b] for a, b in R.OFFICIAL_LOGISTICS]),
                 title='Logistics and reminders'),
        ], 'g2') +
        card('<p>The pack links these. They are worth ten minutes each, and the CoderPad ones are worth more than that:</p><ul>%s</ul>'
             % ''.join('<li><b>%s</b> <span class="src">— %s</span></li>' % (esc(a), esc(b)) for a, b in R.OFFICIAL_RESOURCES),
             title='Resources the pack points you to'))

    body = (
        sec('onsite', 'The official onsite — four modules', official,
            kicker='From LinkedIn', why='Staff Virtual Onsite · Systems & Infrastructure') +
        sec('status', 'Status and loop', grid([status, loop], 'g2'), kicker='LinkedIn · Staff Engineer',
            why='Screening cleared · four rounds to go') +
        sec('readiness', 'Readiness dashboard', grid(cards, 'g2'), kicker='Progress',
            why='Computed from what you have actually completed') +
        sec('today', "Today's preparation", '<div id="todayplan" class="card"><p>Loading your plan…</p></div>',
            kicker='Focus', why='Generated from your weakest areas and the research priorities') +
        sec('intel', 'Recent interview intelligence', kpis + conf_key + grid([recurring, new_patterns], 'g2'),
            kicker='Research', why='Last updated %s' % R.DATE) +
        sec('qdb', 'Question database', qdb, kicker='Every reported question',
            why='%d questions · filter by round, year, recurrence, confidence' % len(R.Q)) +
        sec('telling', 'What recent interviews are telling us', grid([tell], 'g2'), kicker='Summary') +
        sec('driven', 'Research-driven preparation', drive, kicker='Priorities') +
        sec('sources', 'Sources and method', sources, kicker='Provenance') +
        sec('how', 'How this workspace works', how, kicker='Guide'))

    tail = r'''
    (function(){
      // question database: reflect practised state + toggle
      function raw(){ try{ return JSON.parse(localStorage.getItem('lp.v1'))||{} }catch(e){ return {} } }
      function paintQ(){
        var s = raw().items||{};
        document.querySelectorAll('#qdb tbody tr').forEach(function(tr){
          var it = s[tr.dataset.id]||{};
          tr.dataset.prep = it.st==='done' ? 'yes' : 'no';
          var b = tr.querySelector('.qprep');
          b.textContent = it.st==='done' ? '✓ Practised' : 'Mark practised';
          b.classList.toggle('on', it.st==='done');
        });
      }
      document.addEventListener('click', function(e){
        var b = e.target.closest('.qprep'); if(!b) return;
        var tr = b.closest('tr'), cur = LP.get(tr.dataset.id).st;
        LP.set(tr.dataset.id, {st: cur==='done'? null : 'done'});
        paintQ();
      });
      paintQ();

      // today's plan
      var ROUND_NAMES = {coding:'Coding', ai:'AI Coding', design:'System Design', hm:'Hiring Manager'};
      var MINUTES = {coding:45, ai:45, design:60, hm:30};
      function plan(){
        var out=[], total=0;
        ['coding','ai','design','hm'].forEach(function(r){
          var st = LP.stats(r); if(!st.total) return;
          var pick = (st.weak.length? st.weak : st.remaining).slice(0,2);
          if(!pick.length) return;
          out.push({r:r, mins:MINUTES[r], pct:st.pct,
                    what: pick.map(function(i){return i.label}).join('  ·  '),
                    topic: pick[0].topic});
          total += MINUTES[r];
        });
        out.sort(function(a,b){ return a.pct-b.pct });
        var s = LP.all();
        var revise = Object.keys(s.items||{}).filter(function(k){ return (s.items[k].st==='revise'||s.items[k].st==='failed') });
        var html = '<p class="lead">A focused session built from your weakest areas right now. Work top to bottom.</p><ul class="plan">';
        out.forEach(function(o){
          html += '<li><span class="t">'+o.mins+' min — '+ROUND_NAMES[o.r]+'</span> <span class="src">('+o.pct+'% ready · weakest: '+
                  (o.topic||'—')+')</span><br>'+o.what+' &nbsp;<a href="'+LP.manifest.rounds[o.r].file+'">open →</a></li>';
        });
        html += '<li><span class="t">15 min — Revision</span><br>'+
                (revise.length? revise.length+' item(s) marked "needs revision" or "failed" across the workspace — redo them from scratch.'
                              : 'Nothing marked for revision yet. Re-do yesterday\'s hardest item from memory.')+'</li>';
        html += '</ul><div class="src">Total: about '+(total+15)+' minutes. The order follows your lowest readiness first.</div>';
        if(!out.length) html = '<p class="lead">Start anywhere — nothing is tracked yet. Suggested first session: '+
          '45 min coding patterns, 45 min the AI round walkthrough, 60 min the rate limiter design, 30 min the migration-at-scale story.</p>';
        document.getElementById('todayplan').innerHTML = html;
      }
      plan();
      window.LPonProgress = function(){ plan(); paintQ(); };
    })();
    '''

    return page('index.html', 'LinkedIn — Staff Engineer full loop',
                'Four rounds, one workspace: coding, AI coding, system design and hiring manager — built on your own material and on what candidates have recently reported.',
                body, round_id='', round_name='LinkedIn loop', crumb_tail='',
                hero_chips=[('done', '✓ Retrospective cleared'), ('', 'Staff Coding'), ('', 'Coding with AI'),
                            ('', 'Systems & Infra Design'), ('', 'Host Leader'),
                            ('', 'Research updated %s' % R.DATE)],
                tail_js=tail)
