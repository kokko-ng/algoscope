class HashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(4)]
        self.size = 0

    def _index(self, key):
        return hash(key) % len(self.buckets)

    def _grow(self):
        old = self.buckets
        self.buckets = [[] for _ in range(2 * len(old))]
        for bucket in old:
            for pair in bucket:
                self.buckets[self._index(pair[0])].append(pair)

    def put(self, key, value):
        bucket = self.buckets[self._index(key)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self.size += 1
        if self.size > len(self.buckets):
            self._grow()

    def get(self, key):
        for pair in self.buckets[self._index(key)]:
            if pair[0] == key:
                return pair[1]
        return None

    def remove(self, key):
        bucket = self.buckets[self._index(key)]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket[i] = bucket[-1]
                bucket.pop()
                self.size -= 1
                return True
        return False

    def __len__(self):
        return self.size
