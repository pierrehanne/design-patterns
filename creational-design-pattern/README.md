# Creational Design Patterns

## What Are Creational Patterns?

Creational patterns deal with **how objects are created**. In simple code, you write `new Thing()` everywhere. But as systems grow, object creation becomes complex:

- What if creating an object requires 10 configuration steps?
- What if you need exactly one instance shared across the app?
- What if the type of object depends on runtime conditions?

Creational patterns solve these problems by **abstracting and controlling the instantiation process**.

### The Core Principle

> **Separate "what gets created" from "how it gets created."**

When client code doesn't care about construction details, you can change how objects are built without touching the code that uses them.

---

## Pattern 1: Singleton

### The Problem

You have a resource that must exist exactly once — a database connection pool, a configuration manager, a logger. If multiple instances exist, they'd conflict with each other or waste memory.

```
BAD: Multiple instances, inconsistent state
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Config A │    │ Config B │    │ Config C │
│ port=3000│    │ port=8080│    │ port=3000│
└──────────┘    └──────────┘    └──────────┘
     ↑               ↑               ↑
  Module 1        Module 2        Module 3
  (reads 3000)    (reads 8080!)   (reads 3000)
```

### The Solution

Ensure only one instance exists. Everyone gets the same object.

```
GOOD: Single instance, consistent state
              ┌──────────┐
              │  Config   │
              │ port=3000 │
              └──────────┘
             ╱      │      ╲
        Module 1  Module 2  Module 3
        (3000)    (3000)    (3000)
```

### How It Works

1. Make the constructor private (or override `__new__` in Python)
2. Provide a static `getInstance()` method
3. First call creates the instance; subsequent calls return the same one
4. For thread safety: use locks, `sync.Once` (Go), or `OnceLock` (Rust)

### When to Use

- Configuration managers
- Connection pools
- Thread pools
- Logger instances
- Hardware interface access (printer spooler)

### When NOT to Use

- When you actually need multiple instances
- When it makes unit testing harder (consider dependency injection instead)
- When you're using it as a fancy global variable (code smell!)

### Implementations
- [`singleton.py`](singleton-pattern/singleton.py) — `__new__` + threading lock
- [`singleton.ts`](singleton-pattern/singleton.ts) — Private constructor + static `getInstance()`
- [`singleton.rs`](singleton-pattern/singleton.rs) — `OnceLock` + `Mutex`
- [`singleton.go`](singleton-pattern/singleton.go) — `sync.Once`

---

## Pattern 2: Factory Method

### The Problem

Your code needs to create objects, but the exact type depends on some condition. If you scatter `if/else` creation logic everywhere, adding a new type means changing every creation site.

```
BAD: Creation logic scattered everywhere
// In checkout.py
if channel == "email":
    notif = EmailNotification(...)
elif channel == "sms":
    notif = SMSNotification(...)
elif channel == "push":                    # Adding "push" means
    notif = PushNotification(...)          # changing EVERY file
                                           # that creates notifications
// In alerts.py (same if/else duplicated!)
// In reminders.py (and again!)
```

### The Solution

Centralize creation in a factory. Client code asks "give me a notification for this channel" and gets the right type back.

```
GOOD: One factory, clients don't know concrete types
                    ┌─────────────────┐
Client code ──────▶ │ NotificationFactory │
  "give me sms"     │  create("sms")      │
                    └────────┬────────┘
                             │ returns
                             ▼
                    ┌─────────────────┐
                    │ SMSNotification  │
                    │ (implements      │
                    │  Notification)   │
                    └─────────────────┘
```

### How It Works

1. Define a **Product interface** (what all created objects share)
2. Create **ConcreteProducts** implementing that interface
3. Write a **Factory** that maps input → concrete class
4. Client code only depends on the interface, never on concrete types

### Adding a New Type

Just create a new class and register it with the factory. **Zero changes to existing code.** This is the Open/Closed Principle in action.

### When to Use

- When the exact type of object isn't known until runtime
- When you want to centralize creation logic
- When you want to make adding new types easy

### Implementations
- [`factory.py`](factory-pattern/factory.py) — Registry-based factory with runtime registration
- [`factory.ts`](factory-pattern/factory.ts) — Map-based factory with constructor types
- [`factory.rs`](factory-pattern/factory.rs) — `match` expression returning trait objects
- [`factory.go`](factory-pattern/factory.go) — `switch` statement returning interfaces

---

## Pattern 3: Abstract Factory

### The Problem

You need to create **families of related objects** that must work together. A dark-themed button should pair with a dark-themed checkbox — mixing a dark button with a light checkbox looks broken.

```
BAD: Risk of mixing families
dark_button + light_checkbox = visual disaster
```

### The Solution

Create a factory for each family. Each factory produces all the components of that family, guaranteeing consistency.

```
GOOD: Each factory produces a consistent family
┌──────────────────┐    ┌──────────────────┐
│ DarkThemeFactory │    │ LightThemeFactory│
├──────────────────┤    ├──────────────────┤
│ createButton()   │──▶ │ createButton()   │──▶ LightButton
│ createCheckbox() │──▶ │ createCheckbox() │──▶ LightCheckbox
│ createTextField()│──▶ │ createTextField()│──▶ LightTextField
└──────────────────┘    └──────────────────┘
All dark components      All light components
guaranteed consistent    guaranteed consistent
```

### Factory Method vs Abstract Factory

| | Factory Method | Abstract Factory |
|---|---|---|
| **Creates** | One product | A family of products |
| **Focus** | "Which type?" | "Which family?" |
| **Example** | Create a notification | Create a themed UI kit |

### When to Use

