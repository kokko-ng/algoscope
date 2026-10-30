def visual():
    return ("stone", "notes")


def fixed():
    return [
        ("", ""),
        ("", "abc"),
        ("abc", ""),
        ("abc", "abc"),
        ("abc", "def"),
        ("abcde", "ace"),
        ("aaaa", "aa"),
    ]


def cases(n, rng):
    alphabet = rng.choice(["ab", "abc", "abcdef"])
    a = "".join(rng.choice(alphabet) for _ in range(n))
    b = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, n + 2)))
    return [(a, b)]


def bench(n, rng):
    a = "".join(rng.choice("abcd") for _ in range(n))
    b = "".join(rng.choice("abcd") for _ in range(n))
    return [(a, b)]
