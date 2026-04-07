//! Strategy Pattern
//! =================
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!     Define a family of algorithms, encapsulate each one, and make them
//!     interchangeable. Strategy lets the algorithm vary independently from
//!     the clients that use it.
//!
//! When to use:
//!     - When you have multiple algorithms for a specific task and want to
//!       switch between them at runtime.
//!     - When you want to avoid conditional statements for selecting behaviors.
//!     - When a class has many related behaviors that differ only in their
//!       implementation.
//!
//! Key Participants:
//!     - Strategy (interface): PaymentStrategy -- declares the interface common
//!       to all supported algorithms.
//!     - ConcreteStrategy: CreditCardPayment, PayPalPayment, CryptoPayment --
//!       implements the algorithm using the Strategy interface.
//!     - Context: PaymentContext -- maintains a reference to a Strategy object
//!       and delegates the work to it.

// ---------------------------------------------------------------------------
// Strategy trait
// ---------------------------------------------------------------------------
trait PaymentStrategy {
    /// Human-readable name of the payment method.
    fn name(&self) -> &str;
    /// Process a payment and return a confirmation message.
    fn pay(&self, amount: f64) -> String;
}

// ---------------------------------------------------------------------------
// Concrete strategies
// ---------------------------------------------------------------------------

/// Processes payments via credit card.
struct CreditCardPayment {
    card_number: String,
    cardholder: String,
}

impl CreditCardPayment {
    fn new(card_number: &str, cardholder: &str) -> Self {
        Self {
            card_number: card_number.to_string(),
            cardholder: cardholder.to_string(),
        }
    }
}

impl PaymentStrategy for CreditCardPayment {
    fn name(&self) -> &str {
        "Credit Card"
    }

    fn pay(&self, amount: f64) -> String {
        let len = self.card_number.len();
        let masked = &self.card_number[len.saturating_sub(4)..];
        format!(
            "Charged ${:.2} to credit card ****-****-****-{} (holder: {})",
            amount, masked, self.cardholder
        )
    }
}

/// Processes payments via PayPal.
struct PayPalPayment {
    email: String,
}

impl PayPalPayment {
    fn new(email: &str) -> Self {
        Self {
            email: email.to_string(),
        }
    }
}

impl PaymentStrategy for PayPalPayment {
    fn name(&self) -> &str {
        "PayPal"
    }

    fn pay(&self, amount: f64) -> String {
        format!("Sent ${:.2} via PayPal to {}", amount, self.email)
    }
}

/// Processes payments via cryptocurrency.
struct CryptoPayment {
    wallet_address: String,
    currency: String,
}

impl CryptoPayment {
    fn new(wallet_address: &str, currency: &str) -> Self {
        Self {
            wallet_address: wallet_address.to_string(),
            currency: currency.to_string(),
        }
    }
}

impl PaymentStrategy for CryptoPayment {
    fn name(&self) -> &str {
        // We return a static string for the trait; the currency is shown in pay().
        "Crypto"
    }

    fn pay(&self, amount: f64) -> String {
        let addr = &self.wallet_address;
        let short = format!(
            "{}...{}",
            &addr[..6.min(addr.len())],
            &addr[addr.len().saturating_sub(4)..]
        );
        format!(
            "Transferred ${:.2} in {} to wallet {}",
            amount, self.currency, short
        )
    }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

/// The context that clients interact with. It delegates the actual payment
/// processing to whatever strategy is currently set.
struct PaymentContext {
    strategy: Box<dyn PaymentStrategy>,
}

impl PaymentContext {
    fn new(strategy: Box<dyn PaymentStrategy>) -> Self {
        Self { strategy }
    }

    /// Swap the payment strategy at runtime.
    fn set_strategy(&mut self, strategy: Box<dyn PaymentStrategy>) {
        self.strategy = strategy;
    }

    /// Process a payment using the current strategy.
    fn checkout(&self, amount: f64) {
        println!(
            "Processing ${:.2} via {}...",
            amount,
            self.strategy.name()
        );
        let result = self.strategy.pay(amount);
        println!("  -> {}\n", result);
    }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
fn main() {
    // Start with credit card
    let cc = CreditCardPayment::new("4111111111111234", "Alice");
    let mut ctx = PaymentContext::new(Box::new(cc));
    ctx.checkout(99.99);

    // Swap to PayPal at runtime
    let paypal = PayPalPayment::new("alice@example.com");
    ctx.set_strategy(Box::new(paypal));
    ctx.checkout(49.50);

    // Swap to crypto at runtime
    let crypto = CryptoPayment::new("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "ETH");
    ctx.set_strategy(Box::new(crypto));
    ctx.checkout(250.00);

    // Demonstrate batch processing with fresh strategy instances
    println!("--- Batch processing with all strategies ---");
    let strategies: Vec<Box<dyn PaymentStrategy>> = vec![
        Box::new(CreditCardPayment::new("4111111111111234", "Alice")),
        Box::new(PayPalPayment::new("alice@example.com")),
        Box::new(CryptoPayment::new("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "ETH")),
    ];

    for strat in strategies {
        ctx.set_strategy(strat);
        ctx.checkout(10.00);
    }
}
