# Structural Design Patterns

## What Are Structural Patterns?

Structural patterns deal with **how objects are composed together** to form larger structures. They help you:

- Make incompatible interfaces work together
- Build flexible tree structures
- Add features to objects without modifying them
- Simplify complex subsystems behind a clean API

### The Core Principle

> **Favor composition over inheritance.**

Instead of creating deep class hierarchies, structural patterns combine simple objects to achieve complex behavior. This makes code more flexible and easier to change.

---

## Pattern 1: Adapter

### The Problem

You have a new system with a clean interface, and an old system (or third-party library) with a completely different interface. You can't change either one.

```
Your code              Legacy system
expects:               provides:
  charge(cents)   ✗     makePayment(dollars)
  refund(id)      ✗     reversePayment(ref)
```

### The Solution

Create a wrapper (adapter) that translates one interface into the other:

```
Your code ────▶ Adapter ────▶ Legacy system
  charge(cents)    │           makePayment(dollars)
                   │ translates:
                   │ cents → dollars
                   │ token → card number
                   │ response → standard format
```

### Real-World Analogy

A power adapter lets a US plug work in a European socket. It doesn't change either the plug or the socket — it just translates between them.

### Adapter vs Bridge

| Adapter | Bridge |
|---------|--------|
| Fixes **existing** incompatibility | Designed **up front** for flexibility |
| Retrofits old code to new interface | Prevents tight coupling from the start |
| "Make these two work together" | "Let these two evolve independently" |

### When to Use

- Integrating third-party libraries with different APIs
- Supporting legacy systems alongside new code
- Making unrelated classes work together

### Implementations
- [`adapter.py`](adapter-pattern/adapter.py) — Legacy payment gateway adapter
- [`adapter.ts`](adapter-pattern/adapter.ts) — Same example, TypeScript style
- [`adapter.rs`](adapter-pattern/adapter.rs) — Trait-based adaptation
- [`adapter.go`](adapter-pattern/adapter.go) — Interface satisfaction through wrapping

---

## Pattern 2: Bridge

### The Problem

You have two dimensions of variation. Without the Bridge pattern, you'd need N x M classes:

```
BAD: 3 notification types × 3 channels = 9 classes!
UrgentEmailNotification     RegularEmailNotification     ScheduledEmailNotification
UrgentSMSNotification       RegularSMSNotification       ScheduledSMSNotification
UrgentSlackNotification     RegularSlackNotification     ScheduledSlackNotification
```

### The Solution

Split into two independent hierarchies connected by composition (the "bridge"):

```
GOOD: 3 types + 3 channels = 6 classes!

Abstraction (WHAT)              Implementation (HOW)
┌────────────────────┐          ┌──────────────────┐
│ RegularNotification│──bridge──│  EmailChannel     │
│ UrgentNotification │──bridge──│  SMSChannel       │
│ ScheduledNotificat.│──bridge──│  SlackChannel     │
└────────────────────┘          └──────────────────┘

Mix and match freely:
  UrgentNotification + SlackChannel ✓
  ScheduledNotification + EmailChannel ✓
  Any combination works!
```

### The Math

Without Bridge: N × M classes (grows multiplicatively)
With Bridge: N + M classes (grows additively)

At 5 × 5, that's 25 classes vs 10. At 10 × 10, it's 100 vs 20.

### When to Use

- When you'd otherwise need a combinatorial explosion of subclasses
- When both the "what" and "how" dimensions need to be extensible
- When you want to swap implementations at runtime

### Implementations
- [`bridge.py`](bridge-pattern/bridge.py) — Notification types × delivery channels
- [`bridge.ts`](bridge-pattern/bridge.ts)
- [`bridge.rs`](bridge-pattern/bridge.rs) — Trait objects as the bridge
- [`bridge.go`](bridge-pattern/bridge.go) — Interface fields as the bridge

---

## Pattern 3: Composite

### The Problem

You have a tree structure (files and folders, organizations, UI components) and you want to treat individual items and groups of items the same way.

```
Without Composite: Different code for files vs directories
if isinstance(entry, File):
    total += entry.size
elif isinstance(entry, Directory):
    for child in entry.children:       # Manual recursion
        if isinstance(child, File):    # everywhere!
            total += child.size
        elif isinstance(child, Directory):
            ...                        # Goes deeper and deeper
```

### The Solution

Give both leaves and branches the **same interface**. Operations propagate recursively through the tree automatically:

```
                    FileSystemEntry (interface)
                    ├── size()
                    ├── display()
                    └── search()
                   ╱                ╲
          File (leaf)          Directory (composite)
          size() → bytes       size() → sum(children.size())
                               display() → self + children.display()

                     project/ (342 bytes)
                    ╱         ╲
              src/ (200)    docs/ (142)
             ╱    ╲            ╲
        main.py  utils.py   README.md
        (128)    (72)        (142)
```

