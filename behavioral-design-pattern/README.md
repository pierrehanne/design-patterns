# Behavioral Design Patterns

## What Are Behavioral Patterns?

Behavioral patterns deal with **how objects communicate and distribute responsibility**. They help you:

- Define clear communication protocols between objects
- Distribute behavior across objects instead of concentrating it in one place
- Make algorithms and workflows flexible and interchangeable

### The Core Principle

> **Objects should do one thing well and collaborate through well-defined interfaces.**

Behavioral patterns are the largest family (11 patterns) because communication between objects is where most complexity lives.

---

## Pattern 1: Chain of Responsibility

### The Problem

A request needs to be handled, but you don't know in advance which handler should process it. Hard-coding the logic in one place creates a massive if/else chain:

```
BAD: One function with all the logic
def handle_ticket(ticket):
    if ticket.priority == LOW:
        send_auto_response(ticket)
    elif ticket.priority == MEDIUM:
        assign_to_l1(ticket)
    elif ticket.priority == HIGH:       # Adding a new level
        escalate_to_l2(ticket)          # means modifying this
    elif ticket.priority == CRITICAL:   # giant function
        page_manager(ticket)
```

### The Solution

Chain handlers together. Each handler decides: "Can I handle this? If not, pass it along."

```
Ticket ──▶ AutoResponder ──▶ Level1 ──▶ Level2 ──▶ Manager
              │                │           │           │
           LOW? ✓          MEDIUM? ✓    HIGH? ✓    CRITICAL? ✓
           handle it       handle it    handle it   handle it
```

### Real-World Examples

- **HTTP middleware**: Auth → Rate Limit → Logging → Handler
- **DOM event bubbling**: Button → Div → Body → Document
- **Exception handling**: Try blocks from inner to outer

### Implementations
- [`chain_of_responsibility.py`](chain-of-responsibility-pattern/chain_of_responsibility.py)
- [`chain_of_responsibility.ts`](chain-of-responsibility-pattern/chain_of_responsibility.ts)
- [`chain_of_responsibility.rs`](chain-of-responsibility-pattern/chain_of_responsibility.rs)
- [`chain_of_responsibility.go`](chain-of-responsibility-pattern/chain_of_responsibility.go)

---

## Pattern 2: Command

### The Problem

You need to support **undo/redo**, queue operations for later, or log all actions. But if actions are just function calls, they're fire-and-forget — you can't reverse them.

### The Solution

Wrap each action as an object with `execute()` and `undo()` methods:

```
                    ┌──────────────┐
                    │   Command    │
                    │  execute()   │
                    │  undo()      │
                    └──────┬───────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        InsertCommand  DeleteCommand  ReplaceCommand
        execute: insert  execute: delete  execute: delete+insert
        undo: delete     undo: insert     undo: reverse both

History stack: [Insert, Insert, Replace]
                                    ↑ undo() pops and reverses
```

### How Undo/Redo Works

```
Execute "Hello"  → history: [Insert("Hello")]     redo: []
Execute ","      → history: [Insert("Hello"), Insert(",")]  redo: []
Undo             → history: [Insert("Hello")]     redo: [Insert(",")]
Redo             → history: [Insert("Hello"), Insert(",")]  redo: []
```

### When to Use

- Text editors, drawing apps (undo/redo)
- Transaction systems (rollback)
- Macro recording and playback
- Task queues and schedulers

### Implementations
- [`command.py`](command-pattern/command.py) — Text editor with undo/redo
- [`command.ts`](command-pattern/command.ts)
- [`command.rs`](command-pattern/command.rs) — `Rc<RefCell>` for shared document access
- [`command.go`](command-pattern/command.go)

---

## Pattern 3: Observer

### The Problem

Multiple components need to react when something changes, but the thing that changes shouldn't need to know about all its dependents:

```
BAD: StockExchange directly calls every display
class StockExchange:
    def update_price(self, price):
        self.price = price
        self.dashboard.update(price)    # Tightly coupled!
        self.mobile.alert(price)        # What if we add 5 more?
        self.logger.log(price)          # Have to modify THIS class
```

### The Solution

The subject maintains a list of observers and notifies them all automatically:

```
GOOD: Subscribe/notify mechanism
┌──────────────┐    notify()     ┌────────────────┐
│ StockExchange │───────────────▶│ PriceDashboard  │
│               │───────────────▶│ MobileAlert     │
│ subscribers:  │───────────────▶│ TradeLogger     │
│ [dash, mob,   │                │                 │
│  log]         │                │ (each implements│
│               │                │  update() )     │
└──────────────┘                └────────────────┘

exchange.subscribe(new_observer)    ← Add at runtime
exchange.unsubscribe(old_observer)  ← Remove at runtime
```

