//! Singleton Pattern
//! =================
//! Category: Creational Design Pattern
//!
//! Intent:
//!   Ensure a class has only ONE instance and provide a global point of access to it.
//!
//! When to use:
//!   - Database connection pools, configuration managers, logging services
//!   - When exactly one object is needed to coordinate actions across the system
//!
//! Key Participants:
//!   - Singleton: A globally accessible, lazily initialized, thread-safe instance.
//!
//! Rust approach:
//!   Rust doesn't have classes, so we use `std::sync::OnceLock` (stable since 1.80)
//!   combined with a `Mutex` for interior mutability. This guarantees:
//!   - Lazy initialization (created on first access)
//!   - Thread safety (Mutex guards concurrent writes)
//!   - Single instance (OnceLock initializes exactly once)

use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};

/// The configuration data held by our singleton.
struct ConfigurationManager {
    settings: HashMap<String, String>,
}

impl ConfigurationManager {
    fn new() -> Self {
        println!("[ConfigurationManager] Initialized (this should appear only once)");
        Self {
            settings: HashMap::new(),
        }
    }

    fn set(&mut self, key: &str, value: &str) {
        self.settings.insert(key.to_string(), value.to_string());
    }

    fn get(&self, key: &str) -> Option<&String> {
        self.settings.get(key)
    }

    fn all(&self) -> &HashMap<String, String> {
        &self.settings
    }
}

/// Global access point. `OnceLock` ensures the Mutex<ConfigurationManager>
/// is created exactly once, even across multiple threads.
fn config() -> &'static Mutex<ConfigurationManager> {
    static INSTANCE: OnceLock<Mutex<ConfigurationManager>> = OnceLock::new();
    INSTANCE.get_or_init(|| Mutex::new(ConfigurationManager::new()))
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    // First access — triggers initialization
    {
        let mut cfg = config().lock().unwrap();
        cfg.set("database_url", "postgres://localhost:5432/mydb");
        cfg.set("log_level", "DEBUG");
    } // MutexGuard is dropped here, releasing the lock

    // Second access — same instance, sees the data we just wrote
    {
        let cfg = config().lock().unwrap();
        println!(
            "database_url: {}",
            cfg.get("database_url").unwrap_or(&String::new())
        );
        println!("All settings: {:?}", cfg.all());
    }

    // Verify identity: both pointers reference the same Mutex
    let ptr1 = config() as *const Mutex<ConfigurationManager>;
    let ptr2 = config() as *const Mutex<ConfigurationManager>;
    println!("Same instance? {}", ptr1 == ptr2); // true
}
