// Flyweight Pattern
// =================
// Category: Structural Design Pattern
//
// Intent:
//   Minimize memory by sharing data between similar objects.
//   Shared = intrinsic state (flyweight). Unique = extrinsic state (passed in).
//
// When to use:
//   - Huge number of similar objects consuming too much memory
//   - Most object state can be externalized
//
// Key Participants:
//   - Flyweight: Stores intrinsic (shared) state
//   - FlyweightFactory: Creates and caches flyweight instances
//   - Client: Maintains extrinsic state and passes it to flyweights

package main

import "fmt"

// ---------------------------------------------------------------------------
// Flyweight — shared intrinsic state (pointer-shared, not copied)
// ---------------------------------------------------------------------------

type ParticleType struct {
	Name      string
	Sprite    string // Imagine this is a large texture reference
	Animation string
	BaseColor string
}

// Render takes extrinsic state (position, scale, opacity) as parameters.
func (pt *ParticleType) Render(x, y int, scale, opacity float64) string {
	return fmt.Sprintf("[%s] sprite=%s at (%d,%d) scale=%.1f opacity=%.1f color=%s",
		pt.Name, pt.Sprite, x, y, scale, opacity, pt.BaseColor)
}

// ---------------------------------------------------------------------------
// Flyweight Factory — ensures each type is created only once
// ---------------------------------------------------------------------------

type ParticleTypeFactory struct {
	cache map[string]*ParticleType
}

func NewParticleTypeFactory() *ParticleTypeFactory {
	return &ParticleTypeFactory{cache: make(map[string]*ParticleType)}
}

func (f *ParticleTypeFactory) Get(name, sprite, animation, baseColor string) *ParticleType {
	key := fmt.Sprintf("%s:%s:%s:%s", name, sprite, animation, baseColor)
	if pt, ok := f.cache[key]; ok {
		return pt // Return existing — shared pointer
	}

	fmt.Printf("  [Factory] Created new flyweight for '%s'\n", name)
	pt := &ParticleType{
		Name:      name,
		Sprite:    sprite,
		Animation: animation,
		BaseColor: baseColor,
	}
	f.cache[key] = pt
	return pt
}

func (f *ParticleTypeFactory) Count() int {
	return len(f.cache)
}

// ---------------------------------------------------------------------------
// Client context — stores extrinsic (per-instance) state
// ---------------------------------------------------------------------------

type Particle struct {
	Type    *ParticleType // Shared pointer to flyweight
	X, Y   int           // Extrinsic: unique position
	Scale   float64
	Opacity float64
}

func (p *Particle) Render() string {
	return p.Type.Render(p.X, p.Y, p.Scale, p.Opacity)
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	factory := NewParticleTypeFactory()
	particles := make([]Particle, 0, 1700)

	// 1000 fire particles — all share ONE *ParticleType
	for i := 0; i < 1000; i++ {
		particles = append(particles, Particle{
			Type:    factory.Get("fire", "sprites/fire.png", "burn_loop", "#FF4500"),
			X:       i % 1920,
			Y:       (i * 7) % 1080,
			Scale:   0.5 + float64(i%15)/10.0,
			Opacity: 0.3 + float64(i%7)/10.0,
		})
	}

	// 500 smoke particles
	for i := 0; i < 500; i++ {
		particles = append(particles, Particle{
			Type:    factory.Get("smoke", "sprites/smoke.png", "fade_up", "#808080"),
			X:       (i * 3) % 1920,
			Y:       (i * 11) % 1080,
			Scale:   1.0 + float64(i%20)/10.0,
			Opacity: 0.1 + float64(i%4)/10.0,
		})
	}

	// 200 spark particles
	for i := 0; i < 200; i++ {
		particles = append(particles, Particle{
			Type:    factory.Get("spark", "sprites/spark.png", "flash", "#FFD700"),
			X:       (i * 9) % 1920,
			Y:       (i * 5) % 1080,
			Scale:   0.2 + float64(i%6)/10.0,
			Opacity: 0.5 + float64(i%5)/10.0,
		})
	}

	fmt.Printf("\nTotal particles: %d\n", len(particles))
	fmt.Printf("Unique flyweights (shared types): %d\n", factory.Count())
	fmt.Printf("Memory savings: %d particles share only %d type objects\n",
		len(particles), factory.Count())

	fmt.Println("\nSample renders:")
	for _, p := range particles[:5] {
		fmt.Printf("  %s\n", p.Render())
	}
}