### Real-World Examples

- **Event listeners** in JavaScript (addEventListener)
- **Reactive frameworks** (React state, Vue reactivity, RxJS)
- **Message brokers** (Kafka topics, Redis pub/sub)
- **MVC architecture** (Model notifies Views)

### Observer vs Mediator

| Observer | Mediator |
|----------|----------|
| One-to-many (one subject, many observers) | Many-to-many (through central hub) |
| Observers don't know about each other | Colleagues don't know about each other |
| Subject broadcasts blindly | Mediator routes intelligently |

### Implementations
- [`observer.py`](observer-pattern/observer.py) — Stock ticker with multiple displays
- [`observer.ts`](observer-pattern/observer.ts)
- [`observer.rs`](observer-pattern/observer.rs)
- [`observer.go`](observer-pattern/observer.go)

---

## Pattern 4: Strategy

### The Problem

You have multiple algorithms for the same task, and the choice depends on runtime conditions. Putting them all in one class with `if/else` is messy and violates Open/Closed Principle.

### The Solution

Extract each algorithm into its own class, all implementing the same interface. The context holds a reference to the current strategy and can swap it at runtime:

```
┌────────────────┐        ┌─────────────────────┐
│ PaymentContext  │───────▶│  PaymentStrategy    │ (interface)
│                 │        │  pay(amount)         │
│ strategy: ──────┤        └──────────┬──────────┘
│                 │           ┌───────┼────────┐
└────────────────┘           ▼       ▼        ▼
                        CreditCard  PayPal   Crypto
                        pay()       pay()    pay()

context.setStrategy(new CryptoPayment())  ← Swap at runtime
context.pay(100)  ← Delegates to current strategy
```

### Strategy vs State

They look identical structurally, but differ in intent:

| Strategy | State |
|----------|-------|
| Client **chooses** which algorithm | Object **transitions** between states |
| Algorithms are independent alternatives | States know about other states |
| "I want to sort by price" | "I'm in Draft, next I go to Review" |

### When to Use

- Multiple ways to do the same thing (sort, compress, encrypt, pay)
- Algorithm choice depends on user input or configuration
- You want to add new algorithms without changing existing code

### Implementations
- [`strategy.py`](strategy-pattern/strategy.py) — Payment processing
- [`strategy.ts`](strategy-pattern/strategy.ts)
- [`strategy.rs`](strategy-pattern/strategy.rs) — Trait objects for runtime dispatch
- [`strategy.go`](strategy-pattern/strategy.go)

---

## Pattern 5: State

### The Problem

An object behaves differently depending on its internal state, leading to complex conditional logic:

```
BAD: Conditionals everywhere
def publish(self):
    if self.state == "draft":
        print("Can't publish a draft! Submit for review first.")
    elif self.state == "review":
        self.state = "published"
        print("Published!")
    elif self.state == "published":
        print("Already published!")
    elif self.state == "archived":
        print("Can't publish archived content!")
```

### The Solution

Each state becomes its own class. The object delegates behavior to its current state object:

```
┌──────────┐   delegates to   ┌──────────────┐
│ Document  │────────────────▶│ Current State │
│           │                  └──────┬───────┘
│ state: ───┤         ┌───────────────┼──────────────┐
│           │         ▼               ▼              ▼
└──────────┘   DraftState      ReviewState     PublishedState
               edit() ✓        edit() ✗        edit() ✗
               submit() → Review  publish() → Published  archive() → Archived
               publish() ✗     archive() ✗     edit() ✗

State transitions happen by replacing the state object:
  document.state = ReviewState()
```

### When to Use

- When an object has 3+ states with different behavior in each
- When you have large switch/if-else blocks on a state variable
- Workflow engines, game character states, UI component states
- Vending machines, TCP connections, document lifecycles

### Implementations
- [`state.py`](state-pattern/state.py) — Document workflow
- [`state.ts`](state-pattern/state.ts)
- [`state.rs`](state-pattern/state.rs) — Enum-based (idiomatic Rust)
- [`state.go`](state-pattern/state.go)

---

## Pattern 6: Mediator

### The Problem

Objects communicate directly with each other, creating a tangled web of dependencies:

```
BAD: Everyone knows about everyone (N×N connections)
    User A ←──→ User B
      ↕    ╲  ╱    ↕
    User C ←──→ User D
```

### The Solution

Route all communication through a central mediator:

```
GOOD: Everyone only knows the mediator (N connections)
    User A ──→ ┌──────────┐ ←── User B
               │ ChatRoom  │
    User C ──→ │ (mediator)│ ←── User D
               └──────────┘
```

### Real-World Examples

