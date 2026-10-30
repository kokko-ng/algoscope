# expect: slow
# Try each candidate length and re-check every word from the start each time.
def solve(words):
    if not words:
        return ""
    best = ""
    for length in range(1, len(words[0]) + 1):
        candidate = words[0][:length]
        for w in words:
            if w[:length] != candidate:
                return best
        best = candidate
    return best
