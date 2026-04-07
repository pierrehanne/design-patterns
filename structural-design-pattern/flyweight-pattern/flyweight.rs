//! Flyweight Pattern
//! =================
//! Category: Structural Design Pattern
//!
//! Intent:
//!   Minimize memory by sharing data between similar objects.
//!   Shared = intrinsic state (in flyweight). Unique = extrinsic state (passed in).
//!
//! When to use:
//!   - Huge number of similar objects consuming too much memory
//!   - Most object state can be externalized
//!
//! Key Participants:
//!   - Flyweight: Stores intrinsic (shared) state
//!   - FlyweightFactory: Creates and caches flyweight instances
//!   - Client: Maintains extrinsic state
//!
//! Rust approach:
//!   We use Rc (reference counting) to share flyweight instances across
//!   multiple particles without cloning the heavy data.

use std::collections::HashMap;
use std::rc::Rc;

// ---------------------------------------------------------------------------
// Flyweight — shared intrinsic state
// ---------------------------------------------------------------------------
#[derive(Debug)]
struct ParticleType {
    name: String,
    sprite: String,     // Imagine this is a large texture
    animation: String,
    base_color: String,
}

impl ParticleType {
    /// Extrinsic state (x, y, scale, opacity) is passed in, not stored.
    fn render(&self, x: i32, y: i32, scale: f32, opacity: f32) -> String {
        format!(
            "[{}] sprite={} at ({},{}) scale={:.1} opacity={:.1} color={}",
            self.name, self.sprite, x, y, scale, opacity, self.base_color
        )
    }
}

// ---------------------------------------------------------------------------
// Flyweight Factory — ensures each type is created only once
// ---------------------------------------------------------------------------
struct ParticleTypeFactory {
    cache: HashMap<String, Rc<ParticleType>>,
}

impl ParticleTypeFactory {
    fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    fn get(
        &mut self,
        name: &str,
        sprite: &str,
        animation: &str,
        base_color: &str,
    ) -> Rc<ParticleType> {
        let key = format!("{}:{}:{}:{}", name, sprite, animation, base_color);

        // Rc::clone only increments the reference count — no data is copied
        self.cache
            .entry(key)
            .or_insert_with(|| {
                println!("  [Factory] Created new flyweight for '{}'", name);
                Rc::new(ParticleType {
                    name: name.to_string(),
                    sprite: sprite.to_string(),
                    animation: animation.to_string(),
                    base_color: base_color.to_string(),
                })
            })
            .clone()
    }

    fn count(&self) -> usize {
        self.cache.len()
    }
}

// ---------------------------------------------------------------------------
// Client context — stores extrinsic (per-instance) state
// ---------------------------------------------------------------------------
struct Particle {
    particle_type: Rc<ParticleType>, // Shared reference to flyweight
    x: i32,
    y: i32,
    scale: f32,
    opacity: f32,
}

impl Particle {
    fn render(&self) -> String {
        self.particle_type
            .render(self.x, self.y, self.scale, self.opacity)
    }
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let mut factory = ParticleTypeFactory::new();
    let mut particles: Vec<Particle> = Vec::new();

    // 1000 fire particles — all share ONE Rc<ParticleType>
    for i in 0..1000 {
        particles.push(Particle {
            particle_type: factory.get("fire", "sprites/fire.png", "burn_loop", "#FF4500"),
            x: i % 1920,
            y: (i * 7) % 1080,
            scale: 0.5 + (i as f32 % 15) / 10.0,
            opacity: 0.3 + (i as f32 % 7) / 10.0,
        });
    }

    // 500 smoke particles
    for i in 0..500 {
        particles.push(Particle {
            particle_type: factory.get("smoke", "sprites/smoke.png", "fade_up", "#808080"),
            x: (i * 3) % 1920,
            y: (i * 11) % 1080,
            scale: 1.0 + (i as f32 % 20) / 10.0,
            opacity: 0.1 + (i as f32 % 4) / 10.0,
        });
    }

    // 200 spark particles
    for i in 0..200 {
        particles.push(Particle {
            particle_type: factory.get("spark", "sprites/spark.png", "flash", "#FFD700"),
            x: (i * 9) % 1920,
            y: (i * 5) % 1080,
            scale: 0.2 + (i as f32 % 6) / 10.0,
            opacity: 0.5 + (i as f32 % 5) / 10.0,
        });
    }

    println!("\nTotal particles: {}", particles.len());
    println!("Unique flyweights (shared types): {}", factory.count());
    println!(
        "Memory savings: {} particles share only {} type objects",
        particles.len(),
        factory.count()
    );

    println!("\nSample renders:");
    for p in particles.iter().take(5) {
        println!("  {}", p.render());
    }
}
