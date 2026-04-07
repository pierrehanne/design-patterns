//! Visitor Pattern
//!
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!   Represent an operation to be performed on elements of an object structure
//!   without changing the classes on which it operates.
//!
//! When to use:
//!   - You need to perform many unrelated operations on an object structure
//!   - The object structure rarely changes, but you often define new operations
//!   - You want to avoid polluting element types with operation-specific logic
//!
//! Key Participants:
//!   - Visitor: declares visit methods for each concrete element type
//!   - ConcreteVisitor: implements each visit method with specific behavior
//!   - Element: declares an accept(visitor) method
//!   - ConcreteElement: implements accept() by calling the visitor's corresponding method
//!
//! Double Dispatch:
//!   The visitor pattern uses double dispatch to invoke the correct operation.
//!   First dispatch: the element calls accept(visitor) -- polymorphic on the element type.
//!   Second dispatch: inside accept(), the element calls visitor.visit_x(self) -- polymorphic
//!   on the visitor type. This two-step indirection lets the runtime resolve both the element
//!   type AND the visitor type, achieving behavior that depends on both.

// ---------------------------------------------------------------------------
// Element hierarchy
// ---------------------------------------------------------------------------

/// Every document element must accept a visitor.
trait Element {
    fn accept(&self, visitor: &dyn ExportVisitor) -> String;
}

struct Paragraph {
    text: String,
}

impl Element for Paragraph {
    fn accept(&self, visitor: &dyn ExportVisitor) -> String {
        // Second dispatch: visitor now knows the concrete element type
        visitor.visit_paragraph(self)
    }
}

struct Image {
    url: String,
    alt_text: String,
}

impl Element for Image {
    fn accept(&self, visitor: &dyn ExportVisitor) -> String {
        visitor.visit_image(self)
    }
}

struct Table {
    headers: Vec<String>,
    rows: Vec<Vec<String>>,
}

impl Element for Table {
    fn accept(&self, visitor: &dyn ExportVisitor) -> String {
        visitor.visit_table(self)
    }
}

// ---------------------------------------------------------------------------
// Visitor hierarchy
// ---------------------------------------------------------------------------

/// Each concrete visitor implements a different export format.
trait ExportVisitor {
    fn visit_paragraph(&self, p: &Paragraph) -> String;
    fn visit_image(&self, img: &Image) -> String;
    fn visit_table(&self, tbl: &Table) -> String;
}

struct HtmlExporter;

impl ExportVisitor for HtmlExporter {
    fn visit_paragraph(&self, p: &Paragraph) -> String {
        format!("<p>{}</p>", p.text)
    }

    fn visit_image(&self, img: &Image) -> String {
        format!(r#"<img src="{}" alt="{}" />"#, img.url, img.alt_text)
    }

    fn visit_table(&self, tbl: &Table) -> String {
        let header_cells: String = tbl
            .headers
            .iter()
            .map(|h| format!("<th>{}</th>", h))
            .collect();
        let rows_html: String = tbl
            .rows
            .iter()
            .map(|row| {
                let cells: String = row.iter().map(|c| format!("<td>{}</td>", c)).collect();
                format!("<tr>{}</tr>", cells)
            })
            .collect();
        format!("<table><tr>{}</tr>{}</table>", header_cells, rows_html)
    }
}

struct MarkdownExporter;

impl ExportVisitor for MarkdownExporter {
    fn visit_paragraph(&self, p: &Paragraph) -> String {
        p.text.clone()
    }

    fn visit_image(&self, img: &Image) -> String {
        format!("![{}]({})", img.alt_text, img.url)
    }

    fn visit_table(&self, tbl: &Table) -> String {
        let header_line = format!("| {} |", tbl.headers.join(" | "));
        let sep_line = format!(
            "| {} |",
            tbl.headers.iter().map(|_| "---").collect::<Vec<_>>().join(" | ")
        );
        let row_lines: String = tbl
            .rows
            .iter()
            .map(|row| format!("| {} |", row.join(" | ")))
            .collect::<Vec<_>>()
            .join("\n");
        format!("{}\n{}\n{}", header_line, sep_line, row_lines)
    }
}

struct PlainTextExporter;

impl ExportVisitor for PlainTextExporter {
    fn visit_paragraph(&self, p: &Paragraph) -> String {
        p.text.clone()
    }

    fn visit_image(&self, img: &Image) -> String {
        format!("[Image: {} ({})]", img.alt_text, img.url)
    }

    fn visit_table(&self, tbl: &Table) -> String {
        // Calculate column widths for alignment
        let mut col_widths: Vec<usize> = tbl.headers.iter().map(|h| h.len()).collect();
        for row in &tbl.rows {
            for (i, cell) in row.iter().enumerate() {
                col_widths[i] = col_widths[i].max(cell.len());
            }
        }

        let fmt_row = |cells: &[String]| -> String {
            cells
                .iter()
                .enumerate()
                .map(|(i, c)| format!("{:width$}", c, width = col_widths[i]))
                .collect::<Vec<_>>()
                .join("  ")
        };

        let mut lines = vec![fmt_row(&tbl.headers)];
        lines.push(
            col_widths
                .iter()
                .map(|&w| "-".repeat(w))
                .collect::<Vec<_>>()
                .join("  "),
        );
        for row in &tbl.rows {
            lines.push(fmt_row(row));
        }
        lines.join("\n")
    }
}

// ---------------------------------------------------------------------------
// Helper: export entire document
// ---------------------------------------------------------------------------

fn export_document(elements: &[Box<dyn Element>], visitor: &dyn ExportVisitor) -> String {
    elements
        .iter()
        .map(|el| el.accept(visitor))
        .collect::<Vec<_>>()
        .join("\n")
}

// ---------------------------------------------------------------------------
// Main -- demonstrate exporting a document in three formats
// ---------------------------------------------------------------------------

fn main() {
    let document: Vec<Box<dyn Element>> = vec![
        Box::new(Paragraph {
            text: "Welcome to the visitor pattern demo.".into(),
        }),
        Box::new(Image {
            url: "https://example.com/photo.png".into(),
            alt_text: "A sample photo".into(),
        }),
        Box::new(Table {
            headers: vec!["Name".into(), "Role".into()],
            rows: vec![
                vec!["Alice".into(), "Engineer".into()],
                vec!["Bob".into(), "Designer".into()],
            ],
        }),
    ];

    let visitors: Vec<(&str, Box<dyn ExportVisitor>)> = vec![
        ("HTML", Box::new(HtmlExporter)),
        ("Markdown", Box::new(MarkdownExporter)),
        ("Plain Text", Box::new(PlainTextExporter)),
    ];

    for (label, visitor) in &visitors {
        println!("=== {} Export ===", label);
        println!("{}", export_document(&document, visitor.as_ref()));
        println!();
    }
}
