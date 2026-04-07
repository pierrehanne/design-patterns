/**
 * Prototype Pattern
 * =================
 * Category: Creational Design Pattern
 *
 * Intent:
 *   Create new objects by cloning an existing instance (the prototype) rather
 *   than building from scratch. Useful when object creation is expensive or
 *   when you want copies with slight variations.
 *
 * When to use:
 *   - When creating an object is expensive (DB queries, complex computation)
 *   - When you need many similar objects with small differences
 *   - When object configuration is complex and you'd rather copy-and-tweak
 *
 * Key Participants:
 *   - Prototype (interface): Declares the clone method
 *   - ConcretePrototype: Implements clone by deep-copying its own state
 *   - Client: Creates new objects by cloning prototypes
 *
 * Deep Copy in TypeScript:
 *   structuredClone() (available since Node 17+) handles deep copying natively.
 *   For older environments, JSON.parse(JSON.stringify()) works for plain objects.
 */

// ---------------------------------------------------------------------------
// Prototype Interface
// ---------------------------------------------------------------------------
interface Cloneable<T> {
  clone(): T;
}

// ---------------------------------------------------------------------------
// Nested object to demonstrate deep copy
// ---------------------------------------------------------------------------
interface DocumentStyle {
  font: string;
  fontSize: number;
  color: string;
  lineSpacing: number;
}

// ---------------------------------------------------------------------------
// Concrete Prototype — Document Template
// ---------------------------------------------------------------------------
class DocumentTemplate implements Cloneable<DocumentTemplate> {
  constructor(
    public title: string,
    public style: DocumentStyle,
    public sections: string[] = [],
    public metadata: Record<string, string> = {}
  ) {}

  /**
   * Deep clone using structuredClone (Node 17+ / modern browsers).
   * Creates a fully independent copy — nested objects are NOT shared.
   */
  clone(): DocumentTemplate {
    return new DocumentTemplate(
      this.title,
      structuredClone(this.style),
      [...this.sections],
      { ...this.metadata }
    );
  }

  toString(): string {
    const sections =
      this.sections.length > 0 ? this.sections.join(", ") : "(none)";
    const meta =
      Object.entries(this.metadata)
        .map(([k, v]) => `${k}=${v}`)
        .join(", ") || "(none)";
    return [
      `Document: '${this.title}'`,
      `  Style: ${this.style.font} ${this.style.fontSize}pt ${this.style.color}`,
      `  Sections: ${sections}`,
      `  Metadata: ${meta}`,
    ].join("\n");
  }
}

// ---------------------------------------------------------------------------
// Prototype Registry — stores named prototypes for easy access
// ---------------------------------------------------------------------------
class TemplateRegistry {
  private templates = new Map<string, DocumentTemplate>();

  register(name: string, template: DocumentTemplate): void {
    this.templates.set(name, template);
  }

  /** Clone a registered prototype. Throws if not found. */
  create(name: string): DocumentTemplate {
    const proto = this.templates.get(name);
    if (!proto) {
      throw new Error(`No template registered as '${name}'`);
    }
    return proto.clone();
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const registry = new TemplateRegistry();

// Register pre-configured prototypes
registry.register(
  "report",
  new DocumentTemplate(
    "Quarterly Report",
    { font: "Times New Roman", fontSize: 11, color: "#333333", lineSpacing: 1.5 },
    ["Executive Summary", "Financials", "Outlook"],
    { author: "Template", department: "Finance" }
  )
);

registry.register(
  "memo",
  new DocumentTemplate(
    "Internal Memo",
    { font: "Helvetica", fontSize: 10, color: "#000000", lineSpacing: 1.15 },
    ["Subject", "Body", "Action Items"],
    { classification: "internal" }
  )
);

// Clone and customize — much cheaper than building from scratch
const q1Report = registry.create("report");
q1Report.title = "Q1 2025 Report";
q1Report.metadata.author = "Alice";
q1Report.sections.push("Risk Assessment");

const q2Report = registry.create("report");
q2Report.title = "Q2 2025 Report";
q2Report.metadata.author = "Bob";

const teamMemo = registry.create("memo");
teamMemo.title = "Engineering All-Hands Notes";
teamMemo.metadata.author = "Charlie";

console.log("=== Q1 Report (cloned + customized) ===");
console.log(q1Report.toString());
console.log("\n=== Q2 Report (cloned + customized) ===");
console.log(q2Report.toString());
console.log("\n=== Team Memo (cloned from memo template) ===");
console.log(teamMemo.toString());

// Verify deep copy: original template is unmodified
const original = registry.create("report");
console.log("\n=== Fresh clone (proves original is untouched) ===");
console.log(original.toString());
