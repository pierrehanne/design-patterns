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

use std::collections::HashMap;
use std::fmt;

// --- Memento ---

/// GameSave is the memento: an immutable snapshot of the character's state.
/// All fields are private to the module; only GameCharacter can create one.
#[derive(Debug, Clone)]
struct GameSave {
    health: i32,
    level: u32,
    position_x: f64,
    position_y: f64,
    inventory: Vec<String>, // owned snapshot
    timestamp: String,
    label: String,
}

impl fmt::Display for GameSave {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "[{}] '{}' -- HP:{} Lv:{} Pos:({},{}) Items:{:?}",
            self.timestamp, self.label, self.health, self.level,
            self.position_x, self.position_y, self.inventory
        )
    }
}

// --- Originator ---

/// GameCharacter is the originator whose state we want to save and restore.
struct GameCharacter {
    name: String,
    health: i32,
    level: u32,
    position_x: f64,
    position_y: f64,
    inventory: Vec<String>,
}

impl GameCharacter {
    fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            health: 100,
            level: 1,
            position_x: 0.0,
            position_y: 0.0,
            inventory: Vec::new(),
        }
    }

    fn take_damage(&mut self, amount: i32) {
        self.health = (self.health - amount).max(0);
        println!("  {} took {} damage. HP: {}", self.name, amount, self.health);
    }

    fn level_up(&mut self) {
        self.level += 1;
        self.health = 100; // full heal on level up
        println!("  {} leveled up to Lv.{}! HP restored.", self.name, self.level);
    }

    fn move_to(&mut self, x: f64, y: f64) {
        self.position_x = x;
        self.position_y = y;
        println!("  {} moved to ({}, {})", self.name, x, y);
    }

    fn pick_up(&mut self, item: &str) {
        self.inventory.push(item.to_string());
        println!("  {} picked up '{}'", self.name, item);
    }

    // --- Memento creation and restoration ---

    /// Create a memento capturing the current state.
    fn save(&self, label: &str) -> GameSave {
        let memento = GameSave {
            health: self.health,
            level: self.level,
            position_x: self.position_x,
            position_y: self.position_y,
            inventory: self.inventory.clone(), // snapshot copy
            timestamp: chrono_placeholder(),
            label: label.to_string(),
        };
        println!("  >> State saved: '{}'", label);
        memento
    }

    /// Restore state from a memento.
    fn restore(&mut self, memento: &GameSave) {
        self.health = memento.health;
        self.level = memento.level;
        self.position_x = memento.position_x;
        self.position_y = memento.position_y;
        self.inventory = memento.inventory.clone(); // restore from snapshot
        println!("  >> State restored from '{}'", memento.label);
    }

    fn status(&self) -> String {
        format!(
            "  {}: HP={} Lv={} Pos=({},{}) Inventory={:?}",
            self.name, self.health, self.level,
            self.position_x, self.position_y, self.inventory
        )
    }
}

/// Simple timestamp placeholder (avoids external crate dependency).
fn chrono_placeholder() -> String {
    // In production, use the `chrono` crate for real timestamps.
    "2026-04-07 12:00:00".to_string()
}

// --- Caretaker ---

/// SaveManager is the caretaker: it stores mementos without inspecting them.
struct SaveManager {
    saves: HashMap<String, GameSave>,
    /// Insertion order tracking (HashMap doesn't preserve order)
    order: Vec<String>,
}

impl SaveManager {
    fn new() -> Self {
        Self {
            saves: HashMap::new(),
            order: Vec::new(),
        }
    }

    fn store(&mut self, key: &str, save: GameSave) {
        if !self.saves.contains_key(key) {
            self.order.push(key.to_string());
        }
        self.saves.insert(key.to_string(), save);
    }

    fn load(&self, key: &str) -> Option<&GameSave> {
        let save = self.saves.get(key);
        if save.is_none() {
            println!("  >> No save found for slot '{}'", key);
        }
        save
    }

    fn list_saves(&self) {
        if self.saves.is_empty() {
            println!("  No saves stored.");
            return;
        }
        println!("  Stored saves:");
        for key in &self.order {
            if let Some(save) = self.saves.get(key) {
                println!("    [{}] {}", key, save);
            }
        }
    }
}

// --- Main ---

fn main() {
    let mut hero = GameCharacter::new("Warrior");
    let mut manager = SaveManager::new();

    println!("=== Starting the adventure ===");
    println!("{}", hero.status());
    println!();

    // Play through some actions
    hero.move_to(10.0, 20.0);
    hero.pick_up("Iron Sword");
    hero.level_up();
    println!("{}", hero.status());
    println!();

    // Save at checkpoint 1
    let checkpoint1 = hero.save("Before the dungeon");
    manager.store("checkpoint1", checkpoint1);
    println!();

    // Enter the dungeon -- things go badly
    hero.move_to(50.0, 80.0);
    hero.take_damage(60);
    hero.pick_up("Rusty Key");
    hero.take_damage(30);
    println!("{}", hero.status());
    println!();

    // Save the risky state too
    let checkpoint2 = hero.save("Deep in dungeon (low HP)");
    manager.store("checkpoint2", checkpoint2);
    println!();

    // Even worse...
    hero.take_damage(50);
    println!("{}", hero.status());
    println!();

    // List all saves
    println!("=== Reviewing saves ===");
    manager.list_saves();
    println!();

    // Restore to the safe checkpoint
    println!("=== Restoring to checkpoint 1 ===");
    if let Some(save) = manager.load("checkpoint1") {
        hero.restore(save);
    }
    println!("{}", hero.status());
}
