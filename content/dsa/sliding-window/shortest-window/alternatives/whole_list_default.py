# expect: fail
# Starts best at len(nums), assuming the whole list always reaches target, so "no run" never returns 0.
def solve(nums, target):
    best = len(nums)
    window_sum = 0
    left = 0
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum >= target:
            best = min(best, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return best
