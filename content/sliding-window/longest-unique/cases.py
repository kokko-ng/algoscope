def visual():
    return (list("abcabdbea"),)


def fixed():
    return [([],), (["a"],), (list("aaaa"),), (list("abcd"),), (list("abba"),), (list("dvdf"),)]


def cases(n, rng):
    alphabet = "abcdefghijklmnopqrstuvwxyz"[: rng.randint(2, 26)]
    return [([rng.choice(alphabet) for _ in range(n)],)]
