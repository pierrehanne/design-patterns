//! Chain of Responsibility Pattern
//! ================================
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!   Pass a request along a chain of handlers. Each handler either processes
//!   the request or forwards it to the next.
//!
//! When to use:
//!   - Middleware pipelines, event processing, escalation systems
//!   - When the handler isn't known in advance
//!
//! Rust approach:
//!   We use a Vec of boxed handler closures rather than linked objects,
//!   which is more idiomatic in Rust and avoids lifetime complexity.

// ---------------------------------------------------------------------------
// Request data
// ---------------------------------------------------------------------------
#[derive(Debug, Clone, PartialEq)]
enum Priority { Low, Medium, High, Critical }

#[derive(Debug)]
struct SupportTicket {
    id: String,
    title: String,
    priority: Priority,
    handled_by: Option<String>,
}

// ---------------------------------------------------------------------------
// Handler trait
// ---------------------------------------------------------------------------
trait SupportHandler {
    fn can_handle(&self, ticket: &SupportTicket) -> bool;
    fn process(&self, ticket: &mut SupportTicket);
    fn name(&self) -> &str;
}

// ---------------------------------------------------------------------------
// Concrete Handlers
// ---------------------------------------------------------------------------
struct AutoResponder;
impl SupportHandler for AutoResponder {
    fn can_handle(&self, ticket: &SupportTicket) -> bool {
        ticket.priority == Priority::Low
    }
    fn process(&self, ticket: &mut SupportTicket) {
        ticket.handled_by = Some("AutoResponder (Bot)".to_string());
        println!("  [AutoResponder] Ticket {}: Sent automated FAQ response", ticket.id);
    }
    fn name(&self) -> &str { "AutoResponder" }
}

struct Level1Support;
impl SupportHandler for Level1Support {
    fn can_handle(&self, ticket: &SupportTicket) -> bool {
        ticket.priority == Priority::Medium
    }
    fn process(&self, ticket: &mut SupportTicket) {
        ticket.handled_by = Some("Level 1 Support Agent".to_string());
        println!("  [Level1] Ticket {}: Assigned to support agent", ticket.id);
    }
    fn name(&self) -> &str { "Level1" }
}

struct Level2Support;
impl SupportHandler for Level2Support {
    fn can_handle(&self, ticket: &SupportTicket) -> bool {
        ticket.priority == Priority::High
    }
    fn process(&self, ticket: &mut SupportTicket) {
        ticket.handled_by = Some("Level 2 Senior Engineer".to_string());
        println!("  [Level2] Ticket {}: Escalated to senior engineer", ticket.id);
    }
    fn name(&self) -> &str { "Level2" }
}

struct ManagerSupport;
impl SupportHandler for ManagerSupport {
    fn can_handle(&self, ticket: &SupportTicket) -> bool {
        ticket.priority == Priority::Critical
    }
    fn process(&self, ticket: &mut SupportTicket) {
        ticket.handled_by = Some("Support Manager".to_string());
        println!("  [Manager] Ticket {}: CRITICAL — Manager notified", ticket.id);
    }
    fn name(&self) -> &str { "Manager" }
}

// ---------------------------------------------------------------------------
// Chain — iterates through handlers until one processes the ticket
// ---------------------------------------------------------------------------
struct SupportChain {
    handlers: Vec<Box<dyn SupportHandler>>,
}

impl SupportChain {
    fn new() -> Self {
        Self { handlers: Vec::new() }
    }

    fn add(mut self, handler: Box<dyn SupportHandler>) -> Self {
        self.handlers.push(handler);
        self
    }

    fn handle(&self, ticket: &mut SupportTicket) {
        for handler in &self.handlers {
            if handler.can_handle(ticket) {
                handler.process(ticket);
                return;
            }
        }
        println!("  [Unhandled] Ticket {} reached end of chain", ticket.id);
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let chain = SupportChain::new()
        .add(Box::new(AutoResponder))
        .add(Box::new(Level1Support))
        .add(Box::new(Level2Support))
        .add(Box::new(ManagerSupport));

    let mut tickets = vec![
        SupportTicket { id: "T-001".into(), title: "Password reset".into(), priority: Priority::Low, handled_by: None },
        SupportTicket { id: "T-002".into(), title: "App crashes".into(), priority: Priority::Medium, handled_by: None },
        SupportTicket { id: "T-003".into(), title: "Data corruption".into(), priority: Priority::High, handled_by: None },
        SupportTicket { id: "T-004".into(), title: "Service outage".into(), priority: Priority::Critical, handled_by: None },
    ];

    println!("Processing support tickets through the chain:\n");
    for ticket in &mut tickets {
        chain.handle(ticket);
        println!("    -> Handled by: {}\n", ticket.handled_by.as_deref().unwrap_or("Nobody"));
    }
}
