/**
 * Facade Pattern
 * ==============
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Provide a unified, simplified interface to a complex subsystem.
 *   The facade hides internal complexity and coordinates multiple services.
 *
 * When to use:
 *   - When a subsystem has many interacting classes
 *   - When clients only need simple operations from a complex system
 *   - When you want to decouple clients from subsystem internals
 *
 * Key Participants:
 *   - Facade: Simple interface delegating to subsystem classes
 *   - Subsystem classes: Do the actual work
 *   - Client: Uses only the facade
 */

// ---------------------------------------------------------------------------
// Subsystem classes
// ---------------------------------------------------------------------------
class InventoryService {
  private stock: Map<string, number> = new Map([
    ["LAPTOP-001", 50],
    ["MOUSE-002", 200],
    ["KEYBOARD-003", 75],
  ]);

  checkAvailability(productId: string, quantity: number): boolean {
    return (this.stock.get(productId) ?? 0) >= quantity;
  }

  reserve(productId: string, quantity: number): boolean {
    if (!this.checkAvailability(productId, quantity)) return false;
    this.stock.set(productId, this.stock.get(productId)! - quantity);
    console.log(`  [Inventory] Reserved ${quantity}x ${productId}`);
    return true;
  }
}

class PaymentService {
  charge(
    customerId: string,
    amount: number
  ): { success: boolean; transactionId: string } {
    console.log(
      `  [Payment] Charged $${amount.toFixed(2)} to customer ${customerId}`
    );
    return { success: true, transactionId: `PAY-${Date.now()}` };
  }
}

class ShippingService {
  calculateCost(weightKg: number, _destination: string): number {
    return 5.99 + weightKg * 1.5;
  }

  createShipment(
    orderId: string,
    destination: string
  ): { trackingNumber: string; destination: string } {
    console.log(
      `  [Shipping] Created shipment for order ${orderId} to ${destination}`
    );
    return { trackingNumber: `SHIP-${Date.now()}`, destination };
  }
}

class NotificationService {
  sendEmail(email: string, subject: string, _body: string): void {
    console.log(`  [Notification] Email to ${email}: ${subject}`);
  }
}

// ---------------------------------------------------------------------------
// Facade — one simple interface for the entire order workflow
// ---------------------------------------------------------------------------
interface OrderResult {
  success: boolean;
  orderId?: string;
  total?: number;
  tracking?: string;
  error?: string;
}

class OrderFacade {
  private inventory = new InventoryService();
  private payment = new PaymentService();
  private shipping = new ShippingService();
  private notification = new NotificationService();

  /**
   * One call replaces 5+ subsystem calls.
   * The facade orchestrates inventory, payment, shipping, and notification.
   */
  placeOrder(
    customerId: string,
    email: string,
    productId: string,
    quantity: number,
    unitPrice: number,
    destination: string
  ): OrderResult {
    console.log(`Processing order for ${customerId}...`);

    // Step 1: Reserve inventory
    if (!this.inventory.reserve(productId, quantity)) {
      return { success: false, error: "Product out of stock" };
    }

    // Step 2: Calculate total
    const shippingCost = this.shipping.calculateCost(quantity * 0.5, destination);
    const total = unitPrice * quantity + shippingCost;

    // Step 3: Process payment
    const payment = this.payment.charge(customerId, total);
    if (!payment.success) {
      return { success: false, error: "Payment failed" };
    }

    // Step 4: Create shipment
    const orderId = `ORD-${Date.now()}`;
    const shipment = this.shipping.createShipment(orderId, destination);

    // Step 5: Notify customer
    this.notification.sendEmail(
      email,
      "Order Confirmed!",
      `Order ${orderId} — tracking: ${shipment.trackingNumber}`
    );

    return { success: true, orderId, total, tracking: shipment.trackingNumber };
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const facade = new OrderFacade();

const result = facade.placeOrder(
  "CUST-42",
  "alice@example.com",
  "LAPTOP-001",
  2,
  999.99,
  "New York, NY"
);
console.log("\nOrder result:", result);

console.log("\n--- Out of stock scenario ---");
const result2 = facade.placeOrder(
  "CUST-99",
  "bob@example.com",
  "NONEXISTENT",
  1,
  49.99,
  "LA, CA"
);
console.log("Order result:", result2);
