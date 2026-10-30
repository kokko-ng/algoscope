# expect: fail
# Jumps to the last copy even when it is already left of the window, so left moves backwards ("abba").
def solve(letters):
    last_seen = {}
    best = 0
    left = 0
    for right in range(len(letters)):
        letter = letters[right]
        if letter in last_seen:
            left = last_seen[letter] + 1
        last_seen[letter] = right
        best = max(best, right - left + 1)
    return best
