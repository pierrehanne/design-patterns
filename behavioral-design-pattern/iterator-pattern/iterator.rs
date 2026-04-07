//! Iterator Pattern
//!
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!   Provide a way to access the elements of an aggregate object sequentially
//!   without exposing its underlying representation.
//!
//! When to use:
//!   - You need to traverse a collection without exposing its internal structure
//!   - You want to support multiple simultaneous traversals of a collection
//!   - You want to provide a uniform interface for traversing different structures
//!
//! Key Participants:
//!   - Iterator: defines the interface for accessing and traversing elements
//!   - ConcreteIterator: implements the Iterator interface and tracks traversal state
//!   - Aggregate/Collection: defines the interface for creating an iterator
//!   - ConcreteAggregate: implements the iterator-creation interface

use std::collections::{BTreeSet, HashMap, VecDeque};

// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct User {
    name: String,
}

impl User {
    fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
        }
    }
}

impl std::fmt::Display for User {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.name)
    }
}

/// A collection of users connected by friendships.
struct SocialNetwork {
    users: HashMap<String, User>,
    // Using BTreeSet for deterministic ordering
    friends: HashMap<String, BTreeSet<String>>,
}

impl SocialNetwork {
    fn new() -> Self {
        Self {
            users: HashMap::new(),
            friends: HashMap::new(),
        }
    }

    fn add_user(&mut self, name: &str) {
        self.users.insert(name.to_string(), User::new(name));
        self.friends.entry(name.to_string()).or_default();
    }

    fn add_friendship(&mut self, name_a: &str, name_b: &str) {
        // Friendships are bidirectional
        self.friends
            .entry(name_a.to_string())
            .or_default()
            .insert(name_b.to_string());
        self.friends
            .entry(name_b.to_string())
            .or_default()
            .insert(name_a.to_string());
    }

    fn get_friends(&self, name: &str) -> Vec<User> {
        self.friends
            .get(name)
            .map(|set| {
                set.iter()
                    .filter_map(|n| self.users.get(n).cloned())
                    .collect()
            })
            .unwrap_or_default()
    }

    // -- Iterator factory methods --

    fn friends_of(&self, name: &str) -> FriendsIterator {
        FriendsIterator {
            friends: self.get_friends(name),
            index: 0,
        }
    }

    fn bfs_from(&self, name: &str) -> BFSIterator {
        let mut visited = BTreeSet::new();
        visited.insert(name.to_string());
        let mut queue = VecDeque::new();
        // Seed the queue with direct friends
        for friend in self.get_friends(name) {
            if visited.insert(friend.name.clone()) {
                queue.push_back(friend);
            }
        }
        BFSIterator {
            network_friends: self
                .friends
                .iter()
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect(),
            users: self.users.clone(),
            visited,
            queue,
        }
    }

    fn mutual_friends(&self, name_a: &str, name_b: &str) -> MutualFriendsIterator {
        let friends_a: BTreeSet<String> = self
            .get_friends(name_a)
            .into_iter()
            .map(|u| u.name)
            .collect();
        let friends_b: BTreeSet<String> = self
            .get_friends(name_b)
            .into_iter()
            .map(|u| u.name)
            .collect();
        let mutual: Vec<User> = friends_a
            .intersection(&friends_b)
            .filter_map(|n| self.users.get(n).cloned())
            .collect();
        MutualFriendsIterator { mutual, index: 0 }
    }
}

// ---------------------------------------------------------------------------
// Concrete iterators (all implement Rust's Iterator trait)
// ---------------------------------------------------------------------------

/// Yields direct friends of a user.
struct FriendsIterator {
    friends: Vec<User>,
    index: usize,
}

impl Iterator for FriendsIterator {
    type Item = User;

    fn next(&mut self) -> Option<Self::Item> {
        if self.index >= self.friends.len() {
            return None;
        }
        let user = self.friends[self.index].clone();
        self.index += 1;
        Some(user)
    }
}

/// Yields users reachable from a starting user via breadth-first traversal.
/// The starting user itself is excluded.
struct BFSIterator {
    network_friends: HashMap<String, BTreeSet<String>>,
    users: HashMap<String, User>,
    visited: BTreeSet<String>,
    queue: VecDeque<User>,
}

impl Iterator for BFSIterator {
    type Item = User;

    fn next(&mut self) -> Option<Self::Item> {
        let user = self.queue.pop_front()?;
        // Enqueue unvisited friends of the current user
        if let Some(friend_names) = self.network_friends.get(&user.name) {
            for friend_name in friend_names {
                if self.visited.insert(friend_name.clone()) {
                    if let Some(friend) = self.users.get(friend_name) {
                        self.queue.push_back(friend.clone());
                    }
                }
            }
        }
        Some(user)
    }
}

/// Yields users who are friends with both user_a and user_b.
struct MutualFriendsIterator {
    mutual: Vec<User>,
    index: usize,
}

impl Iterator for MutualFriendsIterator {
    type Item = User;

    fn next(&mut self) -> Option<Self::Item> {
        if self.index >= self.mutual.len() {
            return None;
        }
        let user = self.mutual[self.index].clone();
        self.index += 1;
        Some(user)
    }
}

// ---------------------------------------------------------------------------
// Main -- demonstrate the three iterators
// ---------------------------------------------------------------------------

fn main() {
    let mut net = SocialNetwork::new();
    for name in &["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"] {
        net.add_user(name);
    }

    net.add_friendship("Alice", "Bob");
    net.add_friendship("Alice", "Charlie");
    net.add_friendship("Bob", "Charlie");
    net.add_friendship("Bob", "Diana");
    net.add_friendship("Charlie", "Eve");
    net.add_friendship("Diana", "Eve");
    net.add_friendship("Eve", "Frank");

    // 1. Direct friends
    println!("=== Alice's Friends ===");
    for user in net.friends_of("Alice") {
        println!("  {}", user);
    }

    // 2. BFS traversal from Alice (friends of friends)
    println!("\n=== BFS from Alice (all reachable) ===");
    for user in net.bfs_from("Alice") {
        println!("  {}", user);
    }

    // 3. Mutual friends of Alice and Bob
    println!("\n=== Mutual Friends of Alice and Bob ===");
    for user in net.mutual_friends("Alice", "Bob") {
        println!("  {}", user);
    }

    // 4. Mutual friends of Bob and Eve
    println!("\n=== Mutual Friends of Bob and Eve ===");
    for user in net.mutual_friends("Bob", "Eve") {
        println!("  {}", user);
    }
}
