# expect: pass
# count shifts through every bit position instead of clearing set bits: still correct.
class Bitset:
    def __init__(self):
        self.bits = 0

    def add(self, i):
        self.bits |= 1 << i

    def remove(self, i):
        if self.bits >> i & 1:
            self.bits -= 1 << i

    def contains(self, i):
        return (self.bits & (1 << i)) != 0

    def union(self, mask):
        self.bits |= mask

    def intersect(self, mask):
        self.bits &= mask

    def mask(self):
        return self.bits

    def count(self):
        total = 0
        rest = self.bits
        while rest:
            total += rest & 1
            rest >>= 1
        return total
