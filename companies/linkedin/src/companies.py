# -*- coding: utf-8 -*-
"""companies/index.html — the level between the guide and a company workspace."""
import io, os
from lib import esc

HTML = '''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Companies · Interview preparation</title>
<link rel="stylesheet" href="linkedin/assets/prep.css">
<style>.main{max-width:980px;margin:0 auto;padding:40px 24px 90px}</style>
</head><body>
<div class="top"><div class="top-in">
  <a class="brand" href="../index.html"><span class="in">in</span> Interview prep</a>
  <div class="crumb"><a href="../index.html">Interview prep</a> › <b>Companies</b></div>
  <div class="top-sp"></div>
  <a class="tbtn" href="../index.html">Design guide</a>
  <a class="tbtn" href="../specialization-aic.html">AIC retrospective</a>
</div></div>
<main class="main">
  <div class="hero"><span class="kicker" style="color:#8ec5ff">Interview preparation</span>
    <h1>Companies</h1>
    <p class="sub">One workspace per company. The guide teaches the concepts; these pages hold the loop, the question banks and the practice.</p>
  </div>
  <div class="grid g2">
    <a class="card round" href="linkedin/index.html">
      <div class="num">ACTIVE LOOP</div><div class="rt">LinkedIn — Staff Engineer</div>
      <div class="rd">Full loop: coding, AI coding, system design, hiring manager. Retrospective round already cleared.</div>
      <div class="meta" style="margin-top:10px">Dashboard · 4 round pages · research-backed question database</div>
    </a>
    <a class="card round" href="../questions-google.html">
      <div class="num">QUESTION BANK</div><div class="rt">Google — L6 / Staff</div>
      <div class="rd">81 tagged system-design questions, filtered to the 58 engineering ones and cross-linked to the guide.</div>
      <div class="meta" style="margin-top:10px">Question bank only</div>
    </a>
  </div>
  <div class="foot">To add a company, copy the LinkedIn folder or the Google bank page — see CLAUDE.md §2b and §2e.</div>
</main></body></html>'''

def build():
    out = '/Users/rishi/code/System-Design/companies/index.html'
    io.open(out, 'w', encoding='utf-8').write(HTML)
    return 'companies/index.html'
