# expect: pass
# Hoare partition with an explicit stack of ranges instead of recursion.
def solve(values):
    stack = [(0, len(values) - 1)]
    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        pivot = values[(low + high) // 2]
        i, j = low, high
        while i <= j:
            while values[i] < pivot:
                i += 1
            while values[j] > pivot:
                j -= 1
            if i <= j:
                values[i], values[j] = values[j], values[i]
                i += 1
                j -= 1
        stack.append((low, j))
        stack.append((i, high))
