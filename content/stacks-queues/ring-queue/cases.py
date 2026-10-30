def visual():
    return [
        ("__init__", 4),
        ("enqueue", 1), ("enqueue", 2), ("enqueue", 3), ("dequeue",), ("dequeue",),
        ("enqueue", 4), ("enqueue", 5), ("enqueue", 6), ("enqueue", 7), ("peek",), ("dequeue",), ("__len__",),
    ]


def fixed():
    return [
        [("dequeue",), ("peek",), ("__len__",)],
        [("__init__", 1), ("enqueue", 1), ("enqueue", 2), ("enqueue", 3), ("dequeue",), ("dequeue",), ("dequeue",), ("dequeue",)],
        [("__init__", 2), ("enqueue", 1), ("dequeue",), ("enqueue", 2), ("enqueue", 3), ("enqueue", 4), ("peek",), ("dequeue",), ("dequeue",), ("dequeue",)],
    ]


def cases(n, rng):
    ops = [("__init__", rng.randint(1, 4))]
    size = 0
    for _ in range(n):
        r = rng.random()
        if r < 0.5:
            ops.append(("enqueue", rng.randint(0, 99)))
            size += 1
        elif r < 0.8:
            ops.append(("dequeue",))
            size = max(0, size - 1)
        elif r < 0.9:
            ops.append(("peek",))
        else:
            ops.append(("__len__",))
    ops += [("dequeue",) for _ in range(size)] + [("__len__",)]
    return [ops]


def bench(n, rng):
    # a long queue that stays long: shifting every element on dequeue costs O(n) each time
    ops = [("__init__", 4)]
    ops += [("enqueue", i) for i in range(n)]
    for i in range(n):
        ops.append(("dequeue",))
        ops.append(("enqueue", n + i))
    ops.append(("__len__",))
    return [ops]
