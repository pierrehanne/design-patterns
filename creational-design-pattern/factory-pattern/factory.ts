/**
 * Factory Method Pattern
 * ======================
 * Category: Creational Design Pattern
 *
 * Intent:
 *   Define an interface for creating objects, but let the factory decide which
 *   concrete class to instantiate. Client code works with the product interface
 *   and never needs to know the concrete type.
 *
 * When to use:
 *   - When a module can't anticipate the type of objects it needs to create
 *   - When you want to centralize and encapsulate object creation logic
 *   - When adding new product types should NOT require changing existing code
 *
 * Key Participants:
 *   - Product (interface): Defines the contract all concrete products implement
 *   - ConcreteProduct: Specific implementations
 *   - Factory: Contains the creation logic that returns Product instances
 */

// ---------------------------------------------------------------------------
// Product Interface
// ---------------------------------------------------------------------------
interface Notification {
  send(recipient: string, message: string): string;
}

// ---------------------------------------------------------------------------
// Concrete Products
// ---------------------------------------------------------------------------
class EmailNotification implements Notification {
  constructor(private sender: string = "noreply@example.com") {}

  send(recipient: string, message: string): string {
    return `[Email] From ${this.sender} to ${recipient}: ${message}`;
  }
}

class SMSNotification implements Notification {
  constructor(private phonePrefix: string = "+1") {}

  send(recipient: string, message: string): string {
    return `[SMS] To ${this.phonePrefix}${recipient}: ${message}`;
  }
}

class PushNotification implements Notification {
  constructor(private platform: string = "mobile") {}

  send(recipient: string, message: string): string {
    return `[Push/${this.platform}] To ${recipient}: ${message}`;
  }
}

// ---------------------------------------------------------------------------
// Factory
// ---------------------------------------------------------------------------
type NotificationConstructor = new (...args: any[]) => Notification;

class NotificationFactory {
  // Registry maps channel names to their constructors
  private static registry: Map<string, NotificationConstructor> = new Map([
    ["email", EmailNotification],
    ["sms", SMSNotification],
    ["push", PushNotification],
  ]);

  /**
   * Create a notification by channel name.
   * The client never directly references concrete classes.
   */
  static create(channel: string, ...args: any[]): Notification {
    const Ctor = this.registry.get(channel);
    if (!Ctor) {
      const available = [...this.registry.keys()].join(", ");
      throw new Error(`Unknown channel '${channel}'. Available: ${available}`);
    }
    return new Ctor(...args);
  }

  /** Register a new notification type at runtime — open/closed principle. */
  static register(channel: string, ctor: NotificationConstructor): void {
    this.registry.set(channel, ctor);
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
for (const channel of ["email", "sms", "push"]) {
  const notification = NotificationFactory.create(channel);
  console.log(notification.send("user@example.com", "Your order has shipped!"));
}

// Demonstrate extensibility: add a new type without modifying the factory
class SlackNotification implements Notification {
  constructor(private workspace: string = "general") {}

  send(recipient: string, message: string): string {
    return `[Slack#${this.workspace}] @${recipient}: ${message}`;
  }
}

NotificationFactory.register("slack", SlackNotification);
const slack = NotificationFactory.create("slack", "engineering");
console.log(slack.send("alice", "Deploy complete!"));
