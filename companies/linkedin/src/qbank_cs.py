# -*- coding: utf-8 -*-
"""Reads the C# listings for the question bank out of src/cs/qbank/.

The page shows the same bytes that `dotnet run` compiled and tested, so a listing on the
page cannot drift from the code that was verified. Nothing here edits C#; it only slices it.
"""
import os, re

CSDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cs', 'qbank')
_cache = {}


def _read(filename):
    if filename not in _cache:
        # 'aicoding/A01_Lru.cs' reads from a sibling project under cs/; a bare name stays in qbank.
        root = os.path.dirname(CSDIR) if '/' in filename else CSDIR
        with open(os.path.join(root, filename), encoding='utf-8') as f:
            _cache[filename] = f.read()
    return _cache[filename]


def _lead_comment(text, start):
    """Pull the comment block immediately above `start` in with the declaration."""
    lines = text[:start].split('\n')
    keep = []
    for line in reversed(lines[:-1] if lines and lines[-1].strip() == '' else lines):
        if line.strip().startswith('//') or line.strip().startswith('///'):
            keep.append(line)
        elif line.strip() == '' and keep:
            break
        elif line.strip() == '':
            continue
        else:
            break
    return '\n'.join(reversed(keep))


def cs_type(filename, typename, comment=True):
    """The whole declaration of a class / interface / struct, brace-matched."""
    text = _read(filename)
    m = re.search(r'^[ \t]*(?:public |internal |private |protected )?(?:sealed |static |abstract )*'
                  r'(?:class|interface|struct|record)\s+' + re.escape(typename) + r'\b',
                  text, re.M)
    if not m:
        raise KeyError('%s: no type %s' % (filename, typename))

    # An interface or class may be one-line-braced or brace-on-next-line; find the first '{'.
    open_at = text.index('{', m.end() - len(typename) - 1 if False else m.start())
    depth, i = 0, open_at
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[m.start():i + 1]
    if comment:
        lead = _lead_comment(text, m.start())
        if lead:
            body = lead + '\n' + body
    return body


def cs_member(filename, typename, signature_contains, comment=True):
    """One method or property of a type, matched on a distinctive part of its signature."""
    block = cs_type(filename, typename, comment=False)
    idx = block.index(signature_contains)
    line_start = block.rindex('\n', 0, idx) + 1

    # a property with => has no braces
    nl = block.index('\n', idx)
    if '{' not in block[idx:nl] and block[idx:nl].rstrip().endswith(';'):
        out = block[line_start:nl]
    else:
        open_at = block.index('{', idx)
        depth, i = 0, open_at
        while i < len(block):
            if block[i] == '{':
                depth += 1
            elif block[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out = block[line_start:i + 1]

    if comment:
        lead = _lead_comment(block, line_start)
        if lead:
            out = lead + '\n' + out
    return _dedent(out)


def cs_whole(filename):
    return _read(filename).strip()


def _dedent(text):
    lines = text.split('\n')
    pads = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    cut = min(pads) if pads else 0
    return '\n'.join(l[cut:] if l.strip() else '' for l in lines)


def line_count(text):
    return len(text.strip().split('\n'))
