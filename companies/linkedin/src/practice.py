# -*- coding: utf-8 -*-
"""07-practice.html — a LeetCode-style runner for the reported LinkedIn questions.

Problem statements are written here in plain English rather than copied from anywhere.
Each problem supplies a C# stub and a harness; the page assembles

    PRELUDE + types + "class Solution { <your code> }" + "Main { <harness> }"

and posts it to the local runner (companies/linkedin/runner.py), which compiles it
with the reader's own dotnet. There is no hosted execution: away from that machine the
page offers the LeetCode link instead.
The harness prints one @@T line per case, which the page renders as a results table.

Harness code stays conservative C# (no "is not null", no target-typed "new()") so it
compiles on older toolchains too. Your own solutions can use whatever your dotnet
supports.
"""
import json, os
import lib
from lib import esc, rich, card, sec, note, grid

# ---------------------------------------------------------------- C# harness support
PRELUDE = r'''using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public static class H {
    static int _pass, _total;
    static readonly System.Diagnostics.Stopwatch _sw = new System.Diagnostics.Stopwatch();

    public static string Fmt(object o) {
        if (o == null) return "null";
        string s = o as string;
        if (s != null) return "\"" + s + "\"";
        if (o is bool) return ((bool)o) ? "true" : "false";
        if (o is double || o is float) return Convert.ToDouble(o).ToString("0.####");
        IEnumerable e = o as IEnumerable;
        if (e != null) {
            List<string> parts = new List<string>();
            foreach (object x in e) parts.Add(Fmt(x));
            return "[" + string.Join(", ", parts) + "]";
        }
        return Convert.ToString(o, System.Globalization.CultureInfo.InvariantCulture);
    }

    public static bool Eq(object a, object b) {
        if (a == null || b == null) return a == null && b == null;
        if (a is string || b is string) return Fmt(a) == Fmt(b);
        IEnumerable ea = a as IEnumerable, eb = b as IEnumerable;
        if ((ea == null) != (eb == null)) return false;
        if (ea != null) {
            List<object> la = new List<object>(), lb = new List<object>();
            foreach (object x in ea) la.Add(x);
            foreach (object x in eb) lb.Add(x);
            if (la.Count != lb.Count) return false;
            for (int i = 0; i < la.Count; i++) if (!Eq(la[i], lb[i])) return false;
            return true;
        }
        if (IsNum(a) && IsNum(b)) return Convert.ToDouble(a) == Convert.ToDouble(b);
        return Fmt(a) == Fmt(b);
    }

    static bool IsNum(object o) {
        return o is int || o is long || o is short || o is byte
            || o is double || o is float || o is decimal;
    }

    /// <summary>Order-insensitive view of a sequence, for answers where order is free.</summary>
    public static object Sorted(object o) {
        IEnumerable e = o as IEnumerable;
        if (e == null || o is string) return o;
        List<string> parts = new List<string>();
        foreach (object x in e) parts.Add(Fmt(x));
        parts.Sort(StringComparer.Ordinal);
        return parts;
    }

    public static void Case(string name, object expected, Func<object> body) {
        _total++;
        object actual;
        _sw.Restart();
        try {
            actual = body();
        } catch (Exception ex) {
            _sw.Stop();
            Console.WriteLine("@@T|" + name + "|ERROR|" + Fmt(expected) + "|" +
                              ex.GetType().Name + ": " + One(ex.Message) + "|" + _sw.ElapsedMilliseconds);
            return;
        }
        _sw.Stop();
        bool ok = Eq(expected, actual);
        if (ok) _pass++;
        Console.WriteLine("@@T|" + name + "|" + (ok ? "PASS" : "FAIL") + "|" +
                          Fmt(expected) + "|" + Fmt(actual) + "|" + _sw.ElapsedMilliseconds);
    }

    /// <summary>For answers where any order is acceptable.</summary>
    public static void CaseAnyOrder(string name, object expected, Func<object> body) {
        Case(name, Sorted(expected), delegate { return Sorted(body()); });
    }

    /// <summary>For answers checked by a rule rather than by equality.</summary>
    public static void CaseCheck(string name, string want, Func<string> body) {
        _total++;
        string verdict;
        _sw.Restart();
        try { verdict = body(); } catch (Exception ex) {
            _sw.Stop();
            Console.WriteLine("@@T|" + name + "|ERROR|" + want + "|" +
                              ex.GetType().Name + ": " + One(ex.Message) + "|" + _sw.ElapsedMilliseconds);
            return;
        }
        _sw.Stop();
        bool ok = verdict == null;
        if (ok) _pass++;
        Console.WriteLine("@@T|" + name + "|" + (ok ? "PASS" : "FAIL") + "|" + want + "|" +
                          (verdict == null ? "ok" : One(verdict)) + "|" + _sw.ElapsedMilliseconds);
    }

    static string One(string s) {
        if (s == null) return "";
        return s.Replace("\r", " ").Replace("\n", " ").Replace("|", "/");
    }

    public static void Done() {
        Console.WriteLine("@@S|" + _pass + "|" + _total);
    }
}
'''

