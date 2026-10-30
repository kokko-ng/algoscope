# System design: a guide with Python samples

## About this guide

This guide explains the system design topics in the algoscope curriculum.
The text uses ASD-STE100 Simplified Technical English.
Each sentence is short and has one instruction or one fact.
Technical names, for example "load balancing", "caching" and "sharding", are used as they are.

In system design, you select components and connect them, so that a service meets its requirements.
Most decisions start with a number.
Most decisions also give a trade-off.

Each section gives:

1. The purpose of the technique.
2. The key ideas and the procedures that it uses.
3. A table of figures or of trade-offs.
4. A Python sample. The sample ends with `assert` lines that show the correct results.

NOTE: The test `harness/tests/test_guide.py` runs each Python sample in this guide.
If you change a sample, run the test again.

NOTE: The figures in this guide are orders of magnitude.
Use them for estimates. Measure your own system before you buy hardware.

## Contents

1. [Back-of-the-envelope estimation](#back-of-the-envelope-estimation)
2. [Scaling the web tier](#scaling-the-web-tier)
3. [Caching](#caching)
4. [Databases and replication](#databases-and-replication)
5. [Partitioning and sharding](#partitioning-and-sharding)
6. [Consistency and quorums](#consistency-and-quorums)
7. [Queues and asynchronous work](#queues-and-asynchronous-work)
8. [Rate limits and resilience](#rate-limits-and-resilience)
9. [Availability and reliability](#availability-and-reliability)
10. [Performance and observability](#performance-and-observability)
11. [Case study: URL shortener](#case-study-url-shortener)
12. [Case study: news feed](#case-study-news-feed)
13. [Case study: chat service](#case-study-chat-service)
14. [How to approach a design](#how-to-approach-a-design)

## Back-of-the-envelope estimation

A back-of-the-envelope estimate is a quick calculation with round numbers.
It shows the size of the problem before you select components.
The result must be correct to within a factor of about 2. It does not need to be exact.

Each later decision depends on these numbers.
For example, 50 requests per second fit on one server.
50,000 requests per second need a load balancer, a cache and many servers.

### Round numbers to remember

| Quantity | Exact value | Round value |
|---|---|---|
| Seconds in a day | 86,400 | 10^5 |
| Seconds in a 30-day month | 2,592,000 | 2.5 x 10^6 |
| Seconds in a year | 31,536,000 | 3 x 10^7 |
| 1 million requests a day | 11.6 per second | 12 per second |
| 1 billion requests a day | 11,574 per second | 12,000 per second |

| Unit | Bytes | Example |
|---|---|---|
| 1 KB | 10^3 | A short text record |
| 1 MB | 10^6 | A compressed photo |
| 1 GB | 10^9 | The memory of a small process |
| 1 TB | 10^12 | One large disk |
| 1 PB | 10^15 | Many racks of disks |

NOTE: This guide uses powers of ten for data sizes.
A kibibyte (KiB) is 1,024 bytes.
The difference is less than 13% up to the petabyte, so it does not change an estimate.

### Latency numbers

The table gives the classic latency numbers as orders of magnitude.
Hardware becomes faster each year, but the ratios between the rows change slowly.

| Operation | Time | Relative to a memory reference |
|---|---|---|
| CPU cache reference | 1 ns | 1/100 |
| Main memory reference | 100 ns | 1 |
| Send 1 KB over a 1 Gbps network | 10 us | 100 |
| Random read of 4 KB from an SSD | 150 us | 1,500 |
| Sequential read of 1 MB from memory | 250 us | 2,500 |
| Round trip in the same data center | 0.5 ms | 5,000 |
| Sequential read of 1 MB from an SSD | 1 ms | 10,000 |
| Disk seek | 10 ms | 100,000 |
| Sequential read of 1 MB from a disk | 20 ms | 200,000 |
| Round trip from California to Europe | 150 ms | 1,500,000 |

Three rules come from this table:

- Memory is about 1,000 times faster than an SSD for random reads.
- A network round trip in one data center costs less than a disk seek.
- A round trip between continents costs more than almost all local work. Only data near the user decreases it.

### Estimation procedure

To estimate the load of a service, do these steps:

1. Write the number of daily active users (DAU).
2. Multiply DAU by the number of actions for each user each day.
3. Divide the result by 86,400 to get the average requests per second (QPS).
4. Multiply the average by a peak factor, for example 2.
5. Separate the reads from the writes.
6. For storage, multiply the writes each day by the size of one item.
7. Multiply the storage each day by the days of retention and by the number of copies.
8. For bandwidth, multiply the QPS by the size of one response.
9. Round each result. Write its unit.

Steps that run one after the other add their latencies.
Steps that run in parallel cost as much as the slowest step.

The sample uses the figures of a photo service.
The service has 10 million daily users, and each user views 20 photos a day.
Users upload 1 million photos of 2 MB each day, and the service keeps 3 copies for 5 years.

```python
import math

SECONDS_PER_DAY = 86_400
MB = 10**6
TB = 10**12
PB = 10**15


def average_qps(daily_users, actions_per_user):
    return daily_users * actions_per_user / SECONDS_PER_DAY


def peak_qps(average, peak_factor=2):
    return average * peak_factor


def storage_bytes(items_per_day, bytes_per_item, years, copies=1):
    return items_per_day * bytes_per_item * 365 * years * copies


def bandwidth_bytes_per_second(qps, bytes_per_response):
    return qps * bytes_per_response


def serial_latency(steps_ms):
    return sum(steps_ms)


def parallel_latency(steps_ms):
    return max(steps_ms)


views = average_qps(10_000_000, 20)
assert round(views) == 2315
assert round(peak_qps(views)) == 4630

assert storage_bytes(1_000_000, 2 * MB, years=1 / 365) == 2 * TB
assert math.isclose(storage_bytes(1_000_000, 2 * MB, years=5, copies=3) / PB, 10.95)

# 2,315 views a second of 2 MB photos is about 4.6 GB each second
assert round(bandwidth_bytes_per_second(views, 2 * MB) / 10**9, 1) == 4.6

# 5 queries of 2 ms, then 3 calls of 0.5 ms network and 4 ms work
queries = serial_latency([2] * 5)
assert serial_latency([queries] + [0.5 + 4] * 3) == 23.5
assert serial_latency([queries, parallel_latency([0.5 + 4] * 3)]) == 14.5
```

CAUTION: Do not plan capacity for the average rate.
A service that handles only the average fails at the busiest hour each day.

## Scaling the web tier

One server has a limit of CPU, memory and network connections.
When the load is more than that limit, you must scale the service.

### Vertical and horizontal scaling

| Approach | What you do | Advantage | Disadvantage |
|---|---|---|---|
| Vertical scaling | Use a larger machine | No change to the code | A hard upper limit, and one point of failure |
| Horizontal scaling | Add more machines | No fixed upper limit, and spare machines | Needs stateless servers and a load balancer |

Horizontal scaling is easy only when the app servers are stateless.
A stateless server keeps no user data in its memory between requests.
Thus, any server can handle any request.

To make an app server stateless, do these steps:

1. Find each value that the server keeps between requests, for example sessions and uploads.
2. Move sessions to a shared store, or into a signed token that the client sends.
3. Move uploaded files to object storage.
4. Move scheduled work to a queue or to a separate worker.
5. Make sure that two requests from one user can go to two different servers.

```text
            ┌─────────┐
            │ Clients │
            └────┬────┘
                 v
         ┌───────────────┐
         │ Load balancer │
         └───────┬───────┘
       ┌─────────┼─────────┐
       v         v         v
  ┌────────┐┌────────┐┌────────┐
  │ App 1  ││ App 2  ││ App 3  │
  └───┬────┘└───┬────┘└───┬────┘
      └─────────┼─────────┘
                v
       ┌─────────────────┐
       │  Shared store   │
       │ (sessions, DB)  │
       └─────────────────┘
```

### Load balancers

A load balancer receives each request and sends it to one server in a pool.
It also stops traffic to a server that fails its health check.

| Layer | What it reads | Use it when |
|---|---|---|
| Layer 4 (transport) | IP addresses and ports | You need high speed and do not need to read the request |
| Layer 7 (application) | The HTTP method, path, headers and cookies | You must send different paths to different pools |

| Algorithm | How it selects a server | Good for |
|---|---|---|
| Round robin | Each server in turn | Equal servers and equal requests |
| Weighted round robin | Each server in turn, in proportion to its weight | Servers of different sizes |
| Least connections | The server with the fewest open requests | Requests with different durations |
| Hash of a key | A hash of the client address or user ID | Cache locality for each user |
| Two random choices | The better of two random servers | Large pools, with a small amount of shared state |

To add a server to the pool, do these steps:

1. Start the server.
2. Make sure that its health check passes.
3. Add the server to the pool of the load balancer.
4. Look at its error rate and its latency for some minutes.

To remove a server from the pool, do these steps:

1. Remove the server from the pool. It gets no new requests.
2. Let the current requests finish. This is "connection draining".
3. Stop the server.

The sample shows two load balancer algorithms.
It also calculates the number of servers for a peak load, with spare capacity.

```python
import itertools
import math


class RoundRobin:
    def __init__(self, servers):
        self._next = itertools.cycle(servers)

    def pick(self):
        return next(self._next)


class LeastConnections:
    def __init__(self, servers):
        self.open = {server: 0 for server in servers}

    def pick(self):
        server = min(self.open, key=self.open.get)
        self.open[server] += 1
        return server

    def release(self, server):
        self.open[server] -= 1


def servers_needed(peak_qps, qps_per_server, target_utilization=0.7, spare=1):
    busy = math.ceil(peak_qps / (qps_per_server * target_utilization))
    return busy + spare


rr = RoundRobin(["a", "b", "c"])
assert [rr.pick() for _ in range(5)] == ["a", "b", "c", "a", "b"]

lc = LeastConnections(["a", "b", "c"])
assert [lc.pick() for _ in range(3)] == ["a", "b", "c"]
lc.release("b")
assert lc.pick() == "b"  # b has the fewest open requests
assert lc.open == {"a": 1, "b": 1, "c": 1}

# 4,630 requests a second at peak, 500 for each server, 70% target load
assert servers_needed(4630, 500) == 15
```

CAUTION: Sticky sessions send each user to the same server.
They make the load uneven, and a server failure removes the sessions of its users.
Keep the sessions in a shared store.

NOTE: A content delivery network (CDN) keeps copies of static files near the users.
It decreases the latency for the users and the load on the web tier.

## Caching

A cache keeps a copy of data in a faster store.
A read that finds the data in the cache is a hit. It does not go to the slower store.
A read that does not find the data is a miss.

A cache helps when clients read the same data many times, and when stale data for a short time is acceptable.

| Layer | Example | Typical latency |
|---|---|---|
| Client | The browser cache | 0 ms, no request |
| Edge | A CDN near the user | 10 ms |
| Application | A dictionary in the memory of the process | Less than 1 us |
| Distributed cache | An in-memory key-value store on the network | 0.5 ms |
| Database | The buffer pool of the database | 1 ms |

### Write policies

| Policy | Read path | Write path | Trade-off |
|---|---|---|---|
| Cache-aside | The app reads the cache, then the database on a miss | The app writes the database, then deletes the cache key | Simple and common. The first read after a change is a miss |
| Read-through | The cache reads the database on a miss | As cache-aside | Simpler app code. The cache must know the database |
| Write-through | As read-through | The cache writes the database at the same time | Fresh data. Each write is slower |
| Write-back | As read-through | The cache writes the database later | Fast writes. A cache failure can lose writes |
| Write-around | As cache-aside | The app writes only the database | The cache keeps only data that clients read |

To read with cache-aside, do these steps:

1. Look for the key in the cache.
2. If the key is in the cache, return the value.
3. If not, read the value from the database.
4. Put the value in the cache with a time to live (TTL).
5. Return the value.

To write with cache-aside, do these steps:

1. Write the new value to the database.
2. Delete the key from the cache. Do not write the new value to the cache.

NOTE: Delete the key after the write, and do not update it.
Two updates in a race can put the older value in the cache, but a delete cannot.

```text
    ┌─────┐   1. get key    ┌───────┐
    │ App ├────────────────>│ Cache │
    └──┬──┘                 └───────┘
       │                        ^
       │ 2. on a miss,          │ 3. put the key
       │    read the database   │    with a TTL
       │                        │
       v                        │
  ┌──────────┐                  │
  │ Database ├──────────────────┘
  └──────────┘
```

### Eviction policies

A cache has a fixed size. When it is full, it must remove a key to add a new key.

| Policy | Removes | Good for |
|---|---|---|
| LRU (least recently used) | The key with the oldest last read | Most workloads |
| LFU (least frequently used) | The key with the fewest reads | Stable sets of popular keys |
| FIFO (first in, first out) | The oldest key | Simple caches |
| TTL (time to live) | Each key after a fixed time | Data that becomes stale |

### Effective latency

The effective latency of a read with a cache is:

effective latency = hit ratio x cache latency + (1 - hit ratio) x (cache latency + database latency)

The hit ratio also decreases the load on the database.
The database gets only the misses: QPS x (1 - hit ratio).

The sample gives an LRU cache.
It uses `OrderedDict`, so that each operation has a cost of O(1).

```python
import math
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = OrderedDict()

    def get(self, key):
        if key not in self.items:
            return None
        self.items.move_to_end(key)
        return self.items[key]

    def put(self, key, value):
        self.items[key] = value
        self.items.move_to_end(key)
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)


def effective_latency(hit_ratio, cache_ms, database_ms):
    return hit_ratio * cache_ms + (1 - hit_ratio) * (cache_ms + database_ms)


def database_qps(qps, hit_ratio):
    return qps * (1 - hit_ratio)


cache = LRUCache(2)
cache.put("a", 1)
cache.put("b", 2)
assert cache.get("a") == 1  # "a" becomes the most recently used key
cache.put("c", 3)  # the cache is full, so it removes "b"
assert cache.get("b") is None
assert list(cache.items) == ["a", "c"]

assert math.isclose(effective_latency(0.95, 0.5, 10), 1.0)
assert math.isclose(effective_latency(0.0, 0.5, 10), 10.5)
assert math.isclose(database_qps(10_000, 0.95), 500)
```

CAUTION: When a popular key expires, many requests miss at the same time.
They all go to the database. This is a cache stampede.
Let only one request load the key, and add a random part to each TTL.

### Cache problems

| Problem | Cause | Remedy |
|---|---|---|
| Stale data | The database changed, but the cache did not | Delete keys on write. Use a short TTL |
| Cache stampede | A popular key expires | One loader for each key. Random TTLs |
| Hot key | One key gets most of the traffic | Copy the key to many cache nodes. Keep it in local memory |
| Cold start | A new cache is empty | Fill the cache before it gets traffic |

## Databases and replication

The database keeps the data that the service must not lose.
Select the type of database from the shape of the data and the queries.

| Type | Data shape | Use it when |
|---|---|---|
| Relational (SQL) | Tables with rows, joins and transactions | Data has relations and needs strong rules |
| Key-value | One value for each key | Access is always by one key |
| Document | Nested records, for example JSON | Each read gets one full record |
| Wide-column | Rows with many columns, partitioned by key | Very high write rates and large data |
| Graph | Nodes and edges | Queries follow many relations |
| Time series | Values with a time | Metrics and events in time order |

An index makes a read faster.
Each write must also update each index, so each index makes writes slower.

### Replication

Replication keeps copies of the data on more than one machine.
It gives three results:

- The data survives when one machine fails.
- More machines can serve reads.
- A copy can be near the users in a different region.

| Model | Writes go to | Advantage | Disadvantage |
|---|---|---|---|
| Single leader | One leader | Simple. No write conflicts | The leader limits write capacity |
| Multi-leader | A leader in each region | Local writes in each region | The service must resolve write conflicts |
| Leaderless | Any W of N replicas | No failover step | Reads and writes need quorums |

| Replication mode | The write returns after | Risk |
|---|---|---|
| Synchronous | Each replica has the write | A slow replica makes each write slow |
| Asynchronous | The leader has the write | A failover can lose the last writes |
| Semi-synchronous | The leader and one replica have the write | A good balance for most services |

```text
            writes                       reads
               │                  ┌────────┴─────┐
               v                  v              v
          ┌────────┐          ┌───────┐      ┌───────┐
          │ Leader ├─────────>│ Rep 1 │      │ Rep 2 │
          └────┬───┘          └───────┘      └───────┘
               │                                 ^
               └─────────────────────────────────┘
                      the leader sends each write to each replica
```

### Replication lag

An asynchronous replica can be some seconds behind the leader.
A user who writes and then reads from a replica can see the old value.
To give "read your writes", send the reads of that user to the leader for a short time after each write.

To fail over to a new leader, do these steps:

1. Find that the leader has failed. Usually a missed heartbeat timeout shows this.
2. Select the replica with the most recent data.
3. Make that replica the new leader.
4. Send all writes to the new leader.
5. Make sure that the old leader cannot accept writes when it comes back.

CAUTION: Read replicas do not increase write capacity.
Each replica must apply each write.
When writes are too many for one leader, partition the data.

```python
import math


def replicas_needed(read_qps, qps_per_replica, target_utilization=0.7):
    return math.ceil(read_qps / (qps_per_replica * target_utilization))


class ReadRouter:
    """Send reads to replicas, except shortly after the same user writes."""

    def __init__(self, replicas, lag_seconds):
        self.replicas = replicas
        self.lag = lag_seconds
        self.last_write = {}
        self.turn = 0

    def write(self, user, now):
        self.last_write[user] = now
        return "leader"

    def read(self, user, now):
        if now - self.last_write.get(user, -math.inf) < self.lag:
            return "leader"
        self.turn = (self.turn + 1) % len(self.replicas)
        return self.replicas[self.turn]


# 20,000 reads a second, 3,000 for each replica at 70% load
assert replicas_needed(20_000, 3_000) == 10

router = ReadRouter(["r1", "r2"], lag_seconds=2.0)
assert router.read("ann", now=0.0) == "r2"
assert router.write("ann", now=10.0) == "leader"
assert router.read("ann", now=11.0) == "leader"  # inside the lag window
assert router.read("bob", now=11.0) == "r1"  # bob did not write
assert router.read("ann", now=12.5) == "r2"  # the replicas have the write
```

## Partitioning and sharding

Partitioning divides the data into parts. Each part goes to a different machine.
A part is a partition, or a shard.
Partition the data when it is too large for one machine, or when the writes are too many for one leader.

### Partition strategies

| Strategy | How a key finds its shard | Advantage | Disadvantage |
|---|---|---|---|
| Range | Each shard holds a range of keys | Range scans are fast | New keys can all go to one shard |
| Hash | hash(key) selects the shard | Even spread of keys | Range scans must read all shards |
| Directory | A lookup table maps each key to a shard | Full control of placement | The table is one more service |
| Geographic | The region of the user | Data stays near the user | Uneven load across regions |

To select a partition key, do these steps:

1. Write the most frequent queries.
2. Find the value that most queries filter by, for example the user ID.
3. Make sure that the value spreads the load evenly.
4. Make sure that the most frequent query reads only one shard.
5. Find the large keys. Plan a separate path for each very large key.

CAUTION: A query that does not include the partition key must read all shards.
Joins across shards are slow.
Keep the data that one query needs in one shard.

### Consistent hashing

With `hash(key) % N`, a change of N moves almost every key.
Consistent hashing moves only about 1/N of the keys.

| Method | Keys that move from N to N + 1 shards | Example, 4 to 5 shards |
|---|---|---|
| hash(key) % N | About N / (N + 1) | About 80% |
| Consistent hashing | About 1 / (N + 1) | About 20% |

Consistent hashing puts the nodes on a ring of hash values.
Each node has many points on the ring. These points are "virtual nodes".
Virtual nodes make the load more even.

```text
        ┌─────── A1 ─────────── B1 ───────┐
        │                                 │
       C2            hash ring            C1
        │                                 │
        └─────── B2 ─────────── A2 ───────┘
```

To find the node for a key, do these steps:

1. Calculate the hash of the key.
2. Move clockwise on the ring to the first point with a hash that is larger.
3. If no point is larger, go to the first point on the ring.
4. Return the node that owns that point.

When you add a node, it takes keys only from the points before its own points.
The other keys stay on their nodes.

```python
import bisect
import hashlib


def ring_hash(text):
    digest = hashlib.sha256(text.encode()).digest()
    return int.from_bytes(digest[:8], "big")


class HashRing:
    def __init__(self, nodes=(), vnodes=100):
        self.vnodes = vnodes
        self.points = []
        self.owner = {}
        for node in nodes:
            self.add(node)

    def add(self, node):
        for i in range(self.vnodes):
            point = ring_hash(f"{node}#{i}")
            bisect.insort(self.points, point)
            self.owner[point] = node

    def remove(self, node):
        self.points = [point for point in self.points if self.owner[point] != node]
        self.owner = {point: n for point, n in self.owner.items() if n != node}

    def node_for(self, key):
        index = bisect.bisect(self.points, ring_hash(key)) % len(self.points)
        return self.owner[self.points[index]]


keys = [f"user:{i}" for i in range(10_000)]

ring = HashRing(["a", "b", "c", "d"])
before = {key: ring.node_for(key) for key in keys}
ring.add("e")
after = {key: ring.node_for(key) for key in keys}
moved = [key for key in keys if before[key] != after[key]]

assert 0.15 < len(moved) / len(keys) < 0.25  # about 1/5 of the keys move
assert all(after[key] == "e" for key in moved)  # they all move to the new node

ring.remove("e")
assert {key: ring.node_for(key) for key in keys} == before

# with modulo placement, most keys move
modulo_moved = sum(ring_hash(key) % 4 != ring_hash(key) % 5 for key in keys)
assert modulo_moved / len(keys) > 0.75

# virtual nodes keep each node near its fair share of 2,500 keys
counts = {node: list(before.values()).count(node) for node in "abcd"}
assert all(1_800 < count < 3_200 for count in counts.values())
```

NOTE: A hot key stays hot after you add shards, because one key always goes to one node.
For a very hot key, add a suffix to the key, for example `post:42#3`, and spread the copies.

## Consistency and quorums

Replicas of the same data can disagree for a short time.
A consistency model tells what a read can return when the replicas disagree.

The CAP theorem: when the network divides the replicas into groups, a system must select one of two results.
It either rejects some requests (consistency), or it answers with data that can be stale (availability).
When the network is healthy, the trade-off is between latency and consistency.

| Model | A read returns | Cost |
|---|---|---|
| Strong (linearizable) | The result of the most recent write | Highest latency. Needs a leader or a quorum |
| Sequential | Writes in one order that all clients agree on | High |
| Causal | Each write after the writes that caused it | Medium |
| Read your writes | Your own writes, at least | Low. Route your reads after a write |
| Monotonic reads | Never an older value than your last read | Low. Keep each user on one replica |
| Eventual | The latest value, at some time after writes stop | Lowest |

### Quorums

A leaderless store keeps N copies of each value.
A write succeeds when W replicas confirm it.
A read asks R replicas and keeps the value with the highest version.

When R + W > N, each read set shares at least one replica with each write set.
Thus, each read sees at least one copy of the latest successful write.

```text
                ┌────┐    ┌────┐    ┌────┐
   N = 3        │ R1 │    │ R2 │    │ R3 │
                └────┘    └────┘    └────┘
   Write, W = 2   v2        v2        v1
   Read,  R = 2             v2        v1
   Overlap                  R2  ──> the read returns v2
```

| N | W | R | R + W > N | Behavior |
|---|---|---|---|---|
| 3 | 2 | 2 | Yes | Balanced. Tolerates 1 failed replica for reads and writes |
| 3 | 3 | 1 | Yes | Fast reads. One failed replica stops all writes |
| 3 | 1 | 3 | Yes | Fast writes. One failed replica stops all reads |
| 3 | 1 | 1 | No | Fastest. Reads can return stale data |
| 5 | 3 | 3 | Yes | Tolerates 2 failed replicas |

To read and write with quorums, do these steps:

1. Give each write a version number.
2. Send the write to all N replicas.
3. Report success after W replicas confirm the write.
4. To read, ask R replicas.
5. Return the value with the highest version.
6. Write that value back to the replicas with older versions. This is "read repair".

NOTE: R + W > N makes the read and write sets overlap.
It does not stop all anomalies, for example two concurrent writes to the same key.
Use W > N / 2, so that two writes that conflict cannot both succeed.

| Conflict method | How it works | Risk |
|---|---|---|
| Last writer wins | Keep the write with the latest timestamp | Loses concurrent writes. Clocks can disagree |
| Version vectors | Keep both values. Let the client merge them | More work for the client |
| Merge function | A data type that merges all writes, for example a counter | Works only for some data types |

```python
from itertools import combinations


def quorum_overlaps(n, r, w):
    return r + w > n


def every_read_meets_every_write(n, r, w):
    replicas = range(n)
    for write_set in combinations(replicas, w):
        for read_set in combinations(replicas, r):
            if not set(write_set) & set(read_set):
                return False
    return True


def quorum_write(replicas, targets, version, value):
    for index in targets:
        replicas[index] = (version, value)


def quorum_read(replicas, targets):
    return max(replicas[index] for index in targets)


for n in range(1, 6):
    for r in range(1, n + 1):
        for w in range(1, n + 1):
            assert quorum_overlaps(n, r, w) == every_read_meets_every_write(n, r, w)

store = [(1, "old")] * 3
quorum_write(store, targets=[0, 1], version=2, value="new")  # W = 2
for read_set in combinations(range(3), 2):  # every possible R = 2
    assert quorum_read(store, read_set) == (2, "new")

assert quorum_read(store, [2]) == (1, "old")  # R = 1 can miss the write
assert not quorum_overlaps(3, 1, 1)
```

## Queues and asynchronous work

A queue keeps messages between a producer and a consumer.
The producer does not wait for the consumer to do the work.

A queue gives four results:

- The request returns quickly. The slow work runs later.
- A burst of messages waits in the queue. The consumers do not get too much load.
- A failed message can go back to the queue and run again.
- The producer and the consumer can scale separately.

```text
  ┌──────────┐     ┌───────┐       ┌────────────┐
  │ Producer ├────>│ Queue ├──┬───>│ Consumer 1 │
  └──────────┘     └───┬───┘  │    └────────────┘
                       │      │    ┌────────────┐
                       │      └───>│ Consumer 2 │
                       │           └────────────┘
                       │ after N failures
                       │
                       v
              ┌───────────────────┐
              │ Dead-letter queue │
              └───────────────────┘
```

| Type | A message goes to | After a read | Use it for |
|---|---|---|---|
| Work queue | One consumer | The queue removes the message | Jobs, for example email delivery or image resize |
| Log (publish and subscribe) | Each consumer group | The message stays. Each group keeps its offset | Events that many services read, and replay |

### Delivery guarantees

| Guarantee | Result | How to get it |
|---|---|---|
| At most once | A consumer never gets a message two times. A message can disappear | Acknowledge before the work |
| At least once | No message disappears. A consumer can get a message two times | Acknowledge after the work |
| Exactly once (effect) | Each message has its effect one time | At least once, and an idempotent consumer |

An idempotent operation gives the same result if it runs one time or many times.
To make a consumer idempotent, give each message a unique ID.
The consumer keeps the IDs that it has finished, and ignores a repeated ID.

To consume a message, do these steps:

1. Receive a message from the queue.
2. If its ID is in the finished set, acknowledge it and stop.
3. Do the work.
4. Record the ID and the result in one transaction.
5. Acknowledge the message.
6. If the work fails, return the message to the queue with a delay.
7. After N failures, move the message to the dead-letter queue.

### Little's law and drain time

Little's law connects three values of a stable system:

L = lambda x W

- L is the mean number of items in the system.
- lambda is the arrival rate.
- W is the mean time that each item stays in the system.

Thus, 500 jobs a second that each take 0.2 s keep 100 jobs in progress.
You need at least 100 workers.

A backlog decreases only when the consumers are faster than the producers.
The drain time is: backlog / (service rate - arrival rate).

| Backlog | Arrival rate | Service rate | Drain time |
|---|---|---|---|
| 1,200,000 | 1,000/s | 1,500/s | 2,400 s (40 min) |
| 1,200,000 | 1,000/s | 2,000/s | 1,200 s (20 min) |
| 1,200,000 | 1,000/s | 1,000/s | Never |

```python
import math


def in_system(arrival_rate, seconds_in_system):
    return arrival_rate * seconds_in_system


def workers_needed(arrival_rate, seconds_per_job, target_utilization=0.8):
    return math.ceil(in_system(arrival_rate, seconds_per_job) / target_utilization)


def drain_seconds(backlog, arrival_rate, service_rate):
    if service_rate <= arrival_rate:
        return math.inf
    return backlog / (service_rate - arrival_rate)


class IdempotentConsumer:
    def __init__(self):
        self.finished = set()
        self.balance = 0

    def handle(self, message_id, amount):
        if message_id in self.finished:
            return False
        self.balance += amount
        self.finished.add(message_id)
        return True


assert in_system(500, 0.2) == 100
assert workers_needed(500, 0.2) == 125

assert drain_seconds(1_200_000, 1_000, 1_500) == 2_400
assert drain_seconds(1_200_000, 1_000, 2_000) == 1_200
assert drain_seconds(1_200_000, 1_000, 1_000) == math.inf

consumer = IdempotentConsumer()
deliveries = [("m1", 10), ("m2", 5), ("m1", 10)]  # m1 arrives two times
results = [consumer.handle(message_id, amount) for message_id, amount in deliveries]
assert results == [True, True, False]
assert consumer.balance == 15
```

CAUTION: If the service rate is not more than the arrival rate, the backlog never decreases.
Add consumers, or make the producers slow down. The second option is "back pressure".

## Rate limits and resilience

A rate limit sets the maximum number of requests that a client can send in a period.
It protects the service from overload and from clients that send too many requests.

Resilience is the ability of a service to continue when a dependency is slow or fails.
Timeouts, retries, circuit breakers and bulkheads give resilience.

### Rate limiting algorithms

| Algorithm | How it works | Bursts | Memory |
|---|---|---|---|
| Token bucket | Tokens refill at a fixed rate. Each request uses one token | Allows bursts up to the bucket size | Two numbers for each client |
| Leaky bucket | Requests leave a queue at a fixed rate | Makes the output smooth | A queue for each client |
| Fixed window | Count requests in each clock minute | Two times the limit at a window edge | One counter for each client |
| Sliding window log | Keep the time of each request | Exact | One entry for each request |
| Sliding window counter | Mix the counts of this window and the last window | Close to exact | Two counters for each client |

To check a request with a token bucket, do these steps:

1. Calculate the time since the last check.
2. Add the refill rate multiplied by that time to the tokens.
3. Keep the tokens at or below the capacity.
4. If at least one token is available, remove one token and allow the request.
5. If not, reject the request with status 429 and a `Retry-After` header.

NOTE: Apply the limit for each client, for example for each API key or each user.
With many servers, keep the counters in a shared store.

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_second, now=0.0):
        self.capacity = capacity
        self.rate = refill_per_second
        self.tokens = float(capacity)
        self.last = now

    def allow(self, now, cost=1):
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


bucket = TokenBucket(capacity=5, refill_per_second=1)
assert [bucket.allow(now=0.0) for _ in range(6)] == [True] * 5 + [False]
assert bucket.allow(now=0.5) is False  # only half a token
assert bucket.allow(now=1.0) is True  # one full token
assert bucket.allow(now=1.0) is False

bucket.allow(now=100.0)
assert bucket.tokens == 4  # the bucket refills only to its capacity, then one is used
```

### Timeouts and retries

Each call to a dependency needs a timeout.
Without a timeout, a slow dependency keeps threads and connections busy, and the caller also becomes slow.

A retry can fix a short failure.
Retry only operations that are idempotent.
Wait longer before each retry. This is "exponential backoff".
Add a random part to each wait. This is "jitter".
With jitter, many clients do not retry at the same time.

| Attempt | Backoff ceiling (base 100 ms) | Wait with full jitter |
|---|---|---|
| 1 | 100 ms | 0 to 100 ms |
| 2 | 200 ms | 0 to 200 ms |
| 3 | 400 ms | 0 to 400 ms |
| 4 | 800 ms | 0 to 800 ms |
| 8 | 12,800 ms, cut to the cap of 10 s | 0 to 10 s |

```python
import random


def backoff_delays(attempts, base=0.1, cap=10.0, rng=None):
    rng = rng or random.Random()
    return [rng.uniform(0, min(cap, base * 2**attempt)) for attempt in range(attempts)]


def call_with_retries(operation, attempts, sleep, rng):
    for delay in backoff_delays(attempts, rng=rng):
        try:
            return operation()
        except ConnectionError:
            sleep(delay)
    return operation()


delays = backoff_delays(8, rng=random.Random(7))
ceilings = [min(10.0, 0.1 * 2**attempt) for attempt in range(8)]
assert all(0 <= delay <= ceiling for delay, ceiling in zip(delays, ceilings))
assert backoff_delays(8, rng=random.Random(7)) == delays  # the same seed gives the same delays

failures = [ConnectionError(), ConnectionError()]


def flaky():
    if failures:
        raise failures.pop()
    return "ok"


slept = []
assert call_with_retries(flaky, attempts=3, sleep=slept.append, rng=random.Random(1)) == "ok"
assert len(slept) == 2
```

CAUTION: Retries multiply the load.
When three layers each try 3 times, one user request can become 27 calls to the last layer.
Retry at one layer only, and set a retry budget.

### Circuit breakers

A circuit breaker stops calls to a dependency that fails.
The dependency gets time to recover, and the caller fails fast and does not wait for timeouts.

| State | Calls | Moves to |
|---|---|---|
| Closed | All calls go through. The breaker counts failures | Open, when failures reach the limit |
| Open | All calls fail at once | Half-open, when the wait time ends |
| Half-open | One trial call goes through | Closed if the trial succeeds. Open if it fails |

```text
   ┌────────┐   failures reach the limit  ┌──────┐
   │ Closed ├────────────────────────────>│ Open │
   └────────┘                             └┬────┬┘
       ^                                   │    ^
       │                    wait time ends │    │ trial fails
       │ trial succeeds                    v    │
       │                             ┌──────────┴┐
       └─────────────────────────────┤ Half-open │
                                     └───────────┘
```

```python
class CircuitBreaker:
    def __init__(self, failure_limit=3, wait_seconds=10.0):
        self.failure_limit = failure_limit
        self.wait = wait_seconds
        self.state = "closed"
        self.failures = 0
        self.opened_at = 0.0
        self.trial_sent = False

    def allow(self, now):
        if self.state == "open" and now - self.opened_at >= self.wait:
            self.state = "half_open"
            self.trial_sent = False
        if self.state == "closed":
            return True
        if self.state == "half_open" and not self.trial_sent:
            self.trial_sent = True
            return True
        return False

    def record_success(self):
        self.state = "closed"
        self.failures = 0

    def record_failure(self, now):
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.failure_limit:
            self.state = "open"
            self.opened_at = now


breaker = CircuitBreaker(failure_limit=3, wait_seconds=10.0)
for second in range(3):
    assert breaker.allow(now=second)
    breaker.record_failure(now=second)
assert breaker.state == "open"
assert breaker.allow(now=5.0) is False  # fail fast

assert breaker.allow(now=12.0) is True  # the wait ended: one trial call
assert breaker.state == "half_open"
assert breaker.allow(now=12.1) is False  # only one trial at a time
breaker.record_failure(now=12.2)
assert breaker.state == "open"

assert breaker.allow(now=22.2) is True
breaker.record_success()
assert breaker.state == "closed"
assert breaker.allow(now=22.3) is True
```

NOTE: A bulkhead gives each dependency its own pool of threads or connections.
When one dependency becomes slow, it fills only its own pool.
Calls to the other dependencies continue.

## Availability and reliability

Availability is the fraction of time that a service works correctly.
Reliability is the ability of a service to keep correct results and data over time.

| Term | Definition |
|---|---|
| SLI (service level indicator) | A measured value, for example the fraction of requests that succeed |
| SLO (service level objective) | The target for an SLI, for example 99.9% of requests succeed in 30 days |
| SLA (service level agreement) | A contract with a penalty if the service misses a target |
| Error budget | 1 - SLO. The failures that the service can have in the period |
| MTBF | Mean time between failures |
| MTTR | Mean time to repair |
| RPO (recovery point objective) | The maximum data loss, as time, after a failure |
| RTO (recovery time objective) | The maximum time to restore the service |

Availability from failure and repair times is: MTBF / (MTBF + MTTR).
Thus, a faster repair increases availability as much as fewer failures do.

### Nines and downtime

| Availability | Downtime a year | Downtime a 30-day month | Downtime a day |
|---|---|---|---|
| 99% (two nines) | 3.65 days | 7.2 hours | 14.4 minutes |
| 99.9% (three nines) | 8.76 hours | 43.2 minutes | 1.44 minutes |
| 99.99% (four nines) | 52.6 minutes | 4.32 minutes | 8.64 seconds |
| 99.999% (five nines) | 5.26 minutes | 25.9 seconds | 0.86 seconds |

### Serial and parallel components

When a request needs all components in a chain, the availabilities multiply.
The chain is less available than its weakest part.

When a request needs only one of some redundant copies, it fails only if all copies fail.
The availability is 1 - (1 - a1) x (1 - a2) x ... .

```text
  Serial: each part must work

  ┌────┐   ┌─────┐   ┌────┐
  │ LB ├──>│ App ├──>│ DB │    0.999 x 0.999 x 0.999 = 0.997
  └────┘   └─────┘   └────┘

  Parallel: one copy must work

         ┌────────┐
     ┌──>│ Copy 1 ├──┐
  ───┤   └────────┘  ├───>     1 - (0.01 x 0.01) = 0.9999
     │   ┌────────┐  │
     └──>│ Copy 2 ├──┘
         └────────┘
```

| Redundancy pattern | How it works | Failover time |
|---|---|---|
| Active-passive | A standby copy takes over when the active copy fails | Seconds to minutes |
| Active-active | All copies serve traffic | Near zero. The other copies take the load |
| N + 1 | One more server than the peak needs | Near zero for one failure |
| Multi-region | Copies in separate regions | Depends on the data replication |

To find the availability of a design, do these steps:

1. Draw the path of one request through the components.
2. Find each group of redundant copies. Calculate its parallel availability.
3. Multiply the availabilities of the parts in the chain.
4. Change the result into downtime a year.
5. Compare the downtime with the SLO.
6. Add redundancy at the part with the lowest availability.

```python
import math

HOURS_PER_YEAR = 365 * 24


def serial(*parts):
    return math.prod(parts)


def parallel(*parts):
    return 1 - math.prod(1 - part for part in parts)


def downtime_hours_per_year(availability):
    return (1 - availability) * HOURS_PER_YEAR


def availability_from_repair(mtbf_hours, mttr_hours):
    return mtbf_hours / (mtbf_hours + mttr_hours)


def error_budget_minutes(slo, days=30):
    return (1 - slo) * days * 24 * 60


assert math.isclose(downtime_hours_per_year(0.999), 8.76)
assert math.isclose(downtime_hours_per_year(0.9999) * 60, 52.56)

assert round(serial(0.999, 0.999, 0.999), 4) == 0.997
assert math.isclose(parallel(0.99, 0.99), 0.9999)

# two app servers of 99% behind a 99.99% load balancer and a 99.95% database
path = serial(0.9999, parallel(0.99, 0.99), 0.9995)
assert round(path, 4) == 0.9993

assert math.isclose(availability_from_repair(999, 1), 0.999)
assert math.isclose(error_budget_minutes(0.999), 43.2)
```

CAUTION: The parallel formula is correct only when the copies fail independently.
Copies that share a power supply, a network switch or a software release can fail together.
Put copies in separate zones, and release new code to one copy at a time.

## Performance and observability

Latency is the time that one request takes.
Throughput is the number of requests that the service completes each second.
The two values connect: at high throughput, requests wait in queues, and latency increases.

### Percentiles

An average hides the slow requests.
Use percentiles. The p99 latency is the value that 99% of the requests do not exceed.

| Percentile | Definition | Use it for |
|---|---|---|
| p50 (median) | Half the requests are faster | The usual experience |
| p95 | 1 request in 20 is slower | Most dashboards |
| p99 | 1 request in 100 is slower | SLOs for services that users call directly |
| p99.9 | 1 request in 1,000 is slower | Large services and fan-out calls |

CAUTION: Do not average percentiles from different servers.
The result is not a percentile.
Merge the raw values or the histograms, then calculate the percentile.

### Tail latency at scale

When one request calls many servers in parallel, it waits for the slowest server.
If each server is slow for a fraction p of its calls, the request is slow with this probability:

1 - (1 - p)^n, where n is the number of servers.

| Servers called (n) | p = 1% | p = 0.1% |
|---|---|---|
| 1 | 1% | 0.1% |
| 10 | 9.6% | 1.0% |
| 100 | 63.4% | 9.5% |
| 1,000 | 99.996% | 63.2% |

To decrease tail latency, send a second copy of a slow request to another server.
Use the first answer. These are "hedged requests".

### Utilization and wait time

In a simple queue model, the mean wait in the queue is the service time x u / (1 - u).
The letter u is the utilization.

| Utilization | Wait, in units of the service time |
|---|---|
| 50% | 1 |
| 80% | 4 |
| 90% | 9 |
| 95% | 19 |

Thus, keep the target utilization at about 60% to 80%.
Above that level, a small increase in load gives a large increase in latency.

### Metrics, logs and traces

| Signal | What it records | Use it to |
|---|---|---|
| Metrics | Numbers over time, for example request rate and p99 latency | Find that a problem exists, and send alerts |
| Logs | One record for each event, with details | Find the cause of one failure |
| Traces | The path and the time of each step of one request across services | Find the slow step in a chain of calls |

| Method | Applies to | Signals |
|---|---|---|
| RED | Each service | Rate, Errors, Duration |
| USE | Each resource, for example CPU or disk | Utilization, Saturation, Errors |

To find the cause of a slow service, do these steps:

1. Look at the RED metrics. Find when the latency increased.
2. Compare the p50 with the p99. If only the p99 increased, look for queues and retries.
3. Find a slow trace from that time.
4. Find the step in the trace that takes the most time.
5. Look at the USE metrics of the resource for that step.
6. Fix the cause. Then make sure that the metrics go back to normal.

```python
import math


def percentile(values, p):
    ordered = sorted(values)
    rank = math.ceil(p / 100 * len(ordered))
    return ordered[max(rank, 1) - 1]


def tail_probability(p_slow, servers):
    return 1 - (1 - p_slow) ** servers


def queue_wait(service_time, utilization):
    return service_time * utilization / (1 - utilization)


latencies = [10] * 95 + [500] * 5  # milliseconds
assert sum(latencies) / len(latencies) == 34.5  # the mean hides the slow requests
assert percentile(latencies, 50) == 10
assert percentile(latencies, 95) == 10
assert percentile(latencies, 99) == 500

assert round(tail_probability(0.01, 100), 3) == 0.634
assert round(tail_probability(0.001, 1_000), 3) == 0.632

assert math.isclose(queue_wait(1, 0.5), 1)
assert math.isclose(queue_wait(1, 0.9), 9)
assert queue_wait(1, 0.95) > 4 * queue_wait(1, 0.8)
```

## Case study: URL shortener

A URL shortener changes a long URL into a short code.
A request for the short code returns a redirect to the long URL.

### Shortener requirements

- Make a short code for a long URL.
- Redirect a short code to its long URL quickly.
- Keep each link for 5 years.
- Reads are many more than writes, about 100 to 1.
- A redirect must have a low latency and high availability.

### Shortener estimates

| Quantity | Calculation | Result |
|---|---|---|
| New URLs a month | Given | 100 million |
| Writes a second | 100,000,000 / (30 x 86,400) | About 40 |
| Reads a second | 40 x 100 | About 4,000. About 8,000 at peak |
| Records in 5 years | 100 million x 12 x 5 | 6 billion |
| Storage | 6 billion x 500 bytes | 3 TB |
| Length of a base62 code | 62^6 = 56.8 billion, more than 6 billion | 6 characters, or 7 for headroom |

### Shortener API and data model

| Method | Path | Body or result |
|---|---|---|
| POST | /urls | Body: the long URL. Result: the short code |
| GET | /{code} | Result: a redirect to the long URL |
| DELETE | /urls/{code} | Result: the service removes the link |

| Field | Type | Note |
|---|---|---|
| code | string, 7 characters | The primary key, and also the partition key |
| long_url | string | Up to 2 KB |
| owner_id | integer | Optional |
| created_at | timestamp | |
| expires_at | timestamp | Optional |

```text
      POST /urls                  GET /{code}
           │                           │
           v                           v
  ┌─────────────────┐        ┌──────────────────┐  1. get      ┌───────┐
  │ Write service   │        │ Redirect service ├─────────────>│ Cache │
  └──┬───────────┬──┘        └─────────┬────────┘              └───────┘
     │           │                     │ 2. on a miss
     v           v                     v
┌───────────┐ ┌────────────────────────────────┐
│ ID blocks │ │ Database: code, long URL       │
└───────────┘ └────────────────────────────────┘
```

### Short code generation

| Method | How it works | Advantage | Disadvantage |
|---|---|---|---|
| Hash and cut | Take the first 7 characters of a hash of the URL | No coordination | Collisions. You must check and try again |
| Counter and base62 | Encode a unique integer in base62 | No collisions. Short codes | Codes are easy to guess. Needs a unique counter |
| Random code | Make a random code, then check that it is free | Hard to guess | One extra read for each write |

To make a code with a counter, do these steps:

1. Each write server takes a block of 1,000 IDs from a counter service.
2. The server gives the next ID in its block to each new URL.
3. Encode the ID in base62.
4. Store the code and the long URL.
5. When the block is empty, take a new block.

A server that stops loses the rest of its block.
This is acceptable, because the ID space is very large.

### Redirect status codes

| Status | Name | Effect |
|---|---|---|
| 301 | Moved permanently | The browser keeps the redirect. Fewer requests, but no click counts |
| 302 | Found (temporary) | Each click reaches the service. You can count clicks and change the target |

```python
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode(number):
    if number == 0:
        return ALPHABET[0]
    digits = []
    while number:
        number, remainder = divmod(number, BASE)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code):
    number = 0
    for char in code:
        number = number * BASE + ALPHABET.index(char)
    return number


class IdBlocks:
    """A counter service that gives each write server a block of IDs."""

    def __init__(self, block_size=1_000):
        self.block_size = block_size
        self.next_start = 0

    def take(self):
        start = self.next_start
        self.next_start += self.block_size
        return iter(range(start, start + self.block_size))


assert BASE == 62
assert encode(0) == "0"
assert encode(61) == "Z"
assert encode(62) == "10"
assert all(decode(encode(n)) == n for n in range(0, 10**6, 997))

assert BASE**6 > 6_000_000_000  # 6 characters hold 5 years of links
assert len(encode(6_000_000_000)) == 6
assert BASE**7 == 3_521_614_606_208

counter = IdBlocks(block_size=1_000)
server_a, server_b = counter.take(), counter.take()
codes = {encode(next(server_a)) for _ in range(500)} | {encode(next(server_b)) for _ in range(500)}
assert len(codes) == 1_000  # two servers, no collisions
```

NOTE: Most redirects read a small set of popular links.
A cache with LRU eviction in front of the database serves most of the reads.

## Case study: news feed

A news feed shows each user the recent posts of the accounts that the user follows.
The main question is when to build each feed: at write time or at read time.

### Feed requirements

- A user can publish a post.
- A user can read a feed of recent posts from the accounts that the user follows.
- The newest posts come first.
- A feed read must be fast. A new post can take some seconds to appear.

### Feed estimates

| Quantity | Calculation | Result |
|---|---|---|
| Daily active users | Given | 10 million |
| Posts a day | 1 user in 10 posts one time | 1 million |
| Mean followers | Given | 200 |
| Feed reads a second | 10 million x 10 reads / 86,400 | About 1,160 |
| Feed inserts with fan-out on write | 1 million x 200 | 200 million a day, about 2,300 a second |
| One post from an account with 50 million followers | 50 million inserts | One post costs as much as 250,000 normal posts |

### Fan-out models

| Model | On a new post | On a feed read | Good for |
|---|---|---|---|
| Fan-out on write (push) | Add the post ID to the feed of each follower | Read one precomputed list | Accounts with few followers |
| Fan-out on read (pull) | Store the post only | Read the recent posts of each followed account, then merge | Accounts with very many followers |
| Hybrid | Push for normal accounts. Store only for very large accounts | Read the precomputed list, then merge the posts of large accounts | Most real feeds |

```text
                ┌────────────┐
   new post ───>│ Post store │
                └─────┬──────┘
                      │ followers < limit
                      v
              ┌────────────────┐     ┌────────────────────────┐
              │ Fan-out worker ├────>│ Feed cache: post IDs,  │
              └────────────────┘     │ one list for each user │
                                     └────────────┬───────────┘
                                                  │
   feed read ─────────────────────────────────────┤
                                                  v
                          ┌──────────────────────────────────┐
                          │ Merge the list with the recent   │
                          │ posts of followed large accounts │
                          └──────────────────────────────────┘
```

To read a feed with the hybrid model, do these steps:

1. Read the precomputed list of post IDs for the user.
2. Find the large accounts that the user follows.
3. Read the recent posts of each large account.
4. Merge the two lists by time, newest first.
5. Read the post bodies for the first page, from a cache.

NOTE: Keep only post IDs in each feed list, and keep only the last few hundred IDs.
The post bodies are in one place, so an edit changes only one record.

```python
import heapq
import itertools


def fanout_on_write_cost(posts):
    """posts is a list of (number of posts, followers) for each account."""
    return sum(count * followers for count, followers in posts)


def hybrid_cost(posts, follower_limit):
    pushed = [(count, followers) for count, followers in posts if followers < follower_limit]
    pulled_accounts = len(posts) - len(pushed)
    return fanout_on_write_cost(pushed), pulled_accounts


def read_feed(precomputed, large_account_posts, limit):
    """Each list holds (timestamp, post_id), newest first."""
    merged = heapq.merge(precomputed, *large_account_posts, key=lambda post: post[0], reverse=True)
    return [post_id for _, post_id in itertools.islice(merged, limit)]


# one million normal posts with 200 followers each
assert fanout_on_write_cost([(1_000_000, 200)]) == 200_000_000
assert round(200_000_000 / 86_400) == 2315

# one large account that posts 10 times a day, with 50 million followers
accounts = [(1_000_000, 200), (10, 50_000_000)]
assert fanout_on_write_cost(accounts) == 700_000_000
assert hybrid_cost(accounts, follower_limit=10_000) == (200_000_000, 1)

feed = [(105, "p5"), (103, "p3"), (100, "p0")]
large = [[(104, "s4"), (101, "s1")], [(102, "t2")]]
assert read_feed(feed, large, limit=4) == ["p5", "s4", "p3", "t2"]
```

CAUTION: Fan-out on write to inactive users wastes work.
Build a feed only for users who were active recently. Build the other feeds at read time.

## Case study: chat service

A chat service sends messages between users in near real time.
It supports one-to-one chats and group chats, and it keeps the history.

### Chat requirements

- A user can send a message to a user or to a group.
- The receivers get the message in less than one second when they are online.
- Offline users get their messages when they connect again.
- Each user sees the messages of a channel in the same order.
- A message is never lost and never shown two times.

### Connection protocols

| Protocol | How it works | Use it for |
|---|---|---|
| Short polling | The client asks for new messages at a fixed interval | Simple clients. Wastes requests |
| Long polling | The server holds the request until a message arrives | Networks that block WebSocket |
| WebSocket | One open two-way connection | Chat. Low latency in both directions |
| Server-sent events | One open connection from server to client | One-way updates |

### Chat estimates

| Quantity | Calculation | Result |
|---|---|---|
| Concurrent connections | Given | 10 million |
| Connections for each gateway server | Given | 100,000 |
| Gateway servers | 10,000,000 / 100,000, plus 30% spare | 130 |
| Messages a day | 50 million users x 40 messages | 2 billion |
| Messages a second | 2,000,000,000 / 86,400 | About 23,000. About 46,000 at peak |
| Storage a day | 2 billion x 200 bytes | 400 GB |

```text
  ┌──────────┐ WebSocket ┌───────────┐       ┌──────────────────┐
  │ Sender   ├──────────>│ Gateway A ├──────>│ Channel service  │
  └──────────┘           └───────────┘       │ (assigns seq)    │
                                             └───┬──────────┬───┘
                                                 │          │
                                                 v          v
  ┌──────────┐ WebSocket ┌───────────┐     ┌──────────┐ ┌──────────────┐
  │ Receiver │<──────────┤ Gateway B │<────┤ Pub/sub  │ │ Message store│
  └──────────┘           └───────────┘     └──────────┘ └──────────────┘
```

### Message order and delivery

Clocks on different servers disagree, so a timestamp cannot give a reliable order.
Give each channel its own sequence of numbers: 1, 2, 3 and so on.
One owner, for example the shard that holds the channel, assigns the numbers.

To send a message, do these steps:

1. The client gives the message a unique client ID.
2. The client sends the message to its gateway.
3. The channel owner checks the client ID. A repeated ID gets the same sequence number.
4. The owner gives the message the next sequence number.
5. The owner stores the message, then publishes it to the gateways of the receivers.
6. The owner returns the sequence number to the sender as an acknowledgement.

To receive messages, do these steps:

1. Keep the last sequence number that you showed for each channel.
2. Show a message only if its number is one more than that number.
3. Keep early messages until the gap closes.
4. Ignore a message with a number that you already showed.
5. When you connect again, ask for all messages after your last number.

| Delivery state | Set when | Shown to the sender as |
|---|---|---|
| Sent | The server stored the message | One mark |
| Delivered | The device of the receiver got the message | Two marks |
| Read | The receiver opened the channel | Two marks in color |

```python
class Channel:
    def __init__(self):
        self.messages = []
        self.seq_for_client_id = {}

    def send(self, client_id, text):
        if client_id in self.seq_for_client_id:
            return self.seq_for_client_id[client_id]
        seq = len(self.messages) + 1
        self.messages.append((seq, text))
        self.seq_for_client_id[client_id] = seq
        return seq

    def since(self, last_seq):
        return self.messages[last_seq:]


class Reader:
    def __init__(self):
        self.last_seq = 0
        self.shown = []
        self.early = {}

    def receive(self, seq, text):
        if seq <= self.last_seq:
            return
        self.early[seq] = text
        while self.last_seq + 1 in self.early:
            self.last_seq += 1
            self.shown.append(self.early.pop(self.last_seq))

    def has_gap(self):
        return bool(self.early)


channel = Channel()
assert channel.send("c1", "hi") == 1
assert channel.send("c2", "how are you?") == 2
assert channel.send("c1", "hi") == 1  # a retry of c1 does not make a copy
assert channel.send("c3", "fine") == 3

reader = Reader()
reader.receive(1, "hi")
reader.receive(3, "fine")  # message 2 is late
assert reader.shown == ["hi"]
assert reader.has_gap()

for seq, text in channel.since(reader.last_seq):  # sync after the gap
    reader.receive(seq, text)
reader.receive(3, "fine")  # a duplicate delivery
assert reader.shown == ["hi", "how are you?", "fine"]
assert not reader.has_gap()
```

NOTE: Presence uses heartbeats.
Each client sends a heartbeat, for example each 10 seconds.
The server marks a user as offline after three heartbeats do not arrive.

CAUTION: A large group multiplies each message by the number of members.
For a group with many thousands of members, send a notice of new messages and let clients pull the messages.

## How to approach a design

A design is a sequence of decisions.
Each decision depends on the requirements and the numbers.
Use the same procedure for each new design.

To design a service, do these steps:

1. Write the functional requirements. List what a user can do.
2. Write the non-functional requirements: scale, latency, availability, consistency and durability.
3. Write what is out of scope.
4. Estimate the QPS, the peak QPS, the storage and the bandwidth.
5. Find the ratio of reads to writes.
6. Write the API. Give each endpoint its method, path, inputs and outputs.
7. Write the data model. Select the type of database from the queries.
8. Select the partition key for each large table.
9. Draw the high-level design with one box for each component.
10. Follow one read and one write through the diagram.
11. Find the parts with the most load or the most risk.
12. Do a deep dive on each of those parts.
13. Write the trade-offs of each decision and the alternatives.
14. Find what fails first when the load increases ten times.

Use the table to find a technique for each requirement.

| Requirement | Technique | Section |
|---|---|---|
| More requests than one server can handle | Stateless servers and load balancing | [Scaling the web tier](#scaling-the-web-tier) |
| Many reads of the same data | Caching | [Caching](#caching) |
| Too many reads for one database | Read replicas | [Databases and replication](#databases-and-replication) |
| Too much data or too many writes for one database | Partitioning and sharding | [Partitioning and sharding](#partitioning-and-sharding) |
| Replicas must agree | Quorums or a single leader | [Consistency and quorums](#consistency-and-quorums) |
| Slow work in a request | A queue and workers | [Queues and asynchronous work](#queues-and-asynchronous-work) |
| Protection from overload and failed dependencies | Rate limits, timeouts, retries, circuit breakers | [Rate limits and resilience](#rate-limits-and-resilience) |
| A target for uptime | Redundancy and an SLO | [Availability and reliability](#availability-and-reliability) |
| A target for latency | Percentiles, traces and capacity headroom | [Performance and observability](#performance-and-observability) |

Each technique gives a trade-off.
The table shows the most common ones.

| Decision | You get | You pay |
|---|---|---|
| Add a cache | Lower latency and less database load | Stale data and invalidation work |
| Add read replicas | More read capacity | Replication lag |
| Partition the data | More write capacity and storage | Cross-shard queries, and work to move data when you add shards |
| Use asynchronous replication | Fast writes | Possible data loss on failover |
| Use strong consistency | Correct reads | Higher latency and lower availability in a partition |
| Add a queue | Smooth bursts and retries | More delay and duplicate deliveries |
| Precompute results (fan-out on write) | Fast reads | Slow, expensive writes |
| Add redundancy | Higher availability | Higher cost and more operations work |

CAUTION: Do not add a component without a reason from the requirements or the numbers.
Each component adds cost, latency and new ways to fail.
