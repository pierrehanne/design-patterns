/**
 * Proxy Pattern
 * =============
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Provide a surrogate or placeholder for another object to control access.
 *   The proxy has the same interface as the real object.
 *
 * When to use:
 *   - Caching Proxy: Avoid redundant expensive operations
 *   - Virtual Proxy: Lazy-load heavy resources
 *   - Protection Proxy: Access control based on permissions
 *   - Logging Proxy: Add monitoring without modifying the real service
 *
 * Key Participants:
 *   - Subject (interface): Common interface for Real and Proxy
 *   - RealSubject: The actual object
 *   - Proxy: Controls access, same interface as RealSubject
 */

// ---------------------------------------------------------------------------
// Subject interface
// ---------------------------------------------------------------------------
interface WeatherService {
  getForecast(city: string): Record<string, any>;
  getTemperature(city: string): number;
}

// ---------------------------------------------------------------------------
// Real Subject — expensive external API
// ---------------------------------------------------------------------------
class RealWeatherService implements WeatherService {
  callCount = 0;

  getForecast(city: string): Record<string, any> {
    this.callCount++;
    console.log(
      `    [RealService] API call #${this.callCount} — fetching forecast for ${city}`
    );
    return {
      city,
      conditions: "Partly Cloudy",
      high: 72,
      low: 58,
      humidity: 45,
    };
  }

  getTemperature(city: string): number {
    this.callCount++;
    console.log(
      `    [RealService] API call #${this.callCount} — fetching temperature for ${city}`
    );
    return 68.5;
  }
}

// ---------------------------------------------------------------------------
// Caching Proxy
// ---------------------------------------------------------------------------
class CachingWeatherProxy implements WeatherService {
  private cache = new Map<string, { timestamp: number; value: any }>();

  constructor(
    private service: WeatherService,
    private ttlMs: number = 60_000
  ) {}

  private getCached(key: string): any | null {
    const entry = this.cache.get(key);
    if (entry) {
      if (Date.now() - entry.timestamp < this.ttlMs) {
        console.log(`    [Cache HIT] ${key}`);
        return entry.value;
      }
      console.log(`    [Cache EXPIRED] ${key}`);
      this.cache.delete(key);
    } else {
      console.log(`    [Cache MISS] ${key}`);
    }
    return null;
  }

  private setCache(key: string, value: any): void {
    this.cache.set(key, { timestamp: Date.now(), value });
  }

  getForecast(city: string): Record<string, any> {
    const key = `forecast:${city}`;
    const cached = this.getCached(key);
    if (cached !== null) return cached;
    const result = this.service.getForecast(city);
    this.setCache(key, result);
    return result;
  }

  getTemperature(city: string): number {
    const key = `temp:${city}`;
    const cached = this.getCached(key);
    if (cached !== null) return cached;
    const result = this.service.getTemperature(city);
    this.setCache(key, result);
    return result;
  }
}

// ---------------------------------------------------------------------------
// Access Control Proxy
// ---------------------------------------------------------------------------
class AccessControlWeatherProxy implements WeatherService {
  private static VALID_KEYS = new Set(["key-alice-123", "key-bob-456"]);

  constructor(private service: WeatherService, private apiKey: string) {}

  private checkAccess(): void {
    if (!AccessControlWeatherProxy.VALID_KEYS.has(this.apiKey)) {
      throw new Error(`Access denied: invalid API key '${this.apiKey}'`);
    }
  }

  getForecast(city: string): Record<string, any> {
    this.checkAccess();
    return this.service.getForecast(city);
  }

  getTemperature(city: string): number {
    this.checkAccess();
    return this.service.getTemperature(city);
  }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const real = new RealWeatherService();

console.log("=== Caching Proxy ===");
const cached = new CachingWeatherProxy(real, 300_000);

console.log("\nFirst request:");
console.log("  Result:", cached.getForecast("New York"));

console.log("\nSecond request (same city):");
console.log("  Result:", cached.getForecast("New York"));

console.log("\nDifferent city:");
console.log("  Result:", cached.getForecast("London"));

console.log(`\nReal service was called ${real.callCount} times (not 3)`);

console.log("\n=== Access Control Proxy ===");
const real2 = new RealWeatherService();

console.log("\nValid API key:");
const authService = new AccessControlWeatherProxy(real2, "key-alice-123");
console.log("  Temperature:", authService.getTemperature("Paris"));

console.log("\nInvalid API key:");
const badService = new AccessControlWeatherProxy(real2, "key-hacker-999");
try {
  badService.getTemperature("Paris");
} catch (e: any) {
  console.log(`  ${e.message}`);
}
