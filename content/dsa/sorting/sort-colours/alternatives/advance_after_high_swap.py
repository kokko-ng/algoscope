# expect: fail
# Advances mid after swapping with high, so the value swapped in is never examined.
def solve(colours):
    low, mid, high = 0, 0, len(colours) - 1
    while mid <= high:
        if colours[mid] == 0:
            colours[low], colours[mid] = colours[mid], colours[low]
            low += 1
        elif colours[mid] == 2:
            colours[mid], colours[high] = colours[high], colours[mid]
            high -= 1
        mid += 1
