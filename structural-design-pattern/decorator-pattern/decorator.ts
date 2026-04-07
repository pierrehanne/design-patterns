/**
 * Decorator Pattern
 * =================
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Attach additional responsibilities to an object dynamically. Decorators
 *   provide a flexible alternative to subclassing for extending functionality.
 *
 * When to use:
 *   - When you want to add behavior without modifying the original class
 *   - When behaviors need to be combined in arbitrary ways at runtime
 *   - Follows Open/Closed Principle: open for extension, closed for modification
 *
 * Key Participants:
 *   - Component (interface): Base interface
 *   - ConcreteComponent: The original object
 *   - Decorator: Wraps a Component and adds behavior before/after delegation
 */

// ---------------------------------------------------------------------------
// Component — base interface
// ---------------------------------------------------------------------------
interface DataSource {
  write(data: string): string;
  read(data: string): string;
}

// ---------------------------------------------------------------------------
// Concrete Component
// ---------------------------------------------------------------------------
class StringDataSource implements DataSource {
  write(data: string): string {
    return data;
  }
  read(data: string): string {
    return data;
  }
}

// ---------------------------------------------------------------------------
// Concrete Decorators
// ---------------------------------------------------------------------------
class EncryptionDecorator implements DataSource {
  constructor(private wrapped: DataSource, private shift: number = 3) {}

  write(data: string): string {
    const encrypted = [...data]
      .map((c) => {
        const code = c.charCodeAt(0);
        if (code >= 32 && code < 127) {
          return String.fromCharCode(((code - 32 + this.shift) % 95) + 32);
        }
        return c;
      })
      .join("");
    return this.wrapped.write(encrypted);
  }

  read(data: string): string {
    const inner = this.wrapped.read(data);
    return [...inner]
      .map((c) => {
        const code = c.charCodeAt(0);
        if (code >= 32 && code < 127) {
          return String.fromCharCode(
            ((code - 32 - this.shift + 95) % 95) + 32
          );
        }
        return c;
      })
      .join("");
  }
}

class CompressionDecorator implements DataSource {
  constructor(private wrapped: DataSource) {}

  write(data: string): string {
    return this.wrapped.write(this.rleEncode(data));
  }

  read(data: string): string {
    return this.rleDecode(this.wrapped.read(data));
  }

  private rleEncode(data: string): string {
    if (!data) return "";
    const result: string[] = [];
    let count = 1;
    for (let i = 1; i <= data.length; i++) {
      if (i < data.length && data[i] === data[i - 1]) {
        count++;
      } else {
        result.push(count > 1 ? `${count}${data[i - 1]}` : data[i - 1]);
        count = 1;
      }
    }
    return result.join("");
  }

  private rleDecode(data: string): string {
    const result: string[] = [];
    let num = "";
    for (const c of data) {
      if (c >= "0" && c <= "9") {
        num += c;
      } else {
        const count = num ? parseInt(num) : 1;
        result.push(c.repeat(count));
        num = "";
      }
    }
    return result.join("");
  }
}

class LoggingDecorator implements DataSource {
  constructor(private wrapped: DataSource) {}

  write(data: string): string {
    console.log(`  [LOG] Writing ${data.length} chars`);
    const result = this.wrapped.write(data);
    console.log(`  [LOG] After processing: ${result.length} chars`);
    return result;
  }

  read(data: string): string {
    console.log(`  [LOG] Reading ${data.length} chars`);
    const result = this.wrapped.read(data);
    console.log(`  [LOG] After processing: ${result.length} chars`);
    return result;
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
console.log("=== Plain write/read ===");
const source = new StringDataSource();
const written = source.write("Hello, World!");
console.log(`Written: ${written}`);
console.log(`Read:    ${source.read(written)}`);

// Stack decorators: Logging → Encryption → Compression → Base
console.log("\n=== Decorated: Logging + Encryption + Compression ===");
const decorated = new LoggingDecorator(
  new EncryptionDecorator(new CompressionDecorator(new StringDataSource()), 5)
);

const data = "aaabbbccc Hello World!!!";
const processed = decorated.write(data);
console.log(`Original:  ${data}`);
console.log(`Processed: ${processed}`);

console.log("\nReading back:");
const restored = decorated.read(processed);
console.log(`Restored:  ${restored}`);
console.log(`Match:     ${data === restored}`);
