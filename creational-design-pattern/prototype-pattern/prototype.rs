//! Prototype Pattern
//! =================
//! Category: Creational Design Pattern
//!
//! Intent:
//!   Create new objects by cloning an existing instance rather than building
//!   from scratch. Useful when object creation is expensive or when you want
//!   copies with slight variations.
//!
//! When to use:
//!   - When creating an object is expensive (DB queries, complex computation)
//!   - When you need many similar objects with small differences
//!   - When object configuration is complex and you'd rather copy-and-tweak
//!
//! Key Participants:
//!   - Prototype: Implements Clone trait
//!   - Client: Creates new objects by calling .clone() on prototypes
//!
//! Rust approach:
//!   Rust has the Clone trait built into the language. Deriving Clone provides
//!   deep copy semantics for all fields that themselves implement Clone.
//!   This makes the Prototype pattern almost trivial in Rust.

use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Product types — derive Clone for deep copy support
// ---------------------------------------------------------------------------

/// Nested struct to demonstrate that Clone is deep (not shared references).
#[derive(Clone, Debug)]
struct DocumentStyle {
    font: String,
    font_size: u32,
    color: String,
    line_spacing: f64,
}

/// The prototype: a document template that can be cloned and customized.
/// Deriving Clone gives us deep copy of all fields including nested structs,
/// Vec, and HashMap.
#[derive(Clone, Debug)]
struct DocumentTemplate {
    title: String,
    style: DocumentStyle,
    sections: Vec<String>,
    metadata: HashMap<String, String>,
}

impl DocumentTemplate {
    fn new(
        title: &str,
        style: DocumentStyle,
        sections: Vec<&str>,
        metadata: Vec<(&str, &str)>,
    ) -> Self {
        Self {
            title: title.to_string(),
            style,
            sections: sections.into_iter().map(String::from).collect(),
            metadata: metadata
                .into_iter()
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect(),
        }
    }
}

impl std::fmt::Display for DocumentTemplate {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let sections = if self.sections.is_empty() {
            "(none)".to_string()
        } else {
            self.sections.join(", ")
        };
        let meta = if self.metadata.is_empty() {
            "(none)".to_string()
        } else {
            self.metadata
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect::<Vec<_>>()
                .join(", ")
        };
        write!(
            f,
            "Document: '{}'\n  Style: {} {}pt {}\n  Sections: {}\n  Metadata: {}",
            self.title, self.style.font, self.style.font_size, self.style.color, sections, meta
        )
    }
}

// ---------------------------------------------------------------------------
// Prototype Registry — stores named prototypes
// ---------------------------------------------------------------------------
struct TemplateRegistry {
    templates: HashMap<String, DocumentTemplate>,
}

impl TemplateRegistry {
    fn new() -> Self {
        Self {
            templates: HashMap::new(),
        }
    }

    fn register(&mut self, name: &str, template: DocumentTemplate) {
        self.templates.insert(name.to_string(), template);
    }

    /// Clone a registered prototype. Returns None if not found.
    fn create(&self, name: &str) -> Option<DocumentTemplate> {
        self.templates.get(name).cloned() // .cloned() calls Clone on the value
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let mut registry = TemplateRegistry::new();

    // Register pre-configured prototypes
    registry.register(
        "report",
        DocumentTemplate::new(
            "Quarterly Report",
            DocumentStyle {
                font: "Times New Roman".to_string(),
                font_size: 11,
                color: "#333333".to_string(),
                line_spacing: 1.5,
            },
            vec!["Executive Summary", "Financials", "Outlook"],
            vec![("author", "Template"), ("department", "Finance")],
        ),
    );

    registry.register(
        "memo",
        DocumentTemplate::new(
            "Internal Memo",
            DocumentStyle {
                font: "Helvetica".to_string(),
                font_size: 10,
                color: "#000000".to_string(),
                line_spacing: 1.15,
            },
            vec!["Subject", "Body", "Action Items"],
            vec![("classification", "internal")],
        ),
    );

    // Clone and customize
    let mut q1_report = registry.create("report").expect("report template not found");
    q1_report.title = "Q1 2025 Report".to_string();
    q1_report.metadata.insert("author".to_string(), "Alice".to_string());
    q1_report.sections.push("Risk Assessment".to_string());

    let mut q2_report = registry.create("report").expect("report template not found");
    q2_report.title = "Q2 2025 Report".to_string();
    q2_report.metadata.insert("author".to_string(), "Bob".to_string());

    let mut team_memo = registry.create("memo").expect("memo template not found");
    team_memo.title = "Engineering All-Hands Notes".to_string();
    team_memo.metadata.insert("author".to_string(), "Charlie".to_string());

    println!("=== Q1 Report (cloned + customized) ===");
    println!("{}\n", q1_report);
    println!("=== Q2 Report (cloned + customized) ===");
    println!("{}\n", q2_report);
    println!("=== Team Memo (cloned from memo template) ===");
    println!("{}\n", team_memo);

    // Verify deep copy: original template is unmodified
    let fresh = registry.create("report").unwrap();
    println!("=== Fresh clone (proves original is untouched) ===");
    println!("{}", fresh);
}
