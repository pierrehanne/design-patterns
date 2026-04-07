/**
 * Observer Pattern
 * =================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Define a one-to-many dependency between objects so that when one object
 *   changes state, all its dependents are notified and updated automatically.
 *
 * When to use:
 *   - When a change to one object requires changing others, and you don't know
 *     how many objects need to change.
 *   - When an object should notify other objects without making assumptions
 *     about who those objects are (loose coupling).
 *   - When you need a publish-subscribe mechanism.
 *
 * Key Participants:
 *   - Subject (Publisher): StockExchange -- maintains a list of observers and
 *     notifies them of state changes.
 *   - Observer (Subscriber): PriceDashboard, MobileAlert, TradeLogger --
 *     objects that want to be notified when the subject's state changes.
 */

// ---------------------------------------------------------------------------
// Observer interface
// ---------------------------------------------------------------------------
interface StockObserver {
  update(symbol: string, price: number): void;
}

// ---------------------------------------------------------------------------
// Concrete observers
// ---------------------------------------------------------------------------
class PriceDashboard implements StockObserver {
  constructor(private name: string = "Main Dashboard") {}

  update(symbol: string, price: number): void {
    console.log(`  [${this.name}] ${symbol} is now $${price.toFixed(2)}`);
  }
}

class MobileAlert implements StockObserver {
  constructor(private threshold: number = 0) {}

  update(symbol: string, price: number): void {
    if (price >= this.threshold || this.threshold === 0) {
      console.log(`  [MobileAlert] PUSH: ${symbol} hit $${price.toFixed(2)}!`);
    }
  }
}

class TradeLogger implements StockObserver {
  private log: string[] = [];

  update(symbol: string, price: number): void {
    const entry = `${symbol}=${price.toFixed(2)}`;
    this.log.push(entry);
    console.log(`  [TradeLogger] Logged: ${entry}`);
  }

  showLog(): void {
    console.log(`  [TradeLogger] Full log: [${this.log.join(", ")}]`);
  }
}

// ---------------------------------------------------------------------------
// Subject (Publisher)
// ---------------------------------------------------------------------------
class StockExchange {
  private observers: StockObserver[] = [];
  private prices: Map<string, number> = new Map();

  /** Register an observer to receive price updates. */
  subscribe(observer: StockObserver): void {
    if (!this.observers.includes(observer)) {
      this.observers.push(observer);
    }
  }

  /** Remove an observer so it no longer receives updates. */
  unsubscribe(observer: StockObserver): void {
    this.observers = this.observers.filter((o) => o !== observer);
  }

  /** Update a stock price and notify all observers. */
  setPrice(symbol: string, price: number): void {
    this.prices.set(symbol, price);
    console.log(`\nStockExchange: ${symbol} updated to $${price.toFixed(2)}`);
    this.notify(symbol, price);
  }

  /** Push the update to every registered observer. */
  private notify(symbol: string, price: number): void {
    for (const observer of this.observers) {
      observer.update(symbol, price);
    }
  }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
function main(): void {
  const exchange = new StockExchange();

  // Create observers
  const dashboard = new PriceDashboard("Trading Floor");
  const mobile = new MobileAlert(150.0);
  const logger = new TradeLogger();

  // Subscribe all three
  exchange.subscribe(dashboard);
  exchange.subscribe(mobile);
  exchange.subscribe(logger);

  // Simulate price changes -- all three observers are notified
  exchange.setPrice("AAPL", 142.5);
  exchange.setPrice("GOOG", 175.3);

  // Unsubscribe the dashboard
  console.log("\n--- Dashboard unsubscribed ---");
  exchange.unsubscribe(dashboard);

  exchange.setPrice("AAPL", 155.0); // mobile alert fires (>= 150)

  // Show the full trade log
  console.log();
  logger.showLog();
}

main();
