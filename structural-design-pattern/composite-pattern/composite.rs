//! Composite Pattern
//! =================
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Compose objects into tree structures to represent part-whole hierarchies.
//!   Clients treat individual objects (leaves) and compositions (branches) uniformly.
//!
//! When to use:
//!   - Tree/hierarchical structures (files/folders, org charts, UI components)
//!   - When clients should treat single objects and groups the same way
//!
//! Key Participants:
//!   - Component (enum or trait): Common interface
//!   - Leaf: End node
//!   - Composite: Node with children
//!
//! Rust approach:
//!   We use an enum rather than trait objects. Enums are idiomatic for closed
//!   hierarchies and avoid the complexity of trait object lifetimes.

// ---------------------------------------------------------------------------
// Component — an enum that can be either a File (leaf) or Directory (composite)
// ---------------------------------------------------------------------------
enum FileSystemEntry {
    File {
        name: String,
        size_bytes: u64,
    },
    Directory {
        name: String,
        children: Vec<FileSystemEntry>,
    },
}

impl FileSystemEntry {
    fn name(&self) -> &str {
        match self {
            FileSystemEntry::File { name, .. } => name,
            FileSystemEntry::Directory { name, .. } => name,
        }
    }

    /// Returns total size in bytes — recursively sums for directories.
    fn size(&self) -> u64 {
        match self {
            FileSystemEntry::File { size_bytes, .. } => *size_bytes,
            FileSystemEntry::Directory { children, .. } => {
                children.iter().map(|c| c.size()).sum()
            }
        }
    }

    /// Tree-like string representation.
    fn display(&self, indent: usize) -> String {
        let prefix = "  ".repeat(indent);
        match self {
            FileSystemEntry::File { name, size_bytes } => {
                format!("{}F {} ({} bytes)", prefix, name, size_bytes)
            }
            FileSystemEntry::Directory { name, children } => {
                let mut lines = vec![format!("{}D {}/ ({} bytes)", prefix, name, self.size())];
                for child in children {
                    lines.push(child.display(indent + 1));
                }
                lines.join("\n")
            }
        }
    }

    /// Search for entries whose name contains the keyword.
    fn search(&self, keyword: &str) -> Vec<String> {
        let kw = keyword.to_lowercase();
        match self {
            FileSystemEntry::File { name, .. } => {
                if name.to_lowercase().contains(&kw) {
                    vec![name.clone()]
                } else {
                    vec![]
                }
            }
            FileSystemEntry::Directory { name, children } => {
                let mut results = Vec::new();
                if name.to_lowercase().contains(&kw) {
                    results.push(format!("{}/", name));
                }
                for child in children {
                    results.extend(child.search(keyword));
                }
                results
            }
        }
    }
}

// Convenience constructors
fn file(name: &str, size: u64) -> FileSystemEntry {
    FileSystemEntry::File {
        name: name.to_string(),
        size_bytes: size,
    }
}

fn dir(name: &str, children: Vec<FileSystemEntry>) -> FileSystemEntry {
    FileSystemEntry::Directory {
        name: name.to_string(),
        children,
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let root = dir("project", vec![
        dir("src", vec![
            file("main.rs", 2048),
            file("utils.rs", 1024),
            file("config.rs", 512),
        ]),
        dir("tests", vec![
            file("test_main.rs", 1536),
            file("test_utils.rs", 768),
        ]),
        dir("docs", vec![
            file("README.md", 4096),
            file("CHANGELOG.md", 2048),
        ]),
        file(".gitignore", 128),
    ]);

    println!("{}", root.display(0));
    println!("\nTotal project size: {} bytes", root.size());
    println!("\nSearch for 'test': {:?}", root.search("test"));
    println!("Search for 'main': {:?}", root.search("main"));
}
