// Chain of Responsibility Pattern
// ================================
// Category: Behavioral Design Pattern
//
// Intent:
//   Pass a request along a chain of handlers. Each handler either processes
//   the request or forwards it to the next handler.
//
// When to use:
//   - HTTP middleware, event processing, support escalation
//   - When the handler isn't known in advance
//   - When handlers should be configurable dynamically
//
// Key Participants:
//   - Handler (interface): Declares Handle and SetNext
//   - ConcreteHandler: Handles specific requests, forwards the rest
//   - Client: Sends request to the first handler

package main

import "fmt"

// ---------------------------------------------------------------------------
// Request data
// ---------------------------------------------------------------------------

type Priority int

const (
	Low      Priority = 1
	Medium   Priority = 2
	High     Priority = 3
	Critical Priority = 4
)

type SupportTicket struct {
	ID          string
	Title       string
	Priority    Priority
	Description string
	HandledBy   string
}

// ---------------------------------------------------------------------------
// Handler interface
// ---------------------------------------------------------------------------

type SupportHandler interface {
	SetNext(handler SupportHandler) SupportHandler
	Handle(ticket *SupportTicket)
}

// ---------------------------------------------------------------------------
// Base handler with next-chaining logic (embedded by concrete handlers)
// ---------------------------------------------------------------------------

type BaseHandler struct {
	next SupportHandler
}

func (b *BaseHandler) SetNext(handler SupportHandler) SupportHandler {
	b.next = handler
	return handler
}

func (b *BaseHandler) HandleNext(ticket *SupportTicket) {
	if b.next != nil {
		b.next.Handle(ticket)
	} else {
		fmt.Printf("  [Unhandled] Ticket %s reached end of chain\n", ticket.ID)
	}
}

// ---------------------------------------------------------------------------
// Concrete Handlers
// ---------------------------------------------------------------------------

type AutoResponder struct{ BaseHandler }

func (h *AutoResponder) Handle(ticket *SupportTicket) {
	if ticket.Priority == Low {
		ticket.HandledBy = "AutoResponder (Bot)"
		fmt.Printf("  [AutoResponder] Ticket %s: Sent automated FAQ response\n", ticket.ID)
	} else {
		h.HandleNext(ticket)
	}
}

type Level1Support struct{ BaseHandler }

func (h *Level1Support) Handle(ticket *SupportTicket) {
	if ticket.Priority == Medium {
		ticket.HandledBy = "Level 1 Support Agent"
		fmt.Printf("  [Level1] Ticket %s: Assigned to support agent\n", ticket.ID)
	} else {
		h.HandleNext(ticket)
	}
}

type Level2Support struct{ BaseHandler }

func (h *Level2Support) Handle(ticket *SupportTicket) {
	if ticket.Priority == High {
		ticket.HandledBy = "Level 2 Senior Engineer"
		fmt.Printf("  [Level2] Ticket %s: Escalated to senior engineer\n", ticket.ID)
	} else {
		h.HandleNext(ticket)
	}
}

type ManagerSupport struct{ BaseHandler }

func (h *ManagerSupport) Handle(ticket *SupportTicket) {
	if ticket.Priority == Critical {
		ticket.HandledBy = "Support Manager"
		fmt.Printf("  [Manager] Ticket %s: CRITICAL — Manager notified\n", ticket.ID)
	} else {
		h.HandleNext(ticket)
	}
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	auto := &AutoResponder{}
	l1 := &Level1Support{}
	l2 := &Level2Support{}
	mgr := &ManagerSupport{}

	// Build the chain
	auto.SetNext(l1).SetNext(l2).SetNext(mgr)

	tickets := []*SupportTicket{
		{ID: "T-001", Title: "Password reset", Priority: Low},
		{ID: "T-002", Title: "App crashes", Priority: Medium},
		{ID: "T-003", Title: "Data corruption", Priority: High},
		{ID: "T-004", Title: "Service outage", Priority: Critical},
	}

	fmt.Println("Processing support tickets through the chain:\n")
	for _, ticket := range tickets {
		auto.Handle(ticket)
		fmt.Printf("    -> Handled by: %s\n\n", ticket.HandledBy)
	}
}
