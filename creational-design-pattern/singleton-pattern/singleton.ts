/**
 * Singleton Pattern
 * =================
 * Category: Creational Design Pattern
 *
 * Intent:
 *   Ensure a class has only ONE instance and provide a global point of access to it.
 *
 * When to use:
 *   - Database connection pools, configuration managers, logging services
 *   - When exactly one object is needed to coordinate actions across the system
 *   - When creating multiple instances would cause conflicts or waste resources
 *
 * Key Participants:
 *   - Singleton: The class that controls its own instantiation and provides
 *     a static method to retrieve the unique instance.
 *
 * TypeScript approach:
 *   We use a private constructor so `new ConfigurationManager()` is impossible
 *   from outside. The only way to get an instance is through `getInstance()`.
 */

class ConfigurationManager {
  // The single instance, lazily created on first access
  private static instance: ConfigurationManager | null = null;

  private settings: Map<string, string> = new Map();

  // Private constructor prevents direct instantiation with `new`
  private constructor() {
    console.log(
      "[ConfigurationManager] Initialized (this should appear only once)"
    );
  }

  /**
   * The global access point. Creates the instance on first call,
   * returns the existing one on all subsequent calls.
   */
  static getInstance(): ConfigurationManager {
    if (!ConfigurationManager.instance) {
      ConfigurationManager.instance = new ConfigurationManager();
    }
    return ConfigurationManager.instance;
  }

  set(key: string, value: string): void {
    this.settings.set(key, value);
  }

  get(key: string, defaultValue: string = ""): string {
    return this.settings.get(key) ?? defaultValue;
  }

  all(): Record<string, string> {
    return Object.fromEntries(this.settings);
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------

const configA = ConfigurationManager.getInstance();
const configB = ConfigurationManager.getInstance();

configA.set("database_url", "postgres://localhost:5432/mydb");
configA.set("log_level", "DEBUG");

// configB sees the same data because it IS the same object
console.log(`configB database_url: ${configB.get("database_url")}`);
console.log(`Same instance? ${configA === configB}`); // true
console.log("All settings:", configB.all());
