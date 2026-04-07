// Strategy Pattern
// =================
// Category: Behavioral Design Pattern
//
// Intent:
//
//	Define a family of algorithms, encapsulate each one, and make them
//	interchangeable. Strategy lets the algorithm vary independently from
//	the clients that use it.
//
// When to use:
//   - When you have multiple algorithms for a specific task and want to
//     switch between them at runtime.
//   - When you want to avoid conditional statements for selecting behaviors.
//   - When a class has many related behaviors that differ only in their
//     implementation.
//
// Key Participants:
//   - Strategy (interface): PaymentStrategy -- declares the interface common
//     to all supported algorithms.
//   - ConcreteStrategy: CreditCardPayment, PayPalPayment, CryptoPayment --
//     implements the algorithm using the Strategy interface.
//   - Context: PaymentContext -- maintains a reference to a Strategy object
//     and delegates the work to it.
package main

import "fmt"

// ---------------------------------------------------------------------------
// Strategy interface
// ---------------------------------------------------------------------------

// PaymentStrategy is implemented by every concrete payment algorithm.
type PaymentStrategy interface {
	// Name returns a human-readable name for the payment method.
	Name() string
	// Pay processes a payment and returns a confirmation message.
	Pay(amount float64) string
}

// ---------------------------------------------------------------------------
// Concrete strategies
// ---------------------------------------------------------------------------

// CreditCardPayment processes payments via credit card.
type CreditCardPayment struct {
	CardNumber string
	Cardholder string
}

func (c *CreditCardPayment) Name() string { return "Credit Card" }

func (c *CreditCardPayment) Pay(amount float64) string {
	masked := c.CardNumber[len(c.CardNumber)-4:]
	return fmt.Sprintf(
		"Charged $%.2f to credit card ****-****-****-%s (holder: %s)",
		amount, masked, c.Cardholder,
	)
}

// PayPalPayment processes payments via PayPal.
type PayPalPayment struct {
	Email string
}

func (p *PayPalPayment) Name() string { return "PayPal" }

func (p *PayPalPayment) Pay(amount float64) string {
	return fmt.Sprintf("Sent $%.2f via PayPal to %s", amount, p.Email)
}

// CryptoPayment processes payments via cryptocurrency.
type CryptoPayment struct {
	WalletAddress string
	Currency      string
}

func (c *CryptoPayment) Name() string {
	return fmt.Sprintf("Crypto (%s)", c.Currency)
}

func (c *CryptoPayment) Pay(amount float64) string {
	addr := c.WalletAddress
	short := addr[:6] + "..." + addr[len(addr)-4:]
	return fmt.Sprintf(
		"Transferred $%.2f in %s to wallet %s",
		amount, c.Currency, short,
	)
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

// PaymentContext delegates payment processing to the current strategy.
type PaymentContext struct {
	strategy PaymentStrategy
}

// NewPaymentContext creates a context with an initial strategy.
func NewPaymentContext(strategy PaymentStrategy) *PaymentContext {
	return &PaymentContext{strategy: strategy}
}

// SetStrategy swaps the payment strategy at runtime.
func (pc *PaymentContext) SetStrategy(strategy PaymentStrategy) {
	pc.strategy = strategy
}

// Checkout processes a payment using the current strategy.
func (pc *PaymentContext) Checkout(amount float64) {
	fmt.Printf("Processing $%.2f via %s...\n", amount, pc.strategy.Name())
	result := pc.strategy.Pay(amount)
	fmt.Printf("  -> %s\n\n", result)
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
func main() {
	// Start with credit card
	cc := &CreditCardPayment{CardNumber: "4111111111111234", Cardholder: "Alice"}
	ctx := NewPaymentContext(cc)
	ctx.Checkout(99.99)

	// Swap to PayPal at runtime
	paypal := &PayPalPayment{Email: "alice@example.com"}
	ctx.SetStrategy(paypal)
	ctx.Checkout(49.50)

	// Swap to crypto at runtime
	crypto := &CryptoPayment{
		WalletAddress: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
		Currency:      "ETH",
	}
	ctx.SetStrategy(crypto)
	ctx.Checkout(250.00)

	// Demonstrate batch processing with all strategies
	fmt.Println("--- Batch processing with all strategies ---")
	strategies := []PaymentStrategy{cc, paypal, crypto}
	for _, strat := range strategies {
		ctx.SetStrategy(strat)
		ctx.Checkout(10.00)
	}
}