Calling `project.size()` automatically recurses through the entire tree. The client doesn't need to know if it's dealing with a file or a directory.

### When to Use

- File systems, organization hierarchies, UI component trees
- Menu structures (items + submenus)
- Mathematical expression trees
- Anything with a part-whole hierarchy

### Implementations
- [`composite.py`](composite-pattern/composite.py) — File system tree
- [`composite.ts`](composite-pattern/composite.ts)
- [`composite.rs`](composite-pattern/composite.rs) — Enum-based (idiomatic Rust)
- [`composite.go`](composite-pattern/composite.go) — Interface-based

---

## Pattern 4: Decorator

### The Problem

You want to add features to an object, but:
- Subclassing leads to a combinatorial explosion (encryption + compression + logging = 8 combinations)
- You need to add/remove features at runtime
- You want to combine features in any order

### The Solution

Wrap objects in decorator layers, each adding one behavior:

```
                  ┌─────────────────────┐
                  │   LoggingDecorator   │ ← Logs read/write
                  │  ┌─────────────────┐│
                  │  │ EncryptDecorator ││ ← Encrypts data
                  │  │ ┌──────────────┐││
                  │  │ │ CompressDecor.│││ ← Compresses data
                  │  │ │ ┌──────────┐ │││
                  │  │ │ │StringData│ │││ ← Base (plain data)
                  │  │ │ └──────────┘ │││
                  │  │ └──────────────┘││
                  │  └─────────────────┘│
                  └─────────────────────┘

Write flow (outside → in): Log → Encrypt → Compress → Store
Read flow (inside → out):  Retrieve → Decompress → Decrypt → Log
```

### How It Works

1. **Component interface**: All objects (base + decorators) share the same interface
2. **Base component**: The original object without decoration
3. **Decorator**: Wraps a component, adds behavior, delegates to the wrapped object
4. Decorators can be **stacked in any order** and **combined freely**

### Decorator vs Subclassing

| Decorator | Subclassing |
|-----------|-------------|
| Adds behavior at **runtime** | Adds behavior at **compile time** |
| Can combine **any** features freely | Each combination needs its own class |
| Follows Open/Closed Principle | Tight coupling to parent class |

### When to Use

- Adding logging, caching, encryption, compression to streams
- GUI widget decoration (borders, scrollbars, shadows)
- Middleware chains
- Any time you need mix-and-match features

### Implementations
- [`decorator.py`](decorator-pattern/decorator.py) — Data stream with encryption, compression, logging
- [`decorator.ts`](decorator-pattern/decorator.ts)
- [`decorator.rs`](decorator-pattern/decorator.rs) — Trait object wrapping
- [`decorator.go`](decorator-pattern/decorator.go) — Interface wrapping

---

## Pattern 5: Facade

### The Problem

A complex subsystem has many interacting classes. Clients need to understand and coordinate multiple services just to do one simple task:

```
BAD: Client must coordinate 4 services manually
client:
    inventory.check("LAPTOP-001", 2)
    inventory.reserve("LAPTOP-001", 2)
    shipping_cost = shipping.calculate(1.0, "NYC")
    total = 999.99 * 2 + shipping_cost
    payment.charge("CUST-42", total)
    shipping.create_shipment("ORD-1", "NYC")
    notification.send_email("alice@co.com", "Order confirmed!")
```

### The Solution

Provide one simple method that handles the entire workflow:

```
GOOD: One call does everything
client:
    order_facade.place_order(customer, product, quantity, destination)

                    ┌──────────────┐
Client ──────────▶  │   Facade     │
  place_order()     │              │
                    │ 1. inventory │
                    │ 2. payment   │
                    │ 3. shipping  │
                    │ 4. notify    │
                    └──────────────┘
```

### Important Note

The Facade doesn't **prevent** direct access to subsystem classes. Power users can still use them directly. It just provides a **convenient shortcut** for common operations.

### When to Use

- When a subsystem is complex and most clients need simple operations
- When you want to layer your architecture (each layer has a facade)
- API gateways, SDK wrappers, service orchestration

### Implementations
- [`facade.py`](facade-pattern/facade.py) — Order processing facade
- [`facade.ts`](facade-pattern/facade.ts)
- [`facade.rs`](facade-pattern/facade.rs)
- [`facade.go`](facade-pattern/facade.go)

---

## Pattern 6: Flyweight

### The Problem

You have thousands (or millions) of similar objects, and each one stores duplicate data:

