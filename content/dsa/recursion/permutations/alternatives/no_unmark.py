# expect: fail
# Forgets to clear used[i] when backtracking, so later branches run out of values.
def solve(nums):
    result = []
    order = []
    used = [False] * len(nums)

    def place():
        if len(order) == len(nums):
            result.append(order[:])
            return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True
                order.append(nums[i])
                place()
                order.pop()

    place()
    return result
