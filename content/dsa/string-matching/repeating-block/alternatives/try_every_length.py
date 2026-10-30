# expect: slow
# Tries each block length that divides n and checks the whole text against it.
def solve(text):
    n = len(text)
    for size in range(1, n + 1):
        if n % size:
            continue
        ok = True
        for i in range(size, n):
            if text[i] != text[i - size]:
                ok = False
                break
        if ok:
            return size
    return n
