// Iterator Pattern
//
// Category: Behavioral Design Pattern
//
// Intent:
//   Provide a way to access the elements of an aggregate object sequentially
//   without exposing its underlying representation.
//
// When to use:
//   - You need to traverse a collection without exposing its internal structure
//   - You want to support multiple simultaneous traversals of a collection
//   - You want to provide a uniform interface for traversing different structures
//
// Key Participants:
//   - Iterator: defines the interface for accessing and traversing elements
//   - ConcreteIterator: implements the Iterator interface and tracks traversal state
//   - Aggregate/Collection: defines the interface for creating an iterator
//   - ConcreteAggregate: implements the iterator-creation interface

package main

import (
	"fmt"
	"sort"
)

// ---------------------------------------------------------------------------
// Domain model
// ---------------------------------------------------------------------------

type User struct {
	Name string
}

func (u *User) String() string {
	return u.Name
}

// SocialNetwork is a collection of users connected by friendships.
type SocialNetwork struct {
	users   map[string]*User
	friends map[string]map[string]bool // adjacency set
}

func NewSocialNetwork() *SocialNetwork {
	return &SocialNetwork{
		users:   make(map[string]*User),
		friends: make(map[string]map[string]bool),
	}
}

func (sn *SocialNetwork) AddUser(name string) *User {
	user := &User{Name: name}
	sn.users[name] = user
	if sn.friends[name] == nil {
		sn.friends[name] = make(map[string]bool)
	}
	return user
}

func (sn *SocialNetwork) AddFriendship(nameA, nameB string) {
	// Friendships are bidirectional
	sn.friends[nameA][nameB] = true
	sn.friends[nameB][nameA] = true
}

func (sn *SocialNetwork) GetFriends(name string) []*User {
	friendSet := sn.friends[name]
	names := make([]string, 0, len(friendSet))
	for n := range friendSet {
		names = append(names, n)
	}
	sort.Strings(names) // deterministic ordering
	result := make([]*User, len(names))
	for i, n := range names {
		result[i] = sn.users[n]
	}
	return result
}

// ---------------------------------------------------------------------------
// Iterator interface (idiomatic Go: HasNext / Next pattern)
// ---------------------------------------------------------------------------

// UserIterator provides sequential access to User elements.
type UserIterator interface {
	HasNext() bool
	Next() *User
}

// ---------------------------------------------------------------------------
// Concrete iterators
// ---------------------------------------------------------------------------

// FriendsIterator yields direct friends of a user.
type FriendsIterator struct {
	friends []*User
	index   int
}

func NewFriendsIterator(network *SocialNetwork, userName string) *FriendsIterator {
	return &FriendsIterator{
		friends: network.GetFriends(userName),
		index:   0,
	}
}

func (fi *FriendsIterator) HasNext() bool {
	return fi.index < len(fi.friends)
}

func (fi *FriendsIterator) Next() *User {
	if !fi.HasNext() {
		return nil
	}
	user := fi.friends[fi.index]
	fi.index++
	return user
}

// BFSIterator yields users reachable from a starting user via breadth-first
// traversal. The starting user itself is excluded.
type BFSIterator struct {
	network *SocialNetwork
	visited map[string]bool
	queue   []*User
}

func NewBFSIterator(network *SocialNetwork, startName string) *BFSIterator {
	visited := map[string]bool{startName: true}
	var queue []*User
	// Seed the queue with direct friends
	for _, friend := range network.GetFriends(startName) {
		if !visited[friend.Name] {
			visited[friend.Name] = true
			queue = append(queue, friend)
		}
	}
	return &BFSIterator{
		network: network,
		visited: visited,
		queue:   queue,
	}
}

func (bi *BFSIterator) HasNext() bool {
	return len(bi.queue) > 0
}

func (bi *BFSIterator) Next() *User {
	if !bi.HasNext() {
		return nil
	}
	// Dequeue front
	user := bi.queue[0]
	bi.queue = bi.queue[1:]
	// Enqueue unvisited friends of the current user
	for _, friend := range bi.network.GetFriends(user.Name) {
		if !bi.visited[friend.Name] {
			bi.visited[friend.Name] = true
			bi.queue = append(bi.queue, friend)
		}
	}
	return user
}

// MutualFriendsIterator yields users who are friends with both userA and userB.
type MutualFriendsIterator struct {
	mutual []*User
	index  int
}

func NewMutualFriendsIterator(network *SocialNetwork, nameA, nameB string) *MutualFriendsIterator {
	friendsA := make(map[string]bool)
	for _, u := range network.GetFriends(nameA) {
		friendsA[u.Name] = true
	}
	var mutual []*User
	for _, u := range network.GetFriends(nameB) {
		if friendsA[u.Name] {
			mutual = append(mutual, u)
		}
	}
	return &MutualFriendsIterator{
		mutual: mutual,
		index:  0,
	}
}

func (mi *MutualFriendsIterator) HasNext() bool {
	return mi.index < len(mi.mutual)
}

func (mi *MutualFriendsIterator) Next() *User {
	if !mi.HasNext() {
		return nil
	}
	user := mi.mutual[mi.index]
	mi.index++
	return user
}

// ---------------------------------------------------------------------------
// Helper: iterate and print
// ---------------------------------------------------------------------------

func printAll(iter UserIterator) {
	for iter.HasNext() {
		fmt.Printf("  %s\n", iter.Next())
	}
}

// ---------------------------------------------------------------------------
// Main -- demonstrate the three iterators
// ---------------------------------------------------------------------------

func main() {
	net := NewSocialNetwork()
	for _, name := range []string{"Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"} {
		net.AddUser(name)
	}

	net.AddFriendship("Alice", "Bob")
	net.AddFriendship("Alice", "Charlie")
	net.AddFriendship("Bob", "Charlie")
	net.AddFriendship("Bob", "Diana")
	net.AddFriendship("Charlie", "Eve")
	net.AddFriendship("Diana", "Eve")
	net.AddFriendship("Eve", "Frank")

	// 1. Direct friends
	fmt.Println("=== Alice's Friends ===")
	printAll(NewFriendsIterator(net, "Alice"))

	// 2. BFS traversal from Alice (friends of friends)
	fmt.Println("\n=== BFS from Alice (all reachable) ===")
	printAll(NewBFSIterator(net, "Alice"))

	// 3. Mutual friends of Alice and Bob
	fmt.Println("\n=== Mutual Friends of Alice and Bob ===")
	printAll(NewMutualFriendsIterator(net, "Alice", "Bob"))

	// 4. Mutual friends of Bob and Eve
	fmt.Println("\n=== Mutual Friends of Bob and Eve ===")
	printAll(NewMutualFriendsIterator(net, "Bob", "Eve"))
}
