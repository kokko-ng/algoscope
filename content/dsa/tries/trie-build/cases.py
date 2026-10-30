def _word(rng, letters, lo, hi):
    return "".join(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def visual():
    return [
        ("insert", "car"),
        ("insert", "cat"),
        ("insert", "cart"),
        ("search", "ca"),
        ("starts_with", "ca"),
        ("search", "cart"),
        ("insert", "do"),
        ("search", "dog"),
        ("starts_with", "x"),
    ]


def fixed():
    return [
        [("search", "a"), ("starts_with", "a"), ("starts_with", "")],
        [("insert", ""), ("search", ""), ("search", "a")],
        [("insert", "abc"), ("search", "ab"), ("starts_with", "ab"), ("search", "abc"), ("search", "abcd")],
        [("insert", "ab"), ("insert", "ab"), ("insert", "abc"), ("search", "ab"), ("starts_with", "abcd")],
    ]


def cases(n, rng):
    ops = []
    words = []
    for _ in range(n):
        r = rng.random()
        if r < 0.5 or not words:
            w = _word(rng, "abc", 1, 5)
            words.append(w)
            ops.append(("insert", w))
        else:
            probe = rng.choice(words)[: rng.randint(0, 5)] if rng.random() < 0.6 else _word(rng, "abc", 0, 5)
            ops.append(("search" if r < 0.75 else "starts_with", probe))
    return [ops]


def bench(n, rng):
    words = [_word(rng, "abcd", 6, 8) for _ in range(n // 2)]
    ops = [("insert", w) for w in words]
    for i in range(n // 2):
        w = rng.choice(words)
        if i % 2:
            ops.append(("search", w if rng.random() < 0.5 else _word(rng, "abcd", 6, 8)))
        else:
            ops.append(("starts_with", w[: rng.randint(2, 6)]))
    return [ops]
