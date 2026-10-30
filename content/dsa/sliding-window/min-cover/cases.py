def visual():
    return (list("adobecab"), list("abc"))


def fixed():
    return [
        ([], ["a"]),
        (["a"], ["a"]),
        (["a"], ["b"]),
        (["a", "a"], ["a", "a"]),
        (["a", "b"], ["a", "a"]),
        (list("bba"), list("ab")),
    ]


def cases(n, rng):
    alphabet = "abcdefgh"[: rng.randint(2, 8)]
    stream = [rng.choice(alphabet) for _ in range(n)]
    needed = [rng.choice(alphabet) for _ in range(rng.randint(1, max(1, n // 4)))]
    return [(stream, needed)]


def bench(n, rng):
    stream = [rng.choice("abcdef") for _ in range(n)]
    return [(stream, list("abcdef"))]
