def solve(nums, k):
    sums = []
    window_sum = 0
    left = 0
    for right in range(len(nums)):
        window_sum += nums[right]
        if right - left + 1 > k:
            window_sum -= nums[left]
            left += 1
        if right - left + 1 == k:
            sums.append(window_sum)
    return sums
