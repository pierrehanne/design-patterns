// Prototype Pattern
// =================
// Category: Creational Design Pattern
//
// Intent:
//   Create new objects by cloning an existing instance rather than building
//   from scratch. Useful when object creation is expensive or when you want
//   copies with slight variations.
//
// When to use:
//   - When creating an object is expensive (DB queries, complex computation)
//   - When you need many similar objects with small differences
//   - When object configuration is complex and you'd rather copy-and-tweak
//
// Key Participants:
//   - Prototype (interface): Declares the Clone method
//   - ConcretePrototype: Implements Clone by deep-copying its own state
//   - Client: Creates new objects by calling Clone on prototypes
//
// Go approach:
//   Go has no built-in clone mechanism. We define a Clone() method that
//   manually copies all fields, including slices and maps (to avoid sharing).

package main

import (
	"fmt"
	"strings"
)

// ---------------------------------------------------------------------------
// Prototype Interface
// ---------------------------------------------------------------------------

type Cloneable interface {
	Clone() Cloneable
}

// ---------------------------------------------------------------------------
// Nested struct (demonstrates deep copy necessity)
// ---------------------------------------------------------------------------

type DocumentStyle struct {
	Font        string
	FontSize    int
	Color       string
	LineSpacing float64
}

// ---------------------------------------------------------------------------
// Concrete Prototype — Document Template
// ---------------------------------------------------------------------------

type DocumentTemplate struct {
	Title    string
	Style    DocumentStyle // Struct value — copied automatically in Go
	Sections []string      // Slice — must be explicitly copied for deep clone
	Metadata map[string]string // Map — must be explicitly copied
}

// Clone creates a fully independent deep copy.
// Go copies struct values automatically, but slices and maps are references
// that must be explicitly duplicated.
func (d *DocumentTemplate) Clone() Cloneable {
	// Copy the slice
	sections := make([]string, len(d.Sections))
	copy(sections, d.Sections)

	// Copy the map
	metadata := make(map[string]string, len(d.Metadata))
	for k, v := range d.Metadata {
		metadata[k] = v
	}

	return &DocumentTemplate{
		Title:    d.Title,
		Style:    d.Style, // Struct value, not a pointer — automatically deep-copied
		Sections: sections,
		Metadata: metadata,
	}
}

func (d *DocumentTemplate) String() string {
	sections := "(none)"
	if len(d.Sections) > 0 {
		sections = strings.Join(d.Sections, ", ")
	}
	meta := "(none)"
	if len(d.Metadata) > 0 {
		pairs := make([]string, 0, len(d.Metadata))
		for k, v := range d.Metadata {
			pairs = append(pairs, fmt.Sprintf("%s=%s", k, v))
		}
		meta = strings.Join(pairs, ", ")
	}
	return fmt.Sprintf("Document: '%s'\n  Style: %s %dpt %s\n  Sections: %s\n  Metadata: %s",
		d.Title, d.Style.Font, d.Style.FontSize, d.Style.Color, sections, meta)
}

// ---------------------------------------------------------------------------
// Prototype Registry — stores named prototypes
// ---------------------------------------------------------------------------

type TemplateRegistry struct {
	templates map[string]*DocumentTemplate
}

func NewTemplateRegistry() *TemplateRegistry {
	return &TemplateRegistry{
		templates: make(map[string]*DocumentTemplate),
	}
}

func (r *TemplateRegistry) Register(name string, template *DocumentTemplate) {
	r.templates[name] = template
}

// Create clones a registered prototype. Returns nil if not found.
func (r *TemplateRegistry) Create(name string) *DocumentTemplate {
	proto, ok := r.templates[name]
	if !ok {
		return nil
	}
	return proto.Clone().(*DocumentTemplate) // Type assert back to concrete type
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	registry := NewTemplateRegistry()

	// Register pre-configured prototypes
	registry.Register("report", &DocumentTemplate{
		Title: "Quarterly Report",
		Style: DocumentStyle{
			Font: "Times New Roman", FontSize: 11,
			Color: "#333333", LineSpacing: 1.5,
		},
		Sections: []string{"Executive Summary", "Financials", "Outlook"},
		Metadata: map[string]string{"author": "Template", "department": "Finance"},
	})

	registry.Register("memo", &DocumentTemplate{
		Title: "Internal Memo",
		Style: DocumentStyle{
			Font: "Helvetica", FontSize: 10,
			Color: "#000000", LineSpacing: 1.15,
		},
		Sections: []string{"Subject", "Body", "Action Items"},
		Metadata: map[string]string{"classification": "internal"},
	})

	// Clone and customize
	q1Report := registry.Create("report")
	q1Report.Title = "Q1 2025 Report"
	q1Report.Metadata["author"] = "Alice"
	q1Report.Sections = append(q1Report.Sections, "Risk Assessment")

	q2Report := registry.Create("report")
	q2Report.Title = "Q2 2025 Report"
	q2Report.Metadata["author"] = "Bob"

	teamMemo := registry.Create("memo")
	teamMemo.Title = "Engineering All-Hands Notes"
	teamMemo.Metadata["author"] = "Charlie"

	fmt.Println("=== Q1 Report (cloned + customized) ===")
	fmt.Println(q1Report)
	fmt.Println("\n=== Q2 Report (cloned + customized) ===")
	fmt.Println(q2Report)
	fmt.Println("\n=== Team Memo (cloned from memo template) ===")
	fmt.Println(teamMemo)

	// Verify deep copy: original is unmodified
	fresh := registry.Create("report")
	fmt.Println("\n=== Fresh clone (proves original is untouched) ===")
	fmt.Println(fresh)
}
