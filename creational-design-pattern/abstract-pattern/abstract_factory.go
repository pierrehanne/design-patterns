// Abstract Factory Pattern
// ========================
// Category: Creational Design Pattern
//
// Intent:
//   Provide an interface for creating FAMILIES of related objects without
//   specifying their concrete types. Swapping the factory swaps the entire
//   product family.
//
// When to use:
//   - When your system needs families of related objects (e.g., themed UI)
//   - When you want to guarantee products from one family aren't mixed with another
//   - When you want to swap entire product families at runtime
//
// Key Participants:
//   - AbstractFactory (interface): Declares creation methods for each product
//   - ConcreteFactory: Implements creation for a specific family
//   - AbstractProduct (interface): Contract for each kind of product
//   - ConcreteProduct: Family-specific implementations

package main

import "fmt"

// ---------------------------------------------------------------------------
// Abstract Products (interfaces)
// ---------------------------------------------------------------------------

type Button interface {
	Render() string
	OnClick(handler string) string
}

type Checkbox interface {
	Render() string
	Toggle() string
}

type TextField interface {
	Render() string
	SetValue(value string) string
}

// ---------------------------------------------------------------------------
// Abstract Factory (interface)
// ---------------------------------------------------------------------------

type UIFactory interface {
	CreateButton() Button
	CreateCheckbox() Checkbox
	CreateTextField() TextField
}

// ---------------------------------------------------------------------------
// Dark Theme Family
// ---------------------------------------------------------------------------

type DarkButton struct{}

func (d *DarkButton) Render() string {
	return "<button class='bg-gray-800 text-white'>Click me</button>"
}
func (d *DarkButton) OnClick(handler string) string {
	return fmt.Sprintf("Dark button triggers: %s", handler)
}

type DarkCheckbox struct{}

func (d *DarkCheckbox) Render() string {
	return "<input type='checkbox' class='border-gray-600 bg-gray-700' />"
}
func (d *DarkCheckbox) Toggle() string {
	return "Dark checkbox toggled with smooth transition"
}

type DarkTextField struct{}

func (d *DarkTextField) Render() string {
	return "<input type='text' class='bg-gray-800 text-white' />"
}
func (d *DarkTextField) SetValue(value string) string {
	return fmt.Sprintf("Dark text field set to: %s", value)
}

type DarkThemeFactory struct{}

func (f *DarkThemeFactory) CreateButton() Button     { return &DarkButton{} }
func (f *DarkThemeFactory) CreateCheckbox() Checkbox  { return &DarkCheckbox{} }
func (f *DarkThemeFactory) CreateTextField() TextField { return &DarkTextField{} }

// ---------------------------------------------------------------------------
// Light Theme Family
// ---------------------------------------------------------------------------

type LightButton struct{}

func (l *LightButton) Render() string {
	return "<button class='bg-white text-black'>Click me</button>"
}
func (l *LightButton) OnClick(handler string) string {
	return fmt.Sprintf("Light button triggers: %s", handler)
}

type LightCheckbox struct{}

func (l *LightCheckbox) Render() string {
	return "<input type='checkbox' class='border-gray-300 bg-white' />"
}
func (l *LightCheckbox) Toggle() string {
	return "Light checkbox toggled with crisp animation"
}

type LightTextField struct{}

func (l *LightTextField) Render() string {
	return "<input type='text' class='bg-white text-black' />"
}
func (l *LightTextField) SetValue(value string) string {
	return fmt.Sprintf("Light text field set to: %s", value)
}

type LightThemeFactory struct{}

func (f *LightThemeFactory) CreateButton() Button     { return &LightButton{} }
func (f *LightThemeFactory) CreateCheckbox() Checkbox  { return &LightCheckbox{} }
func (f *LightThemeFactory) CreateTextField() TextField { return &LightTextField{} }

// ---------------------------------------------------------------------------
// Client Code — works ONLY through interfaces
// ---------------------------------------------------------------------------

func buildLoginForm(factory UIFactory) {
	username := factory.CreateTextField()
	password := factory.CreateTextField()
	remember := factory.CreateCheckbox()
	submit := factory.CreateButton()

	fmt.Println("  Username:", username.Render())
	fmt.Println("  Password:", password.Render())
	fmt.Println("  Remember:", remember.Render())
	fmt.Println("  Submit:  ", submit.Render())
	fmt.Println("  Action:  ", submit.OnClick("submit_login()"))
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
func main() {
	preference := "dark" // could come from config

	// Factory selection is the ONLY place concrete types appear
	var factory UIFactory
	if preference == "dark" {
		factory = &DarkThemeFactory{}
	} else {
		factory = &LightThemeFactory{}
	}

	fmt.Printf("Building login form with %s theme:\n", preference)
	buildLoginForm(factory)

	fmt.Println("\nBuilding login form with light theme:")
	buildLoginForm(&LightThemeFactory{})
}
