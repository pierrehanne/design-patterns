"""
Interpreter Pattern

Category: Behavioral Design Pattern

Intent:
    Define a grammar representation and an interpreter that uses the
    representation to interpret sentences in the language.

When to use:
    - You have a simple domain-specific language (DSL) or expression language
    - The grammar is relatively simple and efficiency is not a primary concern
    - You need to evaluate or transform expressions represented as tree structures

Key Participants:
    - AbstractExpression: declares an interpret() method common to all nodes
    - TerminalExpression: implements interpret() for terminal symbols in the grammar
      (e.g., number literals)
    - NonterminalExpression: implements interpret() for grammar rules that combine
      other expressions (e.g., addition, subtraction, multiplication)
    - Context: contains global information the interpreter may need (optional)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Abstract expression
# ---------------------------------------------------------------------------

class Expression(ABC):
    """Base interface -- every node in the expression tree can be interpreted."""

    @abstractmethod
    def interpret(self) -> float:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Terminal expression
# ---------------------------------------------------------------------------

class NumberExpression(Expression):
    """A leaf node representing a numeric literal."""

    def __init__(self, value: float) -> None:
        self.value = value

    def interpret(self) -> float:
        return self.value

    def __str__(self) -> str:
        # Display as int when there is no fractional part
        if self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)


# ---------------------------------------------------------------------------
# Non-terminal expressions
# ---------------------------------------------------------------------------

class AddExpression(Expression):
    """Represents the addition of two sub-expressions."""

    def __init__(self, left: Expression, right: Expression) -> None:
        self.left = left
        self.right = right

    def interpret(self) -> float:
        return self.left.interpret() + self.right.interpret()

    def __str__(self) -> str:
        return f"({self.left} + {self.right})"


class SubtractExpression(Expression):
    """Represents the subtraction of two sub-expressions."""

    def __init__(self, left: Expression, right: Expression) -> None:
        self.left = left
        self.right = right

    def interpret(self) -> float:
        return self.left.interpret() - self.right.interpret()

    def __str__(self) -> str:
        return f"({self.left} - {self.right})"


class MultiplyExpression(Expression):
    """Represents the multiplication of two sub-expressions."""

    def __init__(self, left: Expression, right: Expression) -> None:
        self.left = left
        self.right = right

    def interpret(self) -> float:
        return self.left.interpret() * self.right.interpret()

    def __str__(self) -> str:
        return f"({self.left} * {self.right})"


# ---------------------------------------------------------------------------
# Main -- build and evaluate expression trees
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Expression: (3 + 5) * 2 = 16
    expr1 = MultiplyExpression(
        AddExpression(NumberExpression(3), NumberExpression(5)),
        NumberExpression(2),
    )
    print(f"{expr1} = {expr1.interpret()}")

    # Expression: 10 - (2 * 3) = 4
    expr2 = SubtractExpression(
        NumberExpression(10),
        MultiplyExpression(NumberExpression(2), NumberExpression(3)),
    )
    print(f"{expr2} = {expr2.interpret()}")

    # Expression: (7 + 3) * (10 - 5) = 50
    expr3 = MultiplyExpression(
        AddExpression(NumberExpression(7), NumberExpression(3)),
        SubtractExpression(NumberExpression(10), NumberExpression(5)),
    )
    print(f"{expr3} = {expr3.interpret()}")

    # Expression: ((2 + 3) * 4) - 6 = 14
    expr4 = SubtractExpression(
        MultiplyExpression(
            AddExpression(NumberExpression(2), NumberExpression(3)),
            NumberExpression(4),
        ),
        NumberExpression(6),
    )
    print(f"{expr4} = {expr4.interpret()}")
