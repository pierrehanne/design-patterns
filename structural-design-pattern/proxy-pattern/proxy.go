// Proxy Pattern
// =============
// Category: Structural Design Pattern
//
// Intent:
//   Provide a surrogate or placeholder for another object to control access.
//   The proxy has the same interface as the real object.
//
// When to use:
//   - Caching Proxy: Avoid redundant expensive operations
//   - Virtual Proxy: Lazy-load heavy resources
//   - Protection Proxy: Access control based on permissions
//   - Logging Proxy: Monitoring without modifying the real service
//
// Key Participants:
//   - Subject (interface): Common interface for Real and Proxy
//   - RealSubject: The actual object
//   - Proxy: Controls access, same interface as RealSubject

package main

import (
	"fmt"
)

// ---------------------------------------------------------------------------
// Subject interface
// ---------------------------------------------------------------------------

type WeatherService interface {
	GetForecast(city string) string
	GetTemperature(city string) (float64, error)
}

// ---------------------------------------------------------------------------
// Real Subject — expensive external API
// ---------------------------------------------------------------------------

type RealWeatherService struct {
	CallCount int
}

func (s *RealWeatherService) GetForecast(city string) string {
	s.CallCount++
	fmt.Printf("    [RealService] API call #%d — fetching forecast for %s\n", s.CallCount, city)
	return fmt.Sprintf("%s: Partly Cloudy, High 72, Low 58, Humidity 45%%", city)
}

func (s *RealWeatherService) GetTemperature(city string) (float64, error) {
	s.CallCount++
	fmt.Printf("    [RealService] API call #%d — fetching temperature for %s\n", s.CallCount, city)
	return 68.5, nil
}

// ---------------------------------------------------------------------------
// Caching Proxy
// ---------------------------------------------------------------------------

type CachingWeatherProxy struct {
	service   WeatherService
	forecast  map[string]string
	tempCache map[string]float64
}

func NewCachingProxy(service WeatherService) *CachingWeatherProxy {
	return &CachingWeatherProxy{
		service:   service,
		forecast:  make(map[string]string),
		tempCache: make(map[string]float64),
	}
}

func (p *CachingWeatherProxy) GetForecast(city string) string {
	key := "forecast:" + city
	if cached, ok := p.forecast[key]; ok {
		fmt.Printf("    [Cache HIT] %s\n", key)
		return cached
	}
	fmt.Printf("    [Cache MISS] %s\n", key)
	result := p.service.GetForecast(city)
	p.forecast[key] = result
	return result
}

func (p *CachingWeatherProxy) GetTemperature(city string) (float64, error) {
	key := "temp:" + city
	if cached, ok := p.tempCache[key]; ok {
		fmt.Printf("    [Cache HIT] %s\n", key)
		return cached, nil
	}
	fmt.Printf("    [Cache MISS] %s\n", key)
	result, err := p.service.GetTemperature(city)
	if err != nil {
		return 0, err
	}
	p.tempCache[key] = result
	return result, nil
}

// ---------------------------------------------------------------------------
// Access Control Proxy
// ---------------------------------------------------------------------------

type AccessControlWeatherProxy struct {
	service WeatherService
	apiKey  string
}

func NewAccessControlProxy(service WeatherService, apiKey string) *AccessControlWeatherProxy {
	return &AccessControlWeatherProxy{service: service, apiKey: apiKey}
}

var validKeys = map[string]bool{
	"key-alice-123": true,
	"key-bob-456":   true,
}

func (p *AccessControlWeatherProxy) checkAccess() error {
	if !validKeys[p.apiKey] {
		return fmt.Errorf("access denied: invalid API key '%s'", p.apiKey)
	}
	return nil
}

func (p *AccessControlWeatherProxy) GetForecast(city string) string {
	if err := p.checkAccess(); err != nil {
		return err.Error()
	}
	return p.service.GetForecast(city)
}

func (p *AccessControlWeatherProxy) GetTemperature(city string) (float64, error) {
	if err := p.checkAccess(); err != nil {
		return 0, err
	}
	return p.service.GetTemperature(city)
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	real := &RealWeatherService{}

	fmt.Println("=== Caching Proxy ===")
	cached := NewCachingProxy(real)

	fmt.Println("\nFirst request:")
	fmt.Println("  Result:", cached.GetForecast("New York"))

	fmt.Println("\nSecond request (same city):")
	fmt.Println("  Result:", cached.GetForecast("New York"))

	fmt.Println("\nDifferent city:")
	fmt.Println("  Result:", cached.GetForecast("London"))

	fmt.Printf("\nReal service was called %d times (not 3)\n", real.CallCount)

	fmt.Println("\n=== Access Control Proxy ===")
	real2 := &RealWeatherService{}

	fmt.Println("\nValid API key:")
	auth := NewAccessControlProxy(real2, "key-alice-123")
	temp, _ := auth.GetTemperature("Paris")
	fmt.Printf("  Temperature: %.1f\n", temp)

	fmt.Println("\nInvalid API key:")
	bad := NewAccessControlProxy(real2, "key-hacker-999")
	_, err := bad.GetTemperature("Paris")
	if err != nil {
		fmt.Printf("  %s\n", err)
	}
}
