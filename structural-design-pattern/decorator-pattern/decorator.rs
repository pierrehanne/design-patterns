//! Decorator Pattern
//! =================
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Attach additional responsibilities to an object dynamically by wrapping it.
//!   Each decorator adds one behavior and delegates to the wrapped object.
//!
//! When to use:
//!   - When you want to add behavior without modifying the original type
//!   - When behaviors need to be combined in arbitrary ways at runtime
//!   - Follows Open/Closed Principle
//!
//! Key Participants:
//!   - Component (trait): Base interface
//!   - ConcreteComponent: The original object
//!   - Decorator: Wraps a trait object and adds behavior

// ---------------------------------------------------------------------------
// Component trait
// ---------------------------------------------------------------------------
trait DataSource {
    fn write(&self, data: &str) -> String;
    fn read(&self, data: &str) -> String;
}

// ---------------------------------------------------------------------------
// Concrete Component
// ---------------------------------------------------------------------------
struct StringDataSource;

impl DataSource for StringDataSource {
    fn write(&self, data: &str) -> String {
        data.to_string()
    }
    fn read(&self, data: &str) -> String {
        data.to_string()
    }
}

// ---------------------------------------------------------------------------
// Encryption Decorator
// ---------------------------------------------------------------------------
struct EncryptionDecorator {
    wrapped: Box<dyn DataSource>,
    shift: u8,
}

impl EncryptionDecorator {
    fn new(wrapped: Box<dyn DataSource>, shift: u8) -> Self {
        Self { wrapped, shift }
    }

    fn shift_char(&self, c: char, forward: bool) -> char {
        let code = c as u32;
        if (32..127).contains(&code) {
            let shifted = if forward {
                ((code - 32 + self.shift as u32) % 95) + 32
            } else {
                ((code - 32 + 95 - self.shift as u32) % 95) + 32
            };
            char::from_u32(shifted).unwrap_or(c)
        } else {
            c
        }
    }
}

impl DataSource for EncryptionDecorator {
    fn write(&self, data: &str) -> String {
        let encrypted: String = data.chars().map(|c| self.shift_char(c, true)).collect();
        self.wrapped.write(&encrypted)
    }

    fn read(&self, data: &str) -> String {
        let inner = self.wrapped.read(data);
        inner.chars().map(|c| self.shift_char(c, false)).collect()
    }
}

// ---------------------------------------------------------------------------
// Compression Decorator (simple RLE)
// ---------------------------------------------------------------------------
struct CompressionDecorator {
    wrapped: Box<dyn DataSource>,
}

impl CompressionDecorator {
    fn new(wrapped: Box<dyn DataSource>) -> Self {
        Self { wrapped }
    }

    fn rle_encode(data: &str) -> String {
        if data.is_empty() {
            return String::new();
        }
        let chars: Vec<char> = data.chars().collect();
        let mut result = String::new();
        let mut count = 1;

        for i in 1..=chars.len() {
            if i < chars.len() && chars[i] == chars[i - 1] {
                count += 1;
            } else {
                if count > 1 {
                    result.push_str(&count.to_string());
                }
                result.push(chars[i - 1]);
                count = 1;
            }
        }
        result
    }

    fn rle_decode(data: &str) -> String {
        let mut result = String::new();
        let mut num = String::new();

        for c in data.chars() {
            if c.is_ascii_digit() {
                num.push(c);
            } else {
                let count: usize = num.parse().unwrap_or(1);
                for _ in 0..count {
                    result.push(c);
                }
                num.clear();
            }
        }
        result
    }
}

impl DataSource for CompressionDecorator {
    fn write(&self, data: &str) -> String {
        let compressed = Self::rle_encode(data);
        self.wrapped.write(&compressed)
    }

    fn read(&self, data: &str) -> String {
        let inner = self.wrapped.read(data);
        Self::rle_decode(&inner)
    }
}

// ---------------------------------------------------------------------------
// Logging Decorator
// ---------------------------------------------------------------------------
struct LoggingDecorator {
    wrapped: Box<dyn DataSource>,
}

impl LoggingDecorator {
    fn new(wrapped: Box<dyn DataSource>) -> Self {
        Self { wrapped }
    }
}

impl DataSource for LoggingDecorator {
    fn write(&self, data: &str) -> String {
        println!("  [LOG] Writing {} chars", data.len());
        let result = self.wrapped.write(data);
        println!("  [LOG] After processing: {} chars", result.len());
        result
    }

    fn read(&self, data: &str) -> String {
        println!("  [LOG] Reading {} chars", data.len());
        let result = self.wrapped.read(data);
        println!("  [LOG] After processing: {} chars", result.len());
        result
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    println!("=== Plain write/read ===");
    let source = StringDataSource;
    let written = source.write("Hello, World!");
    println!("Written: {}", written);
    println!("Read:    {}", source.read(&written));

    // Stack: Logging → Encryption → Compression → Base
    println!("\n=== Decorated: Logging + Encryption + Compression ===");
    let decorated = LoggingDecorator::new(Box::new(EncryptionDecorator::new(
        Box::new(CompressionDecorator::new(Box::new(StringDataSource))),
        5,
    )));

    let data = "aaabbbccc Hello World!!!";
    let processed = decorated.write(data);
    println!("Original:  {}", data);
    println!("Processed: {}", processed);

    println!("\nReading back:");
    let restored = decorated.read(&processed);
    println!("Restored:  {}", restored);
    println!("Match:     {}", data == restored);
}
