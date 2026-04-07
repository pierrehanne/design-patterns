// Adapter Pattern
// ===============
// Category: Structural Design Pattern
//
// Intent:
//   Convert the interface of a type into another interface that clients expect.
//   Acts as a translator between incompatible APIs.
//
// When to use:
//   - Integrating a legacy system or third-party package with a different API
//   - When you can't modify the source of the incompatible type
//
// Key Participants:
//   - Target (interface): What the client expects
//   - Adaptee: The existing type with an incompatible interface
//   - Adapter: Wraps the Adaptee and satisfies the Target interface

package main

import (
	"fmt"
	"strings"
	"time"
)

// ---------------------------------------------------------------------------
// Target — the modern payment interface
// ---------------------------------------------------------------------------

type PaymentResult struct {
	Success       bool
	TransactionID string
	AmountCents   int
	Currency      string
}

type RefundResult struct {
	Success       bool
	TransactionID string
	RefundedCents int
}

type PaymentProcessor interface {
	Charge(amountCents int, currency, cardToken string) PaymentResult
	Refund(transactionID string, amountCents int) RefundResult
}

// ---------------------------------------------------------------------------
// Adaptee — legacy payment gateway with incompatible API
// ---------------------------------------------------------------------------

type LegacyPaymentGateway struct{}

// Uses dollars (not cents), different method name, returns pipe-delimited string.
func (g *LegacyPaymentGateway) MakePayment(dollars float64, cardNumber, curr string) string {
	return fmt.Sprintf("OK|TXN-%d|%.2f|%s", time.Now().UnixNano(), dollars, curr)
}

func (g *LegacyPaymentGateway) ReversePayment(txnRef string) string {
	return fmt.Sprintf("REVERSED|%s", txnRef)
}

// ---------------------------------------------------------------------------
// Adapter — bridges legacy gateway to modern PaymentProcessor interface
// ---------------------------------------------------------------------------

type LegacyPaymentAdapter struct {
	gateway *LegacyPaymentGateway
}

func NewLegacyPaymentAdapter(gw *LegacyPaymentGateway) *LegacyPaymentAdapter {
	return &LegacyPaymentAdapter{gateway: gw}
}

func (a *LegacyPaymentAdapter) Charge(amountCents int, currency, cardToken string) PaymentResult {
	// Translate cents to dollars
	dollars := float64(amountCents) / 100.0

	// Translate token to masked card number
	last4 := cardToken
	if len(cardToken) > 4 {
		last4 = cardToken[len(cardToken)-4:]
	}
	cardNumber := fmt.Sprintf("****-****-****-%s", last4)

	// Call legacy API
	result := a.gateway.MakePayment(dollars, cardNumber, currency)

	// Parse legacy response
	parts := strings.Split(result, "|")
	return PaymentResult{
		Success:       parts[0] == "OK",
		TransactionID: parts[1],
		AmountCents:   amountCents,
		Currency:      currency,
	}
}

func (a *LegacyPaymentAdapter) Refund(transactionID string, amountCents int) RefundResult {
	result := a.gateway.ReversePayment(transactionID)
	parts := strings.Split(result, "|")
	return RefundResult{
		Success:       parts[0] == "REVERSED",
		TransactionID: transactionID,
		RefundedCents: amountCents,
	}
}

// ---------------------------------------------------------------------------
// Modern processor (no adapter needed)
// ---------------------------------------------------------------------------

type StripeProcessor struct{}

func (s *StripeProcessor) Charge(amountCents int, currency, cardToken string) PaymentResult {
	return PaymentResult{
		Success:       true,
		TransactionID: fmt.Sprintf("stripe-%d", time.Now().UnixNano()),
		AmountCents:   amountCents,
		Currency:      currency,
	}
}

func (s *StripeProcessor) Refund(transactionID string, amountCents int) RefundResult {
	return RefundResult{Success: true, TransactionID: transactionID, RefundedCents: amountCents}
}

// ---------------------------------------------------------------------------
// Client Code — works with any PaymentProcessor
// ---------------------------------------------------------------------------

func processCheckout(processor PaymentProcessor, amountCents int) {
	result := processor.Charge(amountCents, "USD", "tok_visa_4242")
	if result.Success {
		fmt.Printf("  Charged %d cents — txn: %s\n", amountCents, result.TransactionID)
	} else {
		fmt.Println("  Payment failed!")
	}
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	fmt.Println("Using modern Stripe processor:")
	processCheckout(&StripeProcessor{}, 2999)

	fmt.Println("\nUsing adapted legacy gateway:")
	adapted := NewLegacyPaymentAdapter(&LegacyPaymentGateway{})
	processCheckout(adapted, 2999)

	fmt.Println("\nRefund through adapted legacy:")
	refund := adapted.Refund("TXN-12345", 2999)
	fmt.Printf("  Refund result: %+v\n", refund)
}
