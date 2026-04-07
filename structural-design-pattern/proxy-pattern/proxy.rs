//! Proxy Pattern
//! =============
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Provide a surrogate or placeholder for another object to control access.
//!   The proxy has the same trait as the real object.
//!
//! When to use:
//!   - Caching Proxy: Avoid redundant expensive operations
//!   - Virtual Proxy: Lazy-load heavy resources
//!   - Protection Proxy: Access control based on permissions
//!
//! Key Participants:
//!   - Subject (trait): Common interface for Real and Proxy
//!   - RealSubject: The actual object
//!   - Proxy: Controls access, same trait as RealSubject

use std::collections::HashMap;
use std::cell::RefCell;

// ---------------------------------------------------------------------------
// Subject trait
// ---------------------------------------------------------------------------
trait WeatherService {
    fn get_forecast(&self, city: &str) -> String;
    fn get_temperature(&self, city: &str) -> f64;
}

// ---------------------------------------------------------------------------
// Real Subject — expensive external API
// ---------------------------------------------------------------------------
struct RealWeatherService {
    call_count: RefCell<u32>,
}

impl RealWeatherService {
    fn new() -> Self {
        Self {
            call_count: RefCell::new(0),
        }
    }

    fn calls(&self) -> u32 {
        *self.call_count.borrow()
    }
}

impl WeatherService for RealWeatherService {
    fn get_forecast(&self, city: &str) -> String {
        *self.call_count.borrow_mut() += 1;
        println!(
            "    [RealService] API call #{} — fetching forecast for {}",
            self.calls(),
            city
        );
        format!("{}: Partly Cloudy, High 72, Low 58, Humidity 45%", city)
    }

    fn get_temperature(&self, city: &str) -> f64 {
        *self.call_count.borrow_mut() += 1;
        println!(
            "    [RealService] API call #{} — fetching temperature for {}",
            self.calls(),
            city
        );
        68.5
    }
}

// ---------------------------------------------------------------------------
// Caching Proxy
// ---------------------------------------------------------------------------
struct CachingWeatherProxy<'a> {
    service: &'a dyn WeatherService,
    cache: RefCell<HashMap<String, String>>,
    temp_cache: RefCell<HashMap<String, f64>>,
}

impl<'a> CachingWeatherProxy<'a> {
    fn new(service: &'a dyn WeatherService) -> Self {
        Self {
            service,
            cache: RefCell::new(HashMap::new()),
            temp_cache: RefCell::new(HashMap::new()),
        }
    }
}

impl<'a> WeatherService for CachingWeatherProxy<'a> {
    fn get_forecast(&self, city: &str) -> String {
        let key = format!("forecast:{}", city);
        if let Some(cached) = self.cache.borrow().get(&key) {
            println!("    [Cache HIT] {}", key);
            return cached.clone();
        }
        println!("    [Cache MISS] {}", key);
        let result = self.service.get_forecast(city);
        self.cache.borrow_mut().insert(key, result.clone());
        result
    }

    fn get_temperature(&self, city: &str) -> f64 {
        let key = format!("temp:{}", city);
        if let Some(&cached) = self.temp_cache.borrow().get(&key) {
            println!("    [Cache HIT] {}", key);
            return cached;
        }
        println!("    [Cache MISS] {}", key);
        let result = self.service.get_temperature(city);
        self.temp_cache.borrow_mut().insert(key, result);
        result
    }
}

// ---------------------------------------------------------------------------
// Access Control Proxy
// ---------------------------------------------------------------------------
struct AccessControlWeatherProxy<'a> {
    service: &'a dyn WeatherService,
    api_key: String,
}

impl<'a> AccessControlWeatherProxy<'a> {
    fn new(service: &'a dyn WeatherService, api_key: &str) -> Self {
        Self {
            service,
            api_key: api_key.to_string(),
        }
    }

    fn check_access(&self) -> Result<(), String> {
        let valid_keys = ["key-alice-123", "key-bob-456"];
        if valid_keys.contains(&self.api_key.as_str()) {
            Ok(())
        } else {
            Err(format!("Access denied: invalid API key '{}'", self.api_key))
        }
    }
}

impl<'a> WeatherService for AccessControlWeatherProxy<'a> {
    fn get_forecast(&self, city: &str) -> String {
        if let Err(e) = self.check_access() {
            return e;
        }
        self.service.get_forecast(city)
    }

    fn get_temperature(&self, city: &str) -> f64 {
        if let Err(e) = self.check_access() {
            eprintln!("{}", e);
            return f64::NAN;
        }
        self.service.get_temperature(city)
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let real = RealWeatherService::new();

    println!("=== Caching Proxy ===");
    let cached = CachingWeatherProxy::new(&real);

    println!("\nFirst request:");
    println!("  Result: {}", cached.get_forecast("New York"));

    println!("\nSecond request (same city):");
    println!("  Result: {}", cached.get_forecast("New York"));

    println!("\nDifferent city:");
    println!("  Result: {}", cached.get_forecast("London"));

    println!("\nReal service was called {} times (not 3)", real.calls());

    println!("\n=== Access Control Proxy ===");
    let real2 = RealWeatherService::new();

    println!("\nValid API key:");
    let auth = AccessControlWeatherProxy::new(&real2, "key-alice-123");
    println!("  Temperature: {}", auth.get_temperature("Paris"));

    println!("\nInvalid API key:");
    let bad = AccessControlWeatherProxy::new(&real2, "key-hacker-999");
    let temp = bad.get_temperature("Paris");
    if temp.is_nan() {
        println!("  Access was denied");
    }
}
