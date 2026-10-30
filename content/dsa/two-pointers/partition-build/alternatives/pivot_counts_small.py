# expect: fail
# Wrong tie rule: values equal to the pivot go into the small group.
def solve(nums, pivot):
    boundary = 0
    for scan in range(len(nums)):
        if nums[scan] <= pivot:
            nums[boundary], nums[scan] = nums[scan], nums[boundary]
            boundary += 1
