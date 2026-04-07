"""
Iterator Pattern

Category: Behavioral Design Pattern

Intent:
    Provide a way to access the elements of an aggregate object sequentially
    without exposing its underlying representation.

When to use:
    - You need to traverse a collection without exposing its internal structure
    - You want to support multiple simultaneous traversals of a collection
    - You want to provide a uniform interface for traversing different structures

Key Participants:
    - Iterator: defines the interface for accessing and traversing elements
    - ConcreteIterator: implements the Iterator interface and tracks traversal state
    - Aggregate/Collection: defines the interface for creating an iterator
    - ConcreteAggregate: implements the iterator-creation interface
"""

from __future__ import annotations
from collections import deque
from typing import Iterator


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

class User:
    """A node in the social network."""

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name


class SocialNetwork:
    """
    A collection of users connected by friendships.
    Supports multiple traversal strategies via dedicated iterators.
    """

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        # Adjacency list: user name -> set of friend names
        self._friends: dict[str, set[str]] = {}

    def add_user(self, name: str) -> User:
        user = User(name)
        self._users[name] = user
        self._friends.setdefault(name, set())
        return user

    def add_friendship(self, name_a: str, name_b: str) -> None:
        """Friendships are bidirectional."""
        self._friends[name_a].add(name_b)
        self._friends[name_b].add(name_a)

    def get_user(self, name: str) -> User:
        return self._users[name]

    def get_friends(self, name: str) -> list[User]:
        return [self._users[f] for f in sorted(self._friends.get(name, set()))]

    # -- Iterator factory methods --

    def friends_of(self, name: str) -> FriendsIterator:
        """Iterate over direct friends of the given user."""
        return FriendsIterator(self, name)

    def bfs_from(self, name: str) -> BFSIterator:
        """Iterate over friends-of-friends using breadth-first search."""
        return BFSIterator(self, name)

    def mutual_friends(self, name_a: str, name_b: str) -> MutualFriendsIterator:
        """Iterate over users who are friends with both given users."""
        return MutualFriendsIterator(self, name_a, name_b)


# ---------------------------------------------------------------------------
# Concrete iterators (all implement Python's iterator protocol)
# ---------------------------------------------------------------------------

class FriendsIterator:
    """Yields direct friends of a user."""

    def __init__(self, network: SocialNetwork, user_name: str) -> None:
        self._friends = network.get_friends(user_name)
        self._index = 0

    def __iter__(self) -> Iterator[User]:
        return self

    def __next__(self) -> User:
        if self._index >= len(self._friends):
            raise StopIteration
        user = self._friends[self._index]
        self._index += 1
        return user


class BFSIterator:
    """
    Yields users reachable from a starting user via breadth-first traversal.
    The starting user itself is excluded.
    """

    def __init__(self, network: SocialNetwork, start_name: str) -> None:
        self._network = network
        self._visited: set[str] = {start_name}
        self._queue: deque[User] = deque()
        # Seed the queue with direct friends
        for friend in network.get_friends(start_name):
            if friend.name not in self._visited:
                self._visited.add(friend.name)
                self._queue.append(friend)

    def __iter__(self) -> Iterator[User]:
        return self

    def __next__(self) -> User:
        if not self._queue:
            raise StopIteration
        user = self._queue.popleft()
        # Enqueue unvisited friends of the current user
        for friend in self._network.get_friends(user.name):
            if friend.name not in self._visited:
                self._visited.add(friend.name)
                self._queue.append(friend)
        return user


class MutualFriendsIterator:
    """Yields users who are friends with both user_a and user_b."""

    def __init__(self, network: SocialNetwork, name_a: str, name_b: str) -> None:
        friends_a = {u.name for u in network.get_friends(name_a)}
        friends_b = {u.name for u in network.get_friends(name_b)}
        mutual_names = sorted(friends_a & friends_b)
        self._mutual = [network.get_user(n) for n in mutual_names]
        self._index = 0

    def __iter__(self) -> Iterator[User]:
        return self

    def __next__(self) -> User:
        if self._index >= len(self._mutual):
            raise StopIteration
        user = self._mutual[self._index]
        self._index += 1
        return user


# ---------------------------------------------------------------------------
# Main -- demonstrate the three iterators
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Build a small social network
    net = SocialNetwork()
    for name in ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]:
        net.add_user(name)

    net.add_friendship("Alice", "Bob")
    net.add_friendship("Alice", "Charlie")
    net.add_friendship("Bob", "Charlie")
    net.add_friendship("Bob", "Diana")
    net.add_friendship("Charlie", "Eve")
    net.add_friendship("Diana", "Eve")
    net.add_friendship("Eve", "Frank")

    # 1. Direct friends
    print("=== Alice's Friends ===")
    for user in net.friends_of("Alice"):
        print(f"  {user}")

    # 2. BFS traversal from Alice (friends of friends)
    print("\n=== BFS from Alice (all reachable) ===")
    for user in net.bfs_from("Alice"):
        print(f"  {user}")

    # 3. Mutual friends of Alice and Bob
    print("\n=== Mutual Friends of Alice and Bob ===")
    for user in net.mutual_friends("Alice", "Bob"):
        print(f"  {user}")

    # 4. Mutual friends of Bob and Eve
    print("\n=== Mutual Friends of Bob and Eve ===")
    for user in net.mutual_friends("Bob", "Eve"):
        print(f"  {user}")
