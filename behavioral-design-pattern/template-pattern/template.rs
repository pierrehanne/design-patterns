// Template Method Pattern
// ========================
// Category: Behavioral Design Pattern
//
// Intent:
//   Define the skeleton of an algorithm in a base class, deferring some steps
//   to subclasses. Template Method lets subclasses redefine certain steps of
//   an algorithm without changing the algorithm's structure.
//
// When to use:
//   - You want to implement the invariant parts of an algorithm once and let
//     subclasses provide the behavior that varies
//   - Common behavior among subclasses should be factored and localized in a
//     single class to avoid duplication
//   - You want to control which steps subclasses can extend (hooks vs. required)
//
// Key Participants:
//   - AbstractClass (DataMiner trait): defines the template method and abstract steps
//   - ConcreteClass (CSVMiner, JSONMiner, DatabaseMiner): implements the steps
//   - Template Method (mine): the algorithm skeleton that calls the steps in order
//
// Hollywood Principle:
//   "Don't call us, we'll call you." -- The trait's default method calls the
//   implementor's methods, not the other way around.
//
// Note: Rust uses traits with default methods to achieve the Template Method pattern.
// Required methods = abstract steps. Default methods = hooks and the template itself.

use std::collections::HashMap;

// --- Record type for parsed data ---

type Record = HashMap<String, String>;

// --- Abstract Class (Trait) ---

/// DataMiner defines the template method `mine()` and the steps of the algorithm.
/// Required methods must be implemented; default methods serve as hooks.
trait DataMiner {
    /// Template method: defines the algorithm skeleton.
    /// Implementors should NOT override this.
    fn mine(&mut self, source: &str) {
        println!("\n{}", "=".repeat(60));
        println!("  Mining data from: {}", source);
        println!("{}", "=".repeat(60));

        let raw_data = self.read_data(source);
        let parsed = self.parse_data(&raw_data);

        // Hook: optional pre-analysis step
        self.before_analysis(&parsed);

        let results = self.analyze_data(&parsed);
        self.generate_report(&results);

        // Hook: optional cleanup step
        self.cleanup();

        println!("  Pipeline complete.\n");
    }

    // --- Required steps (implementors MUST provide) ---

    fn read_data(&mut self, source: &str) -> String;
    fn parse_data(&self, raw_data: &str) -> Vec<Record>;
    fn analyze_data(&self, data: &[Record]) -> HashMap<String, String>;
    fn generate_report(&self, results: &HashMap<String, String>);

    // --- Hook methods (implementors CAN override) ---

    /// Hook: called before analysis. Override to add pre-processing.
    fn before_analysis(&self, _data: &[Record]) {
        // Default: do nothing
    }

    /// Hook: called after the pipeline. Override to release resources.
    fn cleanup(&mut self) {
        // Default: do nothing
    }
}

// --- Concrete Classes ---

/// Mines data from CSV files.
struct CSVMiner;

impl DataMiner for CSVMiner {
    fn read_data(&mut self, source: &str) -> String {
        println!("  [CSV] Reading file: {}", source);
        "name,age,city\nAlice,30,Paris\nBob,25,London\nCharlie,35,Berlin".to_string()
    }

    fn parse_data(&self, raw_data: &str) -> Vec<Record> {
        println!("  [CSV] Parsing CSV rows...");
        let mut lines = raw_data.lines();
        let headers: Vec<&str> = lines.next().unwrap().split(',').collect();

        let records: Vec<Record> = lines
            .map(|line| {
                let values: Vec<&str> = line.split(',').collect();
                headers
                    .iter()
                    .zip(values.iter())
                    .map(|(h, v)| (h.to_string(), v.to_string()))
                    .collect()
            })
            .collect();

        println!("  [CSV] Parsed {} records", records.len());
        records
    }

    fn analyze_data(&self, data: &[Record]) -> HashMap<String, String> {
        println!("  [CSV] Analyzing age distribution...");
        let ages: Vec<i32> = data
            .iter()
            .map(|r| r["age"].parse::<i32>().unwrap())
            .collect();

        let count = ages.len();
        let avg = ages.iter().sum::<i32>() as f64 / count as f64;
        let min = ages.iter().min().unwrap();
        let max = ages.iter().max().unwrap();

        let mut results = HashMap::new();
        results.insert("count".into(), count.to_string());
        results.insert("average_age".into(), format!("{:.1}", avg));
        results.insert("min_age".into(), min.to_string());
        results.insert("max_age".into(), max.to_string());
        results
    }

    fn generate_report(&self, results: &HashMap<String, String>) {
        println!("  [CSV] Report:");
        // Print in a deterministic order
        for key in &["count", "average_age", "min_age", "max_age"] {
            if let Some(val) = results.get(*key) {
                println!("    {}: {}", key, val);
            }
        }
    }
}

/// Mines data from JSON sources.
struct JSONMiner;

