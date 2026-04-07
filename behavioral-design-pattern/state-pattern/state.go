// State Pattern
// =================
// Category: Behavioral Design Pattern
//
// Intent:
//
//	Allow an object to alter its behavior when its internal state changes.
//	The object will appear to change its class.
//
// When to use:
//   - When an object's behavior depends on its state and it must change
//     behavior at runtime depending on that state.
//   - When you want to eliminate large conditional statements that select
//     behavior based on the current state.
//   - When transitions between states need to be explicit and controlled.
//
// Key Participants:
//   - State (interface): DocumentState -- declares methods that all concrete
//     states must implement.
//   - ConcreteState: DraftState, ReviewState, PublishedState, ArchivedState --
//     each implements behavior appropriate for that state of the context.
//   - Context: Document -- maintains a reference to a ConcreteState that
//     defines the current state.
package main

import "fmt"

// ---------------------------------------------------------------------------
// State interface
// ---------------------------------------------------------------------------

// DocumentState defines the behavior for each state of a Document.
type DocumentState interface {
	Name() string
	Edit(doc *Document)
	Submit(doc *Document)
	Publish(doc *Document)
	Archive(doc *Document)
}

// ---------------------------------------------------------------------------
// Concrete states
// ---------------------------------------------------------------------------

// DraftState -- the document is being authored and can be freely edited.
type DraftState struct{}

func (s *DraftState) Name() string { return "Draft" }

func (s *DraftState) Edit(doc *Document) {
	fmt.Println("  [Draft] Editing document content.")
}

func (s *DraftState) Submit(doc *Document) {
	fmt.Println("  [Draft] Submitting document for review.")
	doc.SetState(&ReviewState{})
}

func (s *DraftState) Publish(doc *Document) {
	fmt.Println("  [Draft] ERROR: Cannot publish directly from Draft. Submit for review first.")
}

func (s *DraftState) Archive(doc *Document) {
	fmt.Println("  [Draft] Archiving draft document.")
	doc.SetState(&ArchivedState{})
}

// ReviewState -- the document is under editorial review.
type ReviewState struct{}

func (s *ReviewState) Name() string { return "Under Review" }

func (s *ReviewState) Edit(doc *Document) {
	fmt.Println("  [Review] Sending document back to Draft for edits.")
	doc.SetState(&DraftState{})
}

func (s *ReviewState) Submit(doc *Document) {
	fmt.Println("  [Review] ERROR: Document is already under review.")
}

func (s *ReviewState) Publish(doc *Document) {
	fmt.Println("  [Review] Review approved. Publishing document.")
	doc.SetState(&PublishedState{})
}

func (s *ReviewState) Archive(doc *Document) {
	fmt.Println("  [Review] ERROR: Cannot archive while under review. Publish or reject first.")
}

// PublishedState -- the document is live and visible to readers.
type PublishedState struct{}

func (s *PublishedState) Name() string { return "Published" }

func (s *PublishedState) Edit(doc *Document) {
	fmt.Println("  [Published] ERROR: Cannot edit a published document. Archive it first.")
}

func (s *PublishedState) Submit(doc *Document) {
	fmt.Println("  [Published] ERROR: Document is already published.")
}

func (s *PublishedState) Publish(doc *Document) {
	fmt.Println("  [Published] ERROR: Document is already published.")
}

func (s *PublishedState) Archive(doc *Document) {
	fmt.Println("  [Published] Archiving published document.")
	doc.SetState(&ArchivedState{})
}

// ArchivedState -- the document has been archived and is read-only.
type ArchivedState struct{}

func (s *ArchivedState) Name() string { return "Archived" }

func (s *ArchivedState) Edit(doc *Document) {
	fmt.Println("  [Archived] Un-archiving and moving to Draft for editing.")
	doc.SetState(&DraftState{})
}

func (s *ArchivedState) Submit(doc *Document) {
	fmt.Println("  [Archived] ERROR: Cannot submit an archived document. Edit it first.")
}

func (s *ArchivedState) Publish(doc *Document) {
	fmt.Println("  [Archived] ERROR: Cannot publish an archived document. Edit it first.")
}

func (s *ArchivedState) Archive(doc *Document) {
	fmt.Println("  [Archived] ERROR: Document is already archived.")
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

// Document is the context object that delegates behavior to its current state.
type Document struct {
	Title string
	state DocumentState
}

// NewDocument creates a document starting in the Draft state.
func NewDocument(title string) *Document {
	return &Document{
		Title: title,
		state: &DraftState{},
	}
}

// SetState transitions the document to a new state.
func (d *Document) SetState(newState DocumentState) {
	old := d.state.Name()
	d.state = newState
	fmt.Printf("  >> Document '%s': %s -> %s\n", d.Title, old, d.state.Name())
}

func (d *Document) Edit() {
	fmt.Printf("\nDocument '%s' [%s]: edit()\n", d.Title, d.state.Name())
	d.state.Edit(d)
}

func (d *Document) Submit() {
	fmt.Printf("\nDocument '%s' [%s]: submit()\n", d.Title, d.state.Name())
	d.state.Submit(d)
}

func (d *Document) Publish() {
	fmt.Printf("\nDocument '%s' [%s]: publish()\n", d.Title, d.state.Name())
	d.state.Publish(d)
}

func (d *Document) Archive() {
	fmt.Printf("\nDocument '%s' [%s]: archive()\n", d.Title, d.state.Name())
	d.state.Archive(d)
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
func main() {
	doc := NewDocument("Design Patterns Guide")

	// Normal workflow: Draft -> Review -> Published -> Archived
	doc.Edit()    // OK: editing in draft
	doc.Publish() // ERROR: can't publish from draft
	doc.Submit()  // OK: moves to Review
	doc.Publish() // OK: moves to Published
	doc.Edit()    // ERROR: can't edit published doc
	doc.Archive() // OK: moves to Archived

	// Recover from archived: un-archive by editing
	doc.Edit()    // OK: moves back to Draft
	doc.Submit()  // OK: moves to Review
	doc.Edit()    // OK: rejected, back to Draft
	doc.Submit()  // OK: back to Review
	doc.Publish() // OK: Published again
}
