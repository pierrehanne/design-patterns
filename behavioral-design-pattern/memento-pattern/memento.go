// Memento Pattern
// ================
// Category: Behavioral Design Pattern
//
// Intent:
//   Without violating encapsulation, capture and externalize an object's
//   internal state so that the object can be restored to this state later.
//
// When to use:
//   - You need to save and restore snapshots of an object's state
//   - A direct interface to obtaining the state would expose implementation
//     details and break encapsulation
//   - You need undo/rollback functionality
//
// Key Participants:
//   - Originator (GameCharacter): the object whose state needs saving;
//     creates a memento containing a snapshot of its current internal state
//   - Memento (GameSave): stores the originator's internal state;
//     protects against access by objects other than the originator
//   - Caretaker (SaveManager): responsible for keeping the memento safe;
//     never operates on or examines the contents of a memento

package main

import (
	"fmt"
	"strings"
	"time"
)

// --- Memento ---

// GameSave is the memento: a snapshot of the character's state.
// Fields are unexported (lowercase) to protect encapsulation in a real project.
// Here they are exported for demonstration clarity.
type GameSave struct {
	Health    int
	Level     int
	PositionX float64
	PositionY float64
	Inventory []string // snapshot copy
	Timestamp string
	Label     string
}

func (s *GameSave) String() string {
	return fmt.Sprintf("[%s] '%s' -- HP:%d Lv:%d Pos:(%.0f,%.0f) Items:[%s]",
		s.Timestamp, s.Label, s.Health, s.Level,
		s.PositionX, s.PositionY, strings.Join(s.Inventory, ", "))
}

// --- Originator ---

// GameCharacter is the originator whose state we want to save and restore.
type GameCharacter struct {
	Name      string
	Health    int
	Level     int
	PositionX float64
	PositionY float64
	Inventory []string
}

func NewGameCharacter(name string) *GameCharacter {
	return &GameCharacter{
		Name:      name,
		Health:    100,
		Level:     1,
		Inventory: []string{},
	}
}

func (c *GameCharacter) TakeDamage(amount int) {
	c.Health -= amount
	if c.Health < 0 {
		c.Health = 0
	}
	fmt.Printf("  %s took %d damage. HP: %d\n", c.Name, amount, c.Health)
}

func (c *GameCharacter) LevelUp() {
	c.Level++
	c.Health = 100 // full heal on level up
	fmt.Printf("  %s leveled up to Lv.%d! HP restored.\n", c.Name, c.Level)
}

func (c *GameCharacter) MoveTo(x, y float64) {
	c.PositionX = x
	c.PositionY = y
	fmt.Printf("  %s moved to (%.0f, %.0f)\n", c.Name, x, y)
}

func (c *GameCharacter) PickUp(item string) {
	c.Inventory = append(c.Inventory, item)
	fmt.Printf("  %s picked up '%s'\n", c.Name, item)
}

// Save creates a memento capturing the current state.
func (c *GameCharacter) Save(label string) *GameSave {
	// Make a snapshot copy of the inventory slice
	invCopy := make([]string, len(c.Inventory))
	copy(invCopy, c.Inventory)

	memento := &GameSave{
		Health:    c.Health,
		Level:     c.Level,
		PositionX: c.PositionX,
		PositionY: c.PositionY,
		Inventory: invCopy,
		Timestamp: time.Now().Format("2006-01-02 15:04:05"),
		Label:     label,
	}
	fmt.Printf("  >> State saved: '%s'\n", label)
	return memento
}

// Restore restores state from a memento.
func (c *GameCharacter) Restore(memento *GameSave) {
	c.Health = memento.Health
	c.Level = memento.Level
	c.PositionX = memento.PositionX
	c.PositionY = memento.PositionY

	// Restore inventory from the snapshot
	c.Inventory = make([]string, len(memento.Inventory))
	copy(c.Inventory, memento.Inventory)

	fmt.Printf("  >> State restored from '%s'\n", memento.Label)
}

func (c *GameCharacter) Status() string {
	return fmt.Sprintf("  %s: HP=%d Lv=%d Pos=(%.0f,%.0f) Inventory=[%s]",
		c.Name, c.Health, c.Level, c.PositionX, c.PositionY,
		strings.Join(c.Inventory, ", "))
}

// --- Caretaker ---

// SaveManager is the caretaker: it stores saves without inspecting their contents.
type SaveManager struct {
	saves map[string]*GameSave
	order []string // preserve insertion order
}

func NewSaveManager() *SaveManager {
	return &SaveManager{
		saves: make(map[string]*GameSave),
		order: []string{},
	}
}

func (m *SaveManager) Store(key string, save *GameSave) {
	if _, exists := m.saves[key]; !exists {
		m.order = append(m.order, key)
	}
	m.saves[key] = save
}

func (m *SaveManager) Load(key string) *GameSave {
	save, ok := m.saves[key]
	if !ok {
		fmt.Printf("  >> No save found for slot '%s'\n", key)
		return nil
	}
	return save
}

func (m *SaveManager) ListSaves() {
	if len(m.saves) == 0 {
		fmt.Println("  No saves stored.")
		return
	}
	fmt.Println("  Stored saves:")
	for _, key := range m.order {
		if save, ok := m.saves[key]; ok {
			fmt.Printf("    [%s] %s\n", key, save)
		}
	}
}

// --- Main ---

func main() {
	hero := NewGameCharacter("Warrior")
	manager := NewSaveManager()

	fmt.Println("=== Starting the adventure ===")
	fmt.Println(hero.Status())
	fmt.Println()

	// Play through some actions
	hero.MoveTo(10, 20)
	hero.PickUp("Iron Sword")
	hero.LevelUp()
	fmt.Println(hero.Status())
	fmt.Println()

	// Save at checkpoint 1
	checkpoint1 := hero.Save("Before the dungeon")
	manager.Store("checkpoint1", checkpoint1)
	fmt.Println()

	// Enter the dungeon -- things go badly
	hero.MoveTo(50, 80)
	hero.TakeDamage(60)
	hero.PickUp("Rusty Key")
	hero.TakeDamage(30)
	fmt.Println(hero.Status())
	fmt.Println()

	// Save the risky state too
	checkpoint2 := hero.Save("Deep in dungeon (low HP)")
	manager.Store("checkpoint2", checkpoint2)
	_ = checkpoint2 // used via manager
	fmt.Println()

	// Even worse...
	hero.TakeDamage(50)
	fmt.Println(hero.Status())
	fmt.Println()

	// List all saves
	fmt.Println("=== Reviewing saves ===")
	manager.ListSaves()
	fmt.Println()

	// Restore to the safe checkpoint
	fmt.Println("=== Restoring to checkpoint 1 ===")
	if save := manager.Load("checkpoint1"); save != nil {
		hero.Restore(save)
	}
	fmt.Println(hero.Status())
}
