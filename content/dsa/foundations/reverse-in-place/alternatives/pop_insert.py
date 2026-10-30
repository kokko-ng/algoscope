# expect: slow
# Pop the last item and insert it at position i: in place, but each insert shifts O(n) items.
def solve(items):
    for i in range(len(items)):
        items.insert(i, items.pop())
