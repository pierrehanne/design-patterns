# Design Patterns Field Guide

**23 pattern topics. Four languages. 92 runnable examples.** A practical engineering book about the problems patterns solve, their tradeoffs, and the simpler alternatives worth considering first.

The accompanying GitHub Pages book includes a chapter for every pattern, complete source in Python, TypeScript, Rust, and Go, and five guides on design judgment, pattern selection, production concerns, language differences, and deliberate practice. It supports full-text search, category filtering, source downloads, dark mode, mobile navigation, and printing. Reading does not require JavaScript.

[Read the book](https://pierrehanne.github.io/design-patterns/) · [Build and publish the website](docs/README.md) · [Contribute](CONTRIBUTING.md)

## Explore the examples

| Family | Focus | Topics |
| --- | --- | --- |
| [Creational](creational-design-pattern/README.md) | Creation and ownership | Singleton, Factory, Abstract Factory, Builder, Prototype |
| [Structural](structural-design-pattern/README.md) | Composition and boundaries | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| [Behavioral](behavioral-design-pattern/README.md) | Algorithms and collaboration | Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor |

Each source file contains its own explanation and executable demonstration. These are isolated teaching examples: payment, weather, chat, and database services are simulated. They illustrate design decisions, not complete production integrations. The book identifies limitations and useful next steps for each example.

The factory examples implement **simple factories**. The corresponding chapter distinguishes them from canonical **Factory Method**, where a creator workflow calls an overridable construction method.

## Run an example

Only install the toolchain for the language you want to explore.

| Language | Supported baseline | Dependencies |
| --- | --- | --- |
| Python | 3.11+ | Standard library |
| TypeScript | Node.js 22, TypeScript 5.7.3 | `npm ci` installs the pinned compiler |
| Rust | 1.70+, edition 2021 | Standard library; no Cargo project needed |
| Go | 1.23+ | Standard library; each file is a separate program |

```sh
python3 behavioral-design-pattern/strategy-pattern/strategy.py

go run behavioral-design-pattern/strategy-pattern/strategy.go

rustc --edition=2021 behavioral-design-pattern/strategy-pattern/strategy.rs -o /tmp/strategy
/tmp/strategy

npm ci
npx tsc --project tsconfig.json
node .build/typescript/behavioral-design-pattern/strategy-pattern/strategy.js
```

Compile Go and Rust examples separately: each has its own main function. TypeScript examples are modules so their educational names do not collide with each other or browser globals.

## Check the repository

```sh
# One language, or use --language all with all four toolchains installed
python3 scripts/check_examples.py --language python
python3 scripts/check_examples.py --language typescript
python3 scripts/check_examples.py --language rust
python3 scripts/check_examples.py --language go

# Targeted Python regressions
python3 -m unittest discover -s tests -v

# Generate the book and validate links, anchors, search, and source fidelity
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Checks fail when a required toolchain is missing. Compiled check artifacts live in temporary directories. Regression checks cover concurrent singleton initialization and data round trips through decorators, including digits, delimiters, and Unicode. Go also runs the singleton under the race detector.

## Preview the book

The website build needs only Python 3.11+; it has no generator dependencies.

```sh
python3 scripts/build_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open **http://127.0.0.1:8000**. Chapter code is embedded directly from the source files at build time, with byte-for-byte source downloads. Generated output is ignored by Git.

GitHub Actions checks all four languages and the site before deploying from `main`. Initial setup requires **Settings → Pages → Source → GitHub Actions**. See [publishing instructions](docs/README.md#publish-on-github-pages).

## Study with a purpose

Start with Strategy, Adapter, Factory, Decorator, and Observer. Then explore State, Command, and Memento together, followed by Composite, Iterator, and Visitor. Read the problem, trace a call, challenge an edge case, and compare a second language. Each book chapter includes an exercise and tests worth writing.

Patterns are a vocabulary for decisions. Use them when they clarify a real requirement; a small function or plain value is often the better starting point.

## Repository layout

```text
design-patterns/
├── creational-design-pattern/   # 5 topics × 4 languages
├── structural-design-pattern/   # 7 patterns × 4 languages
├── behavioral-design-pattern/   # 11 patterns × 4 languages
├── docs/
│   ├── book.json                # Curated pattern chapters
│   ├── guides/                  # Five authored engineering essays
│   └── assets/                  # Responsive styles and progressive enhancement
├── scripts/                    # Example checks and static book build/validation
├── tests/                      # Regression contracts and shared fixtures
└── .github/workflows/ci.yml     # Checks and GitHub Pages deployment
```

[MIT license](LICENSE).
