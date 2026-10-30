def solve(items):
    a, b = 0, len(items) - 1
    while a < b:
        items[a], items[b] = items[b], items[a]
        a += 1
        b -= 1
