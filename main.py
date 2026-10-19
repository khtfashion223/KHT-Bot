# KHT FASHION HOUSE BOT

products = []

def add_product():
    name = input("Product name: ")
    cost = float(input("Cost price: "))
    price = float(input("Selling price: "))

    product = {
        "name": name,
        "cost": cost,
        "price": price
    }

    products.append(product)
    print("Product added successfully!")

def show_products():
    if not products:
        print("No products available.")
        return

    for product in products:
        print(
            product["name"],
            "| Price:", product["price"],
            "| Profit:", product["price"] - product["cost"]
        )

def main():
    while True:
        print("\n=== KHT FASHION HOUSE ===")
        print("1. Add Product")
        print("2. Show Products")
        print("3. Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            show_products()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
