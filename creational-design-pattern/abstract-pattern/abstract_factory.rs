//! Abstract Factory Pattern
//! ========================
//! Category: Creational Design Pattern
//!
//! Intent:
//!   Provide an interface (trait) for creating FAMILIES of related objects
//!   without specifying their concrete types. Swapping the factory swaps
//!   the entire product family.
//!
//! When to use:
//!   - When your system needs families of related objects (e.g., themed UI)
//!   - When you want to guarantee that products from one family aren't mixed
//!     with products from another
//!
//! Key Participants:
//!   - AbstractFactory (trait): Declares creation methods for each product
//!   - ConcreteFactory: Implements creation for a specific family
//!   - AbstractProduct (trait): Interface for each kind of product
//!   - ConcreteProduct: Family-specific implementations

// ---------------------------------------------------------------------------
// Abstract Products (traits)
// ---------------------------------------------------------------------------
trait Button {
    fn render(&self) -> String;
    fn on_click(&self, handler: &str) -> String;
}

trait Checkbox {
    fn render(&self) -> String;
    fn toggle(&self) -> String;
}

trait TextField {
    fn render(&self) -> String;
    fn set_value(&self, value: &str) -> String;
}

// ---------------------------------------------------------------------------
// Abstract Factory (trait)
// ---------------------------------------------------------------------------
trait UIFactory {
    fn create_button(&self) -> Box<dyn Button>;
    fn create_checkbox(&self) -> Box<dyn Checkbox>;
    fn create_text_field(&self) -> Box<dyn TextField>;
}

// ---------------------------------------------------------------------------
// Dark Theme Family
// ---------------------------------------------------------------------------
struct DarkButton;
impl Button for DarkButton {
    fn render(&self) -> String {
        "<button class='bg-gray-800 text-white'>Click me</button>".to_string()
    }
    fn on_click(&self, handler: &str) -> String {
        format!("Dark button triggers: {}", handler)
    }
}

struct DarkCheckbox;
impl Checkbox for DarkCheckbox {
    fn render(&self) -> String {
        "<input type='checkbox' class='border-gray-600 bg-gray-700' />".to_string()
    }
    fn toggle(&self) -> String {
        "Dark checkbox toggled with smooth transition".to_string()
    }
}

struct DarkTextField;
impl TextField for DarkTextField {
    fn render(&self) -> String {
        "<input type='text' class='bg-gray-800 text-white' />".to_string()
    }
    fn set_value(&self, value: &str) -> String {
        format!("Dark text field set to: {}", value)
    }
}

struct DarkThemeFactory;
impl UIFactory for DarkThemeFactory {
    fn create_button(&self) -> Box<dyn Button> {
        Box::new(DarkButton)
    }
    fn create_checkbox(&self) -> Box<dyn Checkbox> {
        Box::new(DarkCheckbox)
    }
    fn create_text_field(&self) -> Box<dyn TextField> {
        Box::new(DarkTextField)
    }
}

// ---------------------------------------------------------------------------
// Light Theme Family
// ---------------------------------------------------------------------------
struct LightButton;
impl Button for LightButton {
    fn render(&self) -> String {
        "<button class='bg-white text-black'>Click me</button>".to_string()
    }
    fn on_click(&self, handler: &str) -> String {
        format!("Light button triggers: {}", handler)
    }
}

struct LightCheckbox;
impl Checkbox for LightCheckbox {
    fn render(&self) -> String {
        "<input type='checkbox' class='border-gray-300 bg-white' />".to_string()
    }
    fn toggle(&self) -> String {
        "Light checkbox toggled with crisp animation".to_string()
    }
}

struct LightTextField;
impl TextField for LightTextField {
    fn render(&self) -> String {
        "<input type='text' class='bg-white text-black' />".to_string()
    }
    fn set_value(&self, value: &str) -> String {
        format!("Light text field set to: {}", value)
    }
}

struct LightThemeFactory;
impl UIFactory for LightThemeFactory {
    fn create_button(&self) -> Box<dyn Button> {
        Box::new(LightButton)
    }
    fn create_checkbox(&self) -> Box<dyn Checkbox> {
        Box::new(LightCheckbox)
    }
    fn create_text_field(&self) -> Box<dyn TextField> {
        Box::new(LightTextField)
    }
}

// ---------------------------------------------------------------------------
// Client Code — works ONLY through trait objects
// ---------------------------------------------------------------------------
fn build_login_form(factory: &dyn UIFactory) {
    let username = factory.create_text_field();
    let password = factory.create_text_field();
    let remember = factory.create_checkbox();
    let submit = factory.create_button();

    println!("  Username: {}", username.render());
    println!("  Password: {}", password.render());
    println!("  Remember: {}", remember.render());
    println!("  Submit:   {}", submit.render());
    println!("  Action:   {}", submit.on_click("submit_login()"));
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
fn main() {
    let preference = "dark"; // could come from config

    // The factory selection is the ONLY place concrete types appear
    let factory: Box<dyn UIFactory> = match preference {
        "dark" => Box::new(DarkThemeFactory),
        _ => Box::new(LightThemeFactory),
    };

    println!("Building login form with {} theme:", preference);
    build_login_form(&*factory);

    println!("\nBuilding login form with light theme:");
    build_login_form(&LightThemeFactory);
}
