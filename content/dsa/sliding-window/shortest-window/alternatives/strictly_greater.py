# expect: fail
# Requires the sum to exceed target, but "at least target" includes equality.
def solve(nums, target):
    best = 0
    window_sum = 0
    left = 0
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum > target:
            length = right - left + 1
            if best == 0 or length < best:
                best = length
            window_sum -= nums[left]
            left += 1
    return best
