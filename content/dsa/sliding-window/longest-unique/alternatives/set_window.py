# expect: pass
# A set holds the window; drop letters from the left until the new letter is no longer inside.
def solve(letters):
    window = set()
    best = 0
    left = 0
    for letter in letters:
        while letter in window:
            window.remove(letters[left])
            left += 1
        window.add(letter)
        best = max(best, len(window))
    return best
