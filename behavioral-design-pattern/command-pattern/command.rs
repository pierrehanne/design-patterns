//! Command Pattern
//! ===============
//! Category: Behavioral Design Pattern
//!
//! Intent:
//!   Encapsulate a request as an object, supporting undo/redo,
//!   queuing, and decoupling invoker from receiver.
//!
//! Key Participants:
//!   - Command (trait): Declares execute() and undo()
//!   - ConcreteCommand: Binds a receiver to an action
//!   - Receiver: The object that does the work (TextDocument)
//!   - Invoker: Manages history (TextEditor)

use std::cell::RefCell;
use std::rc::Rc;

// ---------------------------------------------------------------------------
// Receiver
// ---------------------------------------------------------------------------
struct TextDocument {
    content: String,
}

impl TextDocument {
    fn new() -> Self {
        Self { content: String::new() }
    }

    fn insert(&mut self, position: usize, text: &str) {
        self.content.insert_str(position, text);
    }

    fn delete(&mut self, position: usize, length: usize) -> String {
        let deleted: String = self.content[position..position + length].to_string();
        self.content = format!(
            "{}{}",
            &self.content[..position],
            &self.content[position + length..]
        );
        deleted
    }
}

impl std::fmt::Display for TextDocument {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "\"{}\"", self.content)
    }
}

// Shared reference to the document so multiple commands can access it
type DocRef = Rc<RefCell<TextDocument>>;

// ---------------------------------------------------------------------------
// Command trait
// ---------------------------------------------------------------------------
trait Command {
    fn execute(&mut self);
    fn undo(&mut self);
    fn description(&self) -> String;
}

// ---------------------------------------------------------------------------
// Concrete Commands
// ---------------------------------------------------------------------------
struct InsertCommand {
    doc: DocRef,
    position: usize,
    text: String,
}

impl InsertCommand {
    fn new(doc: DocRef, position: usize, text: &str) -> Self {
        Self { doc, position, text: text.to_string() }
    }
}

impl Command for InsertCommand {
    fn execute(&mut self) {
        self.doc.borrow_mut().insert(self.position, &self.text);
    }
    fn undo(&mut self) {
        self.doc.borrow_mut().delete(self.position, self.text.len());
    }
    fn description(&self) -> String {
        format!("Insert \"{}\" at {}", self.text, self.position)
    }
}

struct DeleteCommand {
    doc: DocRef,
    position: usize,
    length: usize,
    deleted_text: String,
}

impl DeleteCommand {
    fn new(doc: DocRef, position: usize, length: usize) -> Self {
        Self { doc, position, length, deleted_text: String::new() }
    }
}

impl Command for DeleteCommand {
    fn execute(&mut self) {
        self.deleted_text = self.doc.borrow_mut().delete(self.position, self.length);
    }
    fn undo(&mut self) {
        self.doc.borrow_mut().insert(self.position, &self.deleted_text);
    }
    fn description(&self) -> String {
        format!("Delete {} chars at {}", self.length, self.position)
    }
}

struct ReplaceCommand {
    doc: DocRef,
    position: usize,
    length: usize,
    new_text: String,
    old_text: String,
}

impl ReplaceCommand {
    fn new(doc: DocRef, position: usize, length: usize, new_text: &str) -> Self {
        Self { doc, position, length, new_text: new_text.to_string(), old_text: String::new() }
    }
}

impl Command for ReplaceCommand {
    fn execute(&mut self) {
        self.old_text = self.doc.borrow_mut().delete(self.position, self.length);
        self.doc.borrow_mut().insert(self.position, &self.new_text);
    }
    fn undo(&mut self) {
        self.doc.borrow_mut().delete(self.position, self.new_text.len());
        self.doc.borrow_mut().insert(self.position, &self.old_text);
    }
    fn description(&self) -> String {
        format!("Replace {} chars at {} with \"{}\"", self.length, self.position, self.new_text)
    }
}

// ---------------------------------------------------------------------------
// Invoker
// ---------------------------------------------------------------------------
struct TextEditor {
    doc: DocRef,
    history: Vec<Box<dyn Command>>,
    redo_stack: Vec<Box<dyn Command>>,
}

impl TextEditor {
    fn new(doc: DocRef) -> Self {
        Self { doc, history: Vec::new(), redo_stack: Vec::new() }
    }

    fn execute(&mut self, mut cmd: Box<dyn Command>) {
        cmd.execute();
        let desc = cmd.description();
        self.history.push(cmd);
        self.redo_stack.clear();
        println!("  [Execute] {} -> {}", desc, self.doc.borrow());
    }

    fn undo(&mut self) {
        if let Some(mut cmd) = self.history.pop() {
            cmd.undo();
            let desc = cmd.description();
            self.redo_stack.push(cmd);
            println!("  [Undo] {} -> {}", desc, self.doc.borrow());
        } else {
            println!("  [Undo] Nothing to undo");
        }
    }

    fn redo(&mut self) {
        if let Some(mut cmd) = self.redo_stack.pop() {
            cmd.execute();
            let desc = cmd.description();
            self.history.push(cmd);
            println!("  [Redo] {} -> {}", desc, self.doc.borrow());
        } else {
            println!("  [Redo] Nothing to redo");
        }
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let doc = Rc::new(RefCell::new(TextDocument::new()));
    let mut editor = TextEditor::new(doc.clone());

    println!("=== Building a document ===");
    editor.execute(Box::new(InsertCommand::new(doc.clone(), 0, "Hello World")));
    editor.execute(Box::new(InsertCommand::new(doc.clone(), 5, ",")));
    let len = doc.borrow().content.len();
    editor.execute(Box::new(InsertCommand::new(doc.clone(), len, "!")));
    editor.execute(Box::new(ReplaceCommand::new(doc.clone(), 7, 5, "Rust")));

    println!("\n=== Undo operations ===");
    editor.undo();
    editor.undo();

    println!("\n=== Redo ===");
    editor.redo();

    println!("\n=== Delete and undo ===");
    editor.execute(Box::new(DeleteCommand::new(doc.clone(), 0, 5)));
    editor.undo();
}
