//! State Pattern
//! =================
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!     Allow an object to alter its behavior when its internal state changes.
//!     The object will appear to change its class.
//!
//! When to use:
//!     - When an object's behavior depends on its state and it must change
//!       behavior at runtime depending on that state.
//!     - When you want to eliminate large conditional statements that select
//!       behavior based on the current state.
//!     - When transitions between states need to be explicit and controlled.
//!
//! Key Participants:
//!     - State (interface): DocumentState -- declares methods that all concrete
//!       states must implement.
//!     - ConcreteState: Draft, UnderReview, Published, Archived --
//!       each implements behavior appropriate for that state of the context.
//!     - Context: Document -- maintains a reference to the current state
//!       and delegates behavior to it.

// ---------------------------------------------------------------------------
// State enum -- idiomatic Rust uses enums instead of trait objects for a
// closed set of states. Each variant carries no data here, but could.
// ---------------------------------------------------------------------------
#[derive(Debug, Clone, PartialEq)]
enum DocumentState {
    Draft,
    UnderReview,
    Published,
    Archived,
}

impl DocumentState {
    fn name(&self) -> &str {
        match self {
            Self::Draft => "Draft",
            Self::UnderReview => "Under Review",
            Self::Published => "Published",
            Self::Archived => "Archived",
        }
    }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

/// A document that moves through a workflow of states.
struct Document {
    title: String,
    state: DocumentState,
}

impl Document {
    fn new(title: &str) -> Self {
        Self {
            title: title.to_string(),
            state: DocumentState::Draft,
        }
    }

    /// Transition to a new state, printing the change.
    fn set_state(&mut self, new_state: DocumentState) {
        let old = self.state.name().to_string();
        self.state = new_state;
        println!(
            "  >> Document '{}': {} -> {}",
            self.title,
            old,
            self.state.name()
        );
    }

    fn edit(&mut self) {
        println!(
            "\nDocument '{}' [{}]: edit()",
            self.title,
            self.state.name()
        );
        match self.state {
            DocumentState::Draft => {
                println!("  [Draft] Editing document content.");
            }
            DocumentState::UnderReview => {
                println!("  [Review] Sending document back to Draft for edits.");
                self.set_state(DocumentState::Draft);
            }
            DocumentState::Published => {
                println!("  [Published] ERROR: Cannot edit a published document. Archive it first.");
            }
            DocumentState::Archived => {
                println!("  [Archived] Un-archiving and moving to Draft for editing.");
                self.set_state(DocumentState::Draft);
            }
        }
    }

    fn submit(&mut self) {
        println!(
            "\nDocument '{}' [{}]: submit()",
            self.title,
            self.state.name()
        );
        match self.state {
            DocumentState::Draft => {
                println!("  [Draft] Submitting document for review.");
                self.set_state(DocumentState::UnderReview);
            }
            DocumentState::UnderReview => {
                println!("  [Review] ERROR: Document is already under review.");
            }
            DocumentState::Published => {
                println!("  [Published] ERROR: Document is already published.");
            }
            DocumentState::Archived => {
                println!("  [Archived] ERROR: Cannot submit an archived document. Edit it first.");
            }
        }
    }

    fn publish(&mut self) {
        println!(
            "\nDocument '{}' [{}]: publish()",
            self.title,
            self.state.name()
        );
        match self.state {
            DocumentState::Draft => {
                println!("  [Draft] ERROR: Cannot publish directly from Draft. Submit for review first.");
            }
            DocumentState::UnderReview => {
                println!("  [Review] Review approved. Publishing document.");
                self.set_state(DocumentState::Published);
            }
            DocumentState::Published => {
                println!("  [Published] ERROR: Document is already published.");
            }
            DocumentState::Archived => {
                println!("  [Archived] ERROR: Cannot publish an archived document. Edit it first.");
            }
        }
    }

    fn archive(&mut self) {
        println!(
            "\nDocument '{}' [{}]: archive()",
            self.title,
            self.state.name()
        );
        match self.state {
            DocumentState::Draft => {
                println!("  [Draft] Archiving draft document.");
                self.set_state(DocumentState::Archived);
            }
            DocumentState::UnderReview => {
                println!("  [Review] ERROR: Cannot archive while under review. Publish or reject first.");
            }
            DocumentState::Published => {
                println!("  [Published] Archiving published document.");
                self.set_state(DocumentState::Archived);
            }
            DocumentState::Archived => {
                println!("  [Archived] ERROR: Document is already archived.");
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------
fn main() {
    let mut doc = Document::new("Design Patterns Guide");

    // Normal workflow: Draft -> Review -> Published -> Archived
    doc.edit();       // OK: editing in draft
    doc.publish();    // ERROR: can't publish from draft
    doc.submit();     // OK: moves to Review
    doc.publish();    // OK: moves to Published
    doc.edit();       // ERROR: can't edit published doc
    doc.archive();    // OK: moves to Archived

    // Recover from archived: un-archive by editing
    doc.edit();       // OK: moves back to Draft
    doc.submit();     // OK: moves to Review
    doc.edit();       // OK: rejected, back to Draft
    doc.submit();     // OK: back to Review
    doc.publish();    // OK: Published again
}