- UI theming systems (dark/light/high-contrast)
- Cross-platform widgets (Windows/Mac/Linux)
- Database drivers (PostgreSQL/MySQL/SQLite)
- Any time you have N families × M product types

### Implementations
- [`abstract_factory.py`](abstract-pattern/abstract_factory.py)
- [`abstract_factory.ts`](abstract-pattern/abstract_factory.ts)
- [`abstract_factory.rs`](abstract-pattern/abstract_factory.rs)
- [`abstract_factory.go`](abstract-pattern/abstract_factory.go)

---

## Pattern 4: Builder

### The Problem

You have an object with many parameters, some required, some optional. The constructor becomes unwieldy:

```python
# BAD: Telescoping constructor — what does each argument mean?
request = HttpRequest("GET", "https://api.com", {"Auth": "Bearer x"},
                      {"page": "1"}, None, 30, 3, True)
#                     ^^^^  What's None? What's 30? What's True?
```

### The Solution

A step-by-step builder with named methods that reads like English:

```python
# GOOD: Self-documenting, flexible, readable
request = (HttpRequestBuilder()
    .get("https://api.com")
    .header("Auth", "Bearer x")
    .query("page", "1")
    .timeout(30)
    .retries(3)
    .build())
```

### How It Works

```
┌────────┐  .get()   ┌────────┐  .header()  ┌────────┐  .build()  ┌─────────┐
│ Builder │────────▶  │ Builder │──────────▶  │ Builder │────────▶  │ Product │
│ (empty) │          │(+url)  │             │(+header)│           │(immutable)│
└────────┘          └────────┘             └────────┘           └─────────┘
```

1. **Builder** accumulates configuration via chained method calls
2. Each method returns `self`/`this` for chaining
3. `.build()` validates and produces the final immutable object
4. **Director** (optional) provides presets for common configurations

### When to Use

- Objects with 4+ constructor parameters
- Objects with many optional configuration fields
- When you want validation at build-time
- When you want readable, self-documenting construction
- Very common in Rust (no default parameters) and Java

### Implementations
- [`builder.py`](builder-pattern/builder.py) — HTTP request builder with director
- [`builder.ts`](builder-pattern/builder.ts) — Fluent API with TypeScript `this` return type
- [`builder.rs`](builder-pattern/builder.rs) — Ownership-based chaining (move semantics)
- [`builder.go`](builder-pattern/builder.go) — Pointer receiver methods for chaining

---

## Pattern 5: Prototype

### The Problem

Creating objects from scratch is expensive (DB queries, file I/O, complex computation), and you need many similar objects with slight variations.

```
BAD: Build each from scratch (slow)
Template → DB query → parse → validate → configure → Object A
Template → DB query → parse → validate → configure → Object B  (same work!)
Template → DB query → parse → validate → configure → Object C  (again!)
```

### The Solution

Build one object (the **prototype**), then **clone** it and tweak the copies:

```
GOOD: Build once, clone many times (fast)
Template → DB query → parse → validate → configure → Prototype
                                                        │
                                              clone()───┤───clone()
                                                │       │       │
                                                ▼       ▼       ▼
                                            Object A  Object B  Object C
                                           (tweak    (tweak    (tweak
                                            title)    author)   both)
```

### Deep Copy vs Shallow Copy

This is the most important concept in the Prototype pattern:

```
SHALLOW COPY                          DEEP COPY
┌──────────┐   ┌──────────┐         ┌──────────┐   ┌──────────┐
│ Original │   │  Clone   │         │ Original │   │  Clone   │
│ name: "A"│   │ name: "B"│         │ name: "A"│   │ name: "B"│
│ style: ──┼──▶│ style: ──┼──┐      │ style:───┤   │ style:───┤
└──────────┘   └──────────┘  │      └────┬─────┘   └────┬─────┘
                             │           ▼               ▼
                      ┌──────┴──┐   ┌─────────┐   ┌─────────┐
                      │ SHARED! │   │ Copy A  │   │ Copy B  │
                      │ (danger)│   │(independent) │(independent)
                      └─────────┘   └─────────┘   └─────────┘

Changing clone's style      Changing clone's style
ALSO changes original!      does NOT affect original ✓
```

**Rule: Always use deep copy unless you explicitly want shared nested state.**

### When to Use

- When object creation is expensive and you need many similar copies
- Document templates, game character presets, configuration profiles
- When combined with a registry of named prototypes

### Implementations
- [`prototype.py`](prototype-pattern/prototype.py) — `copy.deepcopy()` + registry
- [`prototype.ts`](prototype-pattern/prototype.ts) — `structuredClone()` for deep copy
- [`prototype.rs`](prototype-pattern/prototype.rs) — `#[derive(Clone)]` (deep by default in Rust)
- [`prototype.go`](prototype-pattern/prototype.go) — Manual deep copy of slices and maps

---

## Comparison: When to Use Which?

| I need to... | Use |
|---|---|
| Ensure exactly one instance | **Singleton** |
| Create objects without knowing exact type | **Factory Method** |
| Create consistent families of objects | **Abstract Factory** |
| Build complex objects step by step | **Builder** |
| Copy existing objects cheaply | **Prototype** |

### Decision Flowchart

```
Do you need to create objects?
│
├─ Need exactly ONE instance? ──────────▶ Singleton
│
├─ Need FAMILIES of related objects? ───▶ Abstract Factory
│
├─ Object has MANY parameters? ─────────▶ Builder
│
├─ Creating from scratch is EXPENSIVE? ─▶ Prototype
│
└─ Need to DECOUPLE creation logic? ────▶ Factory Method
```
