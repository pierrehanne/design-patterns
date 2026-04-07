// Visitor Pattern
//
// Category: Behavioral Design Pattern
//
// Intent:
//   Represent an operation to be performed on elements of an object structure
//   without changing the classes on which it operates.
//
// When to use:
//   - You need to perform many unrelated operations on an object structure
//   - The object structure rarely changes, but you often define new operations
//   - You want to avoid polluting element types with operation-specific logic
//
// Key Participants:
//   - Visitor: declares visit methods for each concrete element type
//   - ConcreteVisitor: implements each visit method with specific behavior
//   - Element: declares an accept(visitor) method
//   - ConcreteElement: implements accept() by calling the visitor's corresponding method
//
// Double Dispatch:
//   The visitor pattern uses double dispatch to invoke the correct operation.
//   First dispatch: the element calls Accept(visitor) -- polymorphic on the element type.
//   Second dispatch: inside Accept(), the element calls visitor.VisitX(self) -- polymorphic
//   on the visitor type. This two-step indirection lets the runtime resolve both the element
//   type AND the visitor type, achieving behavior that depends on both.

package main

import (
	"fmt"
	"strings"
)

// ---------------------------------------------------------------------------
// Element hierarchy
// ---------------------------------------------------------------------------

// Element is the base interface -- every document element must accept a visitor.
type Element interface {
	Accept(visitor ExportVisitor) string
}

type Paragraph struct {
	Text string
}

func (p *Paragraph) Accept(visitor ExportVisitor) string {
	// Second dispatch: visitor now knows the concrete element type
	return visitor.VisitParagraph(p)
}

type Image struct {
	URL     string
	AltText string
}

func (img *Image) Accept(visitor ExportVisitor) string {
	return visitor.VisitImage(img)
}

type Table struct {
	Headers []string
	Rows    [][]string
}

func (tbl *Table) Accept(visitor ExportVisitor) string {
	return visitor.VisitTable(tbl)
}

// ---------------------------------------------------------------------------
// Visitor hierarchy
// ---------------------------------------------------------------------------

// ExportVisitor defines the interface for each export format.
type ExportVisitor interface {
	VisitParagraph(p *Paragraph) string
	VisitImage(img *Image) string
	VisitTable(tbl *Table) string
}

// --- HtmlExporter ---

type HtmlExporter struct{}

func (h *HtmlExporter) VisitParagraph(p *Paragraph) string {
	return fmt.Sprintf("<p>%s</p>", p.Text)
}

func (h *HtmlExporter) VisitImage(img *Image) string {
	return fmt.Sprintf(`<img src="%s" alt="%s" />`, img.URL, img.AltText)
}

func (h *HtmlExporter) VisitTable(tbl *Table) string {
	var headerCells string
	for _, hdr := range tbl.Headers {
		headerCells += fmt.Sprintf("<th>%s</th>", hdr)
	}
	var rowsHTML string
	for _, row := range tbl.Rows {
		var cells string
		for _, c := range row {
			cells += fmt.Sprintf("<td>%s</td>", c)
		}
		rowsHTML += fmt.Sprintf("<tr>%s</tr>", cells)
	}
	return fmt.Sprintf("<table><tr>%s</tr>%s</table>", headerCells, rowsHTML)
}

// --- MarkdownExporter ---

type MarkdownExporter struct{}

func (m *MarkdownExporter) VisitParagraph(p *Paragraph) string {
	return p.Text
}

func (m *MarkdownExporter) VisitImage(img *Image) string {
	return fmt.Sprintf("![%s](%s)", img.AltText, img.URL)
}

func (m *MarkdownExporter) VisitTable(tbl *Table) string {
	headerLine := "| " + strings.Join(tbl.Headers, " | ") + " |"
	seps := make([]string, len(tbl.Headers))
	for i := range seps {
		seps[i] = "---"
	}
	sepLine := "| " + strings.Join(seps, " | ") + " |"

	var rowLines []string
	for _, row := range tbl.Rows {
		rowLines = append(rowLines, "| "+strings.Join(row, " | ")+" |")
	}
	return headerLine + "\n" + sepLine + "\n" + strings.Join(rowLines, "\n")
}

// --- PlainTextExporter ---

type PlainTextExporter struct{}

func (pt *PlainTextExporter) VisitParagraph(p *Paragraph) string {
	return p.Text
}

func (pt *PlainTextExporter) VisitImage(img *Image) string {
	return fmt.Sprintf("[Image: %s (%s)]", img.AltText, img.URL)
}

func (pt *PlainTextExporter) VisitTable(tbl *Table) string {
	// Calculate column widths for alignment
	colWidths := make([]int, len(tbl.Headers))
	for i, h := range tbl.Headers {
		colWidths[i] = len(h)
	}
	for _, row := range tbl.Rows {
		for i, cell := range row {
			if len(cell) > colWidths[i] {
				colWidths[i] = len(cell)
			}
		}
	}

	fmtRow := func(cells []string) string {
		parts := make([]string, len(cells))
		for i, c := range cells {
			parts[i] = fmt.Sprintf("%-*s", colWidths[i], c)
		}
		return strings.Join(parts, "  ")
	}

	var lines []string
	lines = append(lines, fmtRow(tbl.Headers))
	dashes := make([]string, len(colWidths))
	for i, w := range colWidths {
		dashes[i] = strings.Repeat("-", w)
	}
	lines = append(lines, strings.Join(dashes, "  "))
	for _, row := range tbl.Rows {
		lines = append(lines, fmtRow(row))
	}
	return strings.Join(lines, "\n")
}

// ---------------------------------------------------------------------------
// Helper: export entire document
// ---------------------------------------------------------------------------

func exportDocument(elements []Element, visitor ExportVisitor) string {
	parts := make([]string, len(elements))
	for i, el := range elements {
		parts[i] = el.Accept(visitor)
	}
	return strings.Join(parts, "\n")
}

// ---------------------------------------------------------------------------
// Main -- demonstrate exporting a document in three formats
// ---------------------------------------------------------------------------

func main() {
	document := []Element{
		&Paragraph{Text: "Welcome to the visitor pattern demo."},
		&Image{URL: "https://example.com/photo.png", AltText: "A sample photo"},
		&Table{
			Headers: []string{"Name", "Role"},
			Rows: [][]string{
				{"Alice", "Engineer"},
				{"Bob", "Designer"},
			},
		},
	}

	visitors := []struct {
		Label   string
		Visitor ExportVisitor
	}{
		{"HTML", &HtmlExporter{}},
		{"Markdown", &MarkdownExporter{}},
		{"Plain Text", &PlainTextExporter{}},
	}

	for _, v := range visitors {
		fmt.Printf("=== %s Export ===\n", v.Label)
		fmt.Println(exportDocument(document, v.Visitor))
		fmt.Println()
	}
}
