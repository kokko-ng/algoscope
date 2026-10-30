# expect: fail
# Uses Python's // for division, which floors (-7 // 2 is -4) instead of truncating toward zero.
def solve(tokens):
    stack = []
    for token in tokens:
        if token not in ("+", "-", "*", "/"):
            stack.append(int(token))
            continue
        right = stack.pop()
        left = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            stack.append(left // right)
    return stack[0]
