"""Module 2 · Lesson 9 — Async tools (parallel execution).

THE PROBLEM:
Three warehouse lookups at 2 seconds each = 6 seconds if done one by one.

THE FIX:
Make the tool `async` and use agent.invoke_async(). The three calls run in
PARALLEL, so the whole thing takes about 2 seconds instead of 6.

WATCH THE PRINTED TIMING at the end — that IS the lesson.

    python shivank2/09_async_tools.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from strands import Agent, tool
from strands.models.bedrock import BedrockModel
from my_project.aws.config import NOVA_LITE
from strands_tools import use_aws, http_request, calculator, file_write

class InventoryTools:
    def __init__(self):
        # Shared resource: all tools access the same data store.
        # In production: self.db = connect_to_database()   <-- opened ONCE
        self.products = {
            "PROD-123": {"name": "Wireless Mouse", "quantity": 15, "price": 29.99},
            "PROD-456": {"name": "USB-C Hub", "quantity": 0, "price": 49.99},
            "PROD-789": {"name": "Mechanical Keyboard", "quantity": 8, "price": 89.99},
        }

    @tool
    def check_stock(self, product_id: str) -> str:
        """Check product stock level.

        Args:
            product_id: The product ID to check
        """
        product = self.products.get(product_id)
        if not product:
            return f"Product {product_id} not found"
        return f"{product['name']}: {product['quantity']} units at ${product['price']}"

    @tool
    def update_stock(self, product_id: str, quantity: int) -> str:
        """Update product stock quantity.

        Args:
            product_id: The product ID to update
            quantity: New quantity to set
        """
        if product_id in self.products:
            self.products[product_id]["quantity"] = quantity
            return f"Updated {product_id} to {quantity} units"
        return f"Product {product_id} not found"

@tool
async def check_warehouse_inventory(product_id: str, warehouse: str) -> dict:
    """Check inventory at a specific warehouse.

    Args:
        product_id: Product ID to check
        warehouse: Warehouse identifier (e.g., "east", "west", "central")
    """
    # Simulate an API call delay
    await asyncio.sleep(2)

    data = {
        "east":    {"PROD-123": 45, "PROD-456": 12},
        "west":    {"PROD-123": 30, "PROD-456": 0},
        "central": {"PROD-123": 60, "PROD-456": 25},
    }

    quantity = data.get(warehouse, {}).get(product_id, 0)
    return {"warehouse": warehouse, "product_id": product_id, "quantity": quantity}


async def main():
    inventory = InventoryTools()
    agent = Agent(
        model=BedrockModel(model_id=NOVA_LITE),
        tools=[check_warehouse_inventory, use_aws, inventory.check_stock, inventory.update_stock, use_aws, http_request, calculator, file_write],
    )
    start = time.time()
    response = await agent.invoke_async(
        "List all IAM users in my account."
    )
    elapsed = time.time() - start
    print(response.message["content"][0]["text"])
    print(f"\nTotal time: {elapsed:.1f}s (sequential would be ~6s)")


if __name__ == "__main__":
    # In a script use asyncio.run(). In a Jupyter cell, just: await main()
    asyncio.run(main())
