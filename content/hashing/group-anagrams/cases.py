def visual():
    return (["tea", "eat", "tan", "ate", "nat", "bat"],)


def fixed():
    return [([],), (["a"],), (["", ""],), (["ab", "ba", "abc"],), (["aab", "abb"],)]


def cases(n, rng):
    stems = ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 5))) for _ in range(max(1, n // 3))]
    words = []
    for _ in range(n):
        letters = list(rng.choice(stems))
        rng.shuffle(letters)
        words.append("".join(letters))
    return [(words,)]


def check(case, got, expected):
    def norm(groups):
        return sorted(sorted(g) for g in groups)

    try:
        return norm(got) == norm(expected)
    except TypeError:
        return False
