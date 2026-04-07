/**
 * Memento Pattern
 * ================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Without violating encapsulation, capture and externalize an object's
 *   internal state so that the object can be restored to this state later.
 *
 * When to use:
 *   - You need to save and restore snapshots of an object's state
 *   - A direct interface to obtaining the state would expose implementation
 *     details and break encapsulation
 *   - You need undo/rollback functionality
 *
 * Key Participants:
 *   - Originator (GameCharacter): the object whose state needs saving;
 *     creates a memento containing a snapshot of its current internal state
 *   - Memento (GameSave): stores the originator's internal state;
 *     protects against access by objects other than the originator
 *   - Caretaker (SaveManager): responsible for keeping the memento safe;
 *     never operates on or examines the contents of a memento
 */

// --- Memento ---

/**
 * GameSave is the memento: an immutable snapshot of the character's state.
 * We use Readonly<> to prevent external mutation.
 */
interface GameSaveData {
  readonly health: number;
  readonly level: number;
  readonly positionX: number;
  readonly positionY: number;
  readonly inventory: readonly string[]; // immutable copy
  readonly timestamp: string;
  readonly label: string;
}

class GameSave implements GameSaveData {
  readonly health: number;
  readonly level: number;
  readonly positionX: number;
  readonly positionY: number;
  readonly inventory: readonly string[];
  readonly timestamp: string;
  readonly label: string;

  constructor(data: GameSaveData) {
    this.health = data.health;
    this.level = data.level;
    this.positionX = data.positionX;
    this.positionY = data.positionY;
    this.inventory = Object.freeze([...data.inventory]); // deep-freeze the copy
    this.timestamp = data.timestamp;
    this.label = data.label;
  }

  toString(): string {
    return (
      `[${this.timestamp}] '${this.label}' -- ` +
      `HP:${this.health} Lv:${this.level} ` +
      `Pos:(${this.positionX},${this.positionY}) ` +
      `Items:[${this.inventory.join(", ")}]`
    );
  }
}

// --- Originator ---

/**
 * GameCharacter is the originator whose state we want to save and restore.
 * Only the character itself knows how to create and restore from a memento.
 */
class GameCharacter {
  health = 100;
  level = 1;
  positionX = 0;
  positionY = 0;
  inventory: string[] = [];

  constructor(public readonly name: string) {}

  takeDamage(amount: number): void {
    this.health = Math.max(0, this.health - amount);
    console.log(`  ${this.name} took ${amount} damage. HP: ${this.health}`);
  }

  levelUp(): void {
    this.level += 1;
    this.health = 100; // full heal on level up
    console.log(`  ${this.name} leveled up to Lv.${this.level}! HP restored.`);
  }

  moveTo(x: number, y: number): void {
    this.positionX = x;
    this.positionY = y;
    console.log(`  ${this.name} moved to (${x}, ${y})`);
  }

  pickUp(item: string): void {
    this.inventory.push(item);
    console.log(`  ${this.name} picked up '${item}'`);
  }

  // --- Memento creation and restoration ---

  /** Create a memento capturing the current state. */
  save(label: string): GameSave {
    const memento = new GameSave({
      health: this.health,
      level: this.level,
      positionX: this.positionX,
      positionY: this.positionY,
      inventory: [...this.inventory], // snapshot copy
      timestamp: new Date().toISOString().replace("T", " ").slice(0, 19),
      label,
    });
    console.log(`  >> State saved: '${label}'`);
    return memento;
  }

  /** Restore state from a memento. */
  restore(memento: GameSave): void {
    this.health = memento.health;
    this.level = memento.level;
    this.positionX = memento.positionX;
    this.positionY = memento.positionY;
    this.inventory = [...memento.inventory]; // mutable copy from frozen array
    console.log(`  >> State restored from '${memento.label}'`);
  }

  status(): string {
    return (
      `  ${this.name}: HP=${this.health} Lv=${this.level} ` +
      `Pos=(${this.positionX},${this.positionY}) ` +
      `Inventory=[${this.inventory.join(", ")}]`
    );
  }
}

// --- Caretaker ---

/**
 * SaveManager is the caretaker: it manages saves without knowing their internals.
 * It never inspects or modifies the memento's state.
 */
class SaveManager {
  private saves = new Map<string, GameSave>();

  store(key: string, save: GameSave): void {
    this.saves.set(key, save);
  }

  load(key: string): GameSave | undefined {
    const save = this.saves.get(key);
    if (!save) {
      console.log(`  >> No save found for slot '${key}'`);
    }
    return save;
  }

  listSaves(): void {
    if (this.saves.size === 0) {
      console.log("  No saves stored.");
      return;
    }
    console.log("  Stored saves:");
    for (const [key, save] of this.saves) {
      console.log(`    [${key}] ${save.toString()}`);
    }
  }
}

// --- Main ---

function main(): void {
  const hero = new GameCharacter("Warrior");
  const manager = new SaveManager();

  console.log("=== Starting the adventure ===");
  console.log(hero.status());
  console.log();

  // Play through some actions
  hero.moveTo(10, 20);
  hero.pickUp("Iron Sword");
  hero.levelUp();
  console.log(hero.status());
  console.log();

  // Save at checkpoint 1
  const checkpoint1 = hero.save("Before the dungeon");
  manager.store("checkpoint1", checkpoint1);
  console.log();

  // Enter the dungeon -- things go badly
  hero.moveTo(50, 80);
  hero.takeDamage(60);
  hero.pickUp("Rusty Key");
  hero.takeDamage(30);
  console.log(hero.status());
  console.log();

  // Save the risky state too
  const checkpoint2 = hero.save("Deep in dungeon (low HP)");
  manager.store("checkpoint2", checkpoint2);
  console.log();

  // Even worse...
  hero.takeDamage(50);
  console.log(hero.status());
  console.log();

  // List all saves
  console.log("=== Reviewing saves ===");
  manager.listSaves();
  console.log();

  // Restore to the safe checkpoint
  console.log("=== Restoring to checkpoint 1 ===");
  const save = manager.load("checkpoint1");
  if (save) {
    hero.restore(save);
  }
  console.log(hero.status());
}

main();
