// Interpreter Pattern
//
// Category: Behavioral Design Pattern
//
// Intent:
//   Define a grammar representation and an interpreter that uses the
//   representation to interpret sentences in the language.
//
// When to use:
//   - You have a simple domain-specific language (DSL) or expression language
//   - The grammar is relatively simple and efficiency is not a primary concern
//   - You need to evaluate or transform expressions represented as tree structures
//
// Key Participants:
//   - AbstractExpression: declares an interpret() method common to all nodes
//   - TerminalExpression: implements interpret() for terminal symbols in the grammar
//     (e.g., number literals)
//   - NonterminalExpression: implements interpret() for grammar rules that combine
//     other expressions (e.g., addition, subtraction, multiplication)
//   - Context: contains global information the interpreter may need (optional)

package main

import "fmt"

// ---------------------------------------------------------------------------
// Abstract expression
// ---------------------------------------------------------------------------

// Expression is the interface every node in the expression tree implements.
type Expression interface {
	Interpret() float64
	String() string
}

// ---------------------------------------------------------------------------
// Terminal expression
// ---------------------------------------------------------------------------

// NumberExpression is a leaf node representing a numeric literal.
type NumberExpression struct {
	Value float64
}

func (n *NumberExpression) Interpret() float64 {
	return n.Value
}

func (n *NumberExpression) String() string {
	// Display as integer when there is no fractional part
	if n.Value == float64(int64(n.Value)) {
		return fmt.Sprintf("%d", int64(n.Value))
	}
	return fmt.Sprintf("%g", n.Value)
}

// ---------------------------------------------------------------------------
// Non-terminal expressions
// ---------------------------------------------------------------------------

// AddExpression represents the addition of two sub-expressions.
type AddExpression struct {
	Left  Expression
	Right Expression
}

func (a *AddExpression) Interpret() float64 {
	return a.Left.Interpret() + a.Right.Interpret()
}

func (a *AddExpression) String() string {
	return fmt.Sprintf("(%s + %s)", a.Left, a.Right)
}

// SubtractExpression represents the subtraction of two sub-expressions.
type SubtractExpression struct {
	Left  Expression
	Right Expression
}

func (s *SubtractExpression) Interpret() float64 {
	return s.Left.Interpret() - s.Right.Interpret()
}

func (s *SubtractExpression) String() string {
	return fmt.Sprintf("(%s - %s)", s.Left, s.Right)
}

// MultiplyExpression represents the multiplication of two sub-expressions.
type MultiplyExpression struct {
	Left  Expression
	Right Expression
}

func (m *MultiplyExpression) Interpret() float64 {
	return m.Left.Interpret() * m.Right.Interpret()
}

func (m *MultiplyExpression) String() string {
	return fmt.Sprintf("(%s * %s)", m.Left, m.Right)
}

// ---------------------------------------------------------------------------
// Main -- build and evaluate expression trees
// ---------------------------------------------------------------------------

func main() {
	// Expression: (3 + 5) * 2 = 16
	expr1 := &MultiplyExpression{
		Left: &AddExpression{
			Left:  &NumberExpression{Value: 3},
			Right: &NumberExpression{Value: 5},
		},
		Right: &NumberExpression{Value: 2},
	}
	fmt.Printf("%s = %g\n", expr1, expr1.Interpret())

	// Expression: 10 - (2 * 3) = 4
	expr2 := &SubtractExpression{
		Left: &NumberExpression{Value: 10},
		Right: &MultiplyExpression{
			Left:  &NumberExpression{Value: 2},
			Right: &NumberExpression{Value: 3},
		},
	}
	fmt.Printf("%s = %g\n", expr2, expr2.Interpret())

	// Expression: (7 + 3) * (10 - 5) = 50
	expr3 := &MultiplyExpression{
		Left: &AddExpression{
			Left:  &NumberExpression{Value: 7},
			Right: &NumberExpression{Value: 3},
		},
		Right: &SubtractExpression{
			Left:  &NumberExpression{Value: 10},
			Right: &NumberExpression{Value: 5},
		},
	}
	fmt.Printf("%s = %g\n", expr3, expr3.Interpret())

	// Expression: ((2 + 3) * 4) - 6 = 14
	expr4 := &SubtractExpression{
		Left: &MultiplyExpression{
			Left: &AddExpression{
				Left:  &NumberExpression{Value: 2},
				Right: &NumberExpression{Value: 3},
			},
			Right: &NumberExpression{Value: 4},
		},
		Right: &NumberExpression{Value: 6},
	}
	fmt.Printf("%s = %g\n", expr4, expr4.Interpret())
}
