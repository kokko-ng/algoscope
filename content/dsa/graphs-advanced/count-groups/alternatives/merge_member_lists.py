# expect: pass
# Label every item with its group and move the smaller group's members into the larger one.
def solve(n, pairs):
    label = list(range(n))
    members = [[i] for i in range(n)]
    groups = n
    counts = []
    for a, b in pairs:
        la, lb = label[a], label[b]
        if la != lb:
            if len(members[la]) < len(members[lb]):
                la, lb = lb, la
            for x in members[lb]:
                label[x] = la
                members[la].append(x)
            members[lb] = []
            groups -= 1
        counts.append(groups)
    return counts
