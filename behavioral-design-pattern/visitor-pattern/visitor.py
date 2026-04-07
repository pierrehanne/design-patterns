"""
Visitor Pattern

Category: Behavioral Design Pattern

Intent:
    Represent an operation to be performed on elements of an object structure
    without changing the classes on which it operates.

When to use:
    - You need to perform many unrelated operations on an object structure
    - The object structure rarely changes, but you often define new operations
    - You want to avoid polluting element classes with operation-specific logic

Key Participants:
    - Visitor: declares visit methods for each concrete element type
    - ConcreteVisitor: implements each visit method with specific behavior
    - Element: declares an accept(visitor) method
    - ConcreteElement: implements accept() by calling the visitor's corresponding method

Double Dispatch:
    The visitor pattern uses double dispatch to invoke the correct operation.
    First dispatch: the element calls accept(visitor) -- polymorphic on the element type.
    Second dispatch: inside accept(), the element calls visitor.visit_X(self) -- polymorphic
    on the visitor type. This two-step indirection lets the runtime resolve both the element
    type AND the visitor type, achieving behavior that depends on both.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Element hierarchy
# ---------------------------------------------------------------------------

class Element(ABC):
    """Base interface -- every document element must accept a visitor."""

    @abstractmethod
    def accept(self, visitor: ExportVisitor) -> str:
        ...


class Paragraph(Element):
    def __init__(self, text: str) -> None:
        self.text = text

    def accept(self, visitor: ExportVisitor) -> str:
        # Second dispatch: visitor now knows the concrete element type
        return visitor.visit_paragraph(self)


class Image(Element):
    def __init__(self, url: str, alt_text: str) -> None:
        self.url = url
        self.alt_text = alt_text

    def accept(self, visitor: ExportVisitor) -> str:
        return visitor.visit_image(self)


class Table(Element):
    def __init__(self, headers: list[str], rows: list[list[str]]) -> None:
        self.headers = headers
        self.rows = rows

    def accept(self, visitor: ExportVisitor) -> str:
        return visitor.visit_table(self)


# ---------------------------------------------------------------------------
# Visitor hierarchy
# ---------------------------------------------------------------------------

class ExportVisitor(ABC):
    """Each concrete visitor implements a different export format."""

    @abstractmethod
    def visit_paragraph(self, p: Paragraph) -> str:
        ...

    @abstractmethod
    def visit_image(self, img: Image) -> str:
        ...

    @abstractmethod
    def visit_table(self, tbl: Table) -> str:
        ...


class HtmlExporter(ExportVisitor):
    def visit_paragraph(self, p: Paragraph) -> str:
        return f"<p>{p.text}</p>"

    def visit_image(self, img: Image) -> str:
        return f'<img src="{img.url}" alt="{img.alt_text}" />'

    def visit_table(self, tbl: Table) -> str:
        header_cells = "".join(f"<th>{h}</th>" for h in tbl.headers)
        rows_html = ""
        for row in tbl.rows:
            cells = "".join(f"<td>{c}</td>" for c in row)
            rows_html += f"<tr>{cells}</tr>"
        return f"<table><tr>{header_cells}</tr>{rows_html}</table>"


class MarkdownExporter(ExportVisitor):
    def visit_paragraph(self, p: Paragraph) -> str:
        return p.text

    def visit_image(self, img: Image) -> str:
        return f"![{img.alt_text}]({img.url})"

    def visit_table(self, tbl: Table) -> str:
        header_line = "| " + " | ".join(tbl.headers) + " |"
        sep_line = "| " + " | ".join("---" for _ in tbl.headers) + " |"
        row_lines = "\n".join(
            "| " + " | ".join(row) + " |" for row in tbl.rows
        )
        return f"{header_line}\n{sep_line}\n{row_lines}"


class PlainTextExporter(ExportVisitor):
    def visit_paragraph(self, p: Paragraph) -> str:
        return p.text

    def visit_image(self, img: Image) -> str:
        return f"[Image: {img.alt_text} ({img.url})]"

    def visit_table(self, tbl: Table) -> str:
        col_widths = [len(h) for h in tbl.headers]
        for row in tbl.rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        def fmt_row(cells: list[str]) -> str:
            return "  ".join(c.ljust(w) for c, w in zip(cells, col_widths))

        lines = [fmt_row(tbl.headers)]
        lines.append("  ".join("-" * w for w in col_widths))
        for row in tbl.rows:
            lines.append(fmt_row(row))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helper: export entire document
# ---------------------------------------------------------------------------

def export_document(elements: list[Element], visitor: ExportVisitor) -> str:
    """Apply the visitor to every element and join the results."""
    return "\n".join(el.accept(visitor) for el in elements)


# ---------------------------------------------------------------------------
# Main -- demonstrate exporting a document in three formats
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Build a small document
    document: list[Element] = [
        Paragraph("Welcome to the visitor pattern demo."),
        Image("https://example.com/photo.png", "A sample photo"),
        Table(
            headers=["Name", "Role"],
            rows=[
                ["Alice", "Engineer"],
                ["Bob", "Designer"],
            ],
        ),
    ]

    visitors = {
        "HTML": HtmlExporter(),
        "Markdown": MarkdownExporter(),
        "Plain Text": PlainTextExporter(),
    }

    for label, visitor in visitors.items():
        print(f"=== {label} Export ===")
        print(export_document(document, visitor))
        print()