```
BAD: 10,000 fire particles, each with its own copy of the sprite texture
Particle 1: { sprite: "fire.png" (2MB), x: 100, y: 200 }
Particle 2: { sprite: "fire.png" (2MB), x: 300, y: 150 }
...
Particle 10000: { sprite: "fire.png" (2MB), x: 50, y: 900 }
Total memory: 10,000 × 2MB = 20GB!
```

### The Solution

Split object data into two categories:
- **Intrinsic state**: Shared data that's the same for all similar objects (sprite, animation)
- **Extrinsic state**: Unique data that varies per instance (position, scale)

Store intrinsic state once and share it:

```
GOOD: 10,000 particles share ONE sprite reference
┌──────────────────┐
│ ParticleType      │  ← ONE instance (intrinsic)
│ sprite: "fire.png"│     shared by all fire particles
│ animation: "burn" │
│ color: "#FF4500"  │
└────────┬─────────┘
         │ (reference)
    ┌────┴────┬────────┬────────┐
    │         │        │        │
Particle 1  Particle 2  ...  Particle 10000   ← extrinsic only
{x:100,y:200} {x:300,y:150}    {x:50,y:900}  (position, scale)

Total memory: 1 × 2MB + 10,000 × 16 bytes ≈ 2MB!
```

### When to Use

- Game particles, tiles, sprites
- Text editor character rendering (font glyphs shared)
- Map markers with shared icons
- Any scenario with thousands of similar objects

### Implementations
- [`flyweight.py`](flyweight-pattern/flyweight.py) — Game particle system
- [`flyweight.ts`](flyweight-pattern/flyweight.ts)
- [`flyweight.rs`](flyweight-pattern/flyweight.rs) — `Rc` (reference counting) for sharing
- [`flyweight.go`](flyweight-pattern/flyweight.go) — Pointer sharing

---

## Pattern 7: Proxy

### The Problem

You need to add a layer of control before accessing an object, without changing the object itself:
- **Caching**: Don't repeat expensive API calls
- **Access control**: Check permissions before allowing access
- **Lazy loading**: Don't create heavy objects until needed
- **Logging**: Monitor how an object is used

### The Solution

A proxy sits between the client and the real object, with the **exact same interface**:

```
Client ────▶ Proxy ────▶ Real Object
              │
              ├── Check cache? Return cached result
              ├── Check permissions? Block if unauthorized
              ├── Log the access? Write to audit log
              └── First access? Create the real object now (lazy)
```

### Types of Proxies

| Type | What It Does | Example |
|------|-------------|---------|
| **Caching Proxy** | Stores results to avoid repeated work | API response cache |
| **Protection Proxy** | Checks credentials before access | API key validation |
| **Virtual Proxy** | Delays creation until first use | Lazy-loaded images |
| **Logging Proxy** | Records all interactions | Request audit log |

### Proxy vs Decorator

They look similar (both wrap an object), but the intent differs:

| Proxy | Decorator |
|-------|-----------|
| **Controls access** to an object | **Adds behavior** to an object |
| Client may not know it's there | Client deliberately stacks decorators |
| Usually one proxy per object | Multiple decorators can be stacked |

### Implementations
- [`proxy.py`](proxy-pattern/proxy.py) — Caching + access control proxy for weather API
- [`proxy.ts`](proxy-pattern/proxy.ts)
- [`proxy.rs`](proxy-pattern/proxy.rs) — `RefCell` for interior mutability in cache
- [`proxy.go`](proxy-pattern/proxy.go)

---

## Comparison: When to Use Which?

| I need to... | Use |
|---|---|
| Make two incompatible APIs work together | **Adapter** |
| Avoid N×M class explosion with 2 dimensions | **Bridge** |
| Treat trees uniformly (parts and wholes) | **Composite** |
| Add features without modifying or subclassing | **Decorator** |
| Simplify a complex subsystem | **Facade** |
| Share data across thousands of similar objects | **Flyweight** |
| Control access to an object | **Proxy** |

### Decision Flowchart

```
Do you need to compose objects?
│
├─ Two things with INCOMPATIBLE interfaces? ─▶ Adapter
│
├─ Two DIMENSIONS that vary independently? ──▶ Bridge
│
├─ TREE structure with parts and wholes? ────▶ Composite
│
├─ ADD FEATURES dynamically? ────────────────▶ Decorator
│
├─ SIMPLIFY a complex subsystem? ────────────▶ Facade
│
├─ MANY similar objects using too much RAM? ─▶ Flyweight
│
└─ CONTROL ACCESS (cache/auth/lazy/log)? ────▶ Proxy
```

### Patterns That Look Similar

```
Adapter   ≠ Bridge    (retrofit vs upfront design)
Decorator ≠ Proxy     (add behavior vs control access)
Facade    ≠ Adapter   (simplify vs translate)
Composite ≠ Decorator (tree structure vs wrapping)
```
