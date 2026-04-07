// Observer Pattern
// =================
// Category: Behavioral Design Pattern
//
// Intent:
//
//	Define a one-to-many dependency between objects so that when one object
//	changes state, all its dependents are notified and updated automatically.
//
// When to use:
//   - When a change to one object requires changing others, and you don't know
//     how many objects need to change.
//   - When an object should notify other objects without making assumptions
//     about who those objects are (loose coupling).
//   - When you need a publish-subscribe mechanism.
//
// Key Participants:
//   - Subject (Publisher): StockExchange -- maintains a list of observers and
//     notifies them of state changes.
//   - Observer (Subscriber): PriceDashboard, MobileAlert, TradeLogger --
//     objects that want to be notified when the subject's state changes.
package main

import "fmt"

// ---------------------------------------------------------------------------
// Observer interface
// ---------------------------------------------------------------------------

// StockObserver is implemented by any type that wants price updates.
type StockObserver interface {
	Update(symbol string, price float64)
}

// ---------------------------------------------------------------------------
// Concrete observers
// ---------------------------------------------------------------------------

// PriceDashboard displays the latest prices on a dashboard.
type PriceDashboard struct {
	Name string
}

func (d *PriceDashboard) Update(symbol string, price float64) {
	fmt.Printf("  [%s] %s is now $%.2f\n", d.Name, symbol, price)
}

// MobileAlert sends push notifications when a price exceeds a threshold.
type MobileAlert struct {
	Threshold float64
}

func (m *MobileAlert) Update(symbol string, price float64) {
	if price >= m.Threshold || m.Threshold == 0 {
		fmt.Printf("  [MobileAlert] PUSH: %s hit $%.2f!\n", symbol, price)
	}
}

// TradeLogger logs every price change to an audit trail.
type TradeLogger struct {
	Log []string
}

func (t *TradeLogger) Update(symbol string, price float64) {
	entry := fmt.Sprintf("%s=%.2f", symbol, price)
	t.Log = append(t.Log, entry)
	fmt.Printf("  [TradeLogger] Logged: %s\n", entry)
}

func (t *TradeLogger) ShowLog() {
	fmt.Printf("  [TradeLogger] Full log: %v\n", t.Log)
}

// ---------------------------------------------------------------------------
// Subject (Publisher)
// ---------------------------------------------------------------------------

// StockExchange holds current stock prices and notifies observers on changes.
type StockExchange struct {
	observers map[string]StockObserver
	prices    map[string]float64
}

func NewStockExchange() *StockExchange {
	return &StockExchange{
		observers: make(map[string]StockObserver),
		prices:    make(map[string]float64),
	}
}

// Subscribe registers an observer with a given ID.
func (se *StockExchange) Subscribe(id string, observer StockObserver) {
	se.observers[id] = observer
}

// Unsubscribe removes an observer by ID.
func (se *StockExchange) Unsubscribe(id string) {
	delete(se.observers, id)
}

// SetPrice updates a stock price and notifies all observers.
func (se *StockExchange) SetPrice(symbol string, price float64) {
	se.prices[symbol] = price
	fmt.Printf("\nStockExchange: %s updated to $%.2f\n", symbol, price)
	se.notify(symbol, price)
}

func (se *StockExchange) notify(symbol string, price float64) {
	for _, observer := range se.observers {
		observer.Update(symbol, price)
	}
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
func main() {
	exchange := NewStockExchange()

	// Create observers
	dashboard := &PriceDashboard{Name: "Trading Floor"}
	mobile := &MobileAlert{Threshold: 150.0}
	logger := &TradeLogger{}

	// Subscribe all three
	exchange.Subscribe("dashboard", dashboard)
	exchange.Subscribe("mobile", mobile)
	exchange.Subscribe("logger", logger)

	// Simulate price changes -- all three observers are notified
	exchange.SetPrice("AAPL", 142.50)
	exchange.SetPrice("GOOG", 175.30)

	// Unsubscribe the dashboard -- only mobile and logger receive updates
	fmt.Println("\n--- Dashboard unsubscribed ---")
	exchange.Unsubscribe("dashboard")

	exchange.SetPrice("AAPL", 155.00) // mobile alert fires (>= 150)

	// Show the full trade log
	fmt.Println()
	logger.ShowLog()
}