TREENODE = r'''public class TreeNode {
    public int val;
    public TreeNode left, right;
    public TreeNode(int v) { val = v; }
}

public static class T {
    /// <summary>Level-order build: null means "no node". [1,2,3,null,null,4]</summary>
    public static TreeNode Build(int?[] a) {
        if (a.Length == 0 || a[0] == null) return null;
        TreeNode root = new TreeNode(a[0].Value);
        Queue<TreeNode> q = new Queue<TreeNode>();
        q.Enqueue(root);
        int i = 1;
        while (q.Count > 0 && i < a.Length) {
            TreeNode n = q.Dequeue();
            if (i < a.Length) { if (a[i] != null) { n.left = new TreeNode(a[i].Value); q.Enqueue(n.left); } i++; }
            if (i < a.Length) { if (a[i] != null) { n.right = new TreeNode(a[i].Value); q.Enqueue(n.right); } i++; }
        }
        return root;
    }

    /// <summary>Level-order serialise with trailing nulls trimmed.</summary>
    public static IList<object> Ser(TreeNode root) {
        List<object> outp = new List<object>();
        if (root == null) return outp;
        Queue<TreeNode> q = new Queue<TreeNode>();
        q.Enqueue(root);
        while (q.Count > 0) {
            TreeNode n = q.Dequeue();
            if (n == null) { outp.Add(null); continue; }
            outp.Add(n.val);
            q.Enqueue(n.left); q.Enqueue(n.right);
        }
        while (outp.Count > 0 && outp[outp.Count - 1] == null) outp.RemoveAt(outp.Count - 1);
        return outp;
    }
}
'''


def P(**kw):
    kw.setdefault('types', '')
    kw.setdefault('hint', '')
    # wrap=False puts your code at the top level instead of inside class Solution,
    # which is what design questions need: you are writing the class, not a method.
    kw.setdefault('wrap', True)
    return kw


