/**
 * Template Method Pattern
 * ========================
 * Category: Behavioral Design Pattern
 *
 * Intent:
 *   Define the skeleton of an algorithm in a base class, deferring some steps
 *   to subclasses. Template Method lets subclasses redefine certain steps of
 *   an algorithm without changing the algorithm's structure.
 *
 * When to use:
 *   - You want to implement the invariant parts of an algorithm once and let
 *     subclasses provide the behavior that varies
 *   - Common behavior among subclasses should be factored and localized in a
 *     single class to avoid duplication
 *   - You want to control which steps subclasses can extend (hooks vs. required)
 *
 * Key Participants:
 *   - AbstractClass (DataMiner): defines the template method and abstract steps
 *   - ConcreteClass (CSVMiner, JSONMiner, DatabaseMiner): implements the steps
 *   - Template Method (mine): the algorithm skeleton that calls the steps in order
 *
 * Hollywood Principle:
 *   "Don't call us, we'll call you." -- The base class calls the subclass methods,
 *   not the other way around. Subclasses plug into the algorithm; they don't drive it.
 */

// --- Abstract Class ---

/**
 * DataMiner defines the template method `mine()`.
 * The algorithm skeleton is fixed; subclasses override individual steps.
 */
abstract class DataMiner {
  /**
   * Template method: defines the algorithm skeleton.
   * This method should NOT be overridden by subclasses.
   */
  mine(source: string): void {
    console.log(`\n${"=".repeat(60)}`);
    console.log(`  Mining data from: ${source}`);
    console.log("=".repeat(60));

    const rawData = this.readData(source);
    const parsed = this.parseData(rawData);

    // Hook: optional pre-analysis step (subclasses may override)
    this.beforeAnalysis(parsed);

    const results = this.analyzeData(parsed);
    this.generateReport(results);

    // Hook: optional cleanup step
    this.cleanup();

    console.log("  Pipeline complete.\n");
  }

  // --- Abstract steps (subclasses MUST implement) ---

  /** Read raw data from the source. */
  protected abstract readData(source: string): string;

  /** Parse raw data into structured records. */
  protected abstract parseData(rawData: string): Record<string, string | number>[];

  /** Analyze parsed data and produce results. */
  protected abstract analyzeData(data: Record<string, string | number>[]): Record<string, unknown>;

  /** Generate a report from the analysis results. */
  protected abstract generateReport(results: Record<string, unknown>): void;

  // --- Hook methods (subclasses CAN override, but don't have to) ---

  /** Hook: called before analysis. Override to add pre-processing. */
  protected beforeAnalysis(_data: Record<string, string | number>[]): void {
    // Default: do nothing
  }

  /** Hook: called after the pipeline. Override to release resources. */
  protected cleanup(): void {
    // Default: do nothing
  }
}

// --- Concrete Classes ---

/** Mines data from CSV files. */
class CSVMiner extends DataMiner {
  protected readData(source: string): string {
    console.log(`  [CSV] Reading file: ${source}`);
    // Simulated CSV content
    return "name,age,city\nAlice,30,Paris\nBob,25,London\nCharlie,35,Berlin";
  }

  protected parseData(rawData: string): Record<string, string>[] {
    console.log("  [CSV] Parsing CSV rows...");
    const lines = rawData.trim().split("\n");
    const headers = lines[0].split(",");
    const records = lines.slice(1).map((line) => {
      const values = line.split(",");
      const record: Record<string, string> = {};
      headers.forEach((h, i) => (record[h] = values[i]));
      return record;
    });
    console.log(`  [CSV] Parsed ${records.length} records`);
    return records;
  }

  protected analyzeData(data: Record<string, string>[]): Record<string, number> {
    console.log("  [CSV] Analyzing age distribution...");
    const ages = data.map((r) => parseInt(r.age, 10));
    return {
      count: ages.length,
      average_age: ages.reduce((a, b) => a + b, 0) / ages.length,
      min_age: Math.min(...ages),
      max_age: Math.max(...ages),
    };
  }

