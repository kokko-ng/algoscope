# expect: slow
# Naive growth: extend every known subset by every value and keep it if it is not already listed.
def solve(nums):
    result = [[]]
    grew = True
    while grew:
        grew = False
        for s in result[:]:
            for v in nums:
                if v not in s:
                    t = s + [v]
                    t.sort()
                    if t not in result:
                        result.append(t)
                        grew = True
    return result
