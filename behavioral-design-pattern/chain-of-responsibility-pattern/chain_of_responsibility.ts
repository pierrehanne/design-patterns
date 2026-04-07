/**
 * Chain of Responsibility Pattern
 * ================================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Pass a request along a chain of handlers. Each handler either processes
 *   the request or forwards it to the next handler in the chain.
 *
 * When to use:
 *   - HTTP middleware pipelines, event processing, support ticket escalation
 *   - When multiple objects can handle a request and the handler isn't known in advance
 *   - When handlers should be configurable dynamically
 *
 * Key Participants:
 *   - Handler (abstract): Declares handle method and next reference
 *   - ConcreteHandler: Handles specific requests, forwards the rest
 *   - Client: Sends request to the first handler
 */

// ---------------------------------------------------------------------------
// Request data
// ---------------------------------------------------------------------------
enum Priority {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4,
}

interface SupportTicket {
  id: string;
  title: string;
  priority: Priority;
  description: string;
  handledBy: string | null;
}

// ---------------------------------------------------------------------------
// Handler base class
// ---------------------------------------------------------------------------
abstract class SupportHandler {
  private next: SupportHandler | null = null;

  setNext(handler: SupportHandler): SupportHandler {
    this.next = handler;
    return handler; // Enables chaining: a.setNext(b).setNext(c)
  }

  handle(ticket: SupportTicket): SupportTicket {
    if (this.canHandle(ticket)) {
      return this.process(ticket);
    }
    if (this.next) {
      return this.next.handle(ticket);
    }
    console.log(`  [Unhandled] Ticket ${ticket.id} reached end of chain`);
    return ticket;
  }

  protected abstract canHandle(ticket: SupportTicket): boolean;
  protected abstract process(ticket: SupportTicket): SupportTicket;
}

// ---------------------------------------------------------------------------
// Concrete Handlers
// ---------------------------------------------------------------------------
class AutoResponder extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.priority === Priority.LOW;
  }
  protected process(ticket: SupportTicket): SupportTicket {
    ticket.handledBy = "AutoResponder (Bot)";
    console.log(`  [AutoResponder] Ticket ${ticket.id}: Sent automated FAQ response`);
    return ticket;
  }
}

class Level1Support extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.priority === Priority.MEDIUM;
  }
  protected process(ticket: SupportTicket): SupportTicket {
    ticket.handledBy = "Level 1 Support Agent";
    console.log(`  [Level1] Ticket ${ticket.id}: Assigned to support agent`);
    return ticket;
  }
}

class Level2Support extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.priority === Priority.HIGH;
  }
  protected process(ticket: SupportTicket): SupportTicket {
    ticket.handledBy = "Level 2 Senior Engineer";
    console.log(`  [Level2] Ticket ${ticket.id}: Escalated to senior engineer`);
    return ticket;
  }
}

class ManagerSupport extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.priority === Priority.CRITICAL;
  }
  protected process(ticket: SupportTicket): SupportTicket {
    ticket.handledBy = "Support Manager";
    console.log(`  [Manager] Ticket ${ticket.id}: CRITICAL — Manager notified`);
    return ticket;
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const auto = new AutoResponder();
const l1 = new Level1Support();
const l2 = new Level2Support();
const manager = new ManagerSupport();

// Build the chain
auto.setNext(l1).setNext(l2).setNext(manager);

const tickets: SupportTicket[] = [
  { id: "T-001", title: "Password reset", priority: Priority.LOW, description: "Can't remember", handledBy: null },
  { id: "T-002", title: "App crashes", priority: Priority.MEDIUM, description: "Error on iOS", handledBy: null },
  { id: "T-003", title: "Data corruption", priority: Priority.HIGH, description: "Inconsistent", handledBy: null },
  { id: "T-004", title: "Service outage", priority: Priority.CRITICAL, description: "Prod down!", handledBy: null },
];

console.log("Processing support tickets through the chain:\n");
for (const ticket of tickets) {
  const result = auto.handle(ticket);
  console.log(`    -> Handled by: ${result.handledBy}\n`);
}
