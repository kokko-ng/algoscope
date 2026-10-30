# expect: fail
# Ignores order: pops the operands as if the first pop were the left one.
def solve(tokens):
    stack = []
    for token in tokens:
        if token not in ("+", "-", "*", "/"):
            stack.append(int(token))
            continue
        left = stack.pop()
        right = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        elif token == "*":
            stack.append(left * right)
        else:
            q = abs(left) // abs(right)
            stack.append(q if (left < 0) == (right < 0) else -q)
    return stack[0]
