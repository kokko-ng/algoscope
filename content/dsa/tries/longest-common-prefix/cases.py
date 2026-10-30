def _word(rng, letters, lo, hi):
    return "".join(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def visual():
    return (["flower", "flow", "flight", "flask"],)


def fixed():
    return [
        ([],),
        ([""],),
        (["a"],),
        (["ab", "a"],),
        (["abc", "abd"],),
        (["x", "y"],),
        (["same", "same"],),
        (["abc", "", "abc"],),
    ]


def cases(n, rng):
    shared = _word(rng, "ab", 0, 4)
    return [([shared + _word(rng, "ab", 0, 4) for _ in range(n)],)]


def bench(n, rng):
    # a few words whose shared prefix grows with n: repeated prefix checks cost O(L^2), one pass costs O(L)
    shared = _word(rng, "abcd", n, n)
    return [([shared + _word(rng, "abcd", 1, 3) for _ in range(8)],)]
