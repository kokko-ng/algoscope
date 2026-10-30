# expect: slow
# Search for the first operator and splice its result into the list: O(n) per operator.
def solve(tokens):
    tokens = list(tokens)
    while len(tokens) > 1:
        i = 0
        while tokens[i] not in ("+", "-", "*", "/"):
            i += 1
        left, right = int(tokens[i - 2]), int(tokens[i - 1])
        op = tokens[i]
        if op == "+":
            value = left + right
        elif op == "-":
            value = left - right
        elif op == "*":
            value = left * right
        else:
            q = abs(left) // abs(right)
            value = q if (left < 0) == (right < 0) else -q
        tokens[i - 2 : i + 1] = [str(value)]
    return int(tokens[0])
