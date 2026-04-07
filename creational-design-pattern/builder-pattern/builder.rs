//! Builder Pattern
//! ================
//! Category: Creational Design Pattern
//!
//! Intent:
//!   Separate the construction of a complex object from its representation,
//!   allowing step-by-step construction with a fluent, chainable API.
//!
//! When to use:
//!   - When a struct has many fields, some optional
//!   - When you want compile-time or runtime validation before creation
//!   - When you want readable, self-documenting construction code
//!
//! Key Participants:
//!   - Builder: Accumulates configuration via chained method calls
//!   - Product: The final immutable struct
//!
//! Rust note:
//!   The builder pattern is extremely common in Rust because the language
//!   has no default parameters or method overloading. Libraries like
//!   `reqwest`, `tokio`, and `clap` all use builders extensively.

use std::collections::HashMap;

// ---------------------------------------------------------------------------
// Product — immutable once built
// ---------------------------------------------------------------------------
#[derive(Debug)]
struct HttpRequest {
    method: String,
    url: String,
    headers: HashMap<String, String>,
    query_params: HashMap<String, String>,
    body: Option<String>,
    timeout_seconds: u32,
    retries: u32,
    follow_redirects: bool,
}

impl std::fmt::Display for HttpRequest {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut url = self.url.clone();
        if !self.query_params.is_empty() {
            let qs: Vec<String> = self
                .query_params
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect();
            url = format!("{}?{}", url, qs.join("&"));
        }
        writeln!(f, "{} {}", self.method, url)?;
        for (k, v) in &self.headers {
            writeln!(f, "  {}: {}", k, v)?;
        }
        if let Some(ref body) = self.body {
            let preview: String = body.chars().take(80).collect();
            writeln!(f, "  Body: {}...", preview)?;
        }
        write!(
            f,
            "  Timeout: {}s | Retries: {} | Follow redirects: {}",
            self.timeout_seconds, self.retries, self.follow_redirects
        )
    }
}

// ---------------------------------------------------------------------------
// Builder — fluent API with method chaining
// ---------------------------------------------------------------------------
struct HttpRequestBuilder {
    method: String,
    url: String,
    headers: HashMap<String, String>,
    query_params: HashMap<String, String>,
    body: Option<String>,
    timeout: u32,
    retries: u32,
    follow_redirects: bool,
}

impl HttpRequestBuilder {
    fn new() -> Self {
        Self {
            method: "GET".to_string(),
            url: String::new(),
            headers: HashMap::new(),
            query_params: HashMap::new(),
            body: None,
            timeout: 30,
            retries: 0,
            follow_redirects: true,
        }
    }

    // HTTP method shortcuts — each consumes and returns self (move semantics)
    fn get(mut self, url: &str) -> Self {
        self.method = "GET".to_string();
        self.url = url.to_string();
        self
    }

    fn post(mut self, url: &str) -> Self {
        self.method = "POST".to_string();
        self.url = url.to_string();
        self
    }

    fn put(mut self, url: &str) -> Self {
        self.method = "PUT".to_string();
        self.url = url.to_string();
        self
    }

    fn delete(mut self, url: &str) -> Self {
        self.method = "DELETE".to_string();
        self.url = url.to_string();
        self
    }

    // Configuration methods
    fn header(mut self, key: &str, value: &str) -> Self {
        self.headers.insert(key.to_string(), value.to_string());
        self
    }

    fn query(mut self, key: &str, value: &str) -> Self {
        self.query_params.insert(key.to_string(), value.to_string());
        self
    }

    fn body(mut self, content: &str) -> Self {
        self.body = Some(content.to_string());
        self
    }

    fn timeout(mut self, seconds: u32) -> Self {
        self.timeout = seconds;
        self
    }

    fn retries(mut self, count: u32) -> Self {
        self.retries = count;
        self
    }

    fn no_follow_redirects(mut self) -> Self {
        self.follow_redirects = false;
        self
    }

    /// Validate and produce the immutable HttpRequest.
    fn build(self) -> Result<HttpRequest, String> {
        if self.url.is_empty() {
            return Err("URL is required".to_string());
        }
        if (self.method == "POST" || self.method == "PUT") && self.body.is_none() {
            return Err(format!("{} requests should have a body", self.method));
        }

        Ok(HttpRequest {
            method: self.method,
            url: self.url,
            headers: self.headers,
            query_params: self.query_params,
            body: self.body,
            timeout_seconds: self.timeout,
            retries: self.retries,
            follow_redirects: self.follow_redirects,
        })
    }
}

// ---------------------------------------------------------------------------
// Director (optional) — preset construction sequences
// ---------------------------------------------------------------------------
struct RequestDirector;

impl RequestDirector {
    fn json_api_get(url: &str) -> HttpRequestBuilder {
        HttpRequestBuilder::new()
            .get(url)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json")
            .timeout(10)
            .retries(3)
    }

    fn authenticated_post(url: &str, token: &str, body: &str) -> HttpRequestBuilder {
        HttpRequestBuilder::new()
            .post(url)
            .header("Authorization", &format!("Bearer {}", token))
            .header("Content-Type", "application/json")
            .body(body)
            .timeout(30)
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    // Manual step-by-step building with chaining
    let request = HttpRequestBuilder::new()
        .get("https://api.example.com/users")
        .header("Authorization", "Bearer abc123")
        .query("page", "1")
        .query("limit", "50")
        .timeout(15)
        .retries(2)
        .build()
        .expect("Failed to build request");

    println!("Manual build:");
    println!("{}\n", request);

    // Director preset
    let api_request = RequestDirector::json_api_get("https://api.example.com/products")
        .query("category", "electronics")
        .build()
        .expect("Failed to build request");

    println!("Director preset (JSON API GET):");
    println!("{}\n", api_request);

    let post_request = RequestDirector::authenticated_post(
        "https://api.example.com/orders",
        "secret-token",
        r#"{"item": "laptop", "qty": 1}"#,
    )
    .build()
    .expect("Failed to build request");

    println!("Director preset (Authenticated POST):");
    println!("{}", post_request);
}
