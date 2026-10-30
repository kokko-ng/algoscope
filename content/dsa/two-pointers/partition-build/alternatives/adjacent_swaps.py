# expect: slow
# Bubble small values left with adjacent swaps until none move: in place, but O(n^2).
def solve(nums, pivot):
    moved = True
    while moved:
        moved = False
        for i in range(len(nums) - 1):
            if nums[i] >= pivot and nums[i + 1] < pivot:
                nums[i], nums[i + 1] = nums[i + 1], nums[i]
                moved = True
