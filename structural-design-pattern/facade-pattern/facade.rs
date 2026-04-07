//! Facade Pattern
//! ==============
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Provide a unified, simplified interface to a complex subsystem.
//!   The facade hides internal complexity and coordinates multiple services.
//!
//! When to use:
//!   - When a subsystem has many interacting types
//!   - When clients only need simple operations from a complex system
//!
//! Key Participants:
//!   - Facade: Simple API that delegates to subsystem types
//!   - Subsystem types: Do the actual work
//!   - Client: Uses only the facade

use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Subsystem: Inventory
// ---------------------------------------------------------------------------
struct InventoryService {
    stock: HashMap<String, u32>,
}

impl InventoryService {
    fn new() -> Self {
        let mut stock = HashMap::new();
        stock.insert("LAPTOP-001".to_string(), 50);
        stock.insert("MOUSE-002".to_string(), 200);
        stock.insert("KEYBOARD-003".to_string(), 75);
        Self { stock }
    }

    fn reserve(&mut self, product_id: &str, quantity: u32) -> bool {
        let available = self.stock.get(product_id).copied().unwrap_or(0);
        if available >= quantity {
            self.stock.insert(product_id.to_string(), available - quantity);
            println!("  [Inventory] Reserved {}x {}", quantity, product_id);
            true
        } else {
            false
        }
    }
}

// ---------------------------------------------------------------------------
// Subsystem: Payment
// ---------------------------------------------------------------------------
struct PaymentService;

impl PaymentService {
    fn charge(&self, customer_id: &str, amount: f64) -> (bool, String) {
        println!(
            "  [Payment] Charged ${:.2} to customer {}",
            amount, customer_id
        );
        (true, format!("PAY-{}", rand_id()))
    }
}

// ---------------------------------------------------------------------------
// Subsystem: Shipping
// ---------------------------------------------------------------------------
struct ShippingService;

impl ShippingService {
    fn calculate_cost(&self, weight_kg: f64, _destination: &str) -> f64 {
        5.99 + weight_kg * 1.50
    }

    fn create_shipment(&self, order_id: &str, destination: &str) -> String {
        let tracking = format!("SHIP-{}", rand_id());
        println!(
            "  [Shipping] Created shipment for order {} to {}",
            order_id, destination
        );
        tracking
    }
}

// ---------------------------------------------------------------------------
// Subsystem: Notification
// ---------------------------------------------------------------------------
struct NotificationService;

impl NotificationService {
    fn send_email(&self, email: &str, subject: &str, _body: &str) {
        println!("  [Notification] Email to {}: {}", email, subject);
    }
}

fn rand_id() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_nanos() as u64
}

// ---------------------------------------------------------------------------
// Facade
// ---------------------------------------------------------------------------
struct OrderFacade {
    inventory: InventoryService,
    payment: PaymentService,
    shipping: ShippingService,
    notification: NotificationService,
}

#[derive(Debug)]
struct OrderResult {
    success: bool,
    order_id: Option<String>,
    total: Option<f64>,
    tracking: Option<String>,
    error: Option<String>,
}

impl OrderFacade {
    fn new() -> Self {
        Self {
            inventory: InventoryService::new(),
            payment: PaymentService,
            shipping: ShippingService,
            notification: NotificationService,
        }
    }

    fn place_order(
        &mut self,
        customer_id: &str,
        email: &str,
        product_id: &str,
        quantity: u32,
        unit_price: f64,
        destination: &str,
    ) -> OrderResult {
        println!("Processing order for {}...", customer_id);

        if !self.inventory.reserve(product_id, quantity) {
            return OrderResult {
                success: false,
                error: Some("Product out of stock".to_string()),
                order_id: None,
                total: None,
                tracking: None,
            };
        }

        let shipping_cost = self
            .shipping
            .calculate_cost(quantity as f64 * 0.5, destination);
        let total = unit_price * quantity as f64 + shipping_cost;

        let (paid, _txn_id) = self.payment.charge(customer_id, total);
        if !paid {
            return OrderResult {
                success: false,
                error: Some("Payment failed".to_string()),
                order_id: None,
                total: None,
                tracking: None,
            };
        }

        let order_id = format!("ORD-{}", rand_id());
        let tracking = self.shipping.create_shipment(&order_id, destination);

        self.notification.send_email(
            email,
            "Order Confirmed!",
            &format!("Order {} — tracking: {}", order_id, tracking),
        );

        OrderResult {
            success: true,
            order_id: Some(order_id),
            total: Some(total),
            tracking: Some(tracking),
            error: None,
        }
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let mut facade = OrderFacade::new();

    let result = facade.place_order(
        "CUST-42",
        "alice@example.com",
        "LAPTOP-001",
        2,
        999.99,
        "New York, NY",
    );
    println!("\nOrder result: {:?}", result);

    println!("\n--- Out of stock scenario ---");
    let result2 = facade.place_order(
        "CUST-99",
        "bob@example.com",
        "NONEXISTENT",
        1,
        49.99,
        "LA, CA",
    );
    println!("Order result: {:?}", result2);
}
