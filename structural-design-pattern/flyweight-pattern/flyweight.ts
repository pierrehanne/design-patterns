/**
 * Flyweight Pattern
 * =================
 * Category: Structural Design Pattern
 *
 * Intent:
 *   Minimize memory usage by sharing data between similar objects.
 *   Shared data = "intrinsic state" (in the flyweight).
 *   Unique data = "extrinsic state" (passed by the client).
 *
 * When to use:
 *   - Huge number of similar objects consuming too much memory
 *   - Most object state can be externalized
 *   - Common in: text editors, game engines (particles, tiles), caching
 *
 * Key Participants:
 *   - Flyweight: Stores intrinsic (shared) state
 *   - FlyweightFactory: Creates and caches flyweight instances
 *   - Client: Maintains extrinsic state
 */

// ---------------------------------------------------------------------------
// Flyweight — shared intrinsic state (immutable)
// ---------------------------------------------------------------------------
class ParticleType {
  constructor(
    readonly name: string,
    readonly sprite: string, // Imagine this is a large texture reference
    readonly animation: string,
    readonly baseColor: string
  ) {}

  /** Extrinsic state (x, y, scale, opacity) is passed in, not stored. */
  render(x: number, y: number, scale: number, opacity: number): string {
    return `[${this.name}] sprite=${this.sprite} at (${x},${y}) scale=${scale.toFixed(1)} opacity=${opacity.toFixed(1)} color=${this.baseColor}`;
  }
}

// ---------------------------------------------------------------------------
// Flyweight Factory — ensures each type is created only once
// ---------------------------------------------------------------------------
class ParticleTypeFactory {
  private cache = new Map<string, ParticleType>();

  get(
    name: string,
    sprite: string,
    animation: string,
    baseColor: string
  ): ParticleType {
    const key = `${name}:${sprite}:${animation}:${baseColor}`;
    if (!this.cache.has(key)) {
      this.cache.set(key, new ParticleType(name, sprite, animation, baseColor));
      console.log(`  [Factory] Created new flyweight for '${name}'`);
    }
    return this.cache.get(key)!;
  }

  get count(): number {
    return this.cache.size;
  }
}

// ---------------------------------------------------------------------------
// Client context — stores extrinsic (per-instance) state
// ---------------------------------------------------------------------------
interface Particle {
  type: ParticleType; // Reference to shared flyweight
  x: number; // Extrinsic: unique position
  y: number;
  scale: number;
  opacity: number;
}

function renderParticle(p: Particle): string {
  return p.type.render(p.x, p.y, p.scale, p.opacity);
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const factory = new ParticleTypeFactory();
const particles: Particle[] = [];

// 1000 fire particles — all share ONE ParticleType flyweight
for (let i = 0; i < 1000; i++) {
  particles.push({
    type: factory.get("fire", "sprites/fire.png", "burn_loop", "#FF4500"),
    x: Math.floor(Math.random() * 1920),
    y: Math.floor(Math.random() * 1080),
    scale: 0.5 + Math.random() * 1.5,
    opacity: 0.3 + Math.random() * 0.7,
  });
}

// 500 smoke particles
for (let i = 0; i < 500; i++) {
  particles.push({
    type: factory.get("smoke", "sprites/smoke.png", "fade_up", "#808080"),
    x: Math.floor(Math.random() * 1920),
    y: Math.floor(Math.random() * 1080),
    scale: 1.0 + Math.random() * 2.0,
    opacity: 0.1 + Math.random() * 0.4,
  });
}

// 200 spark particles
for (let i = 0; i < 200; i++) {
  particles.push({
    type: factory.get("spark", "sprites/spark.png", "flash", "#FFD700"),
    x: Math.floor(Math.random() * 1920),
    y: Math.floor(Math.random() * 1080),
    scale: 0.2 + Math.random() * 0.6,
    opacity: 0.5 + Math.random() * 0.5,
  });
}

console.log(`\nTotal particles: ${particles.length}`);
console.log(`Unique flyweights (shared types): ${factory.count}`);
console.log(
  `Memory savings: ${particles.length} particles share only ${factory.count} type objects`
);

console.log("\nSample renders:");
particles.slice(0, 5).forEach((p) => console.log(`  ${renderParticle(p)}`));
