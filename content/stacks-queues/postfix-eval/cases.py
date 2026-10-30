def truncate_div(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def expression(operands, rng):
    """A random valid postfix expression with `operands` numbers, avoiding division by zero and huge values."""
    tokens, values, left = [], [], operands
    while left or len(values) > 1:
        if len(values) >= 2 and (left == 0 or rng.random() < 0.45):
            right, a = values.pop(), values.pop()
            ops = ["+", "-"]
            if right != 0:
                ops.append("/")
            if abs(a * right) < 10**6:
                ops.append("*")
            op = rng.choice(ops)
            values.append({"+": a + right, "-": a - right, "*": a * right, "/": truncate_div(a, right) if right else 0}[op])
            tokens.append(op)
        else:
            v = rng.randint(-20, 20)
            tokens.append(str(v))
            values.append(v)
            left -= 1
    return tokens


def visual():
    return (["5", "1", "2", "+", "4", "*", "+", "3", "-"],)


def fixed():
    return [(["7"],), (["-7", "2", "/"],), (["7", "-2", "/"],), (["2", "3", "-"],), (["6", "3", "/", "4", "*"],)]


def cases(n, rng):
    return [(expression(max(n, 1), rng),)]


def bench(n, rng):
    # every operator at the end: 1 2 3 ... + - + ..., so the first operator sits far from the start
    tokens = [str(i % 9 + 1) for i in range(n + 1)]
    tokens += ["+" if i % 2 else "-" for i in range(n)]
    return [(tokens,)]
