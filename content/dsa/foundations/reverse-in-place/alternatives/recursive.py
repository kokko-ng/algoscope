# expect: pass
# Recursive outside-in swap instead of a while loop, returning items for convenience.
def solve(items):
    def swap(a, b):
        if a < b:
            items[a], items[b] = items[b], items[a]
            swap(a + 1, b - 1)

    swap(0, len(items) - 1)
    return items
