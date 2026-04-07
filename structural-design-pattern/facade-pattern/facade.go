// Facade Pattern
// ==============
// Category: Structural Design Pattern
//
// Intent:
//   Provide a unified, simplified interface to a complex subsystem.
//   The facade hides internal complexity and coordinates multiple services.
//
// When to use:
//   - When a subsystem has many interacting types
//   - When clients only need simple operations from a complex system
//   - When you want to decouple clients from subsystem internals
//
// Key Participants:
//   - Facade: Simple API that delegates to subsystem types
//   - Subsystem types: Do the actual work
//   - Client: Uses only the facade

package main

import (
	"fmt"
	"time"
)

// ---------------------------------------------------------------------------
// Subsystem: Inventory
// ---------------------------------------------------------------------------

type InventoryService struct {
	stock map[string]int
}

func NewInventoryService() *InventoryService {
	return &InventoryService{
		stock: map[string]int{
			"LAPTOP-001":   50,
			"MOUSE-002":    200,
			"KEYBOARD-003": 75,
		},
	}
}

func (s *InventoryService) Reserve(productID string, quantity int) bool {
	available := s.stock[productID]
	if available >= quantity {
		s.stock[productID] -= quantity
		fmt.Printf("  [Inventory] Reserved %dx %s\n", quantity, productID)
		return true
	}
	return false
}

// ---------------------------------------------------------------------------
// Subsystem: Payment
// ---------------------------------------------------------------------------

type PaymentService struct{}

func (p *PaymentService) Charge(customerID string, amount float64) (bool, string) {
	fmt.Printf("  [Payment] Charged $%.2f to customer %s\n", amount, customerID)
	return true, fmt.Sprintf("PAY-%d", time.Now().UnixNano())
}

// ---------------------------------------------------------------------------
// Subsystem: Shipping
// ---------------------------------------------------------------------------

type ShippingService struct{}

func (s *ShippingService) CalculateCost(weightKg float64) float64 {
	return 5.99 + weightKg*1.50
}

func (s *ShippingService) CreateShipment(orderID, destination string) string {
	tracking := fmt.Sprintf("SHIP-%d", time.Now().UnixNano())
	fmt.Printf("  [Shipping] Created shipment for order %s to %s\n", orderID, destination)
	return tracking
}

// ---------------------------------------------------------------------------
// Subsystem: Notification
// ---------------------------------------------------------------------------

type NotificationService struct{}

func (n *NotificationService) SendEmail(email, subject string) {
	fmt.Printf("  [Notification] Email to %s: %s\n", email, subject)
}

// ---------------------------------------------------------------------------
// Facade
// ---------------------------------------------------------------------------

type OrderResult struct {
	Success  bool
	OrderID  string
	Total    float64
	Tracking string
	Error    string
}

type OrderFacade struct {
	inventory    *InventoryService
	payment      *PaymentService
	shipping     *ShippingService
	notification *NotificationService
}

func NewOrderFacade() *OrderFacade {
	return &OrderFacade{
		inventory:    NewInventoryService(),
		payment:      &PaymentService{},
		shipping:     &ShippingService{},
		notification: &NotificationService{},
	}
}

// PlaceOrder — one simple call replaces 5+ subsystem calls.
func (f *OrderFacade) PlaceOrder(customerID, email, productID string, quantity int, unitPrice float64, destination string) OrderResult {
	fmt.Printf("Processing order for %s...\n", customerID)

	if !f.inventory.Reserve(productID, quantity) {
		return OrderResult{Success: false, Error: "Product out of stock"}
	}

	shippingCost := f.shipping.CalculateCost(float64(quantity) * 0.5)
	total := unitPrice*float64(quantity) + shippingCost

	paid, _ := f.payment.Charge(customerID, total)
	if !paid {
		return OrderResult{Success: false, Error: "Payment failed"}
	}

	orderID := fmt.Sprintf("ORD-%d", time.Now().UnixNano())
	tracking := f.shipping.CreateShipment(orderID, destination)

	f.notification.SendEmail(email, "Order Confirmed!")

	return OrderResult{
		Success:  true,
		OrderID:  orderID,
		Total:    total,
		Tracking: tracking,
	}
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	facade := NewOrderFacade()

	result := facade.PlaceOrder("CUST-42", "alice@example.com", "LAPTOP-001", 2, 999.99, "New York, NY")
	fmt.Printf("\nOrder result: %+v\n", result)

	fmt.Println("\n--- Out of stock scenario ---")
	result2 := facade.PlaceOrder("CUST-99", "bob@example.com", "NONEXISTENT", 1, 49.99, "LA, CA")
	fmt.Printf("Order result: %+v\n", result2)
}
