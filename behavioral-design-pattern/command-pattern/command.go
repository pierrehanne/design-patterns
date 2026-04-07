// Command Pattern
// ===============
// Category: Behavioral Design Pattern
//
// Intent:
//   Encapsulate a request as an object, supporting undo/redo,
//   queuing, and decoupling invoker from receiver.
//
// Key Participants:
//   - Command (interface): Declares Execute() and Undo()
//   - ConcreteCommand: Binds a receiver to an action
//   - Receiver: TextDocument
//   - Invoker: TextEditor with history

package main

import "fmt"

// ---------------------------------------------------------------------------
// Receiver
// ---------------------------------------------------------------------------

type TextDocument struct {
	Content string
}

func (d *TextDocument) Insert(position int, text string) {
	d.Content = d.Content[:position] + text + d.Content[position:]
}

func (d *TextDocument) Delete(position, length int) string {
	deleted := d.Content[position : position+length]
	d.Content = d.Content[:position] + d.Content[position+length:]
	return deleted
}

func (d *TextDocument) String() string {
	return fmt.Sprintf("%q", d.Content)
}

// ---------------------------------------------------------------------------
// Command interface
// ---------------------------------------------------------------------------

type Command interface {
	Execute()
	Undo()
	Description() string
}

// ---------------------------------------------------------------------------
// Concrete Commands
// ---------------------------------------------------------------------------

type InsertCommand struct {
	doc      *TextDocument
	position int
	text     string
}

func (c *InsertCommand) Execute()         { c.doc.Insert(c.position, c.text) }
func (c *InsertCommand) Undo()            { c.doc.Delete(c.position, len(c.text)) }
func (c *InsertCommand) Description() string {
	return fmt.Sprintf("Insert %q at %d", c.text, c.position)
}

type DeleteCommand struct {
	doc         *TextDocument
	position    int
	length      int
	deletedText string
}

func (c *DeleteCommand) Execute() {
	c.deletedText = c.doc.Delete(c.position, c.length)
}
func (c *DeleteCommand) Undo() { c.doc.Insert(c.position, c.deletedText) }
func (c *DeleteCommand) Description() string {
	return fmt.Sprintf("Delete %d chars at %d", c.length, c.position)
}

type ReplaceCommand struct {
	doc      *TextDocument
	position int
	length   int
	newText  string
	oldText  string
}

func (c *ReplaceCommand) Execute() {
	c.oldText = c.doc.Delete(c.position, c.length)
	c.doc.Insert(c.position, c.newText)
}
func (c *ReplaceCommand) Undo() {
	c.doc.Delete(c.position, len(c.newText))
	c.doc.Insert(c.position, c.oldText)
}
func (c *ReplaceCommand) Description() string {
	return fmt.Sprintf("Replace %d chars at %d with %q", c.length, c.position, c.newText)
}

// ---------------------------------------------------------------------------
// Invoker
// ---------------------------------------------------------------------------

type TextEditor struct {
	doc       *TextDocument
	history   []Command
	redoStack []Command
}

func NewTextEditor(doc *TextDocument) *TextEditor {
	return &TextEditor{doc: doc}
}

func (e *TextEditor) Execute(cmd Command) {
	cmd.Execute()
	e.history = append(e.history, cmd)
	e.redoStack = nil
	fmt.Printf("  [Execute] %s -> %s\n", cmd.Description(), e.doc)
}

func (e *TextEditor) Undo() {
	if len(e.history) == 0 {
		fmt.Println("  [Undo] Nothing to undo")
		return
	}
	cmd := e.history[len(e.history)-1]
	e.history = e.history[:len(e.history)-1]
	cmd.Undo()
	e.redoStack = append(e.redoStack, cmd)
	fmt.Printf("  [Undo] %s -> %s\n", cmd.Description(), e.doc)
}

func (e *TextEditor) Redo() {
	if len(e.redoStack) == 0 {
		fmt.Println("  [Redo] Nothing to redo")
		return
	}
	cmd := e.redoStack[len(e.redoStack)-1]
	e.redoStack = e.redoStack[:len(e.redoStack)-1]
	cmd.Execute()
	e.history = append(e.history, cmd)
	fmt.Printf("  [Redo] %s -> %s\n", cmd.Description(), e.doc)
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	doc := &TextDocument{}
	editor := NewTextEditor(doc)

	fmt.Println("=== Building a document ===")
	editor.Execute(&InsertCommand{doc: doc, position: 0, text: "Hello World"})
	editor.Execute(&InsertCommand{doc: doc, position: 5, text: ","})
	editor.Execute(&InsertCommand{doc: doc, position: len(doc.Content), text: "!"})
	editor.Execute(&ReplaceCommand{doc: doc, position: 7, length: 5, newText: "Go"})

	fmt.Println("\n=== Undo ===")
	editor.Undo()
	editor.Undo()

	fmt.Println("\n=== Redo ===")
	editor.Redo()

	fmt.Println("\n=== Delete and undo ===")
	editor.Execute(&DeleteCommand{doc: doc, position: 0, length: 5})
	editor.Undo()
}
