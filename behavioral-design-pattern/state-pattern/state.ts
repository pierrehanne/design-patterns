/**
 * State Pattern
 * =================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Allow an object to alter its behavior when its internal state changes.
 *   The object will appear to change its class.
 *
 * When to use:
 *   - When an object's behavior depends on its state and it must change
 *     behavior at runtime depending on that state.
 *   - When you want to eliminate large conditional statements that select
 *     behavior based on the current state.
 *   - When transitions between states need to be explicit and controlled.
 *
 * Key Participants:
 *   - State (interface): DocumentState -- declares methods that all concrete
 *     states must implement.
 *   - ConcreteState: DraftState, ReviewState, PublishedState, ArchivedState --
 *     each implements behavior appropriate for that state of the context.
 *   - Context: Document -- maintains a reference to a ConcreteState subclass
 *     that defines the current state.
 */

// ---------------------------------------------------------------------------
// State interface
// ---------------------------------------------------------------------------
interface DocumentState {
  readonly name: string;
  edit(doc: WorkflowDocument): void;
  submit(doc: WorkflowDocument): void;
  publish(doc: WorkflowDocument): void;
  archive(doc: WorkflowDocument): void;
}

// ---------------------------------------------------------------------------
// Concrete states
// ---------------------------------------------------------------------------

class DraftState implements DocumentState {
  readonly name = "Draft";

  edit(doc: WorkflowDocument): void {
    console.log("  [Draft] Editing document content.");
  }

  submit(doc: WorkflowDocument): void {
    console.log("  [Draft] Submitting document for review.");
    doc.setState(new ReviewState());
  }

  publish(doc: WorkflowDocument): void {
    console.log(
      "  [Draft] ERROR: Cannot publish directly from Draft. Submit for review first.",
    );
  }

  archive(doc: WorkflowDocument): void {
    console.log("  [Draft] Archiving draft document.");
    doc.setState(new ArchivedState());
  }
}

class ReviewState implements DocumentState {
  readonly name = "Under Review";

  edit(doc: WorkflowDocument): void {
    console.log("  [Review] Sending document back to Draft for edits.");
    doc.setState(new DraftState());
  }

  submit(doc: WorkflowDocument): void {
    console.log("  [Review] ERROR: Document is already under review.");
  }

  publish(doc: WorkflowDocument): void {
    console.log("  [Review] Review approved. Publishing document.");
    doc.setState(new PublishedState());
  }

  archive(doc: WorkflowDocument): void {
    console.log(
      "  [Review] ERROR: Cannot archive while under review. Publish or reject first.",
    );
  }
}

class PublishedState implements DocumentState {
  readonly name = "Published";

  edit(doc: WorkflowDocument): void {
    console.log(
      "  [Published] ERROR: Cannot edit a published document. Archive it first.",
    );
  }

  submit(doc: WorkflowDocument): void {
    console.log("  [Published] ERROR: Document is already published.");
  }

  publish(doc: WorkflowDocument): void {
    console.log("  [Published] ERROR: Document is already published.");
  }

  archive(doc: WorkflowDocument): void {
    console.log("  [Published] Archiving published document.");
    doc.setState(new ArchivedState());
  }
}

class ArchivedState implements DocumentState {
  readonly name = "Archived";

  edit(doc: WorkflowDocument): void {
    console.log("  [Archived] Un-archiving and moving to Draft for editing.");
    doc.setState(new DraftState());
  }

  submit(doc: WorkflowDocument): void {
    console.log(
      "  [Archived] ERROR: Cannot submit an archived document. Edit it first.",
    );
  }

  publish(doc: WorkflowDocument): void {
    console.log(
      "  [Archived] ERROR: Cannot publish an archived document. Edit it first.",
    );
  }

  archive(doc: WorkflowDocument): void {
    console.log("  [Archived] ERROR: Document is already archived.");
  }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

class WorkflowDocument {
  private state: DocumentState;

  constructor(public readonly title: string) {
    this.state = new DraftState();
  }

  get stateName(): string {
    return this.state.name;
  }

  /** Transition to a new state (called by state objects). */
  setState(newState: DocumentState): void {
    const old = this.state.name;
    this.state = newState;
    console.log(
      `  >> Document '${this.title}': ${old} -> ${this.state.name}`,
    );
  }

  edit(): void {
    console.log(`\nDocument '${this.title}' [${this.stateName}]: edit()`);
    this.state.edit(this);
  }

  submit(): void {
    console.log(`\nDocument '${this.title}' [${this.stateName}]: submit()`);
    this.state.submit(this);
  }

  publish(): void {
    console.log(`\nDocument '${this.title}' [${this.stateName}]: publish()`);
    this.state.publish(this);
  }

  archive(): void {
    console.log(`\nDocument '${this.title}' [${this.stateName}]: archive()`);
    this.state.archive(this);
  }
}

// ---------------------------------------------------------------------------
// Runnable example
// ---------------------------------------------------------------------------

function main(): void {
  const doc = new WorkflowDocument("Design Patterns Guide");

  // Normal workflow: Draft -> Review -> Published -> Archived
  doc.edit(); // OK: editing in draft
  doc.publish(); // ERROR: can't publish from draft
  doc.submit(); // OK: moves to Review
  doc.publish(); // OK: moves to Published
  doc.edit(); // ERROR: can't edit published doc
  doc.archive(); // OK: moves to Archived

  // Recover from archived: un-archive by editing
  doc.edit(); // OK: moves back to Draft
  doc.submit(); // OK: moves to Review
  doc.edit(); // OK: rejected, back to Draft
  doc.submit(); // OK: back to Review
  doc.publish(); // OK: Published again
}

main();
