/**
 * Composite Pattern
 * =================
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Compose objects into tree structures to represent part-whole hierarchies.
 *   Clients treat individual objects (leaves) and compositions (branches) uniformly.
 *
 * When to use:
 *   - Tree/hierarchical structures (files/folders, org charts, UI components)
 *   - When clients should treat single objects and groups the same way
 *   - When operations should propagate recursively through the tree
 *
 * Key Participants:
 *   - Component (interface): Common interface for leaves and composites
 *   - Leaf: End node with no children
 *   - Composite: Node that contains children
 */

// ---------------------------------------------------------------------------
// Component — common interface
// ---------------------------------------------------------------------------
interface FileSystemEntry {
  name: string;
  size(): number;
  display(indent?: number): string;
  search(keyword: string): string[];
}

// ---------------------------------------------------------------------------
// Leaf — a file (no children)
// ---------------------------------------------------------------------------
class File implements FileSystemEntry {
  constructor(public name: string, private sizeBytes: number) {}

  size(): number {
    return this.sizeBytes;
  }

  display(indent: number = 0): string {
    const prefix = "  ".repeat(indent);
    return `${prefix}F ${this.name} (${this.sizeBytes} bytes)`;
  }

  search(keyword: string): string[] {
    return this.name.toLowerCase().includes(keyword.toLowerCase())
      ? [this.name]
      : [];
  }
}

// ---------------------------------------------------------------------------
// Composite — a directory (has children)
// ---------------------------------------------------------------------------
class Directory implements FileSystemEntry {
  private children: FileSystemEntry[] = [];

  constructor(public name: string) {}

  add(entry: FileSystemEntry): this {
    this.children.push(entry);
    return this;
  }

  remove(name: string): void {
    this.children = this.children.filter((c) => c.name !== name);
  }

  size(): number {
    // Recursively sums all children — uniform treatment
    return this.children.reduce((sum, child) => sum + child.size(), 0);
  }

  display(indent: number = 0): string {
    const prefix = "  ".repeat(indent);
    const lines = [`${prefix}D ${this.name}/ (${this.size()} bytes)`];
    for (const child of this.children) {
      lines.push(child.display(indent + 1));
    }
    return lines.join("\n");
  }

  search(keyword: string): string[] {
    const results: string[] = [];
    if (this.name.toLowerCase().includes(keyword.toLowerCase())) {
      results.push(this.name + "/");
    }
    for (const child of this.children) {
      results.push(...child.search(keyword));
    }
    return results;
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const root = new Directory("project");

const src = new Directory("src");
src.add(new File("main.ts", 2048));
src.add(new File("utils.ts", 1024));
src.add(new File("config.ts", 512));

const tests = new Directory("tests");
tests.add(new File("test_main.ts", 1536));
tests.add(new File("test_utils.ts", 768));

const docs = new Directory("docs");
docs.add(new File("README.md", 4096));
docs.add(new File("CHANGELOG.md", 2048));

root.add(src).add(tests).add(docs).add(new File(".gitignore", 128));

console.log(root.display());
console.log(`\nTotal project size: ${root.size()} bytes`);
console.log(`Source code size: ${src.size()} bytes`);
console.log(`\nSearch for 'test': ${root.search("test")}`);
console.log(`Search for 'main': ${root.search("main")}`);
