def solve(letters):
    last_seen = {}
    best = 0
    left = 0
    for right in range(len(letters)):
        letter = letters[right]
        if letter in last_seen and last_seen[letter] >= left:
            left = last_seen[letter] + 1
        last_seen[letter] = right
        best = max(best, right - left + 1)
    return best
