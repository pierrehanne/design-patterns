//! Adapter Pattern
//! ===============
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Convert the interface of a type into another interface that clients expect.
//!   Acts as a translator between incompatible APIs.
//!
//! When to use:
//!   - Integrating a legacy system or third-party crate with a different API
//!   - When you can't modify the source of the incompatible type
//!
//! Key Participants:
//!   - Target (trait): What the client expects
//!   - Adaptee: The existing type with an incompatible interface
//!   - Adapter: Wraps the Adaptee and implements the Target trait

use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Target — the modern payment trait our system uses
// ---------------------------------------------------------------------------
#[derive(Debug)]
struct PaymentResult {
    success: bool,
    transaction_id: String,
    amount_cents: u64,
    currency: String,
}

#[derive(Debug)]
struct RefundResult {
    success: bool,
    transaction_id: String,
    refunded_cents: u64,
}

trait PaymentProcessor {
    fn charge(&self, amount_cents: u64, currency: &str, card_token: &str) -> PaymentResult;
    fn refund(&self, transaction_id: &str, amount_cents: u64) -> RefundResult;
}

// ---------------------------------------------------------------------------
// Adaptee — legacy payment gateway with incompatible API
// ---------------------------------------------------------------------------
struct LegacyPaymentGateway;

impl LegacyPaymentGateway {
    /// Uses dollars (not cents), different method name, returns pipe-delimited string.
    fn make_payment(&self, dollars: f64, card_number: &str, curr: &str) -> String {
        format!("OK|TXN-{:x}|{}|{}", rand_id(), dollars, curr)
    }

    fn reverse_payment(&self, txn_ref: &str) -> String {
        format!("REVERSED|{}", txn_ref)
    }
}

fn rand_id() -> u64 {
    // Simple pseudo-random for demo purposes
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos() as u64
}

// ---------------------------------------------------------------------------
// Adapter — bridges legacy gateway to modern PaymentProcessor trait
// ---------------------------------------------------------------------------
struct LegacyPaymentAdapter {
    gateway: LegacyPaymentGateway,
}

impl LegacyPaymentAdapter {
    fn new(gateway: LegacyPaymentGateway) -> Self {
        Self { gateway }
    }
}

impl PaymentProcessor for LegacyPaymentAdapter {
    fn charge(&self, amount_cents: u64, currency: &str, card_token: &str) -> PaymentResult {
        // Translate cents to dollars
        let dollars = amount_cents as f64 / 100.0;
        // Translate token to masked card number
        let last4 = &card_token[card_token.len().saturating_sub(4)..];
        let card_number = format!("****-****-****-{}", last4);

        // Call legacy API
        let result = self.gateway.make_payment(dollars, &card_number, currency);

        // Parse legacy response into standard format
        let parts: Vec<&str> = result.split('|').collect();
        PaymentResult {
            success: parts[0] == "OK",
            transaction_id: parts[1].to_string(),
            amount_cents,
            currency: currency.to_string(),
        }
    }

    fn refund(&self, transaction_id: &str, amount_cents: u64) -> RefundResult {
        let result = self.gateway.reverse_payment(transaction_id);
        let parts: Vec<&str> = result.split('|').collect();
        RefundResult {
            success: parts[0] == "REVERSED",
            transaction_id: transaction_id.to_string(),
            refunded_cents: amount_cents,
        }
    }
}

// ---------------------------------------------------------------------------
// Modern processor (no adapter needed)
// ---------------------------------------------------------------------------
struct StripeProcessor;

impl PaymentProcessor for StripeProcessor {
    fn charge(&self, amount_cents: u64, currency: &str, card_token: &str) -> PaymentResult {
        PaymentResult {
            success: true,
            transaction_id: format!("stripe-{:x}", rand_id()),
            amount_cents,
            currency: currency.to_string(),
        }
    }

    fn refund(&self, transaction_id: &str, amount_cents: u64) -> RefundResult {
        RefundResult {
            success: true,
            transaction_id: transaction_id.to_string(),
            refunded_cents: amount_cents,
        }
    }
}

// ---------------------------------------------------------------------------
// Client Code — works with any PaymentProcessor
// ---------------------------------------------------------------------------
fn process_checkout(processor: &dyn PaymentProcessor, amount_cents: u64) {
    let result = processor.charge(amount_cents, "USD", "tok_visa_4242");
    if result.success {
        println!(
            "  Charged {} cents — txn: {}",
            amount_cents, result.transaction_id
        );
    } else {
        println!("  Payment failed!");
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    println!("Using modern Stripe processor:");
    process_checkout(&StripeProcessor, 2999);

    println!("\nUsing adapted legacy gateway:");
    let adapted = LegacyPaymentAdapter::new(LegacyPaymentGateway);
    process_checkout(&adapted, 2999);

    println!("\nRefund through adapted legacy:");
    let refund = adapted.refund("TXN-12345", 2999);
    println!("  Refund result: {:?}", refund);
}
