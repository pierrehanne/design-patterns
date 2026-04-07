// Singleton Pattern
// =================
// Category: Creational Design Pattern
//
// Intent:
//   Ensure a type has only ONE instance and provide a global point of access to it.
//
// When to use:
//   - Database connection pools, configuration managers, logging services
//   - When exactly one object is needed to coordinate actions across the system
//   - When creating multiple instances would cause conflicts or waste resources
//
// Key Participants:
//   - Singleton: A package-level instance guarded by sync.Once to guarantee
//     one-time initialization, even under concurrent access.
//
// Go approach:
//   Go has no classes or constructors. We use sync.Once, which guarantees that
//   the initialization function runs exactly once regardless of how many
//   goroutines call it concurrently.

package main

import (
	"fmt"
	"sync"
)

// ConfigurationManager holds application-wide settings.
type ConfigurationManager struct {
	mu       sync.RWMutex      // Protects concurrent read/write to settings
	settings map[string]string
}

var (
	instance *ConfigurationManager
	once     sync.Once // Guarantees the init function runs exactly once
)

// GetConfig returns the singleton instance. The first call creates it;
// all subsequent calls return the same pointer.
func GetConfig() *ConfigurationManager {
	once.Do(func() {
		fmt.Println("[ConfigurationManager] Initialized (this should appear only once)")
		instance = &ConfigurationManager{
			settings: make(map[string]string),
		}
	})
	return instance
}

// Set stores a configuration key-value pair (write-locked).
func (c *ConfigurationManager) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.settings[key] = value
}

// Get retrieves a configuration value (read-locked).
func (c *ConfigurationManager) Get(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	v, ok := c.settings[key]
	return v, ok
}

// All returns a copy of all settings.
func (c *ConfigurationManager) All() map[string]string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	copy := make(map[string]string, len(c.settings))
	for k, v := range c.settings {
		copy[k] = v
	}
	return copy
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	configA := GetConfig()
	configB := GetConfig()

	configA.Set("database_url", "postgres://localhost:5432/mydb")
	configA.Set("log_level", "DEBUG")

	// configB sees the same data because it IS the same object
	if url, ok := configB.Get("database_url"); ok {
		fmt.Println("configB database_url:", url)
	}
	fmt.Println("Same instance?", configA == configB) // true

	// Demonstrate goroutine safety
	var wg sync.WaitGroup
	pointers := make(chan uintptr, 10)
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c := GetConfig()
			pointers <- uintptr(fmt.Sprintf("%p", c)[2:][0]) // just to show it's same
		}()
	}
	wg.Wait()
	close(pointers)

	fmt.Println("All settings:", configA.All())
}
