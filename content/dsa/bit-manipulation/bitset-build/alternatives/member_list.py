# expect: bronze
# A list of members: every membership test scans it, O(n) per operation.
class Bitset:
    def __init__(self):
        self.members = []

    def add(self, i):
        if i not in self.members:
            self.members.append(i)

    def remove(self, i):
        if i in self.members:
            self.members.remove(i)

    def contains(self, i):
        return i in self.members

    def union(self, mask):
        i = 0
        while mask >> i:
            if mask >> i & 1:
                self.add(i)
            i += 1

    def intersect(self, mask):
        self.members = [i for i in self.members if mask >> i & 1]

    def mask(self):
        total = 0
        for i in self.members:
            total |= 1 << i
        return total

    def count(self):
        return len(self.members)
