import json
import os
from datetime import datetime

DATA_FILE = "kht_data.json"


class KHTFashionBot:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        return {"products": [], "orders": []}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                ensure_ascii=False,
                indent=2
            )

    def add_product(self):
        print("\n--- ADD PRODUCT ---")

        name = input("Product name: ").strip()

        if not name:
            print("Product name is required.")
            return

        try:
            cost = float(input("Cost price (MMK): "))
            price = float(input("Selling price (MMK): "))
            stock = int(input("Stock quantity: "))

            if cost < 0 or price < 0 or stock < 0:
                print("Values cannot be negative.")
                return

        except ValueError:
            print("Please enter valid numbers.")
            return

        product_id = max(
            [p["id"] for p in self.data["products"]],
            default=0
        ) + 1

        product = {
            "id": product_id,
            "name": name,
            "cost": cost,
            "price": price,
            "stock": stock
        }

        self.data["products"].append(product)
        self.save_data()

        print(f"Product added successfully! ID: {product_id}")

    def show_products(self):
        print("\n--- PRODUCT LIST ---")

        products = self.data["products"]

        if not products:
            print("No products available.")
            return

        for p in products:
            profit = p["price"] - p["cost"]

            print(
                f'ID: {p["id"]} | {p["name"]} | '
                f'Price: {p["price"]:,.0f} MMK | '
                f'Stock: {p["stock"]} | '
                f'Profit/unit: {profit:,.0f} MMK'
            )

    def create_order(self):
        print("\n--- NEW ORDER ---")

        customer = input("Customer name: ").strip()
        if not customer:
            print("Customer name is required.")
            return

        self.show_products()

        try:
            product_id = int(input("Product ID: "))
            quantity = int(input("Quantity: "))

            if quantity <= 0:
                print("Quantity must be greater than zero.")
                return

        except ValueError:
            print("Please enter valid numbers.")
            return

        product = next(
            (
                p for p in self.data["products"]
                if p["id"] == product_id
            ),
            None
        )

        if product is None:
            print("Product not found.")
            return

        if product["stock"] < quantity:
            print("Not enough stock.")
            return

        total = product["price"] * quantity
        cost = product["cost"] * quantity
        order_id = max(
            [o["id"] for o in self.data["orders"]],
            default=0
        ) + 1

        order = {
            "id": order_id,
            "customer": customer,
            "product_id": product_id,
            "product": product["name"],
            "quantity": quantity,
            "total": total,
            "cost": cost,
            "status": "Pending",
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            )
        }

        product["stock"] -= quantity
        self.data["orders"].append(order)
        self.save_data()

        print(f"Order #{order_id} created successfully!")
        print(f"Total: {total:,.0f} MMK")
        print("Status: Pending")

    def show_orders(self):
        print("\n--- ORDER LIST ---")

        orders = self.data["orders"]

        if not orders:
            print("No orders available.")
            return

        for o in orders:
            print(
                f'Order #{o["id"]} | {o["customer"]} | '
                f'{o["product"]} x{o["quantity"]} | '
                f'{o["total"]:,.0f} MMK | '
                f'Status: {o["status"]}'
            )

    def update_order(self):
        self.show_orders()

        try:
            order_id = int(input("Order ID: "))
        except ValueError:
            print("Invalid order ID.")
            return

        order = next(
            (
                o for o in self.data["orders"]
                if o["id"] == order_id
            ),
            None
        )

        if order is None:
            print("Order not found.")
            return

        print("1. Confirm")
        print("2. Shipped")
        print("3. Delivered")
        print("4. Cancel")

        choice = input("Select status: ").strip()

        statuses = {
            "1": "Confirmed",
            "2": "Shipped",
            "3": "Delivered",
            "4": "Cancelled"
        }

        if choice not in statuses:
            print("Invalid selection.")
            return

        new_status = statuses[choice]

        if order["status"] == "Cancelled":
            print("This order was already cancelled.")
            return

        if new_status == "Cancelled":
            product = next(
                (
                    p for p in self.data["products"]
                    if p["id"] == order["product_id"]
                ),
                None
            )

            if product:
                product["stock"] += order["quantity"]

        order["status"] = new_status
        self.save_data()

        print(f"Order #{order_id}: {new_status}")

    def show_profit(self):
        orders = [
            o for o in self.data["orders"]
            if o["status"] == "Delivered"
        ]

        revenue = sum(o["total"] for o in orders)
        cost = sum(o["cost"] for o in orders)
        profit = revenue - cost

        print("\n--- BUSINESS SUMMARY ---")
        print(f"Products: {len(self.data['products'])}")
        print(f"Total orders: {len(self.data['orders'])}")
        print(f"Delivered sales: {revenue:,.0f} MMK")
        print(f"Product cost: {cost:,.0f} MMK")
        print(f"Gross profit: {profit:,.0f} MMK")
        print(
            "Note: Delivery fees and other expenses "
            "are not included."
        )

    def run(self):
        while True:
            print("\n" + "=" * 32)
            print("   KHT FASHION HOUSE BOT")
            print("=" * 32)
            print("1. Add product")
            print("2. Show products")
            print("3. Create order")
            print("4. Show orders")
            print("5. Update order status")
            print("6. Business summary")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            actions = {
                "1": self.add_product,
                "2": self.show_products,
                "3": self.create_order,
                "4": self.show_orders,
                "5": self.update_order,
                "6": self.show_profit
            }

            if choice == "0":
                print("KHT Bot stopped.")
                break

            action = actions.get(choice)

            if action:
                action()
            else:
                print("Invalid option. Try again.")


if __name__ == "__main__":
    KHTFashionBot().run()
