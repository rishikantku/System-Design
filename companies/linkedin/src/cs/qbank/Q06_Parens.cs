// Q6 — are the parentheses in a mixed string correctly matched?
public static class ParenCheck {

    // One bracket type, so a signed counter is enough: no stack, O(1) space.
    // Every other character is irrelevant and is skipped.
    public static bool IsBalanced(string s) {
        if (string.IsNullOrEmpty(s)) return true;

        int open = 0;
        foreach (char c in s) {
            if (c == '(') open++;
            else if (c == ')') {
                open--;
                if (open < 0) return false;   // a close with nothing open: fail immediately
            }
        }
        return open == 0;                     // anything left open at the end is unmatched
    }

    // The moment there is more than one bracket type, the counter stops working:
    // "([)]" has balanced counts and is still wrong. That needs the stack.
    public static bool IsBalancedMultiType(string s) {
        if (string.IsNullOrEmpty(s)) return true;

        var partner = new Dictionary<char, char> { [')'] = '(', [']'] = '[', ['}'] = '{' };
        var stack = new Stack<char>();

        foreach (char c in s) {
            if (c == '(' || c == '[' || c == '{') stack.Push(c);
            else if (partner.TryGetValue(c, out char want)) {
                if (stack.Count == 0 || stack.Pop() != want) return false;
            }
        }
        return stack.Count == 0;
    }
}
