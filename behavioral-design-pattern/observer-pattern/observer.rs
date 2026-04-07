//! Observer Pattern
//! =================
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!     Define a one-to-many dependency between objects so that when one object
//!     changes state, all its dependents are notified and updated automatically.
//!
//! When to use:
//!     - When a change to one object requires changing others, and you don't know
//!       how many objects need to change.
//!     - When an object should notify other objects without making assumptions
//!       about who those objects are (loose coupling).
//!     - When you need a publish-subscribe mechanism.
//!
//! Key Participants:
//!     - Subject (Publisher): StockExchange -- maintains a list of observers and
//!       notifies them of state changes.
//!     - Observer (Subscriber): PriceDashboard, MobileAlert, TradeLogger --
//!       objects that want to be notified when the subject's state changes.

use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Observer trait
// ---------------------------------------------------------------------------
trait StockObserver {
    /// Called by the subject whenever a stock price changes.
    fn update(&mut self, symbol: &str, price: f64);
}

// ---------------------------------------------------------------------------
// Concrete observers
// ---------------------------------------------------------------------------

/// Displays the latest prices on a dashboard.
struct PriceDashboard {
    name: String,
}

impl PriceDashboard {
    fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
        }
    }
}

impl StockObserver for PriceDashboard {
    fn update(&mut self, symbol: &str, price: f64) {
        println!("  [{}] {} is now ${:.2}", self.name, symbol, price);
    }
}

/// Sends push notifications when a price exceeds a threshold.
struct MobileAlert {
    threshold: f64,
}

impl MobileAlert {
    fn new(threshold: f64) -> Self {
        Self { threshold }
    }
}

impl StockObserver for MobileAlert {
    fn update(&mut self, symbol: &str, price: f64) {
        if price >= self.threshold || self.threshold == 0.0 {
            println!("  [MobileAlert] PUSH: {} hit ${:.2}!", symbol, price);
        }
    }
}

/// Logs every price change to an audit trail.
struct TradeLogger {
    log: Vec<String>,
}

impl TradeLogger {
    fn new() -> Self {
        Self { log: Vec::new() }
    }

    fn show_log(&self) {
        println!("  [TradeLogger] Full log: {:?}", self.log);
    }
}

impl StockObserver for TradeLogger {
    fn update(&mut self, symbol: &str, price: f64) {
        let entry = format!("{}={:.2}", symbol, price);
        println!("  [TradeLogger] Logged: {}", entry);
        self.log.push(entry);
    }
}

// ---------------------------------------------------------------------------
// Subject (Publisher)
//
// Rust doesn't have inheritance, so we store observers as trait objects behind
// mutable references. For simplicity we use a Vec of boxed trait objects with
// string IDs so we can unsubscribe by name.
// ---------------------------------------------------------------------------
struct StockExchange {
    observers: Vec<(String, Box<dyn StockObserver>)>,
    prices: HashMap<String, f64>,
}

impl StockExchange {
    fn new() -> Self {
        Self {
            observers: Vec::new(),
            prices: HashMap::new(),
        }
    }

    /// Register a named observer to receive price updates.
    fn subscribe(&mut self, id: &str, observer: Box<dyn StockObserver>) {
        self.observers.push((id.to_string(), observer));
    }

    /// Remove an observer by its ID.
    fn unsubscribe(&mut self, id: &str) {
        self.observers.retain(|(name, _)| name != id);
    }

    /// Update a stock price and notify all observers.
    fn set_price(&mut self, symbol: &str, price: f64) {
        self.prices.insert(symbol.to_string(), price);
        println!("\nStockExchange: {} updated to ${:.2}", symbol, price);
        self.notify(symbol, price);
    }

    /// Push the update to every registered observer.
    fn notify(&mut self, symbol: &str, price: f64) {
        for (_, observer) in self.observers.iter_mut() {
            observer.update(symbol, price);
        }
    }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
fn main() {
    let mut exchange = StockExchange::new();

    // Create and subscribe observers
    exchange.subscribe("dashboard", Box::new(PriceDashboard::new("Trading Floor")));
    exchange.subscribe("mobile", Box::new(MobileAlert::new(150.0)));
    exchange.subscribe("logger", Box::new(TradeLogger::new()));

    // Simulate price changes -- all three observers are notified
    exchange.set_price("AAPL", 142.50);
    exchange.set_price("GOOG", 175.30);

    // Unsubscribe the dashboard -- only mobile and logger receive updates
    println!("\n--- Dashboard unsubscribed ---");
    exchange.unsubscribe("dashboard");

    exchange.set_price("AAPL", 155.00); // mobile alert fires (>= 150)

    // Show the trade logger's full log (we need to access it through the observer list)
    for (id, observer) in &exchange.observers {
        if id == "logger" {
            // Downcast to TradeLogger to call show_log
            // In a real app you might use Any or a separate handle.
            println!();
        }
    }
    // Note: Accessing the concrete TradeLogger after boxing requires Any-based
    // downcasting. For this demo, the log entries were already printed above.
    println!("  (TradeLogger entries were printed inline above)");
}
