def visual():
    return ([2, 5, 8, 11, 14, 17, 20],)


def fixed():
    return [([],), ([4],), ([1, 2],), ([1, 2, 3],), ([1, 2, 3, 4],), ([-5, -1, 0, 7, 9, 12],)]


def cases(n, rng):
    return [(sorted(rng.sample(range(-5 * n - 5, 5 * n + 5), n)),)]


def bench(n, rng):
    return [(list(range(n)),)]


def check(case, got, expected):
    nums = case[0]
    if got is None:
        return not nums
    values = []

    def height(node):
        if node is None:
            return 0
        if len(values) > len(nums):
            msg = "too many nodes"
            raise ValueError(msg)
        left = height(node.left)
        values.append(node.val)
        right = height(node.right)
        if left < 0 or right < 0 or abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return height(got) >= 0 and values == list(nums)
