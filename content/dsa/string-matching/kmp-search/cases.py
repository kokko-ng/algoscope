def visual():
    return (list("abababcababc"), list("ababc"))


def fixed():
    return [
        ([], ["a"]),
        (["a"], ["a"]),
        (["a"], ["b"]),
        (list("ab"), list("abc")),
        (list("aaaa"), list("aa")),
        (list("aaab"), list("aab")),
        (list("abcabcab"), list("cab")),
        (list("abababab"), list("abab")),
    ]


def cases(n, rng):
    alphabet = rng.choice(["ab", "abc", "abcd"])
    text = [rng.choice(alphabet) for _ in range(n)]
    m = rng.randint(1, max(1, min(6, n)))
    if n >= m and rng.random() < 0.6:
        start = rng.randrange(n - m + 1)
        pattern = text[start : start + m]
    else:
        pattern = [rng.choice(alphabet) for _ in range(m)]
    return [(text, pattern)]


def bench(n, rng):
    m = n // 2
    return [(["a"] * (n - 1) + ["b"], ["a"] * (m - 1) + ["b"])]