- Air traffic control (planes don't talk to each other, they talk to the tower)
- Chat rooms, Slack channels
- UI forms where changing one field affects others

### Implementations
- [`mediator.py`](mediator-pattern/mediator.py) — Chat room
- [`mediator.ts`](mediator-pattern/mediator.ts)
- [`mediator.rs`](mediator-pattern/mediator.rs)
- [`mediator.go`](mediator-pattern/mediator.go)

---

## Pattern 7: Memento

### The Problem

You need to save and restore an object's state (undo, checkpoints, save games) without exposing its internal structure.

### The Solution

Three roles working together:

```
┌───────────┐  creates   ┌─────────┐  stores   ┌───────────┐
│ Originator│───────────▶│ Memento │◀──────────│ Caretaker  │
│ (Game     │            │ (Save   │           │ (Save      │
│  Character)│◀───────────│  File)  │           │  Manager)  │
│           │  restores   │         │           │ [save1,    │
│ health: 100│ from       │ snapshot│           │  save2,    │
│ level: 5  │             │ of state│           │  save3]    │
└───────────┘            └─────────┘           └───────────┘

Key rule: The Caretaker stores mementos but NEVER looks inside them.
Only the Originator can create and read mementos (encapsulation preserved).
```

### When to Use

- Game save/load systems
- Undo functionality (alternative to Command pattern)
- Database transaction rollback
- Configuration snapshots before risky changes

### Memento vs Command for Undo

| Memento | Command |
|---------|---------|
| Saves entire **state snapshot** | Saves the **operation** and its inverse |
| Simple but can use more memory | Memory-efficient but harder to implement |
| Works for any state | Each operation needs explicit undo logic |

### Implementations
- [`memento.py`](memento-pattern/memento.py) — Game save system
- [`memento.ts`](memento-pattern/memento.ts)
- [`memento.rs`](memento-pattern/memento.rs)
- [`memento.go`](memento-pattern/memento.go)

---

## Pattern 8: Template Method

### The Problem

Multiple classes follow the **same algorithm structure** but differ in specific steps:

```
CSV Mining:   read CSV file → parse rows → analyze numbers → generate report
JSON Mining:  read JSON file → parse objects → analyze numbers → generate report
DB Mining:    connect to DB → query rows → analyze numbers → generate report
              ~~~~~~~~~~~~   ~~~~~~~~~~~   ^same steps^     ^same steps^
              different!     different!    (shared)          (shared)
```

### The Solution

Define the algorithm's skeleton in a base class. Subclasses override specific steps:

```
DataMiner (base)
├── mine()  ← TEMPLATE METHOD (calls steps in order, DON'T override)
│   ├── readData()      ← abstract (subclass MUST override)
│   ├── parseData()     ← abstract (subclass MUST override)
│   ├── analyzeData()   ← concrete (shared implementation)
│   └── generateReport()← concrete (shared implementation)
│
├── CSVMiner (override readData + parseData)
├── JSONMiner (override readData + parseData)
└── DatabaseMiner (override readData + parseData)
```

### The Hollywood Principle

> "Don't call us, we'll call you."

The base class controls the flow. Subclasses don't call the base — the base calls subclass methods at the right time.

### When to Use

- When multiple classes share the same algorithm structure
- ETL pipelines, test frameworks, build systems
- When you want to control the overall flow but allow customization of steps

### Implementations
- [`template.py`](template-pattern/template.py) — Data mining pipeline
- [`template.ts`](template-pattern/template.ts)
- [`template.rs`](template-pattern/template.rs) — Trait with default methods
- [`template.go`](template-pattern/template.go) — Interface composition with type assertions for hooks

---

## Pattern 9: Visitor

### The Problem

You have a fixed set of element types (Paragraph, Image, Table) and want to add new operations (export to HTML, Markdown, PDF) without modifying the element classes.

### The Solution

**Double dispatch**: Elements accept a visitor, the visitor has a method for each element type:

```
                    Element                         Visitor
             ┌─────────────────┐            ┌──────────────────┐
             │ accept(visitor)  │            │ visitParagraph() │
             └────────┬────────┘            │ visitImage()     │
          ┌───────────┼───────────┐         │ visitTable()     │
          ▼           ▼           ▼         └────────┬─────────┘
     Paragraph     Image       Table        ┌────────┼─────────┐
     accept(v):    accept(v):  accept(v):   ▼        ▼         ▼
      v.visitP(this) v.visitI(this) v.visitT(this)  HTML   Markdown  PlainText

1st dispatch: element.accept(visitor)  → calls the right accept()
2nd dispatch: visitor.visitX(this)     → calls the right visitX()
```

### Adding New Operations

Just create a new Visitor. **No changes to element classes.** This is the opposite of normal OOP where adding methods is easy but adding types requires changing every class.

### Trade-off

| Easy to add... | Hard to add... |
|----------------|----------------|
| New **operations** (new Visitor) | New **element types** (must update all Visitors) |

### Implementations
- [`visitor.py`](visitor-pattern/visitor.py) — Document export (HTML, Markdown, PlainText)
- [`visitor.ts`](visitor-pattern/visitor.ts)
- [`visitor.rs`](visitor-pattern/visitor.rs)
- [`visitor.go`](visitor-pattern/visitor.go)

---

## Pattern 10: Interpreter

### The Problem

You need to evaluate expressions, queries, or rules defined in a simple language.

### The Solution

Represent the grammar as a tree of expression objects:

```
Expression: (3 + 5) * 2

       MultiplyExpression
        ╱              ╲
  AddExpression    NumberExpression(2)
   ╱         ╲
Number(3)   Number(5)

Evaluate bottom-up:
  Number(3) → 3
  Number(5) → 5
  Add(3,5)  → 8
  Multiply(8,2) → 16
```

### When to Use

- Math expression evaluators
- SQL-like query parsers
- Business rule engines
- Configuration DSLs
- **Note**: For complex grammars, use a proper parser generator instead

### Implementations
- [`interpreter.py`](interpreter-pattern/interpreter.py) — Math expression evaluator
- [`interpreter.ts`](interpreter-pattern/interpreter.ts)
- [`interpreter.rs`](interpreter-pattern/interpreter.rs) — Enum-based expression tree
- [`interpreter.go`](interpreter-pattern/interpreter.go)

---

## Pattern 11: Iterator

### The Problem

A custom collection (graph, tree, matrix) needs to support different traversal strategies without exposing its internal structure.

### The Solution

Extract traversal logic into separate iterator objects:

```
SocialNetwork collection (internal: adjacency map)
     │
     ├── FriendsIterator       → Alice's direct friends
     ├── BFSIterator           → Friends of friends (breadth-first)
     └── MutualFriendsIterator → Friends shared between two users

Client code:
    for user in network.friends_of("Alice"):
        print(user)    # Doesn't know about adjacency maps!
```

### Language-Specific Iteration

Each language has its own iterator protocol:

| Language | Protocol | Your Iterator Must Implement |
|----------|----------|------------------------------|
| Python | `__iter__` / `__next__` | Raise `StopIteration` when done |
| TypeScript | `Symbol.iterator` | Return `{ value, done }` objects |
| Rust | `Iterator` trait | `next() → Option<Item>` |
| Go | Convention | `HasNext() bool` + `Next() T` |

### When to Use

- Custom data structures (graphs, trees, skip lists)
- Multiple traversal strategies for the same collection
- When you want to hide internal representation

### Implementations
- [`iterator.py`](iterator-pattern/iterator.py) — Social network traversal
- [`iterator.ts`](iterator-pattern/iterator.ts)
- [`iterator.rs`](iterator-pattern/iterator.rs) — Implementing `Iterator` trait
- [`iterator.go`](iterator-pattern/iterator.go)

---

## Comparison: When to Use Which?

| I need to... | Use |
|---|---|
| Pass a request until someone handles it | **Chain of Responsibility** |
| Undo/redo operations | **Command** |
| Evaluate expressions or rules | **Interpreter** |
| Traverse a collection in different ways | **Iterator** |
| Reduce direct dependencies between objects | **Mediator** |
| Save and restore object state | **Memento** |
| Notify multiple objects of changes | **Observer** |
| Change behavior based on internal state | **State** |
| Swap algorithms at runtime | **Strategy** |
| Define algorithm skeleton with customizable steps | **Template Method** |
| Add operations to classes without modifying them | **Visitor** |

### Patterns That Solve Similar Problems

```
Undo/Redo:    Command (stores operations) vs Memento (stores snapshots)
Decouple:     Observer (1-to-many) vs Mediator (many-to-many)
Swap behavior: Strategy (client chooses) vs State (object transitions)
Add behavior: Decorator (wrapping) vs Visitor (double dispatch)
```

### Decision Flowchart

```
How do your objects need to communicate?
│
├─ One object changes, many react? ──────▶ Observer
│
├─ Many objects interact chaotically? ───▶ Mediator
│
├─ Request needs to find its handler? ───▶ Chain of Responsibility
│
├─ Need to undo/redo actions? ───────────▶ Command or Memento
│
├─ Object acts differently per state? ───▶ State
│
├─ Need to swap algorithms? ─────────────▶ Strategy
│
├─ Same algorithm, different steps? ─────▶ Template Method
│
├─ Add operations without modifying types?▶ Visitor
│
├─ Evaluate a simple language? ──────────▶ Interpreter
│
└─ Traverse a collection? ──────────────▶ Iterator
```
