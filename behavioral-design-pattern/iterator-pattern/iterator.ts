/**
 * Iterator Pattern
 *
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Provide a way to access the elements of an aggregate object sequentially
 *   without exposing its underlying representation.
 *
 * When to use:
 *   - You need to traverse a collection without exposing its internal structure
 *   - You want to support multiple simultaneous traversals of a collection
 *   - You want to provide a uniform interface for traversing different structures
 *
 * Key Participants:
 *   - Iterator: defines the interface for accessing and traversing elements
 *   - ConcreteIterator: implements the Iterator interface and tracks traversal state
 *   - Aggregate/Collection: defines the interface for creating an iterator
 *   - ConcreteAggregate: implements the iterator-creation interface
 */

// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

class User {
  constructor(public readonly name: string) {}

  toString(): string {
    return this.name;
  }
}

class SocialNetwork {
  private users = new Map<string, User>();
  private friends = new Map<string, Set<string>>();

  addUser(name: string): User {
    const user = new User(name);
    this.users.set(name, user);
    if (!this.friends.has(name)) {
      this.friends.set(name, new Set());
    }
    return user;
  }

  addFriendship(nameA: string, nameB: string): void {
    // Friendships are bidirectional
    this.friends.get(nameA)!.add(nameB);
    this.friends.get(nameB)!.add(nameA);
  }

  getUser(name: string): User {
    return this.users.get(name)!;
  }

  getFriends(name: string): User[] {
    const friendNames = this.friends.get(name) ?? new Set<string>();
    return [...friendNames]
      .sort()
      .map((n) => this.users.get(n)!);
  }

  // -- Iterator factory methods --

  friendsOf(name: string): FriendsIterator {
    return new FriendsIterator(this, name);
  }

  bfsFrom(name: string): BFSIterator {
    return new BFSIterator(this, name);
  }

  mutualFriends(nameA: string, nameB: string): MutualFriendsIterator {
    return new MutualFriendsIterator(this, nameA, nameB);
  }
}

// ---------------------------------------------------------------------------
// Concrete iterators (all implement Symbol.iterator protocol)
// ---------------------------------------------------------------------------

/** Yields direct friends of a user. */
class FriendsIterator implements Iterable<User>, Iterator<User> {
  private friendsList: User[];
  private index = 0;

  constructor(network: SocialNetwork, userName: string) {
    this.friendsList = network.getFriends(userName);
  }

  [Symbol.iterator](): Iterator<User> {
    return this;
  }

  next(): IteratorResult<User> {
    if (this.index >= this.friendsList.length) {
      return { done: true, value: undefined };
    }
    return { done: false, value: this.friendsList[this.index++] };
  }
}

/**
 * Yields users reachable from a starting user via breadth-first traversal.
 * The starting user itself is excluded.
 */
class BFSIterator implements Iterable<User>, Iterator<User> {
  private visited: Set<string>;
  private queue: User[] = [];
  private network: SocialNetwork;

  constructor(network: SocialNetwork, startName: string) {
    this.network = network;
    this.visited = new Set([startName]);
    // Seed the queue with direct friends
    for (const friend of network.getFriends(startName)) {
      if (!this.visited.has(friend.name)) {
        this.visited.add(friend.name);
        this.queue.push(friend);
      }
    }
  }

  [Symbol.iterator](): Iterator<User> {
    return this;
  }

  next(): IteratorResult<User> {
    if (this.queue.length === 0) {
      return { done: true, value: undefined };
    }
    const user = this.queue.shift()!;
    // Enqueue unvisited friends of the current user
    for (const friend of this.network.getFriends(user.name)) {
      if (!this.visited.has(friend.name)) {
        this.visited.add(friend.name);
        this.queue.push(friend);
      }
    }
    return { done: false, value: user };
  }
}

/** Yields users who are friends with both userA and userB. */
class MutualFriendsIterator implements Iterable<User>, Iterator<User> {
  private mutualList: User[];
  private index = 0;

  constructor(network: SocialNetwork, nameA: string, nameB: string) {
    const friendsA = new Set(network.getFriends(nameA).map((u) => u.name));
    const friendsB = new Set(network.getFriends(nameB).map((u) => u.name));
    const mutualNames = [...friendsA].filter((n) => friendsB.has(n)).sort();
    this.mutualList = mutualNames.map((n) => network.getUser(n));
  }

  [Symbol.iterator](): Iterator<User> {
    return this;
  }

  next(): IteratorResult<User> {
    if (this.index >= this.mutualList.length) {
      return { done: true, value: undefined };
    }
    return { done: false, value: this.mutualList[this.index++] };
  }
}

// ---------------------------------------------------------------------------
// Main -- demonstrate the three iterators
// ---------------------------------------------------------------------------

function main(): void {
  const net = new SocialNetwork();
  for (const name of ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]) {
    net.addUser(name);
  }

  net.addFriendship("Alice", "Bob");
  net.addFriendship("Alice", "Charlie");
  net.addFriendship("Bob", "Charlie");
  net.addFriendship("Bob", "Diana");
  net.addFriendship("Charlie", "Eve");
  net.addFriendship("Diana", "Eve");
  net.addFriendship("Eve", "Frank");

  // 1. Direct friends
  console.log("=== Alice's Friends ===");
  for (const user of net.friendsOf("Alice")) {
    console.log(`  ${user}`);
  }

  // 2. BFS traversal from Alice (friends of friends)
  console.log("\n=== BFS from Alice (all reachable) ===");
  for (const user of net.bfsFrom("Alice")) {
    console.log(`  ${user}`);
  }

  // 3. Mutual friends of Alice and Bob
  console.log("\n=== Mutual Friends of Alice and Bob ===");
  for (const user of net.mutualFriends("Alice", "Bob")) {
    console.log(`  ${user}`);
  }

  // 4. Mutual friends of Bob and Eve
  console.log("\n=== Mutual Friends of Bob and Eve ===");
  for (const user of net.mutualFriends("Bob", "Eve")) {
    console.log(`  ${user}`);
  }
}

main();
