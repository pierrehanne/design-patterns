"""
Template Method Pattern
========================
Category: Behavioral Design Pattern

Intent:
    Define the skeleton of an algorithm in a base class, deferring some steps
    to subclasses. Template Method lets subclasses redefine certain steps of
    an algorithm without changing the algorithm's structure.

When to use:
    - You want to implement the invariant parts of an algorithm once and let
      subclasses provide the behavior that varies
    - Common behavior among subclasses should be factored and localized in a
      single class to avoid duplication
    - You want to control which steps subclasses can extend (hooks vs. required)

Key Participants:
    - AbstractClass (DataMiner): defines the template method and abstract steps
    - ConcreteClass (CSVMiner, JSONMiner, DatabaseMiner): implements the steps
    - Template Method (mine): the algorithm skeleton that calls the steps in order

Hollywood Principle:
    "Don't call us, we'll call you." -- The base class calls the subclass methods,
    not the other way around. Subclasses plug into the algorithm; they don't drive it.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# --- Abstract Class ---

class DataMiner(ABC):
    """
    Abstract class that defines the template method `mine()`.
    The algorithm skeleton is fixed; subclasses override individual steps.
    """

    def mine(self, source: str) -> None:
        """
        Template method: defines the algorithm skeleton.
        This method is final -- subclasses should NOT override it.
        """
        print(f"\n{'='*60}")
        print(f"  Mining data from: {source}")
        print(f"{'='*60}")

        raw_data = self.read_data(source)
        parsed = self.parse_data(raw_data)

        # Hook: optional pre-analysis step (subclasses may override)
        self.before_analysis(parsed)

        results = self.analyze_data(parsed)
        self.generate_report(results)

        # Hook: optional cleanup step
        self.cleanup()

        print("  Pipeline complete.\n")

    # --- Abstract steps (subclasses MUST implement) ---

    @abstractmethod
    def read_data(self, source: str) -> str:
        """Read raw data from the source."""
        pass

    @abstractmethod
    def parse_data(self, raw_data: str) -> list[dict]:
        """Parse raw data into structured records."""
        pass

    @abstractmethod
    def analyze_data(self, data: list[dict]) -> dict:
        """Analyze parsed data and produce results."""
        pass

    @abstractmethod
    def generate_report(self, results: dict) -> None:
        """Generate a report from the analysis results."""
        pass

    # --- Hook methods (subclasses CAN override, but don't have to) ---

    def before_analysis(self, data: list[dict]) -> None:
        """Hook: called before analysis. Override to add pre-processing."""
        pass

    def cleanup(self) -> None:
        """Hook: called after the pipeline. Override to release resources."""
        pass


# --- Concrete Classes ---

class CSVMiner(DataMiner):
    """Mines data from CSV files."""

    def read_data(self, source: str) -> str:
        print(f"  [CSV] Reading file: {source}")
        # Simulated CSV content
        return "name,age,city\nAlice,30,Paris\nBob,25,London\nCharlie,35,Berlin"

    def parse_data(self, raw_data: str) -> list[dict]:
        print("  [CSV] Parsing CSV rows...")
        lines = raw_data.strip().split("\n")
        headers = lines[0].split(",")
        records = []
        for line in lines[1:]:
            values = line.split(",")
            records.append(dict(zip(headers, values)))
        print(f"  [CSV] Parsed {len(records)} records")
        return records

    def analyze_data(self, data: list[dict]) -> dict:
        print("  [CSV] Analyzing age distribution...")
        ages = [int(r["age"]) for r in data]
        return {
            "count": len(ages),
            "average_age": sum(ages) / len(ages),
            "min_age": min(ages),
            "max_age": max(ages),
        }

    def generate_report(self, results: dict) -> None:
        print("  [CSV] Report:")
        for key, value in results.items():
            print(f"    {key}: {value}")


class JSONMiner(DataMiner):
    """Mines data from JSON sources."""

    def read_data(self, source: str) -> str:
        print(f"  [JSON] Fetching JSON from: {source}")
        # Simulated JSON content
        return '[{"product":"Widget","price":9.99},{"product":"Gadget","price":24.99},{"product":"Doohickey","price":4.99}]'

    def parse_data(self, raw_data: str) -> list[dict]:
        import json
        print("  [JSON] Parsing JSON array...")
        records = json.loads(raw_data)
        print(f"  [JSON] Parsed {len(records)} records")
        return records

    def analyze_data(self, data: list[dict]) -> dict:
        print("  [JSON] Analyzing price data...")
        prices = [r["price"] for r in data]
        return {
            "total_products": len(prices),
            "total_revenue_potential": sum(prices),
            "cheapest": min(prices),
            "most_expensive": max(prices),
        }

    def generate_report(self, results: dict) -> None:
        print("  [JSON] Report:")
        for key, value in results.items():
            print(f"    {key}: {value}")

    # Override hook: validate JSON structure before analysis
    def before_analysis(self, data: list[dict]) -> None:
        print("  [JSON] Validating schema: all records have 'product' and 'price'...")
        for record in data:
            assert "product" in record and "price" in record, f"Invalid record: {record}"
        print("  [JSON] Schema validation passed.")


class DatabaseMiner(DataMiner):
    """Mines data from a database connection."""

    def __init__(self) -> None:
        self._connection_open = False

    def read_data(self, source: str) -> str:
        print(f"  [DB] Connecting to database: {source}")
        self._connection_open = True
        print("  [DB] Executing query: SELECT * FROM users")
        # Simulated query result as string
        return "id:1,name:Alice,role:admin|id:2,name:Bob,role:user|id:3,name:Charlie,role:user"

    def parse_data(self, raw_data: str) -> list[dict]:
        print("  [DB] Parsing query results...")
        records = []
        for row in raw_data.split("|"):
            record = {}
            for field in row.split(","):
                key, value = field.split(":")
                record[key] = value
            records.append(record)
        print(f"  [DB] Parsed {len(records)} records")
        return records

    def analyze_data(self, data: list[dict]) -> dict:
        print("  [DB] Analyzing user roles...")
        roles: dict[str, int] = {}
        for record in data:
            role = record["role"]
            roles[role] = roles.get(role, 0) + 1
        return {"total_users": len(data), "role_distribution": roles}

    def generate_report(self, results: dict) -> None:
        print("  [DB] Report:")
        print(f"    Total users: {results['total_users']}")
        for role, count in results["role_distribution"].items():
            print(f"    {role}: {count}")

    # Override hook: close the database connection
    def cleanup(self) -> None:
        if self._connection_open:
            print("  [DB] Closing database connection...")
            self._connection_open = False


# --- Main ---

def main() -> None:
    # Each miner follows the same algorithm (mine), but the steps differ.
    # The base class controls the flow -- Hollywood Principle in action.

    miners: list[tuple[DataMiner, str]] = [
        (CSVMiner(), "users.csv"),
        (JSONMiner(), "https://api.example.com/products"),
        (DatabaseMiner(), "postgres://localhost:5432/mydb"),
    ]

    for miner, source in miners:
        miner.mine(source)


if __name__ == "__main__":
    main()
