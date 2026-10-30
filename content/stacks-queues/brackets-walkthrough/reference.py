def solve(chars):
    closers = {")": "(", "]": "[", "}": "{"}
    stack = []
    for i in range(len(chars)):
        ch = chars[i]
        if ch in "([{":
            stack.append(ch)
        elif ch in closers:
            if not stack or stack.pop() != closers[ch]:
                return False
    return not stack
