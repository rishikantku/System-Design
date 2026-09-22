# -*- coding: utf-8 -*-
"""Verified LeetCode links, so a problem on the coding page can be opened and run.

Every slug and number below was checked against LeetCode's own problem index
(https://leetcode.com/api/problems/all/), not typed from memory - a wrong slug is a
404 and a wrong number is worse, because it looks right.

exact=False means LeetCode only has a near relative. Those are labelled in the UI
rather than linked silently: sending someone to a different problem and letting them
discover the difference themselves is worse than no link.
"""

# slug -> problem number (verified)
NUM = {
    'letter-combinations-of-a-phone-number': 17,
    'the-maze': 490,
    'insert-delete-getrandom-o1-duplicates-allowed': 381,
    'find-k-closest-elements': 658,
    'find-the-celebrity': 277,
    'shortest-word-distance-ii': 244,
    'bulb-switcher': 319,
    'binary-tree-upside-down': 156,
    'merge-two-binary-trees': 617,
    'valid-triangle-number': 611,
    'lru-cache': 146,
    'nested-list-weight-sum-ii': 364,
    'find-leaves-of-binary-tree': 366,
    'max-stack': 716,
    'all-oone-data-structure': 432,
    'course-schedule-ii': 210,
    'repeated-dna-sequences': 187,
    'word-ladder': 127,
    'minimum-window-substring': 76,
    'search-in-rotated-sorted-array-ii': 81,
    'valid-palindrome-ii': 680,
    'merge-intervals': 56,
    'lowest-common-ancestor-of-a-binary-tree': 236,
    'max-consecutive-ones-iii': 1004,
    'valid-parentheses': 20,
}

_NEAR_MERGE = ('LeetCode 617 is the binary-tree version. The reported LinkedIn question was '
               'n-ary with children identified by key, which is the harder half.')
_NEAR_ORDER = ('Course Schedule II is the same topological sort with numeric ids. The reported '
               'version used named targets and asked you to report the cycle.')
_NEAR_LRU = ('This drill is a bug hunt over an LRU cache; LeetCode 146 is the clean '
             'implementation to practise against.')
_NEAR_INTERVALS = ('Merge Intervals is the core of it. The reported variant wrapped it in a class '
                   'with repeated queries.')
_NEAR_LCA = 'LeetCode 236 is the two-node version; the k-node variant is the follow-up.'

# coding page problem id -> (slug, exact, note)
CODING = {
    'letters':     ('letter-combinations-of-a-phone-number', True, ''),
    'maze':        ('the-maze', True, ''),
    'rgetrandom':  ('insert-delete-getrandom-o1-duplicates-allowed', True, ''),
    'kclosest':    ('find-k-closest-elements', True, ''),
    'celebrity':   ('find-the-celebrity', True, ''),
    'swd2':        ('shortest-word-distance-ii', True, ''),
    'bulb':        ('bulb-switcher', True, ''),
    'upsidedown':  ('binary-tree-upside-down', True, ''),
    'triangle':    ('valid-triangle-number', True, ''),
    'nested2':     ('nested-list-weight-sum-ii', True, ''),
    'findleaves':  ('find-leaves-of-binary-tree', True, ''),
    'maxstack':    ('max-stack', True, ''),
    'allone':      ('all-oone-data-structure', True, ''),
    'lru':         ('lru-cache', True, ''),
    'dna':         ('repeated-dna-sequences', True, ''),
    'wordladder':  ('word-ladder', True, ''),
    'minwindow':   ('minimum-window-substring', True, ''),
    'rotated2':    ('search-in-rotated-sorted-array-ii', True, ''),
    'palindrome':  ('valid-palindrome-ii', True, ''),
    'maxones':     ('max-consecutive-ones-iii', True, ''),
    'mergetrees':  ('merge-two-binary-trees', False, _NEAR_MERGE),
    'buildorder':  ('course-schedule-ii', False, _NEAR_ORDER),
    'bug_lru':     ('lru-cache', False, _NEAR_LRU),
    'intervals':   ('merge-intervals', False, _NEAR_INTERVALS),
    'lca':         ('lowest-common-ancestor-of-a-binary-tree', False, _NEAR_LCA),

    # Reported at LinkedIn, no LeetCode equivalent. Said explicitly so an absent link
    # reads as a fact about the question rather than as something missing.
    'degree':      (None, False, 'No LeetCode equivalent. Closest practice is any unweighted '
                                 'shortest-path BFS; the reported follow-up was to return the path.'),
    'compact':     (None, False, 'No LeetCode equivalent - reported only at LinkedIn.'),
    'booths':      (None, False, 'No LeetCode equivalent - from your own list of past questions.'),

    # Drills and the official example: written for this workspace, not LeetCode problems.
    'firefight':   (None, False, ''),
    'bugfix':      (None, False, ''),
    'extensible':  (None, False, ''),
    'bug_range':   (None, False, ''),
    'ext_parser':  (None, False, ''),
    'ext_retry':   (None, False, ''),
    'bug_list':    (None, False, ''),
}

