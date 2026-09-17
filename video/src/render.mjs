// node browser.mjs file:///.../deck.html#from=0&to=100 --script render.mjs
import fs from 'node:fs';
export default async function (page) {
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  // fit answer blocks: shrink body text until the grid fits its box
  await page.evaluate(() => {
    document.querySelectorAll('.slide').forEach(sl => {
      const g = sl.querySelector('.ablocks'); if (!g) return;
      sl.style.display = 'block'; sl.style.opacity = 1;
      g.querySelectorAll('[data-step]').forEach(e => e.style.opacity = 1);
      g.style.gridAutoRows = 'auto';
      let fs = 30;
      const set = () => g.querySelectorAll('.abb').forEach(e => { e.style.fontSize = fs + 'px'; });
      set();
      while (g.scrollHeight > g.clientHeight + 1 && fs > 19) { fs -= 1; set(); }
      sl.style.display = 'none';
    });
  });
  const hash = await page.evaluate(() => location.hash);
  const q = Object.fromEntries(hash.slice(1).split('&').filter(Boolean).map(kv => kv.split('=')));
  const outDir = decodeURIComponent(q.out);
  const plan = await page.evaluate(() => JSON.parse(document.getElementById('plan').textContent));
  const from = +q.from, to = Math.min(+q.to, plan.length);
  let shots = 0, skipped = 0;
  for (let i = from; i < to; i++) {
    for (const f of (q.holds === '1' ? [plan[i].hold] : [...plan[i].frames, plan[i].hold])) {
      const path = `${outDir}/${f.f}.jpg`;
      if (fs.existsSync(path) && q.force !== '1') { skipped++; continue; }
      await page.evaluate((f) => {
        const setStep = (root, cur, p) => {
          root.querySelectorAll('[data-step]').forEach(el => {
            const n = +el.dataset.step;
            let o = n < cur ? 1 : n === cur ? p : 0;
            if (el.dataset.hide !== undefined) { const h = +el.dataset.hide; if (cur > h) o = 0; else if (cur === h) o = Math.min(o, 1 - p); }
            if (el.dataset.dim !== undefined) { const d = +el.dataset.dim; if (cur > d) o = Math.min(o, .22); else if (cur === d) o = Math.min(o, 1 - .78 * p); }
            el.style.opacity = o;
            const ty = n === cur ? (1 - p) * 18 : 0;
            if (!el.classList.contains('arr')) el.style.transform = ty ? `translateY(${ty}px)` : '';
            if (el.dataset.hl !== undefined) {
              const on = el.dataset.hl.split(',').map(Number).includes(cur);
              el.classList.toggle('hl', on);
            }
          });
          root.querySelectorAll('[data-hl]:not([data-step])').forEach(el => el.classList.toggle('hl', el.dataset.hl.split(',').map(Number).includes(cur)));
        };
        document.querySelectorAll('.slide').forEach(s => { s.style.display = 'none'; s.style.opacity = 1; });
        const s = document.getElementById(f.slide);
        if (f.prev && f.prev !== f.slide) {
          const ps = document.getElementById(f.prev);
          ps.style.display = 'block'; ps.style.opacity = 1 - f.fade; setStep(ps, f.prevStep, 1);
          const pk = ps.querySelector('.pkt'); if (pk) pk.style.display = 'none';
        }
        s.style.display = 'block';
        s.style.opacity = f.black !== undefined ? f.black : (f.prev && f.prev !== f.slide ? f.fade : 1);
        setStep(s, f.step, f.p);
        const pk = s.querySelector('.pkt');
        if (pk) {
          if (f.pkt) { pk.style.display = 'block'; pk.style.left = f.pkt[0] + 'px'; pk.style.top = f.pkt[1] + 'px';
            pk.style.setProperty('--c', { shared: '#fbbf24', dp: '#2dd4bf', cp: '#a78bfa', deny: '#f87171', ok: '#34d399', info: '#60a5fa', com: '#94a3b8' }[f.pkt[2]] || '#fbbf24'); }
          else pk.style.display = 'none';
        }
        const pr = s.querySelector('.prog i'); if (pr) pr.style.width = (f.prog * 100).toFixed(2) + '%';
        const tb = s.querySelector('.thinkbar i'); if (tb) tb.style.width = ((f.think ?? 0) * 100) + '%';
        const tc = s.querySelector('.thinkc'); if (tc) tc.textContent = f.cd === undefined || f.cd === null ? '' : (f.cd > 0 ? f.cd + 's' : 'Now listen');
      }, f);
      await page.screenshot({ path, type: 'jpeg', quality: 93 });
      shots++;
    }
  }
  return { from, to, shots, skipped };
}
