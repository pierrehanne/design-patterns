/**
 * Interpreter Pattern
 *
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Define a grammar representation and an interpreter that uses the
 *   representation to interpret sentences in the language.
 *
 * When to use:
 *   - You have a simple domain-specific language (DSL) or expression language
 *   - The grammar is relatively simple and efficiency is not a primary concern
 *   - You need to evaluate or transform expressions represented as tree structures
 *
 * Key Participants:
 *   - AbstractExpression: declares an interpret() method common to all nodes
 *   - TerminalExpression: implements interpret() for terminal symbols in the grammar
 *     (e.g., number literals)
 *   - NonterminalExpression: implements interpret() for grammar rules that combine
 *     other expressions (e.g., addition, subtraction, multiplication)
 *   - Context: contains global information the interpreter may need (optional)
 */

// ---------------------------------------------------------------------------
// Abstract expression
// ---------------------------------------------------------------------------

interface Expression {
  interpret(): number;
  toString(): string;
}

// ---------------------------------------------------------------------------
// Terminal expression
// ---------------------------------------------------------------------------

/** A leaf node representing a numeric literal. */
class NumberExpression implements Expression {
  constructor(private readonly value: number) {}

  interpret(): number {
    return this.value;
  }

  toString(): string {
    return Number.isInteger(this.value)
      ? this.value.toString()
      : this.value.toString();
  }
}

// ---------------------------------------------------------------------------
// Non-terminal expressions
// ---------------------------------------------------------------------------

/** Represents the addition of two sub-expressions. */
class AddExpression implements Expression {
  constructor(
    private readonly left: Expression,
    private readonly right: Expression,
  ) {}

  interpret(): number {
    return this.left.interpret() + this.right.interpret();
  }

  toString(): string {
    return `(${this.left} + ${this.right})`;
  }
}

/** Represents the subtraction of two sub-expressions. */
class SubtractExpression implements Expression {
  constructor(
    private readonly left: Expression,
    private readonly right: Expression,
  ) {}

  interpret(): number {
    return this.left.interpret() - this.right.interpret();
  }

  toString(): string {
    return `(${this.left} - ${this.right})`;
  }
}

/** Represents the multiplication of two sub-expressions. */
class MultiplyExpression implements Expression {
  constructor(
    private readonly left: Expression,
    private readonly right: Expression,
  ) {}

  interpret(): number {
    return this.left.interpret() * this.right.interpret();
  }

  toString(): string {
    return `(${this.left} * ${this.right})`;
  }
}

// ---------------------------------------------------------------------------
// Main -- build and evaluate expression trees
// ---------------------------------------------------------------------------

function main(): void {
  // Expression: (3 + 5) * 2 = 16
  const expr1 = new MultiplyExpression(
    new AddExpression(new NumberExpression(3), new NumberExpression(5)),
    new NumberExpression(2),
  );
  console.log(`${expr1} = ${expr1.interpret()}`);

  // Expression: 10 - (2 * 3) = 4
  const expr2 = new SubtractExpression(
    new NumberExpression(10),
    new MultiplyExpression(new NumberExpression(2), new NumberExpression(3)),
  );
  console.log(`${expr2} = ${expr2.interpret()}`);

  // Expression: (7 + 3) * (10 - 5) = 50
  const expr3 = new MultiplyExpression(
    new AddExpression(new NumberExpression(7), new NumberExpression(3)),
    new SubtractExpression(new NumberExpression(10), new NumberExpression(5)),
  );
  console.log(`${expr3} = ${expr3.interpret()}`);

  // Expression: ((2 + 3) * 4) - 6 = 14
  const expr4 = new SubtractExpression(
    new MultiplyExpression(
      new AddExpression(new NumberExpression(2), new NumberExpression(3)),
      new NumberExpression(4),
    ),
    new NumberExpression(6),
  );
  console.log(`${expr4} = ${expr4.interpret()}`);
}

main();
