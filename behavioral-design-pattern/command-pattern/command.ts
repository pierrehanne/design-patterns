/**
 * Command Pattern
 * ===============
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Encapsulate a request as an object, supporting undo/redo,
 *   queuing, logging, and decoupling invoker from receiver.
 *
 * Key Participants:
 *   - Command (interface): Declares execute() and undo()
 *   - ConcreteCommand: Binds a receiver to an action
 *   - Receiver: The object that does the actual work (TextDocument)
 *   - Invoker: Manages command execution and history (TextEditor)
 */

// ---------------------------------------------------------------------------
// Receiver
// ---------------------------------------------------------------------------
class TextDocument {
  content = "";

  insert(position: number, text: string): void {
    this.content =
      this.content.slice(0, position) + text + this.content.slice(position);
  }

  delete(position: number, length: number): string {
    const deleted = this.content.slice(position, position + length);
    this.content =
      this.content.slice(0, position) + this.content.slice(position + length);
    return deleted;
  }

  toString(): string {
    return `"${this.content}"`;
  }
}

// ---------------------------------------------------------------------------
// Command interface
// ---------------------------------------------------------------------------
interface Command {
  execute(): void;
  undo(): void;
  description(): string;
}

// ---------------------------------------------------------------------------
// Concrete Commands
// ---------------------------------------------------------------------------
class InsertCommand implements Command {
  constructor(
    private doc: TextDocument,
    private position: number,
    private text: string
  ) {}

  execute(): void {
    this.doc.insert(this.position, this.text);
  }
  undo(): void {
    this.doc.delete(this.position, this.text.length);
  }
  description(): string {
    return `Insert "${this.text}" at ${this.position}`;
  }
}

class DeleteCommand implements Command {
  private deletedText = "";

  constructor(
    private doc: TextDocument,
    private position: number,
    private length: number
  ) {}

  execute(): void {
    this.deletedText = this.doc.delete(this.position, this.length);
  }
  undo(): void {
    this.doc.insert(this.position, this.deletedText);
  }
  description(): string {
    return `Delete ${this.length} chars at ${this.position}`;
  }
}

class ReplaceCommand implements Command {
  private oldText = "";

  constructor(
    private doc: TextDocument,
    private position: number,
    private length: number,
    private newText: string
  ) {}

  execute(): void {
    this.oldText = this.doc.delete(this.position, this.length);
    this.doc.insert(this.position, this.newText);
  }
  undo(): void {
    this.doc.delete(this.position, this.newText.length);
    this.doc.insert(this.position, this.oldText);
  }
  description(): string {
    return `Replace ${this.length} chars at ${this.position} with "${this.newText}"`;
  }
}

// ---------------------------------------------------------------------------
// Invoker — manages command history
// ---------------------------------------------------------------------------
class TextEditor {
  private history: Command[] = [];
  private redoStack: Command[] = [];

  constructor(private document: TextDocument) {}

  execute(command: Command): void {
    command.execute();
    this.history.push(command);
    this.redoStack.length = 0;
    console.log(`  [Execute] ${command.description()} -> ${this.document}`);
  }

  undo(): void {
    const cmd = this.history.pop();
    if (!cmd) { console.log("  [Undo] Nothing to undo"); return; }
    cmd.undo();
    this.redoStack.push(cmd);
    console.log(`  [Undo] ${cmd.description()} -> ${this.document}`);
  }

  redo(): void {
    const cmd = this.redoStack.pop();
    if (!cmd) { console.log("  [Redo] Nothing to redo"); return; }
    cmd.execute();
    this.history.push(cmd);
    console.log(`  [Redo] ${cmd.description()} -> ${this.document}`);
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const doc = new TextDocument();
const editor = new TextEditor(doc);

console.log("=== Building a document ===");
editor.execute(new InsertCommand(doc, 0, "Hello World"));
editor.execute(new InsertCommand(doc, 5, ","));
editor.execute(new InsertCommand(doc, doc.content.length, "!"));
editor.execute(new ReplaceCommand(doc, 7, 5, "TypeScript"));

console.log("\n=== Undo operations ===");
editor.undo();
editor.undo();

console.log("\n=== Redo operations ===");
editor.redo();

console.log("\n=== Delete and undo ===");
editor.execute(new DeleteCommand(doc, 0, 5));
editor.undo();