PROBLEMS = [
 P(id='valid-parentheses', title='Valid Parentheses', lesson='1.2', chapter='Ch 1',
   diff='Easy', evidence='Your list + LinkedIn tagged set', pattern='Stack',
   video='c1l2-valid-parens/LinkedIn-Coding-1.2-Valid-Parentheses.mp4',
   statement='<p>A string contains only the characters <code>( ) [ ] { }</code>. Return true if '
             'the brackets are correctly matched <b>and</b> correctly nested.</p>'
             '<p><code>"([)]"</code> is invalid even though the counts balance &mdash; the nesting '
             'is crossed.</p>',
   hint='Nesting is last-in-first-out. Two checks per closing bracket, and one at the end.',
   stub='public bool IsValid(string s) {\n    \n}',
   harness='''H.Case("()[]{}", true, delegate { return new Solution().IsValid("()[]{}"); });
H.Case("crossed nesting ([)]", false, delegate { return new Solution().IsValid("([)]"); });
H.Case("nested ({[]})", true, delegate { return new Solution().IsValid("({[]})"); });
H.Case("unclosed (", false, delegate { return new Solution().IsValid("("); });
H.Case("lone closer )", false, delegate { return new Solution().IsValid(")"); });
H.Case("empty string", true, delegate { return new Solution().IsValid(""); });
H.Case("odd length (()", false, delegate { return new Solution().IsValid("(()"); });'''),

 P(id='find-leaves', title='Find Leaves of Binary Tree', lesson='2.1', chapter='Ch 2',
   diff='Medium', evidence='Your list + reported twice', pattern='Trees &middot; return a height',
   video='c2l1-find-leaves/LinkedIn-Coding-2.1-Find-Leaves.mp4', types=TREENODE,
   statement='<p>Repeatedly collect and remove all the leaves of a binary tree, until the tree is '
             'empty. Return the groups in the order they were removed.</p>'
             '<p>For <code>[1,2,3,4,5]</code> the answer is <code>[[4,5,3],[2],[1]]</code>.</p>',
   hint='Do not actually remove anything. A node\'s height above the leaves is its group index.',
   stub='public IList<IList<int>> FindLeaves(TreeNode root) {\n    \n}',
   harness='''H.Case("[1,2,3,4,5]", new int[][]{ new int[]{4,5,3}, new int[]{2}, new int[]{1} },
    delegate { return new Solution().FindLeaves(T.Build(new int?[]{1,2,3,4,5})); });
H.Case("single node", new int[][]{ new int[]{1} },
    delegate { return new Solution().FindLeaves(T.Build(new int?[]{1})); });
H.Case("empty tree", new int[][]{},
    delegate { return new Solution().FindLeaves(T.Build(new int?[]{})); });
H.Case("left chain [1,2,null,3]", new int[][]{ new int[]{3}, new int[]{2}, new int[]{1} },
    delegate { return new Solution().FindLeaves(T.Build(new int?[]{1,2,null,3})); });
H.Case("[1,2,3,4,null,null,5]", new int[][]{ new int[]{4,5}, new int[]{2,3}, new int[]{1} },
    delegate { return new Solution().FindLeaves(T.Build(new int?[]{1,2,3,4,null,null,5})); });'''),

 P(id='upside-down', title='Binary Tree Upside Down', lesson='2.2', chapter='Ch 2',
   diff='Medium', evidence='Your list, twice', pattern='Trees &middot; return the new root',
   video='c2l2-upside-down/LinkedIn-Coding-2.2-Upside-Down.mp4', types=TREENODE,
   statement='<p>Every right child in this tree is a leaf, and has a sibling. Flip the tree so that '
             'the original left spine becomes the root chain: each left child becomes the parent, '
             'its old sibling becomes its left child, and its old parent becomes its right child.</p>'
             '<p><code>[1,2,3,4,5]</code> becomes <code>[4,5,2,null,null,3,1]</code>.</p>',
   hint='Recurse to the bottom first, then rewire from the parent. The new root comes from the deepest left node and never changes.',
   stub='public TreeNode UpsideDownBinaryTree(TreeNode root) {\n    \n}',
   harness='''H.Case("[1,2,3,4,5]", new object[]{4,5,2,null,null,3,1},
    delegate { return T.Ser(new Solution().UpsideDownBinaryTree(T.Build(new int?[]{1,2,3,4,5}))); });
H.Case("single node", new object[]{1},
    delegate { return T.Ser(new Solution().UpsideDownBinaryTree(T.Build(new int?[]{1}))); });
H.Case("empty tree", new object[]{},
    delegate { return T.Ser(new Solution().UpsideDownBinaryTree(T.Build(new int?[]{}))); });
H.Case("[1,2,3]", new object[]{2,3,1},
    delegate { return T.Ser(new Solution().UpsideDownBinaryTree(T.Build(new int?[]{1,2,3}))); });'''),

 P(id='word-ladder', title='Word Ladder', lesson='3.1', chapter='Ch 3',
   diff='Hard', evidence='Your list + LeetCode Staff report', pattern='BFS on an implicit graph',
   video='c3l1-word-ladder/LinkedIn-Coding-3.1-Word-Ladder.mp4',
   statement='<p>Given a start word, an end word and a dictionary, return the number of words in the '
             'shortest transformation sequence from start to end, changing one letter at a time and '
             'using only dictionary words. Return 0 if there is no such sequence.</p>'
             '<p>The count includes both ends: hit &rarr; hot &rarr; dot &rarr; dog &rarr; cog is 5.</p>',
   hint='Do not compare every pair of words. Generate neighbours with a wildcard at each position.',
   stub='public int LadderLength(string beginWord, string endWord, IList<string> wordList) {\n    \n}',
   harness='''H.Case("hit -> cog", 5, delegate { return new Solution().LadderLength("hit", "cog",
    new List<string>{"hot","dot","dog","lot","log","cog"}); });
H.Case("end word absent", 0, delegate { return new Solution().LadderLength("hit", "cog",
    new List<string>{"hot","dot","dog","lot","log"}); });
H.Case("one step apart", 2, delegate { return new Solution().LadderLength("a", "c",
    new List<string>{"a","b","c"}); });
H.Case("no path", 0, delegate { return new Solution().LadderLength("hit", "zzz",
    new List<string>{"hot","zzz"}); });
H.Case("empty dictionary", 0, delegate { return new Solution().LadderLength("hit", "cog",
    new List<string>()); });'''),

 P(id='the-maze', title='The Maze', lesson='3.2', chapter='Ch 3',
   diff='Medium', evidence='Your list', pattern='BFS &middot; state beyond position',
   video='c3l2-the-maze/LinkedIn-Coding-3.2-The-Maze.mp4',
   statement='<p>A ball rolls through a grid of empty cells (0) and walls (1). Once it starts rolling '
             'in a direction it <b>does not stop until it hits a wall</b>. Given a start and a '
             'destination, return whether the ball can stop exactly at the destination.</p>',
   hint='The nodes of your graph are not cells. They are stopping positions.',
   stub='public bool HasPath(int[][] maze, int[] start, int[] destination) {\n    \n}',
   harness='''int[][] maze = new int[][] {
    new int[]{0,0,1,0,0}, new int[]{0,0,0,0,0}, new int[]{0,0,0,1,0},
    new int[]{1,1,0,1,1}, new int[]{0,0,0,0,0} };
H.Case("reachable stop", true, delegate {
    return new Solution().HasPath(maze, new int[]{0,4}, new int[]{4,4}); });
H.Case("cannot stop there", false, delegate {
    return new Solution().HasPath(maze, new int[]{0,4}, new int[]{3,2}); });
H.Case("start == destination", true, delegate {
    return new Solution().HasPath(maze, new int[]{0,4}, new int[]{0,4}); });
H.Case("single open cell", true, delegate {
    return new Solution().HasPath(new int[][]{ new int[]{0} }, new int[]{0,0}, new int[]{0,0}); });'''),

 P(id='max-consecutive-ones', title='Max Consecutive Ones III', lesson='5.1', chapter='Ch 5',
   diff='Medium', evidence='Your list + LinkedIn tagged set', pattern='Sliding window',
   video='c5l1-consecutive-ones/LinkedIn-Coding-5.1-Max-Consecutive-Ones.mp4',
   statement='<p>Given a binary array and an integer k, return the length of the longest run of 1s '
             'you can get if you may flip at most k zeros to ones.</p>',
   hint='Never actually flip anything. A window is valid while it holds at most k zeros.',
   stub='public int LongestOnes(int[] nums, int k) {\n    \n}',
   harness='''H.Case("k=2", 6, delegate { return new Solution().LongestOnes(
    new int[]{1,1,1,0,0,0,1,1,1,1,0}, 2); });
H.Case("k=3", 10, delegate { return new Solution().LongestOnes(
    new int[]{0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1}, 3); });
H.Case("k=0", 3, delegate { return new Solution().LongestOnes(new int[]{1,1,1,0,1,1}, 0); });
H.Case("all zeros, k=2", 2, delegate { return new Solution().LongestOnes(new int[]{0,0,0,0}, 2); });
H.Case("k >= zeros", 5, delegate { return new Solution().LongestOnes(new int[]{0,0,0,0,0}, 9); });
H.Case("single element", 1, delegate { return new Solution().LongestOnes(new int[]{0}, 1); });'''),

 P(id='valid-palindrome-ii', title='Valid Palindrome II', lesson='5.2', chapter='Ch 5',
   diff='Easy', evidence='Reported with a k-edits extension', pattern='Two pointers',
   video='c5l2-palindrome/LinkedIn-Coding-5.2-Valid-Palindrome.mp4',
   statement='<p>Return true if the string can be made a palindrome by deleting <b>at most one</b> '
             'character.</p>',
   hint='Walk inward. At the first mismatch there are exactly two possibilities, and you can test both.',
   stub='public bool ValidPalindrome(string s) {\n    \n}',
   harness='''H.Case("aba", true, delegate { return new Solution().ValidPalindrome("aba"); });
H.Case("abca (delete c)", true, delegate { return new Solution().ValidPalindrome("abca"); });
H.Case("abc", false, delegate { return new Solution().ValidPalindrome("abc"); });
H.Case("empty", true, delegate { return new Solution().ValidPalindrome(""); });
H.Case("single char", true, delegate { return new Solution().ValidPalindrome("a"); });
H.Case("deletion at the end", true, delegate { return new Solution().ValidPalindrome("abcaa"); });
H.Case("long palindrome", true, delegate { return new Solution().ValidPalindrome("racecar"); });'''),

 P(id='valid-triangle', title='Valid Triangle Number', lesson='5.3', chapter='Ch 5',
   diff='Medium', evidence='LinkedIn phone-screen write-up', pattern='Sort + two pointers',
   video='c5l3-triangle/LinkedIn-Coding-5.3-Valid-Triangle.mp4',
   statement='<p>Count the triplets in an array that can form a triangle with non-zero area.</p>'
             '<p>Duplicated values count as separate triplets.</p>',
   hint='Sort first: two of the three triangle conditions then become automatic. Count a whole range at once.',
   stub='public int TriangleNumber(int[] nums) {\n    \n}',
   harness='''H.Case("[2,2,3,4]", 3, delegate { return new Solution().TriangleNumber(new int[]{2,2,3,4}); });
H.Case("[4,2,3,4]", 4, delegate { return new Solution().TriangleNumber(new int[]{4,2,3,4}); });
H.Case("with zeros", 0, delegate { return new Solution().TriangleNumber(new int[]{0,0,0}); });
H.Case("too few values", 0, delegate { return new Solution().TriangleNumber(new int[]{1,2}); });
H.Case("degenerate 1,2,3", 0, delegate { return new Solution().TriangleNumber(new int[]{1,2,3}); });
H.Case("all equal", 4, delegate { return new Solution().TriangleNumber(new int[]{5,5,5,5}); });'''),

 P(id='repeated-dna', title='Repeated DNA Sequences', lesson='6.1', chapter='Ch 6',
   diff='Medium', evidence='LinkedIn tagged set', pattern='Fixed-window hashing',
   video='c6l1-dna/LinkedIn-Coding-6.1-Repeated-DNA.mp4',
   statement='<p>Given a DNA string over A, C, G and T, return every 10-letter substring that occurs '
             '<b>more than once</b>. Each answer appears once; any order.</p>',
   hint='The window length is fixed, so the scan is linear. The only real cost is allocating substrings.',
   stub='public IList<string> FindRepeatedDnaSequences(string s) {\n    \n}',
   harness='''H.CaseAnyOrder("two repeats", new string[]{"AAAAACCCCC","CCCCCAAAAA"}, delegate {
    return new Solution().FindRepeatedDnaSequences("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"); });
H.CaseAnyOrder("all same letter", new string[]{"AAAAAAAAAA"}, delegate {
    return new Solution().FindRepeatedDnaSequences("AAAAAAAAAAAA"); });
H.CaseAnyOrder("shorter than 10", new string[]{}, delegate {
    return new Solution().FindRepeatedDnaSequences("AAAAA"); });
H.CaseAnyOrder("exactly 10, no repeat", new string[]{}, delegate {
    return new Solution().FindRepeatedDnaSequences("ACGTACGTAC"); });
H.CaseAnyOrder("overlapping repeat", new string[]{"AAAAAAAAAA"}, delegate {
    return new Solution().FindRepeatedDnaSequences("AAAAAAAAAAA"); });'''),

 P(id='k-closest', title='Find K Closest Elements', lesson='7.1', chapter='Ch 7',
   diff='Medium', evidence='Your list + LinkedIn tagged set', pattern='Binary search on a window',
   video='c7l1-k-closest/LinkedIn-Coding-7.1-K-Closest-Elements.mp4',
   statement='<p>Given a <b>sorted</b> array, an integer k and a target x, return the k elements '
             'closest to x, in ascending order. On a tie the smaller value wins.</p>',
   hint='The answer is always k consecutive elements, so the only unknown is where the window starts.',
   stub='public IList<int> FindClosestElements(int[] arr, int k, int x) {\n    \n}',
   harness='''H.Case("x inside", new int[]{1,2,3,4}, delegate {
    return new Solution().FindClosestElements(new int[]{1,2,3,4,5}, 4, 3); });
H.Case("x below range", new int[]{1,2,3,4}, delegate {
    return new Solution().FindClosestElements(new int[]{1,2,3,4,5}, 4, -1); });
H.Case("x above range", new int[]{4,5}, delegate {
    return new Solution().FindClosestElements(new int[]{1,2,3,4,5}, 2, 9); });
H.Case("k equals n", new int[]{1,2,3}, delegate {
    return new Solution().FindClosestElements(new int[]{1,2,3}, 3, 2); });
H.Case("tie prefers smaller", new int[]{1,2,3}, delegate {
    return new Solution().FindClosestElements(new int[]{1,2,3,4}, 3, 2); });'''),

 P(id='letter-combinations', title='Letter Combinations of a Phone Number', lesson='8.1',
   chapter='Ch 8', diff='Medium', evidence='Your list + LinkedIn tagged set',
   pattern='Backtracking', video='c8l1-letters/LinkedIn-Coding-8.1-Letter-Combinations.mp4',
   statement='<p>On a phone keypad 2 maps to <i>abc</i>, 3 to <i>def</i>, and so on to 9. Given a '
             'string of digits, return every letter combination the number could spell. Any order; '
             'empty input returns an empty list.</p>',
   hint='Choose, explore, un-choose. And note the output size is your complexity floor.',
   stub='public IList<string> LetterCombinations(string digits) {\n    \n}',
   harness='''H.CaseAnyOrder("\\"23\\"", new string[]{"ad","ae","af","bd","be","bf","cd","ce","cf"},
    delegate { return new Solution().LetterCombinations("23"); });
H.CaseAnyOrder("empty input", new string[]{}, delegate {
    return new Solution().LetterCombinations(""); });
H.CaseAnyOrder("single digit", new string[]{"a","b","c"}, delegate {
    return new Solution().LetterCombinations("2"); });
H.CaseAnyOrder("four-letter key", new string[]{"p","q","r","s"}, delegate {
    return new Solution().LetterCombinations("7"); });
H.Case("count for \\"234\\"", 27, delegate {
    return new Solution().LetterCombinations("234").Count; });'''),

 P(id='bulb-switcher', title='Bulb Switcher', lesson='8.2', chapter='Ch 8',
   diff='Medium', evidence='Your list', pattern='Maths &middot; reasoning out loud',
   video='c8l2-bulbs/LinkedIn-Coding-8.2-Bulb-Switcher.mp4',
   statement='<p>n bulbs start off. On pass i you toggle every i-th bulb, for i from 1 to n. '
             'How many bulbs are on at the end?</p>',
   hint='A bulb is toggled once per divisor. Divisors pair up — except when they do not.',
   stub='public int BulbSwitch(int n) {\n    \n}',
   harness='''H.Case("n=0", 0, delegate { return new Solution().BulbSwitch(0); });
H.Case("n=1", 1, delegate { return new Solution().BulbSwitch(1); });
H.Case("n=3", 1, delegate { return new Solution().BulbSwitch(3); });
H.Case("n=10", 3, delegate { return new Solution().BulbSwitch(10); });
H.Case("n=99", 9, delegate { return new Solution().BulbSwitch(99); });
H.Case("n=1000000", 1000, delegate { return new Solution().BulbSwitch(1000000); });'''),

 P(id='build-order', title='getBuildOrder', lesson='3.4', chapter='Ch 3',
   diff='Medium', evidence='Blind infra report + Glassdoor', pattern='Topological sort',
   video='c3l4-build-order/LinkedIn-Coding-3.4-Build-Order.mp4',
   statement='<p>Given build targets and dependency pairs <code>[a, b]</code> meaning '
             '<b>a must be built before b</b>, return a valid build order. '
             'Return an empty list if the dependencies contain a cycle.</p>'
             '<p>Any valid order is accepted &mdash; the tests check the ordering, not one answer.</p>',
   hint='Kahn\'s algorithm. The cycle check is free: count what you emitted.',
   stub='public IList<string> GetBuildOrder(IList<string> targets, IList<string[]> deps) {\n    \n}',
   harness='''Func<IList<string>, IList<string[]>, string> check = delegate (IList<string> targets, IList<string[]> deps) {
    IList<string> got = new Solution().GetBuildOrder(targets, deps);
    if (got == null) return "returned null";
    if (got.Count != targets.Count) return "expected " + targets.Count + " targets, got " + got.Count;
    Dictionary<string,int> at = new Dictionary<string,int>();
    for (int i = 0; i < got.Count; i++) {
        if (at.ContainsKey(got[i])) return "duplicate: " + got[i];
        at[got[i]] = i;
    }
    foreach (string t in targets) if (!at.ContainsKey(t)) return "missing: " + t;
    foreach (string[] d in deps)
        if (at[d[0]] > at[d[1]]) return d[0] + " must come before " + d[1];
    return null;
};

H.CaseCheck("a chain", "a valid order", delegate {
    return check(new List<string>{"a","b","c","d"},
                 new List<string[]>{ new string[]{"a","b"}, new string[]{"b","c"}, new string[]{"c","d"} }); });
H.CaseCheck("a diamond", "a valid order", delegate {
    return check(new List<string>{"a","b","c","d"},
                 new List<string[]>{ new string[]{"a","b"}, new string[]{"a","c"},
                                     new string[]{"b","d"}, new string[]{"c","d"} }); });
H.CaseCheck("no dependencies", "a valid order", delegate {
    return check(new List<string>{"a","b","c"}, new List<string[]>()); });
H.Case("cycle returns empty", 0, delegate {
    return new Solution().GetBuildOrder(new List<string>{"a","b"},
        new List<string[]>{ new string[]{"a","b"}, new string[]{"b","a"} }).Count; });
H.CaseCheck("single target", "a valid order", delegate {
    return check(new List<string>{"only"}, new List<string[]>()); });'''),
]


