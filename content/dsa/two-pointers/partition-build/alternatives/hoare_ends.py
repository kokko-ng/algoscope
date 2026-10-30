# expect: pass
# Pointers from both ends that swap a misplaced pair, returning nothing.
def solve(nums, pivot):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        if nums[lo] < pivot:
            lo += 1
        elif nums[hi] >= pivot:
            hi -= 1
        else:
            nums[lo], nums[hi] = nums[hi], nums[lo]
