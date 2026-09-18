# Contributing

Keep examples runnable as independent files, and explain the design decision before adding abstraction. The goal is a clear teaching repository with honest limitations.

## Changing an example

1. State the observable behavior being added or repaired.
2. Preserve a small executable demo and standard-library-only runtime dependencies.
3. Consider whether the same correction applies to the other three languages.
4. Add a regression check for a meaningful failure or invariant, rather than asserting the shape of the implementation.
5. Run `python3 scripts/check_examples.py --language <python|typescript|rust|go>` for the affected languages.
6. Update the matching chapter in `docs/book.json`, rebuild the book, and run `python3 scripts/check_site.py`.

Use language idioms where they express the same intent more clearly. Identical class hierarchies and output are not required. Document differences in ownership, errors, iteration, mutability, or text indexing when they affect behavior.

## Changing the book

Every chapter should explain the actual implementation, a simpler alternative, its tradeoffs, useful tests, and a practice exercise. Distinguish local demonstration behavior from production guarantees. Avoid claims that a pattern automatically supplies thread safety, atomicity, secure encryption, durable delivery, or deep immutability.

See [the book maintenance guide](docs/README.md) for content structure, browser checks, and publishing. Keep links relative, source listings generated, and reading accessible without JavaScript.

## Pull requests

Describe the concrete problem and resulting behavior. Include the checks you ran and any relevant limitations. Keep changes focused enough that a reviewer can trace the design decision into the example and its chapter.
