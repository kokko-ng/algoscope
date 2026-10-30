# expect: slow
# Copies every window into a tuple and looks it up in a set: O(n * m).
def solve(text, patterns):
    m = len(patterns[0])
    wanted = {tuple(pattern) for pattern in patterns}
    return [i for i in range(len(text) - m + 1) if tuple(text[i : i + m]) in wanted]
