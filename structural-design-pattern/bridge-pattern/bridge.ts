/**
 * Bridge Pattern
 * ==============
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Decouple an abstraction from its implementation so the two can vary
 *   independently. Split a combinatorial class hierarchy into two separate
 *   hierarchies connected by composition (the "bridge").
 *
 * When to use:
 *   - When you'd need N × M subclasses without the bridge
 *   - When both abstraction and implementation need to be extensible
 *   - When you want to switch implementations at runtime
 *
 * Key Participants:
 *   - Abstraction: High-level logic (notification urgency)
 *   - Implementation: Low-level mechanism (delivery channel)
 *   - Bridge: The reference from Abstraction → Implementation
 */

// ---------------------------------------------------------------------------
// Implementation hierarchy — delivery channels
// ---------------------------------------------------------------------------
interface MessageChannel {
  send(title: string, body: string, recipient: string): string;
}

class EmailChannel implements MessageChannel {
  send(title: string, body: string, recipient: string): string {
    return `[Email → ${recipient}] Subject: ${title} | ${body}`;
  }
}

class SMSChannel implements MessageChannel {
  send(title: string, body: string, recipient: string): string {
    const short = body.length > 160 ? body.slice(0, 160) : body;
    return `[SMS → ${recipient}] ${short}`;
  }
}

class SlackChannel implements MessageChannel {
  constructor(private workspace: string = "default") {}

  send(title: string, body: string, recipient: string): string {
    return `[Slack#${this.workspace} → @${recipient}] *${title}*\n${body}`;
  }
}

// ---------------------------------------------------------------------------
// Abstraction hierarchy — notification types
// ---------------------------------------------------------------------------
abstract class Notification {
  // The "bridge" — composition, not inheritance
  constructor(protected channel: MessageChannel) {}

  abstract notify(recipient: string, message: string): string;
}

class RegularNotification extends Notification {
  notify(recipient: string, message: string): string {
    return this.channel.send("Notification", message, recipient);
  }
}

class UrgentNotification extends Notification {
  notify(recipient: string, message: string): string {
    const time = new Date().toLocaleTimeString();
    return this.channel.send(
      "URGENT",
      `[${time}] ${message} — Immediate action required!`,
      recipient
    );
  }
}

class ScheduledNotification extends Notification {
  constructor(channel: MessageChannel, private scheduledTime: string) {
    super(channel);
  }

  notify(recipient: string, message: string): string {
    return this.channel.send(
      `Scheduled (${this.scheduledTime})`,
      `${message} [Will be delivered at ${this.scheduledTime}]`,
      recipient
    );
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
// Without Bridge: 3 types × 3 channels = 9 classes
// With Bridge:    3 types + 3 channels  = 6 classes

console.log("=== Regular via Email ===");
console.log(
  new RegularNotification(new EmailChannel()).notify(
    "alice@co.com",
    "Your report is ready"
  )
);

console.log("\n=== Urgent via SMS ===");
console.log(
  new UrgentNotification(new SMSChannel()).notify(
    "555-1234",
    "Server CPU at 98%"
  )
);

console.log("\n=== Urgent via Slack ===");
console.log(
  new UrgentNotification(new SlackChannel("ops")).notify(
    "oncall",
    "Database failover triggered"
  )
);

console.log("\n=== Scheduled via Email ===");
console.log(
  new ScheduledNotification(new EmailChannel(), "2025-03-15 09:00").notify(
    "team@co.com",
    "Weekly standup reminder"
  )
);

// Swap channel at runtime
console.log("\n=== Same notification, different channels ===");
const channels: MessageChannel[] = [
  new EmailChannel(),
  new SMSChannel(),
  new SlackChannel("general"),
];
for (const ch of channels) {
  console.log(new UrgentNotification(ch).notify("bob", "Deploy failed"));
}
