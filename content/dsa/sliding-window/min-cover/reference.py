def solve(stream, needed):
    missing = {}
    for item in needed:
        missing[item] = missing.get(item, 0) + 1
    outstanding = len(needed)
    best = 0
    left = 0
    for right in range(len(stream)):
        item = stream[right]
        if missing.get(item, 0) > 0:
            outstanding -= 1
        missing[item] = missing.get(item, 0) - 1
        while outstanding == 0:
            length = right - left + 1
            if best == 0 or length < best:
                best = length
            gone = stream[left]
            missing[gone] += 1
            if missing[gone] > 0:
                outstanding += 1
            left += 1
    return best
