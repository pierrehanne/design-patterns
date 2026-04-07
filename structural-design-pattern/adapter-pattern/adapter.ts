/**
 * Adapter Pattern
 * ===============
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Convert the interface of a class into another interface that clients expect.
 *   Acts as a translator between incompatible APIs — old/new, third-party/internal.
 *
 * When to use:
 *   - Integrating a legacy system or third-party library with a different API
 *   - Migrating from one API to another without rewriting client code
 *   - When you can't modify the source of the incompatible class
 *
 * Key Participants:
 *   - Target (interface): What the client expects
 *   - Adaptee: The existing class with an incompatible interface
 *   - Adapter: Translates Target calls into Adaptee calls
 */

// ---------------------------------------------------------------------------
// Target — the modern payment interface our system uses
// ---------------------------------------------------------------------------
interface PaymentResult {
  success: boolean;
  transactionId: string;
  amountCents: number;
  currency: string;
}

interface RefundResult {
  success: boolean;
  transactionId: string;
  refundedCents: number;
}

interface PaymentProcessor {
  charge(amountCents: number, currency: string, cardToken: string): PaymentResult;
  refund(transactionId: string, amountCents: number): RefundResult;
}

// ---------------------------------------------------------------------------
// Adaptee — legacy payment gateway with an incompatible API
// ---------------------------------------------------------------------------
class LegacyPaymentGateway {
  /** Uses dollars (not cents), different method name, returns pipe-delimited string. */
  makePayment(dollars: number, cardNumber: string, curr: string): string {
    return `OK|TXN-${Date.now()}|${dollars}|${curr}`;
  }

  reversePayment(txnRef: string): string {
    return `REVERSED|${txnRef}`;
  }
}

// ---------------------------------------------------------------------------
// Adapter — bridges legacy gateway to modern PaymentProcessor interface
// ---------------------------------------------------------------------------
class LegacyPaymentAdapter implements PaymentProcessor {
  constructor(private gateway: LegacyPaymentGateway) {}

  charge(amountCents: number, currency: string, cardToken: string): PaymentResult {
    // Translate cents → dollars
    const dollars = amountCents / 100;
    // Translate token → masked card number
    const cardNumber = `****-****-****-${cardToken.slice(-4)}`;

    // Call the legacy API
    const result = this.gateway.makePayment(dollars, cardNumber, currency);

    // Parse legacy response into our standard format
    const parts = result.split("|");
    return {
      success: parts[0] === "OK",
      transactionId: parts[1],
      amountCents,
      currency,
    };
  }

  refund(transactionId: string, amountCents: number): RefundResult {
    const result = this.gateway.reversePayment(transactionId);
    const parts = result.split("|");
    return {
      success: parts[0] === "REVERSED",
      transactionId,
      refundedCents: amountCents,
    };
  }
}

// ---------------------------------------------------------------------------
// Modern processor (no adapter needed)
// ---------------------------------------------------------------------------
class StripeProcessor implements PaymentProcessor {
  charge(amountCents: number, currency: string, cardToken: string): PaymentResult {
    return {
      success: true,
      transactionId: `stripe-${Date.now()}`,
      amountCents,
      currency,
    };
  }

  refund(transactionId: string, amountCents: number): RefundResult {
    return { success: true, transactionId, refundedCents: amountCents };
  }
}

// ---------------------------------------------------------------------------
// Client Code — works with any PaymentProcessor
// ---------------------------------------------------------------------------
function processCheckout(processor: PaymentProcessor, amountCents: number): void {
  const result = processor.charge(amountCents, "USD", "tok_visa_4242");
  if (result.success) {
    console.log(`  Charged ${amountCents} cents — txn: ${result.transactionId}`);
  } else {
    console.log("  Payment failed!");
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
console.log("Using modern Stripe processor:");
processCheckout(new StripeProcessor(), 2999);

console.log("\nUsing adapted legacy gateway:");
const adapted = new LegacyPaymentAdapter(new LegacyPaymentGateway());
processCheckout(adapted, 2999);

console.log("\nRefund through adapted legacy:");
console.log(adapted.refund("TXN-12345", 2999));
