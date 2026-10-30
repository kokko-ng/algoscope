# expect: fail
# Functional quicksort that returns a new sorted list and leaves values untouched.
def solve(values):
    if len(values) <= 1:
        return values
    pivot = values[len(values) // 2]
    less = [v for v in values if v < pivot]
    same = [v for v in values if v == pivot]
    more = [v for v in values if v > pivot]
    return solve(less) + same + solve(more)
