# Design Patterns — A Complete Guide

## What Are Design Patterns?

Design patterns are **proven solutions to recurring problems** in software design. Think of them as blueprints — not finished code, but templates you adapt to your specific situation.

They were popularized by the "Gang of Four" (GoF) in their 1994 book *Design Patterns: Elements of Reusable Object-Oriented Software*. Every senior developer uses them, often without even naming them.

### Why Should You Care?

1. **You don't reinvent the wheel** — These problems have been solved thousands of times
2. **Common vocabulary** — Say "Observer pattern" and every developer knows what you mean
3. **Better architecture** — Patterns guide you toward flexible, maintainable code
4. **Job interviews** — Design patterns are a staple of technical interviews

### How to Read This Repository

Each pattern is implemented in **4 languages**: Python, TypeScript, Rust, and Go. Every file contains:
- A header explaining the pattern's intent and when to use it
- A realistic, practical example (not abstract `Shape`/`Animal` toy code)
- Inline comments explaining the non-obvious parts
- A runnable `main` section you can execute to see it in action

---

## The Three Categories

Design patterns are divided into three families based on what kind of problem they solve:

| Category | Question It Answers | Example Problem |
|----------|-------------------|-----------------|
| **[Creational](creational-design-pattern/README.md)** | *How do I create objects?* | "I need exactly one database connection shared everywhere" |
| **[Structural](structural-design-pattern/README.md)** | *How do I compose objects?* | "I need to make a legacy API work with my new code" |
| **[Behavioral](behavioral-design-pattern/README.md)** | *How do objects communicate?* | "I need to notify 10 components when data changes" |

---

## Quick Reference — All 23 Patterns at a Glance

### Creational Patterns — Object Creation

| Pattern | One-Line Summary | Use When... |
|---------|-----------------|-------------|
| **Singleton** | One instance, global access | You need exactly one shared resource (config, pool, logger) |
| **Factory Method** | Create without specifying exact class | You want to decouple "what" from "how" in object creation |
| **Abstract Factory** | Create families of related objects | You need themed/consistent groups (dark UI, light UI) |
| **Builder** | Step-by-step complex construction | Constructors would have 5+ parameters, some optional |
| **Prototype** | Clone existing objects | Creating from scratch is expensive; copy and tweak instead |

### Structural Patterns — Object Composition

| Pattern | One-Line Summary | Use When... |
|---------|-----------------|-------------|
| **Adapter** | Convert one interface to another | Integrating legacy code or third-party libraries |
| **Bridge** | Separate abstraction from implementation | You'd otherwise need N×M subclasses |
| **Composite** | Tree structures with uniform interface | Files/folders, org charts, UI component trees |
| **Decorator** | Add behavior by wrapping | You need mix-and-match features without subclass explosion |
| **Facade** | Simple interface to complex subsystem | You want one function instead of coordinating 5 services |
| **Flyweight** | Share data to save memory | Thousands of similar objects (particles, characters) |
| **Proxy** | Control access to another object | Caching, access control, lazy loading, logging |

### Behavioral Patterns — Object Communication

| Pattern | One-Line Summary | Use When... |
|---------|-----------------|-------------|
| **Chain of Responsibility** | Pass request along a handler chain | Middleware, escalation, event pipelines |
| **Command** | Encapsulate request as object | Undo/redo, queuing, macro recording |
| **Interpreter** | Evaluate a language/grammar | Expression parsers, query languages, rule engines |
| **Iterator** | Sequential access without exposing internals | Custom collections with multiple traversal strategies |
| **Mediator** | Central hub for object communication | Chat rooms, air traffic control, UI component coordination |
| **Memento** | Capture and restore state | Save/load systems, undo snapshots, checkpoints |
| **Observer** | Notify dependents of state changes | Event systems, pub/sub, reactive UIs |
| **State** | Change behavior when state changes | Workflows, vending machines, replacing complex if/else chains |
| **Strategy** | Swap algorithms at runtime | Payment methods, sorting algorithms, compression options |
| **Template Method** | Define algorithm skeleton, let subclasses fill in steps | ETL pipelines, test frameworks, data processing |
| **Visitor** | Add operations to objects without modifying them | Exporters, analyzers, serializers for a fixed set of types |

---

## How to Run the Examples

### Python
```bash
python creational-design-pattern/singleton-pattern/singleton.py
```

### TypeScript (with ts-node or Deno)
```bash
npx ts-node creational-design-pattern/singleton-pattern/singleton.ts
# or
deno run creational-design-pattern/singleton-pattern/singleton.ts
```

### Rust
```bash
rustc creational-design-pattern/singleton-pattern/singleton.rs -o singleton && ./singleton
```

### Go
```bash
go run creational-design-pattern/singleton-pattern/singleton.go
```

---

## How to Study Design Patterns

1. **Start with the intent** — Read the "When to use" section before the code
2. **Understand the problem first** — What happens WITHOUT the pattern?
3. **Trace the code** — Follow the flow from `main` through each participant
4. **Compare languages** — See how the same concept adapts to different paradigms
5. **Don't memorize** — Understand the principle, not the exact implementation
6. **Build something** — Pick a pattern and use it in a personal project

### Recommended Learning Order

Start with the most common patterns you'll encounter in real codebases:

1. **Strategy** — Simplest behavioral pattern, very common
2. **Observer** — Foundation of event-driven programming
3. **Factory** — Most common creational pattern
4. **Singleton** — Simple but controversial (learn why)
5. **Decorator** — Understand wrapping and composition
6. **Adapter** — You'll use this every time you integrate external code
7. **Builder** — Essential for APIs and configuration
8. **Command** — Foundation of undo/redo
9. **State** — Elegantly replaces complex conditionals
10. Then explore the rest as needed

---

## Project Structure

```
engineering/
├── README.md                          ← You are here
├── creational-design-pattern/
│   ├── README.md                      ← Creational patterns explained
│   ├── singleton-pattern/
│   │   ├── singleton.py
│   │   ├── singleton.ts
│   │   ├── singleton.rs
│   │   └── singleton.go
│   ├── factory-pattern/
│   ├── abstract-pattern/
│   ├── builder-pattern/
│   └── prototype-pattern/
├── structural-design-pattern/
│   ├── README.md                      ← Structural patterns explained
│   ├── adapter-pattern/
│   ├── bridge-pattern/
│   ├── composite-pattern/
│   ├── decorator-pattern/
│   ├── facade-pattern/
│   ├── flyweight-pattern/
│   └── proxy-pattern/
└── behavioral-design-pattern/
    ├── README.md                      ← Behavioral patterns explained
    ├── chain-of-responsibility-pattern/
    ├── command-pattern/
    ├── interpreter-pattern/
    ├── iterator-pattern/
    ├── mediator-pattern/
    ├── memento-pattern/
    ├── observer-pattern/
    ├── state-pattern/
    ├── strategy-pattern/
    ├── template-pattern/
    └── visitor-pattern/
```
