"""
Flyweight Pattern
=================
Category: Structural Design Pattern

Intent:
    Minimize memory usage by sharing as much data as possible between similar
    objects. The shared part is called "intrinsic state" (stored in the flyweight),
    while the unique part is "extrinsic state" (passed in by the client).

When to use:
    - When you have a huge number of similar objects consuming too much memory
    - When most object state can be made extrinsic (passed in rather than stored)
    - Common in: text editors (character rendering), game engines (particles, tiles),
      caching systems, icon/image pools

Key Participants:
    - Flyweight: Stores intrinsic (shared) state
    - FlyweightFactory: Creates and caches flyweight objects
    - Client: Maintains extrinsic state and passes it to flyweights

Intrinsic vs Extrinsic state:
    - Intrinsic: Shared, immutable data (e.g., character font, glyph bitmap)
    - Extrinsic: Unique per usage, passed in at runtime (e.g., position, color)
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Flyweight — stores INTRINSIC (shared) state
# ---------------------------------------------------------------------------
@dataclass(frozen=True)  # Immutable — safe to share
class ParticleType:
    """
    Shared data for a type of game particle. A "fire" particle always uses
    the same sprite, animation, and base color regardless of where it appears.
    These are the INTRINSIC properties.
    """
    name: str
    sprite: str      # Path to sprite image (imagine this is a large texture)
    animation: str    # Animation sequence name
    base_color: str   # Default color

    def render(self, x: int, y: int, scale: float, opacity: float) -> str:
        """
        Render this particle type at a specific position.
        x, y, scale, opacity are EXTRINSIC state — unique per particle instance.
        """
        return (
            f"[{self.name}] sprite={self.sprite} at ({x},{y}) "
            f"scale={scale:.1f} opacity={opacity:.1f} color={self.base_color}"
        )


# ---------------------------------------------------------------------------
# Flyweight Factory — creates and caches flyweights
# ---------------------------------------------------------------------------
class ParticleTypeFactory:
    """
    Ensures each unique ParticleType is created only once.
    If 10,000 fire particles exist, they all share ONE ParticleType instance.
    """

    def __init__(self) -> None:
        self._cache: dict[str, ParticleType] = {}

    def get(self, name: str, sprite: str, animation: str, base_color: str) -> ParticleType:
        key = f"{name}:{sprite}:{animation}:{base_color}"
        if key not in self._cache:
            self._cache[key] = ParticleType(name, sprite, animation, base_color)
            print(f"  [Factory] Created new flyweight for '{name}'")
        return self._cache[key]

    @property
    def count(self) -> int:
        return len(self._cache)


# ---------------------------------------------------------------------------
# Client context — stores EXTRINSIC (per-instance) state
# ---------------------------------------------------------------------------
@dataclass
class Particle:
    """
    An individual particle in the game world. The heavy data (sprite, animation)
    is shared via the flyweight. Only position, scale, and opacity are unique.
    """
    particle_type: ParticleType  # Reference to shared flyweight
    x: int                       # Extrinsic: unique position
    y: int
    scale: float
    opacity: float

    def render(self) -> str:
        return self.particle_type.render(self.x, self.y, self.scale, self.opacity)


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import random

    factory = ParticleTypeFactory()

    # Imagine a game creating thousands of particles
    particles: list[Particle] = []

    # Create 1000 fire particles — all share ONE ParticleType flyweight
    for _ in range(1000):
        ptype = factory.get("fire", "sprites/fire.png", "burn_loop", "#FF4500")
        particles.append(Particle(
            particle_type=ptype,
            x=random.randint(0, 1920),
            y=random.randint(0, 1080),
            scale=random.uniform(0.5, 2.0),
            opacity=random.uniform(0.3, 1.0),
        ))

    # Create 500 smoke particles — share another flyweight
    for _ in range(500):
        ptype = factory.get("smoke", "sprites/smoke.png", "fade_up", "#808080")
        particles.append(Particle(
            particle_type=ptype,
            x=random.randint(0, 1920),
            y=random.randint(0, 1080),
            scale=random.uniform(1.0, 3.0),
            opacity=random.uniform(0.1, 0.5),
        ))

    # Create 200 spark particles
    for _ in range(200):
        ptype = factory.get("spark", "sprites/spark.png", "flash", "#FFD700")
        particles.append(Particle(
            particle_type=ptype,
            x=random.randint(0, 1920),
            y=random.randint(0, 1080),
            scale=random.uniform(0.2, 0.8),
            opacity=random.uniform(0.5, 1.0),
        ))

    print(f"\nTotal particles: {len(particles)}")
    print(f"Unique flyweights (shared types): {factory.count}")
    print(f"Memory savings: instead of {len(particles)} sprite/animation copies,")
    print(f"  we only have {factory.count} (shared via flyweight references)")

    # Render a sample
    print("\nSample renders:")
    for p in particles[:5]:
        print(f"  {p.render()}")
