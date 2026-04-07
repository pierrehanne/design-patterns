"""
Facade Pattern
==============
Category: Structural Design Pattern

Intent:
    Provide a unified, simplified interface to a set of interfaces in a complex
    subsystem. The facade hides the complexity and makes the subsystem easier
    to use for common tasks.

When to use:
    - When a subsystem has many interacting classes and clients only need simple operations
    - When you want to layer your system (facade = entry point to each layer)
    - When you want to decouple clients from subsystem internals

Key Participants:
    - Facade: Simple interface that delegates to subsystem classes
    - Subsystem classes: Do the actual work, unaware of the facade
    - Client: Uses the facade instead of calling subsystem classes directly

Note:
    The facade doesn't prevent direct subsystem access — it just provides
    a convenient shortcut for the most common use cases.
"""


# ---------------------------------------------------------------------------
# Subsystem classes — each handles one concern of order processing
# ---------------------------------------------------------------------------
class InventoryService:
    """Manages product stock levels."""

    def __init__(self) -> None:
        self._stock: dict[str, int] = {
            "LAPTOP-001": 50,
            "MOUSE-002": 200,
            "KEYBOARD-003": 75,
        }

    def check_availability(self, product_id: str, quantity: int) -> bool:
        available = self._stock.get(product_id, 0)
        return available >= quantity

    def reserve(self, product_id: str, quantity: int) -> bool:
        if not self.check_availability(product_id, quantity):
            return False
        self._stock[product_id] -= quantity
        print(f"  [Inventory] Reserved {quantity}x {product_id}")
        return True


class PaymentService:
    """Processes payments."""

    def charge(self, customer_id: str, amount: float) -> dict:
        # Simulates payment processing
        print(f"  [Payment] Charged ${amount:.2f} to customer {customer_id}")
        return {"success": True, "transaction_id": f"PAY-{id(self)}", "amount": amount}


class ShippingService:
    """Handles shipping logistics."""

    def calculate_cost(self, weight_kg: float, destination: str) -> float:
        base_rate = 5.99
        per_kg = 1.50
        return base_rate + (weight_kg * per_kg)

    def create_shipment(self, order_id: str, destination: str) -> dict:
        print(f"  [Shipping] Created shipment for order {order_id} to {destination}")
        return {"tracking_number": f"SHIP-{id(self)}", "destination": destination}


class NotificationService:
    """Sends notifications to customers."""

    def send_email(self, email: str, subject: str, body: str) -> None:
        print(f"  [Notification] Email to {email}: {subject}")

    def send_sms(self, phone: str, message: str) -> None:
        print(f"  [Notification] SMS to {phone}: {message}")


# ---------------------------------------------------------------------------
# Facade — simplifies the complex order processing workflow
# ---------------------------------------------------------------------------
class OrderFacade:
    """
    Provides a simple interface for placing orders. Internally coordinates
    inventory, payment, shipping, and notification services.

    Without the facade, the client would need to know about and coordinate
    all four services manually.
    """

    def __init__(self) -> None:
        self._inventory = InventoryService()
        self._payment = PaymentService()
        self._shipping = ShippingService()
        self._notification = NotificationService()

    def place_order(
        self,
        customer_id: str,
        email: str,
        product_id: str,
        quantity: int,
        unit_price: float,
        destination: str,
    ) -> dict:
        """
        One simple call replaces what would be 5+ subsystem calls.
        The facade orchestrates the entire workflow.
        """
        print(f"Processing order for {customer_id}...")

        # Step 1: Check and reserve inventory
        if not self._inventory.reserve(product_id, quantity):
            return {"success": False, "error": "Product out of stock"}

        # Step 2: Calculate total with shipping
        shipping_cost = self._shipping.calculate_cost(quantity * 0.5, destination)
        total = (unit_price * quantity) + shipping_cost

        # Step 3: Process payment
        payment = self._payment.charge(customer_id, total)
        if not payment["success"]:
            return {"success": False, "error": "Payment failed"}

        # Step 4: Create shipment
        order_id = f"ORD-{id(self)}"
        shipment = self._shipping.create_shipment(order_id, destination)

        # Step 5: Notify customer
        self._notification.send_email(
            email,
            "Order Confirmed!",
            f"Order {order_id} — tracking: {shipment['tracking_number']}",
        )

        return {
            "success": True,
            "order_id": order_id,
            "total": total,
            "tracking": shipment["tracking_number"],
        }


# ---------------------------------------------------------------------------
# Usage Example
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Client uses one simple call instead of coordinating 4 services
    facade = OrderFacade()

    result = facade.place_order(
        customer_id="CUST-42",
        email="alice@example.com",
        product_id="LAPTOP-001",
        quantity=2,
        unit_price=999.99,
        destination="New York, NY",
    )

    print(f"\nOrder result: {result}")

    # Demonstrate out-of-stock scenario
    print("\n--- Out of stock scenario ---")
    result2 = facade.place_order(
        customer_id="CUST-99",
        email="bob@example.com",
        product_id="NONEXISTENT",
        quantity=1,
        unit_price=49.99,
        destination="LA, CA",
    )
    print(f"Order result: {result2}")
