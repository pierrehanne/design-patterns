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
//
// Note: Rust's ownership model makes the classic OOP mediator tricky.
// We use indices into a shared Vec instead of reference cycles.

use std::fmt;

// --- Message type for the log ---

#[derive(Debug, Clone)]
struct LogEntry {
    sender: String,
    recipient: Option<String>, // None = broadcast
    message: String,
}

impl fmt::Display for LogEntry {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self.recipient {
            Some(r) => write!(f, "DM {} -> {}: {}", self.sender, r, self.message),
            None => write!(f, "BROADCAST {}: {}", self.sender, self.message),
        }
    }
}

// --- Colleague ---

#[derive(Debug)]
struct User {
    name: String,
    inbox: Vec<String>,
}

impl User {
    fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            inbox: Vec::new(),
        }
    }

    /// Called by the mediator to deliver a message to this user.
    fn receive(&mut self, message: &str, sender_name: &str) {
        println!("  [{}] received from {}: '{}'", self.name, sender_name, message);
        self.inbox.push(format!("{}: {}", sender_name, message));
    }
}

// --- Concrete Mediator ---
// The ChatRoom owns all users and coordinates their communication.

struct ChatRoom {
    room_name: String,
    users: Vec<User>,
    log: Vec<LogEntry>,
}

impl ChatRoom {
    fn new(room_name: &str) -> Self {
        Self {
            room_name: room_name.to_string(),
            users: Vec::new(),
            log: Vec::new(),
        }
    }

    /// Register a user and return their index (used as an ID).
    fn add_user(&mut self, name: &str) -> usize {
        let idx = self.users.len();
        self.users.push(User::new(name));
        println!("  >> {} joined '{}'", name, self.room_name);
        idx
    }

    /// Broadcast a message from sender to all other users.
    fn broadcast(&mut self, sender_idx: usize, message: &str) {
        let sender_name = self.users[sender_idx].name.clone();
        println!("[{}] sends '{}' to everyone", sender_name, message);

        self.log.push(LogEntry {
            sender: sender_name.clone(),
            recipient: None,
            message: message.to_string(),
        });

        // Deliver to every user except the sender
        for i in 0..self.users.len() {
            if i != sender_idx {
                self.users[i].receive(message, &sender_name);
            }
        }
    }

    /// Send a direct message from one user to another.
    fn direct_message(&mut self, sender_idx: usize, recipient_idx: usize, message: &str) {
        let sender_name = self.users[sender_idx].name.clone();
        let recipient_name = self.users[recipient_idx].name.clone();
        println!("[{}] sends '{}' to {}", sender_name, message, recipient_name);

        self.log.push(LogEntry {
            sender: sender_name.clone(),
            recipient: Some(recipient_name),
            message: message.to_string(),
        });

        self.users[recipient_idx].receive(message, &sender_name);
    }

    /// Display the full message history kept by the mediator.
    fn show_log(&self) {
        println!("\n--- Chat log for '{}' ---", self.room_name);
        for entry in &self.log {
            println!("  {}", entry);
        }
    }

    /// Get a reference to a user's inbox for inspection.
    fn user_inbox(&self, idx: usize) -> (&str, &[String]) {
        (&self.users[idx].name, &self.users[idx].inbox)
    }
}

// --- Main ---

fn main() {
    // Create the mediator (chat room)
    let mut room = ChatRoom::new("Design Patterns Study Group");

    // Register colleagues (users) -- the room owns them, we keep indices
    let alice = room.add_user("Alice");
    let bob = room.add_user("Bob");
    let charlie = room.add_user("Charlie");

    println!();

    // Broadcast: Alice sends a message to everyone in the room
    room.broadcast(alice, "Hey everyone, ready to discuss the Mediator pattern?");
    println!();

    // Direct message: Bob replies only to Alice
    room.direct_message(bob, alice, "Sure, I just finished reading about it!");
    println!();

    // Broadcast: Charlie shares with the group
    room.broadcast(charlie, "The key insight is that colleagues don't know about each other.");
    println!();

    // Direct message: Alice to Charlie
    room.direct_message(alice, charlie, "Exactly! The mediator handles all the routing.");

    // Show the centralized log maintained by the mediator
    room.show_log();

    // Demonstrate that each user keeps its own inbox
    let (name, inbox) = room.user_inbox(alice);
    println!("\n{}'s inbox: {:?}", name, inbox);
    let (name, inbox) = room.user_inbox(bob);
    println!("{}'s inbox:   {:?}", name, inbox);
}