impl DataMiner for JSONMiner {
    fn read_data(&mut self, source: &str) -> String {
        println!("  [JSON] Fetching JSON from: {}", source);
        // Simulated JSON -- we parse it manually to avoid external dependencies
        r#"product:Widget,price:9.99|product:Gadget,price:24.99|product:Doohickey,price:4.99"#.to_string()
    }

    fn parse_data(&self, raw_data: &str) -> Vec<Record> {
        println!("  [JSON] Parsing JSON array...");
        let records: Vec<Record> = raw_data
            .split('|')
            .map(|entry| {
                entry
                    .split(',')
                    .map(|field| {
                        let mut parts = field.splitn(2, ':');
                        let key = parts.next().unwrap().to_string();
                        let val = parts.next().unwrap().to_string();
                        (key, val)
                    })
                    .collect()
            })
            .collect();
        println!("  [JSON] Parsed {} records", records.len());
        records
    }

    fn analyze_data(&self, data: &[Record]) -> HashMap<String, String> {
        println!("  [JSON] Analyzing price data...");
        let prices: Vec<f64> = data
            .iter()
            .map(|r| r["price"].parse::<f64>().unwrap())
            .collect();

        let total: f64 = prices.iter().sum();
        let min = prices.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = prices.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

        let mut results = HashMap::new();
        results.insert("total_products".into(), prices.len().to_string());
        results.insert("total_revenue_potential".into(), format!("{:.2}", total));
        results.insert("cheapest".into(), format!("{:.2}", min));
        results.insert("most_expensive".into(), format!("{:.2}", max));
        results
    }

    fn generate_report(&self, results: &HashMap<String, String>) {
        println!("  [JSON] Report:");
        for key in &["total_products", "total_revenue_potential", "cheapest", "most_expensive"] {
            if let Some(val) = results.get(*key) {
                println!("    {}: {}", key, val);
            }
        }
    }

    // Override hook: validate structure before analysis
    fn before_analysis(&self, data: &[Record]) {
        println!("  [JSON] Validating schema: all records have 'product' and 'price'...");
        for record in data {
            assert!(
                record.contains_key("product") && record.contains_key("price"),
                "Invalid record: {:?}",
                record
            );
        }
        println!("  [JSON] Schema validation passed.");
    }
}

/// Mines data from a database connection.
struct DatabaseMiner {
    connection_open: bool,
}

impl DatabaseMiner {
    fn new() -> Self {
        Self {
            connection_open: false,
        }
    }
}

impl DataMiner for DatabaseMiner {
    fn read_data(&mut self, source: &str) -> String {
        println!("  [DB] Connecting to database: {}", source);
        self.connection_open = true;
        println!("  [DB] Executing query: SELECT * FROM users");
        "id:1,name:Alice,role:admin|id:2,name:Bob,role:user|id:3,name:Charlie,role:user".to_string()
    }

    fn parse_data(&self, raw_data: &str) -> Vec<Record> {
        println!("  [DB] Parsing query results...");
        let records: Vec<Record> = raw_data
            .split('|')
            .map(|row| {
                row.split(',')
                    .map(|field| {
                        let mut parts = field.splitn(2, ':');
                        let key = parts.next().unwrap().to_string();
                        let val = parts.next().unwrap().to_string();
                        (key, val)
                    })
                    .collect()
            })
            .collect();
        println!("  [DB] Parsed {} records", records.len());
        records
    }

    fn analyze_data(&self, data: &[Record]) -> HashMap<String, String> {
        println!("  [DB] Analyzing user roles...");
        let mut roles: HashMap<String, usize> = HashMap::new();
        for record in data {
            *roles.entry(record["role"].clone()).or_insert(0) += 1;
        }

        let mut results = HashMap::new();
        results.insert("total_users".into(), data.len().to_string());
        // Serialize role distribution
        let dist: Vec<String> = roles.iter().map(|(k, v)| format!("{}={}", k, v)).collect();
        results.insert("role_distribution".into(), dist.join(", "));
        results
    }

    fn generate_report(&self, results: &HashMap<String, String>) {
        println!("  [DB] Report:");
        if let Some(total) = results.get("total_users") {
            println!("    Total users: {}", total);
        }
        if let Some(dist) = results.get("role_distribution") {
            println!("    Roles: {}", dist);
        }
    }

    // Override hook: close the database connection
    fn cleanup(&mut self) {
        if self.connection_open {
            println!("  [DB] Closing database connection...");
            self.connection_open = false;
        }
    }
}

// --- Main ---

fn main() {
    // Each miner follows the same algorithm (mine), but the steps differ.
    // The trait's default method controls the flow -- Hollywood Principle in action.

    let mut csv_miner = CSVMiner;
    csv_miner.mine("users.csv");

    let mut json_miner = JSONMiner;
    json_miner.mine("https://api.example.com/products");

    let mut db_miner = DatabaseMiner::new();
    db_miner.mine("postgres://localhost:5432/mydb");
}
