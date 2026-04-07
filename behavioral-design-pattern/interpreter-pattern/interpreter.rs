//! Interpreter Pattern
//!
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!   Define a grammar representation and an interpreter that uses the
//!   representation to interpret sentences in the language.
//!
//! When to use:
//!   - You have a simple domain-specific language (DSL) or expression language
//!   - The grammar is relatively simple and efficiency is not a primary concern
//!   - You need to evaluate or transform expressions represented as tree structures
//!
//! Key Participants:
//!   - AbstractExpression: declares an interpret() method common to all nodes
//!   - TerminalExpression: implements interpret() for terminal symbols in the grammar
//!     (e.g., number literals)
//!   - NonterminalExpression: implements interpret() for grammar rules that combine
//!     other expressions (e.g., addition, subtraction, multiplication)
//!   - Context: contains global information the interpreter may need (optional)

use std::fmt;

// ---------------------------------------------------------------------------
// Expression trait (abstract expression)
// ---------------------------------------------------------------------------

/// Every node in the expression tree can be interpreted and displayed.
trait Expression: fmt::Display {
    fn interpret(&self) -> f64;
}

// ---------------------------------------------------------------------------
// Terminal expression
// ---------------------------------------------------------------------------

/// A leaf node representing a numeric literal.
struct NumberExpression {
    value: f64,
}

impl Expression for NumberExpression {
    fn interpret(&self) -> f64 {
        self.value
    }
}

impl fmt::Display for NumberExpression {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Display as integer when there is no fractional part
        if self.value == (self.value as i64) as f64 {
            write!(f, "{}", self.value as i64)
        } else {
            write!(f, "{}", self.value)
        }
    }
}

// ---------------------------------------------------------------------------
// Non-terminal expressions
// ---------------------------------------------------------------------------

/// Represents the addition of two sub-expressions.
struct AddExpression {
    left: Box<dyn Expression>,
    right: Box<dyn Expression>,
}

impl Expression for AddExpression {
    fn interpret(&self) -> f64 {
        self.left.interpret() + self.right.interpret()
    }
}

impl fmt::Display for AddExpression {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({} + {})", self.left, self.right)
    }
}

/// Represents the subtraction of two sub-expressions.
struct SubtractExpression {
    left: Box<dyn Expression>,
    right: Box<dyn Expression>,
}

impl Expression for SubtractExpression {
    fn interpret(&self) -> f64 {
        self.left.interpret() - self.right.interpret()
    }
}

impl fmt::Display for SubtractExpression {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({} - {})", self.left, self.right)
    }
}

/// Represents the multiplication of two sub-expressions.
struct MultiplyExpression {
    left: Box<dyn Expression>,
    right: Box<dyn Expression>,
}

impl Expression for MultiplyExpression {
    fn interpret(&self) -> f64 {
        self.left.interpret() * self.right.interpret()
    }
}

impl fmt::Display for MultiplyExpression {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({} * {})", self.left, self.right)
    }
}

// ---------------------------------------------------------------------------
// Convenience constructors
// ---------------------------------------------------------------------------

fn num(v: f64) -> Box<dyn Expression> {
    Box::new(NumberExpression { value: v })
}

fn add(left: Box<dyn Expression>, right: Box<dyn Expression>) -> Box<dyn Expression> {
    Box::new(AddExpression { left, right })
}

fn sub(left: Box<dyn Expression>, right: Box<dyn Expression>) -> Box<dyn Expression> {
    Box::new(SubtractExpression { left, right })
}

fn mul(left: Box<dyn Expression>, right: Box<dyn Expression>) -> Box<dyn Expression> {
    Box::new(MultiplyExpression { left, right })
}

// ---------------------------------------------------------------------------
// Main -- build and evaluate expression trees
// ---------------------------------------------------------------------------

fn main() {
    // Expression: (3 + 5) * 2 = 16
    let expr1 = mul(add(num(3.0), num(5.0)), num(2.0));
    println!("{} = {}", expr1, expr1.interpret());

    // Expression: 10 - (2 * 3) = 4
    let expr2 = sub(num(10.0), mul(num(2.0), num(3.0)));
    println!("{} = {}", expr2, expr2.interpret());

    // Expression: (7 + 3) * (10 - 5) = 50
    let expr3 = mul(add(num(7.0), num(3.0)), sub(num(10.0), num(5.0)));
    println!("{} = {}", expr3, expr3.interpret());

    // Expression: ((2 + 3) * 4) - 6 = 14
    let expr4 = sub(mul(add(num(2.0), num(3.0)), num(4.0)), num(6.0));
    println!("{} = {}", expr4, expr4.interpret());
}
