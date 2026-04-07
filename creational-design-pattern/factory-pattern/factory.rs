//! Factory Method Pattern
//! ======================
//! Category: Creational Design Pattern
//!
//! Intent:
//!   Define an interface (trait) for creating objects, but let the factory decide
//!   which concrete type to instantiate. Client code works with the trait object
//!   and never needs to know the concrete type.
//!
//! When to use:
//!   - When a module can't anticipate the type of objects it needs to create
//!   - When you want to centralize object creation behind a single function
//!   - When adding new product types should NOT require changing existing code
//!
//! Key Participants:
//!   - Product (trait): Defines the contract all concrete products implement
//!   - ConcreteProduct: Specific implementations of the trait
//!   - Factory function: Returns a trait object (`Box<dyn Notification>`)

// ---------------------------------------------------------------------------
// Product Trait
// ---------------------------------------------------------------------------
trait Notification {
    fn send(&self, recipient: &str, message: &str) -> String;
}

// ---------------------------------------------------------------------------
// Concrete Products
// ---------------------------------------------------------------------------
struct EmailNotification {
    sender: String,
}

impl EmailNotification {
    fn new(sender: &str) -> Self {
        Self {
            sender: sender.to_string(),
        }
    }
}

impl Notification for EmailNotification {
    fn send(&self, recipient: &str, message: &str) -> String {
        format!("[Email] From {} to {}: {}", self.sender, recipient, message)
    }
}

struct SMSNotification {
    phone_prefix: String,
}

impl SMSNotification {
    fn new(prefix: &str) -> Self {
        Self {
            phone_prefix: prefix.to_string(),
        }
    }
}

impl Notification for SMSNotification {
    fn send(&self, recipient: &str, message: &str) -> String {
        format!(
            "[SMS] To {}{}: {}",
            self.phone_prefix, recipient, message
        )
    }
}

struct PushNotification {
    platform: String,
}

impl PushNotification {
    fn new(platform: &str) -> Self {
        Self {
            platform: platform.to_string(),
        }
    }
}

impl Notification for PushNotification {
    fn send(&self, recipient: &str, message: &str) -> String {
        format!(
            "[Push/{}] To {}: {}",
            self.platform, recipient, message
        )
    }
}

// ---------------------------------------------------------------------------
// Factory Function
// ---------------------------------------------------------------------------
/// Creates the appropriate Notification based on the channel string.
/// Returns a trait object so the caller doesn't know the concrete type.
fn create_notification(channel: &str) -> Result<Box<dyn Notification>, String> {
    match channel {
        "email" => Ok(Box::new(EmailNotification::new("noreply@example.com"))),
        "sms" => Ok(Box::new(SMSNotification::new("+1"))),
        "push" => Ok(Box::new(PushNotification::new("mobile"))),
        other => Err(format!(
            "Unknown channel '{}'. Available: email, sms, push",
            other
        )),
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let channels = ["email", "sms", "push"];

    for channel in &channels {
        match create_notification(channel) {
            Ok(notif) => {
                println!(
                    "{}",
                    notif.send("user@example.com", "Your order has shipped!")
                );
            }
            Err(e) => eprintln!("Error: {}", e),
        }
    }

    // Demonstrate error handling for unknown channel
    if let Err(e) = create_notification("pigeon") {
        println!("Expected error: {}", e);
    }
}
