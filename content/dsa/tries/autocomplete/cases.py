def _word(rng, letters, lo, hi):
    return "".join(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def visual():
    return (["card", "car", "cat", "care", "dog", "do", "dot"], ["ca", "car", "do", "x"])


def fixed():
    return [
        ([], ["", "a"]),
        (["a"], []),
        (["b", "a", "c", "d"], [""]),
        (["ab", "ab", "abc", "abd", "abe"], ["ab", "abc", "abz"]),
        (["", "a"], ["", "a"]),
    ]


def cases(n, rng):
    words = [_word(rng, "abc", 0, 5) for _ in range(n)]
    queries = [_word(rng, "abc", 0, 3) for _ in range(max(1, n // 2))]
    return [(words, queries)]


def bench(n, rng):
    words = [_word(rng, "abcd", 5, 7) for _ in range(n)]
    queries = [_word(rng, "abcd", 2, 4) for _ in range(n)]
    return [(words, queries)]
