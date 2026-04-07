"""
Abstract Factory Pattern
========================
Category: Creational Design Pattern

Intent:
    Provide an interface for creating FAMILIES of related objects without
    specifying their concrete classes. Unlike the simple Factory which creates
    one product type, Abstract Factory creates multiple related products that
    are designed to work together.

When to use:
    - When your system needs to create families of related objects
    - When you want to enforce that products from the same family are used together
    - When you want to swap entire product families (e.g., themes, OS widgets)

Key Participants:
    - AbstractFactory: Declares creation methods for each product type
    - ConcreteFactory: Implements creation methods for a specific family
    - AbstractProduct: Interface for each kind of product
    - ConcreteProduct: Family-specific implementations of each product

Difference from Factory Method:
    - Factory Method creates ONE product; Abstract Factory creates a FAMILY
    - Abstract Factory uses composition (a factory object), not inheritance
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# Abstract Products — each product type has its own interface
# ---------------------------------------------------------------------------
class Button(ABC):
    @abstractmethod
    def render(self) -> str:
        ...

    @abstractmethod
    def on_click(self, handler: str) -> str:
        ...


class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str:
        ...

    @abstractmethod
    def toggle(self) -> str:
        ...


class TextField(ABC):
    @abstractmethod
    def render(self) -> str:
        ...

    @abstractmethod
    def set_value(self, value: str) -> str:
        ...


# ---------------------------------------------------------------------------
# Concrete Products — Dark Theme Family
# ---------------------------------------------------------------------------
class DarkButton(Button):
    def render(self) -> str:
        return "<button class='bg-gray-800 text-white'>Click me</button>"

    def on_click(self, handler: str) -> str:
        return f"Dark button triggers: {handler}"


class DarkCheckbox(Checkbox):
    def render(self) -> str:
        return "<input type='checkbox' class='border-gray-600 bg-gray-700' />"

    def toggle(self) -> str:
        return "Dark checkbox toggled with smooth transition"


class DarkTextField(TextField):
    def render(self) -> str:
        return "<input type='text' class='bg-gray-800 text-white border-gray-600' />"

    def set_value(self, value: str) -> str:
        return f"Dark text field set to: {value}"


# ---------------------------------------------------------------------------
# Concrete Products — Light Theme Family
# ---------------------------------------------------------------------------
class LightButton(Button):
    def render(self) -> str:
        return "<button class='bg-white text-black border-gray-300'>Click me</button>"

    def on_click(self, handler: str) -> str:
        return f"Light button triggers: {handler}"


class LightCheckbox(Checkbox):
    def render(self) -> str:
        return "<input type='checkbox' class='border-gray-300 bg-white' />"

    def toggle(self) -> str:
        return "Light checkbox toggled with crisp animation"


class LightTextField(TextField):
    def render(self) -> str:
        return "<input type='text' class='bg-white text-black border-gray-300' />"

    def set_value(self, value: str) -> str:
        return f"Light text field set to: {value}"


# ---------------------------------------------------------------------------
# Abstract Factory
# ---------------------------------------------------------------------------
class UIFactory(ABC):
    """Creates a family of UI components that are guaranteed to work together."""

    @abstractmethod
    def create_button(self) -> Button:
        ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        ...

    @abstractmethod
    def create_text_field(self) -> TextField:
        ...


# ---------------------------------------------------------------------------
# Concrete Factories
# ---------------------------------------------------------------------------
class DarkThemeFactory(UIFactory):
    """Produces dark-themed UI components that share a consistent dark style."""

    def create_button(self) -> Button:
        return DarkButton()

    def create_checkbox(self) -> Checkbox:
        return DarkCheckbox()

    def create_text_field(self) -> TextField:
        return DarkTextField()


class LightThemeFactory(UIFactory):
    """Produces light-themed UI components that share a consistent light style."""

    def create_button(self) -> Button:
        return LightButton()

    def create_checkbox(self) -> Checkbox:
        return LightCheckbox()

    def create_text_field(self) -> TextField:
        return LightTextField()


# ---------------------------------------------------------------------------
# Client Code — works with factories and products through abstract interfaces
# ---------------------------------------------------------------------------
def build_login_form(factory: UIFactory) -> None:
    """
    This function has NO idea whether it's building a dark or light form.
    It only depends on the abstract UIFactory and abstract product interfaces.
    Swapping the factory swaps the entire look-and-feel.
    """
    username = factory.create_text_field()
    password = factory.create_text_field()
    remember = factory.create_checkbox()
    submit = factory.create_button()

    print("  Username:", username.render())
    print("  Password:", password.render())
    print("  Remember:", remember.render())
    print("  Submit:  ", submit.render())
    print("  Action:  ", submit.on_click("submit_login()"))


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # The theme choice is the ONLY place we reference concrete factories.
    # Everything else works through abstractions.
    user_preference = "dark"  # could come from config, env, user setting

    factory: UIFactory
    if user_preference == "dark":
        factory = DarkThemeFactory()
    else:
        factory = LightThemeFactory()

    print(f"Building login form with {user_preference} theme:")
    build_login_form(factory)

    print(f"\nBuilding login form with light theme:")
    build_login_form(LightThemeFactory())
