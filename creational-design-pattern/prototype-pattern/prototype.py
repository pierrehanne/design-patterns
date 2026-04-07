"""
Prototype Pattern
=================
Category: Creational Design Pattern

Intent:
    Create new objects by cloning an existing instance (the prototype) rather
    than building from scratch. Useful when object creation is expensive or
    when you want to produce copies with slight variations.

When to use:
    - When creating an object is expensive (DB queries, file I/O, complex computation)
    - When you need many similar objects with small differences
    - When you want to avoid a proliferation of factory subclasses
    - When object configuration is complex and you'd rather copy-and-tweak

Key Participants:
    - Prototype (interface): Declares the clone method
    - ConcretePrototype: Implements clone by copying its own state
    - Client: Creates new objects by asking a prototype to clone itself

Deep vs Shallow Copy:
    - Shallow copy: copies primitive fields, but nested objects are shared references
    - Deep copy: recursively copies everything — changes to the clone don't affect original
    Always use deep copy unless you explicitly want shared nested state.
"""

import copy
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Prototype — Document Template System
# ---------------------------------------------------------------------------
@dataclass
class DocumentStyle:
    """Nested object to demonstrate deep vs shallow copy."""
    font: str = "Arial"
    font_size: int = 12
    color: str = "#000000"
    line_spacing: float = 1.5


@dataclass
class DocumentTemplate:
    """
    A document prototype that can be cloned.
    Deep copying ensures nested objects (like style) are independent copies.
    """
    title: str
    style: DocumentStyle
    sections: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def clone(self) -> "DocumentTemplate":
        """
        Deep clone: creates a fully independent copy.
        Modifying the clone's style, sections, or metadata won't affect the original.
        """
        return copy.deepcopy(self)

    def shallow_clone(self) -> "DocumentTemplate":
        """
        Shallow clone: nested objects (style, sections, metadata) are SHARED.
        Mutating them on the clone WILL affect the original. Use with caution.
        """
        return copy.copy(self)

    def __str__(self) -> str:
        sections = ", ".join(self.sections) if self.sections else "(none)"
        meta = ", ".join(f"{k}={v}" for k, v in self.metadata.items()) or "(none)"
        return (
            f"Document: '{self.title}'\n"
            f"  Style: {self.style.font} {self.style.font_size}pt {self.style.color}\n"
            f"  Sections: {sections}\n"
            f"  Metadata: {meta}"
        )


# ---------------------------------------------------------------------------
# Prototype Registry — stores named prototypes for easy access
# ---------------------------------------------------------------------------
class TemplateRegistry:
    """
    A registry of pre-configured prototypes. Instead of constructing
    complex templates from scratch, clone a registered prototype and customize.
    """

    def __init__(self) -> None:
        self._templates: dict[str, DocumentTemplate] = {}

    def register(self, name: str, template: DocumentTemplate) -> None:
        self._templates[name] = template

    def create(self, name: str) -> DocumentTemplate:
        """Clone a registered prototype. Raises KeyError if not found."""
        prototype = self._templates.get(name)
        if prototype is None:
            raise KeyError(f"No template registered as '{name}'")
        return prototype.clone()


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Set up a registry with pre-configured prototypes
    registry = TemplateRegistry()

    # Register a "report" prototype — expensive to configure from scratch
    report_style = DocumentStyle(font="Times New Roman", font_size=11, color="#333333")
    report_template = DocumentTemplate(
        title="Quarterly Report",
        style=report_style,
        sections=["Executive Summary", "Financials", "Outlook"],
        metadata={"author": "Template", "department": "Finance"},
    )
    registry.register("report", report_template)

    # Register a "memo" prototype
    memo_style = DocumentStyle(font="Helvetica", font_size=10, color="#000000", line_spacing=1.15)
    memo_template = DocumentTemplate(
        title="Internal Memo",
        style=memo_style,
        sections=["Subject", "Body", "Action Items"],
        metadata={"classification": "internal"},
    )
    registry.register("memo", memo_template)

    # Clone and customize — much cheaper than building from scratch
    q1_report = registry.create("report")
    q1_report.title = "Q1 2025 Report"
    q1_report.metadata["author"] = "Alice"
    q1_report.sections.append("Risk Assessment")

    q2_report = registry.create("report")
    q2_report.title = "Q2 2025 Report"
    q2_report.metadata["author"] = "Bob"

    team_memo = registry.create("memo")
    team_memo.title = "Engineering All-Hands Notes"
    team_memo.metadata["author"] = "Charlie"

    print("=== Original template (unchanged because we deep-copied) ===")
    print(report_template)
    print()
    print("=== Q1 Report (cloned + customized) ===")
    print(q1_report)
    print()
    print("=== Q2 Report (cloned + customized) ===")
    print(q2_report)
    print()
    print("=== Team Memo (cloned from memo template) ===")
    print(team_memo)

    # Demonstrate deep vs shallow copy difference
    print("\n=== Deep vs Shallow Copy Demo ===")
    deep = report_template.clone()
    shallow = report_template.shallow_clone()

    deep.style.color = "#FF0000"     # Only affects the deep clone
    shallow.style.font_size = 99     # ALSO affects the original!

    print(f"Original font_size after shallow clone mutation: {report_template.style.font_size}")
    print(f"Original color after deep clone mutation: {report_template.style.color}")