import leetcode as LC

from practice_more import MORE
PROBLEMS = PROBLEMS + MORE


def build():
    data = []
    for p in PROBLEMS:
        row = {k: p[k] for k in
               ('id', 'title', 'lesson', 'chapter', 'diff', 'evidence', 'pattern',
                'statement', 'hint', 'stub', 'harness', 'types', 'video', 'wrap')}
        href, num, exact, lc_note = LC.entry(LC.PRACTICE, p['id'])
        row['lc'] = {'url': href, 'num': num, 'exact': exact, 'note': lc_note}
        data.append(row)

    payload = 'var PRELUDE = %s;\nvar PROBLEMS = %s;\n' % (
        json.dumps(PRELUDE), json.dumps(data))
    with open(os.path.join(lib.OUT, 'assets', 'problems.js'), 'w', encoding='utf-8') as f:
        f.write(payload)

    body = sec('how', 'How this works',
        card(rich(
          'Pick a problem, write C# in the editor, press **Run** (or &#8984;&#8629;). The page '
          'assembles a complete program &mdash; your code plus a generated test harness &mdash; '
          'compiles it with **your own dotnet**, and shows each case with what it expected and '
          'what it got. The tests include the edge cases the matching lesson calls out.\n\n'
          'Execution is local, so start the runner and use the URL it prints:\n')) +
        '<div class="codeblock"><pre>python3 companies/linkedin/runner.py</pre></div>' +
        note(rich(
          '**Anywhere else &mdash; including the deployed site &mdash; there is no compiler.** '
          'Every problem carries a **LeetCode link** instead, which runs against their judge and '
          'needs nothing installed. A few questions are LinkedIn-only and have no LeetCode '
          'equivalent; those say so.'), kind='', label='Away from your machine'),
        kicker='Practice', why='Write it, run it, see which edge case you missed')

    body += ('<section class="sec" id="sec-run"><div class="sec-h"><div>'
             '<span class="kicker">Runner</span><h2 id="run">Problems</h2></div>'
             '<span class="why">%d problems from the reported set &middot; C# &middot; '
             'tests include the edge cases each lesson names</span></div>'
             '<div id="practice"></div></section>' % len(PROBLEMS))

    return lib.page('07-practice.html', 'Code practice',
        'Write and run C# against the reported LinkedIn questions, with the edge cases from each lesson as tests.',
        body, crumb_tail='Code practice', autonav=False,
        hero_chips=[('', '%d problems' % len(PROBLEMS)), ('', 'C#'),
                    ('', 'runs locally, or on LeetCode')],
        extra_head='<link rel="stylesheet" href="assets/practice.css">',
        tail_scripts=['assets/problems.js', 'assets/practice.js'])
