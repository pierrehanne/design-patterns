/**
 * Visitor Pattern
 *
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Represent an operation to be performed on elements of an object structure
 *   without changing the classes on which it operates.
 *
 * When to use:
 *   - You need to perform many unrelated operations on an object structure
 *   - The object structure rarely changes, but you often define new operations
 *   - You want to avoid polluting element classes with operation-specific logic
 *
 * Key Participants:
 *   - Visitor: declares visit methods for each concrete element type
 *   - ConcreteVisitor: implements each visit method with specific behavior
 *   - Element: declares an accept(visitor) method
 *   - ConcreteElement: implements accept() by calling the visitor's corresponding method
 *
 * Double Dispatch:
 *   The visitor pattern uses double dispatch to invoke the correct operation.
 *   First dispatch: the element calls accept(visitor) -- polymorphic on the element type.
 *   Second dispatch: inside accept(), the element calls visitor.visitX(this) -- polymorphic
 *   on the visitor type. This two-step indirection lets the runtime resolve both the element
 *   type AND the visitor type, achieving behavior that depends on both.
 */

// ---------------------------------------------------------------------------
// Element hierarchy
// ---------------------------------------------------------------------------

interface Element {
  accept(visitor: ExportVisitor): string;
}

class Paragraph implements Element {
  constructor(public readonly text: string) {}

  accept(visitor: ExportVisitor): string {
    // Second dispatch: visitor now knows the concrete element type
    return visitor.visitParagraph(this);
  }
}

class ImageElement implements Element {
  constructor(
    public readonly url: string,
    public readonly altText: string,
  ) {}

  accept(visitor: ExportVisitor): string {
    return visitor.visitImage(this);
  }
}

class Table implements Element {
  constructor(
    public readonly headers: string[],
    public readonly rows: string[][],
  ) {}

  accept(visitor: ExportVisitor): string {
    return visitor.visitTable(this);
  }
}

// ---------------------------------------------------------------------------
// Visitor hierarchy
// ---------------------------------------------------------------------------

interface ExportVisitor {
  visitParagraph(p: Paragraph): string;
  visitImage(img: ImageElement): string;
  visitTable(tbl: Table): string;
}

class HtmlExporter implements ExportVisitor {
  visitParagraph(p: Paragraph): string {
    return `<p>${p.text}</p>`;
  }

  visitImage(img: ImageElement): string {
    return `<img src="${img.url}" alt="${img.altText}" />`;
  }

  visitTable(tbl: Table): string {
    const headerCells = tbl.headers.map((h) => `<th>${h}</th>`).join("");
    const rowsHtml = tbl.rows
      .map((row) => `<tr>${row.map((c) => `<td>${c}</td>`).join("")}</tr>`)
      .join("");
    return `<table><tr>${headerCells}</tr>${rowsHtml}</table>`;
  }
}

class MarkdownExporter implements ExportVisitor {
  visitParagraph(p: Paragraph): string {
    return p.text;
  }

  visitImage(img: ImageElement): string {
    return `![${img.altText}](${img.url})`;
  }

  visitTable(tbl: Table): string {
    const headerLine = "| " + tbl.headers.join(" | ") + " |";
    const sepLine = "| " + tbl.headers.map(() => "---").join(" | ") + " |";
    const rowLines = tbl.rows
      .map((row) => "| " + row.join(" | ") + " |")
      .join("\n");
    return `${headerLine}\n${sepLine}\n${rowLines}`;
  }
}

class PlainTextExporter implements ExportVisitor {
  visitParagraph(p: Paragraph): string {
    return p.text;
  }

  visitImage(img: ImageElement): string {
    return `[Image: ${img.altText} (${img.url})]`;
  }

  visitTable(tbl: Table): string {
    // Calculate column widths for alignment
    const colWidths = tbl.headers.map((h, i) =>
      Math.max(h.length, ...tbl.rows.map((r) => r[i].length)),
    );
    const pad = (s: string, w: number) => s.padEnd(w);
    const fmtRow = (cells: string[]) =>
      cells.map((c, i) => pad(c, colWidths[i])).join("  ");

    const lines: string[] = [
      fmtRow(tbl.headers),
      colWidths.map((w) => "-".repeat(w)).join("  "),
      ...tbl.rows.map((row) => fmtRow(row)),
    ];
    return lines.join("\n");
  }
}

// ---------------------------------------------------------------------------
// Helper: export entire document
// ---------------------------------------------------------------------------

function exportDocument(elements: Element[], visitor: ExportVisitor): string {
  return elements.map((el) => el.accept(visitor)).join("\n");
}

// ---------------------------------------------------------------------------
// Main -- demonstrate exporting a document in three formats
// ---------------------------------------------------------------------------

function main(): void {
  const document: Element[] = [
    new Paragraph("Welcome to the visitor pattern demo."),
    new ImageElement("https://example.com/photo.png", "A sample photo"),
    new Table(
      ["Name", "Role"],
      [
        ["Alice", "Engineer"],
        ["Bob", "Designer"],
      ],
    ),
  ];

  const visitors: Record<string, ExportVisitor> = {
    HTML: new HtmlExporter(),
    Markdown: new MarkdownExporter(),
    "Plain Text": new PlainTextExporter(),
  };

  for (const [label, visitor] of Object.entries(visitors)) {
    console.log(`=== ${label} Export ===`);
    console.log(exportDocument(document, visitor));
    console.log();
  }
}

main();
