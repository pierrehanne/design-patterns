// Bridge Pattern
// ==============
// Category: Structural Design Pattern
//
// Intent:
//   Decouple an abstraction from its implementation so both can vary
//   independently. Avoids N × M combinatorial explosion.
//
// When to use:
//   - When you'd need many class combinations without the bridge
//   - When both abstraction and implementation need to be extensible
//   - When you want to swap implementations at runtime
//
// Key Participants:
//   - Abstraction (struct + interface): High-level logic
//   - Implementation (interface): Low-level mechanism
//   - Bridge: The implementation interface field in the abstraction struct

package main

import "fmt"

// ---------------------------------------------------------------------------
// Implementation interface — delivery channels
// ---------------------------------------------------------------------------

type MessageChannel interface {
	Send(title, body, recipient string) string
}

type EmailChannel struct{}

func (e *EmailChannel) Send(title, body, recipient string) string {
	return fmt.Sprintf("[Email → %s] Subject: %s | %s", recipient, title, body)
}

type SMSChannel struct{}

func (s *SMSChannel) Send(title, body, recipient string) string {
	short := body
	if len(body) > 160 {
		short = body[:160]
	}
	return fmt.Sprintf("[SMS → %s] %s", recipient, short)
}

type SlackChannel struct {
	Workspace string
}

func (s *SlackChannel) Send(title, body, recipient string) string {
	return fmt.Sprintf("[Slack#%s → @%s] *%s*\n%s", s.Workspace, recipient, title, body)
}

// ---------------------------------------------------------------------------
// Abstraction interface — notification types
// ---------------------------------------------------------------------------

type Notification interface {
	Notify(recipient, message string) string
}

// RegularNotification — standard priority
type RegularNotification struct {
	Channel MessageChannel // The "bridge" — composition
}

func (n *RegularNotification) Notify(recipient, message string) string {
	return n.Channel.Send("Notification", message, recipient)
}

// UrgentNotification — high priority with urgency markers
type UrgentNotification struct {
	Channel MessageChannel
}

func (n *UrgentNotification) Notify(recipient, message string) string {
	body := fmt.Sprintf("%s — Immediate action required!", message)
	return n.Channel.Send("URGENT", body, recipient)
}

// ScheduledNotification — deferred delivery
type ScheduledNotification struct {
	Channel       MessageChannel
	ScheduledTime string
}

func (n *ScheduledNotification) Notify(recipient, message string) string {
	title := fmt.Sprintf("Scheduled (%s)", n.ScheduledTime)
	body := fmt.Sprintf("%s [Will be delivered at %s]", message, n.ScheduledTime)
	return n.Channel.Send(title, body, recipient)
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	// Without Bridge: 3 types × 3 channels = 9 structs
	// With Bridge:    3 types + 3 channels  = 6 structs

	fmt.Println("=== Regular via Email ===")
	fmt.Println((&RegularNotification{Channel: &EmailChannel{}}).Notify(
		"alice@co.com", "Your report is ready"))

	fmt.Println("\n=== Urgent via SMS ===")
	fmt.Println((&UrgentNotification{Channel: &SMSChannel{}}).Notify(
		"555-1234", "Server CPU at 98%"))

	fmt.Println("\n=== Urgent via Slack ===")
	fmt.Println((&UrgentNotification{Channel: &SlackChannel{Workspace: "ops"}}).Notify(
		"oncall", "Database failover triggered"))

	fmt.Println("\n=== Scheduled via Email ===")
	fmt.Println((&ScheduledNotification{
		Channel:       &EmailChannel{},
		ScheduledTime: "2025-03-15 09:00",
	}).Notify("team@co.com", "Weekly standup reminder"))

	// Swap channel at runtime
	fmt.Println("\n=== Same notification, different channels ===")
	channels := []MessageChannel{
		&EmailChannel{},
		&SMSChannel{},
		&SlackChannel{Workspace: "general"},
	}
	for _, ch := range channels {
		fmt.Println((&UrgentNotification{Channel: ch}).Notify("bob", "Deploy failed"))
	}
}
