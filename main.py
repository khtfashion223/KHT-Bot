# KHT AI BOT
# Version 1.0

class KHTBot:
    def __init__(self):
        self.name = "KHT AI BOT"
        self.version = "1.0"

    def start(self):
        print("=" * 30)
        print(f"Welcome to {self.name}")
        print(f"Version: {self.version}")
        print("KHT Fashion House Management System")
        print("=" * 30)

    def menu(self):
        print("\n1. Product Management")
        print("2. Order Management")
        print("3. Profit Calculator")
        print("4. AI Assistant")
        print("5. Exit")

if __name__ == "__main__":
    bot = KHTBot()
    bot.start()
    bot.menu()
