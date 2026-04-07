/**
 * Strategy Pattern
 * =================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Define a family of algorithms, encapsulate each one, and make them
 *   interchangeable. Strategy lets the algorithm vary independently from
 *   the clients that use it.
 *
 * When to use:
 *   - When you have multiple algorithms for a specific task and want to
 *     switch between them at runtime.
 *   - When you want to avoid conditional statements for selecting behaviors.
 *   - When a class has many related behaviors that differ only in their
 *     implementation.
 *
 * Key Participants:
 *   - Strategy (interface): PaymentStrategy -- declares the interface common
 *     to all supported algorithms.
 *   - ConcreteStrategy: CreditCardPayment, PayPalPayment, CryptoPayment --
 *     implements the algorithm using the Strategy interface.
 *   - Context: PaymentContext -- maintains a reference to a Strategy object
 *     and delegates the work to it.
 */

// ---------------------------------------------------------------------------
// Strategy interface
// ---------------------------------------------------------------------------
interface PaymentStrategy {
  /** Human-readable name of the payment method. */
  readonly name: string;
  /** Process a payment and return a confirmation message. */
  pay(amount: number): string;
}

// ---------------------------------------------------------------------------
// Concrete strategies
// ---------------------------------------------------------------------------

class CreditCardPayment implements PaymentStrategy {
  readonly name = "Credit Card";

  constructor(
    private cardNumber: string,
    private cardholder: string,
  ) {}

  pay(amount: number): string {
    const masked = `****-****-****-${this.cardNumber.slice(-4)}`;
    return `Charged $${amount.toFixed(2)} to credit card ${masked} (holder: ${this.cardholder})`;
  }
}

class PayPalPayment implements PaymentStrategy {
  readonly name = "PayPal";

  constructor(private email: string) {}

  pay(amount: number): string {
    return `Sent $${amount.toFixed(2)} via PayPal to ${this.email}`;
  }
}

class CryptoPayment implements PaymentStrategy {
  readonly name: string;

  constructor(
    private walletAddress: string,
    private currency: string = "BTC",
  ) {
    this.name = `Crypto (${currency})`;
  }

  pay(amount: number): string {
    const shortAddr = `${this.walletAddress.slice(0, 6)}...${this.walletAddress.slice(-4)}`;
    return `Transferred $${amount.toFixed(2)} in ${this.currency} to wallet ${shortAddr}`;
  }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

class PaymentContext {
  constructor(private strategy: PaymentStrategy) {}

  /** Swap the payment strategy at runtime. */
  setStrategy(strategy: PaymentStrategy): void {
    this.strategy = strategy;
  }

  /** Process a payment using the current strategy. */
  checkout(amount: number): void {
    console.log(
      `Processing $${amount.toFixed(2)} via ${this.strategy.name}...`,
    );
    const result = this.strategy.pay(amount);
    console.log(`  -> ${result}\n`);
  }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------

function main(): void {
  // Start with credit card
  const cc = new CreditCardPayment("4111111111111234", "Alice");
  const ctx = new PaymentContext(cc);
  ctx.checkout(99.99);

  // Swap to PayPal at runtime
  const paypal = new PayPalPayment("alice@example.com");
  ctx.setStrategy(paypal);
  ctx.checkout(49.5);

  // Swap to crypto at runtime
  const crypto = new CryptoPayment(
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "ETH",
  );
  ctx.setStrategy(crypto);
  ctx.checkout(250.0);

  // Demonstrate that the context is agnostic to the concrete strategy
  const strategies: PaymentStrategy[] = [cc, paypal, crypto];
  console.log("--- Batch processing with all strategies ---");
  for (const strat of strategies) {
    ctx.setStrategy(strat);
    ctx.checkout(10.0);
  }
}

main();
