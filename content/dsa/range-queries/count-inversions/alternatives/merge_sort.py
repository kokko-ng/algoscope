# expect: pass
# Merge sort: when a value from the right half is placed first, it jumps every value left in the left half.
def solve(nums):
    def sort(items):
        if len(items) <= 1:
            return items, 0
        mid = len(items) // 2
        left, a = sort(items[:mid])
        right, b = sort(items[mid:])
        merged = []
        count = a + b
        i = j = 0
        while i < len(left) and j < len(right):
            if right[j] < left[i]:
                merged.append(right[j])
                count += len(left) - i
                j += 1
            else:
                merged.append(left[i])
                i += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, count

    return sort(nums)[1]
