def visual():
    return (list("abracadabra"), [list("abr"), list("cad"), list("bra")])


def fixed():
    return [
        ([], [["a"]]),
        (["a"], [["a"]]),
        (list("abc"), [list("abcd")]),
        (list("aaaa"), [list("aa")]),
        (list("abab"), [list("ab"), list("ba"), list("ab")]),
        (list("xyz"), [list("zy"), list("yx")]),
    ]


def cases(n, rng):
    alphabet = rng.choice(["ab", "abc", "abcdef"])
    text = [rng.choice(alphabet) for _ in range(n)]
    m = rng.randint(1, max(1, min(5, n)))
    patterns = []
    for _ in range(rng.randint(1, 4)):
        if n >= m and rng.random() < 0.6:
            start = rng.randrange(n - m + 1)
            patterns.append(text[start : start + m])
        else:
            patterns.append([rng.choice(alphabet) for _ in range(m)])
    return [(text, patterns)]


def bench(n, rng):
    m = n // 4
    text = ["a"] * (n - 1) + ["b"]
    patterns = [["a"] * (m - 1 - j) + ["b"] + ["a"] * j for j in range(4)]
    return [(text, patterns)]
