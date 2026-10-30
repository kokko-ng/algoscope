# expect: pass
# A table of operator functions, with truncating division written as int(left / right).
OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: int(a / b),
}


def solve(tokens):
    stack = []
    for token in tokens:
        if token in OPS:
            right = stack.pop()
            stack[-1] = OPS[token](stack[-1], right)
        else:
            stack.append(int(token))
    return stack.pop()
