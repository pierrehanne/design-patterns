// Mediator Pattern
// =================
// Category: Behavioral Design Pattern
//
// Intent:
//   Define an object that encapsulates how a set of objects interact.
//   The Mediator promotes loose coupling by keeping objects from referring
//   to each other explicitly, and lets you vary their interaction independently.
//
// When to use:
//   - A set of objects communicate in well-defined but complex ways
//   - Reusing an object is difficult because it refers to many other objects
//   - Behavior distributed between several classes should be customizable
//     without a lot of subclassing
//
// Key Participants:
//   - Mediator: defines the interface for communication between Colleague objects
//   - ConcreteMediator (ChatRoom): coordinates communication between Colleague objects
//   - Colleague (User): each Colleague communicates with its Mediator whenever
//     it would have otherwise communicated with another Colleague

package main

import (
	"fmt"
	"strings"
	"time"
)

// --- Mediator Interface ---

// ChatMediator defines the contract for colleague communication.
type ChatMediator interface {
	SendMessage(message string, sender *User, recipient *User)
	AddUser(user *User)
}

// --- Colleague ---

// User is a chat participant that communicates through the mediator, never directly.
type User struct {
	Name     string
	Inbox    []string
	mediator ChatMediator
}

// NewUser creates a user and registers it with the mediator.
func NewUser(name string, mediator ChatMediator) *User {
	u := &User{
		Name:     name,
		Inbox:    []string{},
		mediator: mediator,
	}
	mediator.AddUser(u)
	return u
}

// Send sends a message through the mediator. Pass nil for recipient to broadcast.
func (u *User) Send(message string, recipient *User) {
	target := " to everyone"
	if recipient != nil {
		target = " to " + recipient.Name
	}
	fmt.Printf("[%s] sends '%s'%s\n", u.Name, message, target)
	u.mediator.SendMessage(message, u, recipient)
}

// Receive is called by the mediator when a message is delivered to this user.
func (u *User) Receive(message string, sender *User) {
	fmt.Printf("  [%s] received from %s: '%s'\n", u.Name, sender.Name, message)
	u.Inbox = append(u.Inbox, fmt.Sprintf("%s: %s", sender.Name, message))
}

// --- Concrete Mediator ---

// logEntry stores a single message event in the room log.
type logEntry struct {
	timestamp time.Time
	sender    string
	recipient string // empty means broadcast
	message   string
}

// ChatRoom is the concrete mediator that manages users and routes messages.
type ChatRoom struct {
	roomName string
	users    []*User
	log      []logEntry
}

// NewChatRoom creates a new chat room mediator.
func NewChatRoom(roomName string) *ChatRoom {
	return &ChatRoom{
		roomName: roomName,
		users:    []*User{},
		log:      []logEntry{},
	}
}

// AddUser registers a user with the chat room.
func (r *ChatRoom) AddUser(user *User) {
	r.users = append(r.users, user)
	fmt.Printf("  >> %s joined '%s'\n", user.Name, r.roomName)
}

// SendMessage routes a message. If recipient is nil, broadcast to all except sender.
func (r *ChatRoom) SendMessage(message string, sender *User, recipient *User) {
	entry := logEntry{
		timestamp: time.Now(),
		sender:    sender.Name,
		message:   message,
	}

	if recipient != nil {
		// Direct message -- deliver only to the specified recipient
		entry.recipient = recipient.Name
		recipient.Receive(message, sender)
	} else {
		// Broadcast -- deliver to every user except the sender
		for _, user := range r.users {
			if user != sender {
				user.Receive(message, sender)
			}
		}
	}

	r.log = append(r.log, entry)
}

// ShowLog displays the full message history kept by the mediator.
func (r *ChatRoom) ShowLog() {
	fmt.Printf("\n--- Chat log for '%s' ---\n", r.roomName)
	for _, entry := range r.log {
		ts := entry.timestamp.Format("15:04:05")
		if entry.recipient != "" {
			fmt.Printf("  [%s] DM %s -> %s: %s\n", ts, entry.sender, entry.recipient, entry.message)
		} else {
			fmt.Printf("  [%s] BROADCAST %s: %s\n", ts, entry.sender, entry.message)
		}
	}
}

// --- Main ---

func main() {
	// Create the mediator (chat room)
	room := NewChatRoom("Design Patterns Study Group")

	// Create colleagues (users) -- they register themselves with the room
	alice := NewUser("Alice", room)
	bob := NewUser("Bob", room)
	charlie := NewUser("Charlie", room)

	fmt.Println()

	// Broadcast: Alice sends a message to everyone in the room
	alice.Send("Hey everyone, ready to discuss the Mediator pattern?", nil)
	fmt.Println()

	// Direct message: Bob replies only to Alice
	bob.Send("Sure, I just finished reading about it!", alice)
	fmt.Println()

	// Broadcast: Charlie shares with the group
	charlie.Send("The key insight is that colleagues don't know about each other.", nil)
	fmt.Println()

	// Direct message: Alice to Charlie
	alice.Send("Exactly! The mediator handles all the routing.", charlie)

	// Show the centralized log maintained by the mediator
	room.ShowLog()

	// Demonstrate that each user keeps its own inbox
	fmt.Printf("\nAlice's inbox: [%s]\n", strings.Join(alice.Inbox, ", "))
	fmt.Printf("Bob's inbox:   [%s]\n", strings.Join(bob.Inbox, ", "))
}
