# expect: pass
# Literal reading: grow at 3/4 load, delete with del, and put returns whether the key was new.
class HashMap:
    def __init__(self):
        self.buckets = [[] for _ in range(8)]
        self.count = 0

    def put(self, key, value):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return False
        bucket.append([key, value])
        self.count += 1
        if 4 * self.count > 3 * len(self.buckets):
            old = self.buckets
            self.buckets = [[] for _ in range(2 * len(old))]
            for chain in old:
                for pair in chain:
                    self.buckets[hash(pair[0]) % len(self.buckets)].append(pair)
        return True

    def get(self, key):
        for k, v in self.buckets[hash(key) % len(self.buckets)]:
            if k == key:
                return v
        return None

    def remove(self, key):
        bucket = self.buckets[hash(key) % len(self.buckets)]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                del bucket[i]
                self.count -= 1
                return True
        return False

    def __len__(self):
        return self.count
