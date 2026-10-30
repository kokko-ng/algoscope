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
            quotient = abs(left) // abs(right)
            stack.append(quotient if (left < 0) == (right < 0) else -quotient)
    return stack[0]
