# expect: bronze
# Count every value with a full scan: O(n^2).
def solve(nums):
    for value in nums:
        if nums.count(value) == 1:
            return value
