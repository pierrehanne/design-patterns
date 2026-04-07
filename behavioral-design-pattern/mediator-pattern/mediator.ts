/**
 * Mediator Pattern
 * =================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Define an object that encapsulates how a set of objects interact.
 *   The Mediator promotes loose coupling by keeping objects from referring
 *   to each other explicitly, and lets you vary their interaction independently.
 *
 * When to use:
 *   - A set of objects communicate in well-defined but complex ways
 *   - Reusing an object is difficult because it refers to many other objects
 *   - Behavior distributed between several classes should be customizable
 *     without a lot of subclassing
 *
 * Key Participants:
 *   - Mediator: defines the interface for communication between Colleague objects
 *   - ConcreteMediator (ChatRoom): coordinates communication between Colleague objects
 *   - Colleague (User): each Colleague communicates with its Mediator whenever
 *     it would have otherwise communicated with another Colleague
 */

// --- Mediator Interface ---

interface ChatMediator {
  sendMessage(message: string, sender: User, recipient?: User): void;
  addUser(user: User): void;
}

// --- Colleague ---

class User {
  public readonly inbox: string[] = [];

  constructor(
    public readonly name: string,
    private readonly mediator: ChatMediator
  ) {
    // Automatically register with the mediator upon creation
    this.mediator.addUser(this);
  }

  /** Send a message through the mediator (broadcast or direct). */
  send(message: string, recipient?: User): void {
    const target = recipient ? ` to ${recipient.name}` : " to everyone";
    console.log(`[${this.name}] sends '${message}'${target}`);
    this.mediator.sendMessage(message, this, recipient);
  }

  /** Called by the mediator when a message is delivered to this user. */
  receive(message: string, sender: User): void {
    const formatted = `  [${this.name}] received from ${sender.name}: '${message}'`;
    console.log(formatted);
    this.inbox.push(`${sender.name}: ${message}`);
  }
}

// --- Concrete Mediator ---

class ChatRoom implements ChatMediator {
  private users: User[] = [];
  private log: string[] = [];

  constructor(private readonly roomName: string) {}

  addUser(user: User): void {
    this.users.push(user);
    console.log(`  >> ${user.name} joined '${this.roomName}'`);
  }

  sendMessage(message: string, sender: User, recipient?: User): void {
    const timestamp = new Date().toLocaleTimeString();

    if (recipient !== undefined) {
      // Direct message -- only deliver to the specified recipient
      if (!this.users.includes(recipient)) {
        console.log(`  >> Error: ${recipient.name} is not in the room`);
        return;
      }
      recipient.receive(message, sender);
      this.log.push(`[${timestamp}] DM ${sender.name} -> ${recipient.name}: ${message}`);
    } else {
      // Broadcast -- deliver to every user except the sender
      for (const user of this.users) {
        if (user !== sender) {
          user.receive(message, sender);
        }
      }
      this.log.push(`[${timestamp}] BROADCAST ${sender.name}: ${message}`);
    }
  }

  /** Display the full message history kept by the mediator. */
  showLog(): void {
    console.log(`\n--- Chat log for '${this.roomName}' ---`);
    for (const entry of this.log) {
      console.log(`  ${entry}`);
    }
  }
}

// --- Main ---

function main(): void {
  // Create the mediator (chat room)
  const room = new ChatRoom("Design Patterns Study Group");

  // Create colleagues (users) -- they register themselves with the room
  const alice = new User("Alice", room);
  const bob = new User("Bob", room);
  const charlie = new User("Charlie", room);

  console.log();

  // Broadcast: Alice sends a message to everyone in the room
  alice.send("Hey everyone, ready to discuss the Mediator pattern?");
  console.log();

  // Direct message: Bob replies only to Alice
  bob.send("Sure, I just finished reading about it!", alice);
  console.log();

  // Broadcast: Charlie shares with the group
  charlie.send("The key insight is that colleagues don't know about each other.");
  console.log();

  // Direct message: Alice to Charlie
  alice.send("Exactly! The mediator handles all the routing.", charlie);

  // Show the centralized log maintained by the mediator
  room.showLog();

  // Demonstrate that each user keeps its own inbox
  console.log(`\nAlice's inbox:`, alice.inbox);
  console.log(`Bob's inbox:  `, bob.inbox);
}

main();
