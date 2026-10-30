# expect: pass
# Literal reading: separate leftmost and rightmost searches on a closed window, returning a tuple.
def solve(nums, target):
    def edge(leftmost):
        lo, hi, found = 0, len(nums) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                found = mid
                if leftmost:
                    hi = mid - 1
                else:
                    lo = mid + 1
            elif nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return found

    return (edge(True), edge(False))
