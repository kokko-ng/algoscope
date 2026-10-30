def _word(rng, letters, lo, hi):
    return "".join(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def visual():
    return (["car", "cart", "cat", "dog", "do", "care"], ["ca", "car", "d", "z"])


def fixed():
    return [
        ([], ["a", ""]),
        (["a"], []),
        (["", "a"], ["", "a", "aa"]),
        (["ab", "ab", "abc"], ["ab", "abc", "b"]),
    ]


def cases(n, rng):
    words = [_word(rng, "abc", 0, 5) for _ in range(n)]
    prefixes = [_word(rng, "abc", 0, 3) for _ in range(max(1, n // 2))]
    return [(words, prefixes)]


def bench(n, rng):
    words = [_word(rng, "abcd", 6, 6) for _ in range(n)]
    prefixes = [_word(rng, "abcd", 1, 3) for _ in range(n)]
    return [(words, prefixes)]
