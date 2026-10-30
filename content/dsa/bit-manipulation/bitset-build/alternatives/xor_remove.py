# expect: fail
# remove flips the bit with XOR, so removing a non-member adds it.
class Bitset:
    def __init__(self):
        self.bits = 0

    def add(self, i):
        self.bits |= 1 << i

    def remove(self, i):
        self.bits ^= 1 << i

    def contains(self, i):
        return self.bits >> i & 1 == 1

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
            rest &= rest - 1
            total += 1
        return total
