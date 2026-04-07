// Factory Method Pattern
// ======================
// Category: Creational Design Pattern
//
// Intent:
//   Define an interface for creating objects, but let the factory decide which
//   concrete type to instantiate. Client code works with the interface and
//   never needs to know the concrete type.
//
// When to use:
//   - When a module can't anticipate the type of objects it needs to create
//   - When you want to centralize and encapsulate object creation logic
//   - When adding new product types should NOT require changing existing code
//
// Key Participants:
//   - Product (interface): Defines the contract all concrete products implement
//   - ConcreteProduct: Specific implementations of the interface
//   - Factory function: Returns the interface type

package main

import "fmt"

// ---------------------------------------------------------------------------
// Product Interface
// ---------------------------------------------------------------------------

// Notification is the product interface that all notification types implement.
type Notification interface {
	Send(recipient, message string) string
}

// ---------------------------------------------------------------------------
// Concrete Products
// ---------------------------------------------------------------------------

type EmailNotification struct {
	Sender string
}

func (e *EmailNotification) Send(recipient, message string) string {
	return fmt.Sprintf("[Email] From %s to %s: %s", e.Sender, recipient, message)
}

type SMSNotification struct {
	PhonePrefix string
}

func (s *SMSNotification) Send(recipient, message string) string {
	return fmt.Sprintf("[SMS] To %s%s: %s", s.PhonePrefix, recipient, message)
}

type PushNotification struct {
	Platform string
}

func (p *PushNotification) Send(recipient, message string) string {
	return fmt.Sprintf("[Push/%s] To %s: %s", p.Platform, recipient, message)
}

// ---------------------------------------------------------------------------
// Factory Function
// ---------------------------------------------------------------------------

// CreateNotification builds the appropriate Notification based on the channel string.
// The caller receives the Notification interface — never the concrete struct.
func CreateNotification(channel string) (Notification, error) {
	switch channel {
	case "email":
		return &EmailNotification{Sender: "noreply@example.com"}, nil
	case "sms":
		return &SMSNotification{PhonePrefix: "+1"}, nil
	case "push":
		return &PushNotification{Platform: "mobile"}, nil
	default:
		return nil, fmt.Errorf("unknown channel '%s'. Available: email, sms, push", channel)
	}
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	channels := []string{"email", "sms", "push"}

	for _, ch := range channels {
		notif, err := CreateNotification(ch)
		if err != nil {
			fmt.Println("Error:", err)
			continue
		}
		// Client code only uses the Notification interface
		fmt.Println(notif.Send("user@example.com", "Your order has shipped!"))
	}

	// Demonstrate error handling for unknown channel
	_, err := CreateNotification("pigeon")
	if err != nil {
		fmt.Println("Expected error:", err)
	}
}
