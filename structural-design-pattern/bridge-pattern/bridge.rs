//! Bridge Pattern
//! ==============
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Decouple an abstraction from its implementation so both can vary
//!   independently. Avoids combinatorial explosion of types.
//!
//! When to use:
//!   - When you'd need N × M structs without the bridge
//!   - When both abstraction and implementation need to be extensible
//!
//! Key Participants:
//!   - Abstraction (trait): High-level logic (notification urgency)
//!   - Implementation (trait): Low-level mechanism (delivery channel)
//!   - Bridge: The Box<dyn Implementation> held by the abstraction

// ---------------------------------------------------------------------------
// Implementation trait — delivery channels
// ---------------------------------------------------------------------------
trait MessageChannel {
    fn send(&self, title: &str, body: &str, recipient: &str) -> String;
}

struct EmailChannel;
impl MessageChannel for EmailChannel {
    fn send(&self, title: &str, body: &str, recipient: &str) -> String {
        format!("[Email → {}] Subject: {} | {}", recipient, title, body)
    }
}

struct SMSChannel;
impl MessageChannel for SMSChannel {
    fn send(&self, title: &str, body: &str, recipient: &str) -> String {
        let short = if body.len() > 160 { &body[..160] } else { body };
        format!("[SMS → {}] {}", recipient, short)
    }
}

struct SlackChannel {
    workspace: String,
}
impl SlackChannel {
    fn new(workspace: &str) -> Self {
        Self { workspace: workspace.to_string() }
    }
}
impl MessageChannel for SlackChannel {
    fn send(&self, title: &str, body: &str, recipient: &str) -> String {
        format!(
            "[Slack#{} → @{}] *{}*\n{}",
            self.workspace, recipient, title, body
        )
    }
}

// ---------------------------------------------------------------------------
// Abstraction — notification types hold a reference to a channel (the bridge)
// ---------------------------------------------------------------------------
trait Notification {
    fn notify(&self, recipient: &str, message: &str) -> String;
}

/// Regular priority — sends message as-is.
struct RegularNotification {
    channel: Box<dyn MessageChannel>,
}
impl Notification for RegularNotification {
    fn notify(&self, recipient: &str, message: &str) -> String {
        self.channel.send("Notification", message, recipient)
    }
}

/// Urgent — adds urgency markers.
struct UrgentNotification {
    channel: Box<dyn MessageChannel>,
}
impl Notification for UrgentNotification {
    fn notify(&self, recipient: &str, message: &str) -> String {
        let body = format!("{} — Immediate action required!", message);
        self.channel.send("URGENT", &body, recipient)
    }
}

/// Scheduled — includes delivery time.
struct ScheduledNotification {
    channel: Box<dyn MessageChannel>,
    scheduled_time: String,
}
impl Notification for ScheduledNotification {
    fn notify(&self, recipient: &str, message: &str) -> String {
        let title = format!("Scheduled ({})", self.scheduled_time);
        let body = format!(
            "{} [Will be delivered at {}]",
            message, self.scheduled_time
        );
        self.channel.send(&title, &body, recipient)
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    // Without Bridge: 3 types × 3 channels = 9 structs
    // With Bridge:    3 types + 3 channels  = 6 structs

    println!("=== Regular via Email ===");
    let notif = RegularNotification {
        channel: Box::new(EmailChannel),
    };
    println!("{}", notif.notify("alice@co.com", "Your report is ready"));

    println!("\n=== Urgent via SMS ===");
    let notif = UrgentNotification {
        channel: Box::new(SMSChannel),
    };
    println!("{}", notif.notify("555-1234", "Server CPU at 98%"));

    println!("\n=== Urgent via Slack ===");
    let notif = UrgentNotification {
        channel: Box::new(SlackChannel::new("ops")),
    };
    println!("{}", notif.notify("oncall", "Database failover triggered"));

    println!("\n=== Scheduled via Email ===");
    let notif = ScheduledNotification {
        channel: Box::new(EmailChannel),
        scheduled_time: "2025-03-15 09:00".to_string(),
    };
    println!("{}", notif.notify("team@co.com", "Weekly standup reminder"));

    // Swap channel at runtime
    println!("\n=== Same notification type, different channels ===");
    let channels: Vec<Box<dyn MessageChannel>> = vec![
        Box::new(EmailChannel),
        Box::new(SMSChannel),
        Box::new(SlackChannel::new("general")),
    ];
    for ch in channels {
        let notif = UrgentNotification { channel: ch };
        println!("{}", notif.notify("bob", "Deploy failed"));
    }
}