# practice page problem id -> (slug, exact, note)
PRACTICE = {
    'valid-parentheses':    ('valid-parentheses', True, ''),
    'find-leaves':          ('find-leaves-of-binary-tree', True, ''),
    'upside-down':          ('binary-tree-upside-down', True, ''),
    'word-ladder':          ('word-ladder', True, ''),
    'the-maze':             ('the-maze', True, ''),
    'max-consecutive-ones': ('max-consecutive-ones-iii', True, ''),
    'valid-palindrome-ii':  ('valid-palindrome-ii', True, ''),
    'valid-triangle':       ('valid-triangle-number', True, ''),
    'repeated-dna':         ('repeated-dna-sequences', True, ''),
    'k-closest':            ('find-k-closest-elements', True, ''),
    'letter-combinations':  ('letter-combinations-of-a-phone-number', True, ''),
    'bulb-switcher':        ('bulb-switcher', True, ''),
    'nested-sum':           ('nested-list-weight-sum-ii', True, ''),
    'all-oone':             ('all-oone-data-structure', True, ''),
    'getrandom':            ('insert-delete-getrandom-o1-duplicates-allowed', True, ''),
    'word-distance':        ('shortest-word-distance-ii', True, ''),
    'lfu':                  ('lfu-cache', True, ''),
    'celebrity':            ('find-the-celebrity', True, ''),
    'keyed-merge':          ('merge-two-binary-trees', False, _NEAR_MERGE),
    'build-order':          ('course-schedule-ii', False, _NEAR_ORDER),
    'compact-tree':         (None, False, 'No LeetCode equivalent - reported only at LinkedIn.'),
    'min-degree':           (None, False, 'No LeetCode equivalent. Closest practice is any '
                                          'unweighted shortest-path BFS.'),
    'booths':               (None, False, 'No LeetCode equivalent - from your own list.'),
    'threadsafe-lfu':       (None, False, 'No LeetCode equivalent: LeetCode does not test thread '
                                          'safety. Practise this one by hand.'),
}

NUM['lfu-cache'] = 460   # verified alongside the rest


def url(slug):
    return 'https://leetcode.com/problems/%s/' % slug


def entry(table, pid):
    """(url, number, exact, note) for a problem id, or (None, None, False, note)."""
    slug, exact, note = table.get(pid, (None, False, ''))
    if not slug:
        return None, None, False, note
    return url(slug), NUM.get(slug), exact, note


def chip(table, pid):
    """A small 'run it on LeetCode' link, or a muted note when there is nothing to link."""
    href, num, exact, note = entry(table, pid)
    if href:
        label = 'LeetCode %s' % num if exact else 'LeetCode %s &middot; closest' % num
        title = note or 'Opens on LeetCode, where you can run it against their judge'
        return ('<a class="lc" href="%s" target="_blank" rel="noopener" title="%s">%s &#8599;</a>'
                % (href, note.replace('"', "'") if note else title, label))
    if note:
        return '<span class="lc none" title="%s">not on LeetCode</span>' % note.replace('"', "'")
    return ''
