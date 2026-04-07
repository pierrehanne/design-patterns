/**
 * Abstract Factory Pattern
 * ========================
 * Category: Creational Design Pattern
 *
 * Intent:
 *   Provide an interface for creating FAMILIES of related objects without
 *   specifying their concrete classes. Unlike a simple Factory which creates
 *   one product type, Abstract Factory creates multiple related products
 *   guaranteed to work together.
 *
 * When to use:
 *   - When your system needs to create families of related objects
 *   - When you want to enforce that products from the same family are used together
 *   - When you want to swap entire product families (e.g., themes, OS widgets)
 *
 * Key Participants:
 *   - AbstractFactory: Declares creation methods for each product type
 *   - ConcreteFactory: Implements creation for a specific family
 *   - AbstractProduct: Interface for each kind of product
 *   - ConcreteProduct: Family-specific implementations
 */

// ---------------------------------------------------------------------------
// Abstract Products
// ---------------------------------------------------------------------------
interface Button {
  render(): string;
  onClick(handler: string): string;
}

interface Checkbox {
  render(): string;
  toggle(): string;
}

interface TextField {
  render(): string;
  setValue(value: string): string;
}

// ---------------------------------------------------------------------------
// Abstract Factory
// ---------------------------------------------------------------------------
interface UIFactory {
  createButton(): Button;
  createCheckbox(): Checkbox;
  createTextField(): TextField;
}

// ---------------------------------------------------------------------------
// Concrete Products — Dark Theme Family
// ---------------------------------------------------------------------------
class DarkButton implements Button {
  render(): string {
    return "<button class='bg-gray-800 text-white'>Click me</button>";
  }
  onClick(handler: string): string {
    return `Dark button triggers: ${handler}`;
  }
}

class DarkCheckbox implements Checkbox {
  render(): string {
    return "<input type='checkbox' class='border-gray-600 bg-gray-700' />";
  }
  toggle(): string {
    return "Dark checkbox toggled with smooth transition";
  }
}

class DarkTextField implements TextField {
  render(): string {
    return "<input type='text' class='bg-gray-800 text-white border-gray-600' />";
  }
  setValue(value: string): string {
    return `Dark text field set to: ${value}`;
  }
}

// ---------------------------------------------------------------------------
// Concrete Products — Light Theme Family
// ---------------------------------------------------------------------------
class LightButton implements Button {
  render(): string {
    return "<button class='bg-white text-black border-gray-300'>Click me</button>";
  }
  onClick(handler: string): string {
    return `Light button triggers: ${handler}`;
  }
}

class LightCheckbox implements Checkbox {
  render(): string {
    return "<input type='checkbox' class='border-gray-300 bg-white' />";
  }
  toggle(): string {
    return "Light checkbox toggled with crisp animation";
  }
}

class LightTextField implements TextField {
  render(): string {
    return "<input type='text' class='bg-white text-black border-gray-300' />";
  }
  setValue(value: string): string {
    return `Light text field set to: ${value}`;
  }
}

// ---------------------------------------------------------------------------
// Concrete Factories
// ---------------------------------------------------------------------------
class DarkThemeFactory implements UIFactory {
  createButton(): Button {
    return new DarkButton();
  }
  createCheckbox(): Checkbox {
    return new DarkCheckbox();
  }
  createTextField(): TextField {
    return new DarkTextField();
  }
}

class LightThemeFactory implements UIFactory {
  createButton(): Button {
    return new LightButton();
  }
  createCheckbox(): Checkbox {
    return new LightCheckbox();
  }
  createTextField(): TextField {
    return new LightTextField();
  }
}

// ---------------------------------------------------------------------------
// Client Code — works ONLY through abstract interfaces
// ---------------------------------------------------------------------------
function buildLoginForm(factory: UIFactory): void {
  const username = factory.createTextField();
  const password = factory.createTextField();
  const remember = factory.createCheckbox();
  const submit = factory.createButton();

  console.log("  Username:", username.render());
  console.log("  Password:", password.render());
  console.log("  Remember:", remember.render());
  console.log("  Submit:  ", submit.render());
  console.log("  Action:  ", submit.onClick("submit_login()"));
}

// ---------------------------------------------------------------------------
// Usage Example
// ---------------------------------------------------------------------------
const userPreference = "dark"; // could come from config, env, user setting

const factory: UIFactory =
  userPreference === "dark" ? new DarkThemeFactory() : new LightThemeFactory();

console.log(`Building login form with ${userPreference} theme:`);
buildLoginForm(factory);

console.log("\nBuilding login form with light theme:");
buildLoginForm(new LightThemeFactory());
