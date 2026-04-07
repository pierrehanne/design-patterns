// Composite Pattern
// =================
// Category: Structural Design Pattern
//
// Intent:
//   Compose objects into tree structures to represent part-whole hierarchies.
//   Clients treat individual objects (leaves) and compositions (branches) uniformly.
//
// When to use:
//   - Tree/hierarchical structures (files/folders, org charts, UI components)
//   - When clients should treat single objects and groups the same way
//   - When operations should propagate recursively through the tree
//
// Key Participants:
//   - Component (interface): Common interface for leaves and composites
//   - Leaf: End node (File)
//   - Composite: Node with children (Directory)

package main

import (
	"fmt"
	"strings"
)

// ---------------------------------------------------------------------------
// Component — common interface
// ---------------------------------------------------------------------------

type FileSystemEntry interface {
	Name() string
	Size() int
	Display(indent int) string
	Search(keyword string) []string
}

// ---------------------------------------------------------------------------
// Leaf — a file (no children)
// ---------------------------------------------------------------------------

type File struct {
	name      string
	sizeBytes int
}

func NewFile(name string, size int) *File {
	return &File{name: name, sizeBytes: size}
}

func (f *File) Name() string { return f.name }
func (f *File) Size() int    { return f.sizeBytes }

func (f *File) Display(indent int) string {
	prefix := strings.Repeat("  ", indent)
	return fmt.Sprintf("%sF %s (%d bytes)", prefix, f.name, f.sizeBytes)
}

func (f *File) Search(keyword string) []string {
	if strings.Contains(strings.ToLower(f.name), strings.ToLower(keyword)) {
		return []string{f.name}
	}
	return nil
}

// ---------------------------------------------------------------------------
// Composite — a directory (has children)
// ---------------------------------------------------------------------------

type Directory struct {
	name     string
	children []FileSystemEntry
}

func NewDirectory(name string) *Directory {
	return &Directory{name: name}
}

func (d *Directory) Name() string { return d.name }

func (d *Directory) Add(entries ...FileSystemEntry) *Directory {
	d.children = append(d.children, entries...)
	return d
}

// Size recursively sums all children — uniform treatment
func (d *Directory) Size() int {
	total := 0
	for _, child := range d.children {
		total += child.Size()
	}
	return total
}

func (d *Directory) Display(indent int) string {
	prefix := strings.Repeat("  ", indent)
	lines := []string{fmt.Sprintf("%sD %s/ (%d bytes)", prefix, d.name, d.Size())}
	for _, child := range d.children {
		lines = append(lines, child.Display(indent+1))
	}
	return strings.Join(lines, "\n")
}

func (d *Directory) Search(keyword string) []string {
	var results []string
	if strings.Contains(strings.ToLower(d.name), strings.ToLower(keyword)) {
		results = append(results, d.name+"/")
	}
	for _, child := range d.children {
		results = append(results, child.Search(keyword)...)
	}
	return results
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	src := NewDirectory("src")
	src.Add(NewFile("main.go", 2048), NewFile("utils.go", 1024), NewFile("config.go", 512))

	tests := NewDirectory("tests")
	tests.Add(NewFile("test_main.go", 1536), NewFile("test_utils.go", 768))

	docs := NewDirectory("docs")
	docs.Add(NewFile("README.md", 4096), NewFile("CHANGELOG.md", 2048))

	root := NewDirectory("project")
	root.Add(src, tests, docs, NewFile(".gitignore", 128))

	fmt.Println(root.Display(0))
	fmt.Printf("\nTotal project size: %d bytes\n", root.Size())
	fmt.Printf("Source code size: %d bytes\n", src.Size())
	fmt.Printf("\nSearch for 'test': %v\n", root.Search("test"))
	fmt.Printf("Search for 'main': %v\n", root.Search("main"))
}
