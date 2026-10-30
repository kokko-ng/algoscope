# expect: fail
# remove deletes the pair but forgets to decrement the size.
class HashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(4)]
        self.size = 0

    def _grow(self):
        old = self.buckets
        self.buckets = [[] for _ in range(2 * len(old))]
        for bucket in old:
            for pair in bucket:
                self.buckets[hash(pair[0]) % len(self.buckets)].append(pair)

    def put(self, key, value):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self.size += 1
        if self.size > len(self.buckets):
            self._grow()

    def get(self, key):
        for pair in self.buckets[hash(key) % len(self.buckets)]:
            if pair[0] == key:
                return pair[1]
        return None

    def remove(self, key):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                del bucket[i]
                return True
        return False

    def __len__(self):
        return self.size