  protected generateReport(results: Record<string, number>): void {
    console.log("  [CSV] Report:");
    for (const [key, value] of Object.entries(results)) {
      console.log(`    ${key}: ${value}`);
    }
  }
}

/** Mines data from JSON sources. */
class JSONMiner extends DataMiner {
  protected readData(source: string): string {
    console.log(`  [JSON] Fetching JSON from: ${source}`);
    return '[{"product":"Widget","price":9.99},{"product":"Gadget","price":24.99},{"product":"Doohickey","price":4.99}]';
  }

  protected parseData(rawData: string): Record<string, string | number>[] {
    console.log("  [JSON] Parsing JSON array...");
    const records = JSON.parse(rawData) as Record<string, string | number>[];
    console.log(`  [JSON] Parsed ${records.length} records`);
    return records;
  }

  protected analyzeData(data: Record<string, string | number>[]): Record<string, number> {
    console.log("  [JSON] Analyzing price data...");
    const prices = data.map((r) => r.price as number);
    return {
      total_products: prices.length,
      total_revenue_potential: prices.reduce((a, b) => a + b, 0),
      cheapest: Math.min(...prices),
      most_expensive: Math.max(...prices),
    };
  }

  protected generateReport(results: Record<string, number>): void {
    console.log("  [JSON] Report:");
    for (const [key, value] of Object.entries(results)) {
      console.log(`    ${key}: ${value}`);
    }
  }

  // Override hook: validate JSON structure before analysis
  protected beforeAnalysis(data: Record<string, string | number>[]): void {
    console.log("  [JSON] Validating schema: all records have 'product' and 'price'...");
    for (const record of data) {
      if (!("product" in record) || !("price" in record)) {
        throw new Error(`Invalid record: ${JSON.stringify(record)}`);
      }
    }
    console.log("  [JSON] Schema validation passed.");
  }
}

/** Mines data from a database connection. */
class DatabaseMiner extends DataMiner {
  private connectionOpen = false;

  protected readData(source: string): string {
    console.log(`  [DB] Connecting to database: ${source}`);
    this.connectionOpen = true;
    console.log("  [DB] Executing query: SELECT * FROM users");
    return "id:1,name:Alice,role:admin|id:2,name:Bob,role:user|id:3,name:Charlie,role:user";
  }

  protected parseData(rawData: string): Record<string, string>[] {
    console.log("  [DB] Parsing query results...");
    const records = rawData.split("|").map((row) => {
      const record: Record<string, string> = {};
      row.split(",").forEach((field) => {
        const [key, value] = field.split(":");
        record[key] = value;
      });
      return record;
    });
    console.log(`  [DB] Parsed ${records.length} records`);
    return records;
  }

  protected analyzeData(data: Record<string, string>[]): Record<string, unknown> {
    console.log("  [DB] Analyzing user roles...");
    const roles: Record<string, number> = {};
    for (const record of data) {
      roles[record.role] = (roles[record.role] || 0) + 1;
    }
    return { total_users: data.length, role_distribution: roles };
  }

  protected generateReport(results: Record<string, unknown>): void {
    console.log("  [DB] Report:");
    console.log(`    Total users: ${results.total_users}`);
    const dist = results.role_distribution as Record<string, number>;
    for (const [role, count] of Object.entries(dist)) {
      console.log(`    ${role}: ${count}`);
    }
  }

  // Override hook: close the database connection
  protected cleanup(): void {
    if (this.connectionOpen) {
      console.log("  [DB] Closing database connection...");
      this.connectionOpen = false;
    }
  }
}

// --- Main ---

function main(): void {
  // Each miner follows the same algorithm (mine), but the steps differ.
  // The base class controls the flow -- Hollywood Principle in action.

  const pipelines: [DataMiner, string][] = [
    [new CSVMiner(), "users.csv"],
    [new JSONMiner(), "https://api.example.com/products"],
    [new DatabaseMiner(), "postgres://localhost:5432/mydb"],
  ];

  for (const [miner, source] of pipelines) {
    miner.mine(source);
  }
}

main();
