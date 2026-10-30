# expect: slow
# Scan right from every position for the first larger value: correct, but O(n^2) on falling input.
def solve(nums):
    result = []
    for i in range(len(nums)):
        found = -1
        for j in range(i + 1, len(nums)):
            if nums[j] > nums[i]:
                found = nums[j]
                break
        result.append(found)
    return result
