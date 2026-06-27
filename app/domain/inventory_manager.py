from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.validation.all_validation import Validation


class InventoryManager:

    @staticmethod
    def get_inventory():
        data = ReadWrite.read(Path.inventory_data_path)
        return data.get("inventory", [])

    @staticmethod
    def save_inventory(inventory):
        ReadWrite.write_json({"inventory": inventory}, Path.inventory_data_path)

    @staticmethod
    def view_low_stock():
        inventory = InventoryManager.get_inventory()
        low = [
            item for item in inventory
            if item.get("available_half_qty", item.get("available_qty", 0)) < 100
        ]

        print("\n" + "=" * 50)
        print("         LOW STOCK ITEMS (below 100)")
        print("=" * 50)

        if not low:
            print("All items are sufficiently stocked.")
        else:
            print(f"{'No':<4} {'Item':<32} {'Stock'}")
            print("-" * 50)
            for i, item in enumerate(low):
                qty = item.get("available_half_qty", item.get("available_qty", 0))
                print(f"{i+1:<4} {item.get('name', 'N/A')[:31]:<32} {qty}")
        print("=" * 50)

    @staticmethod
    def view_all():
        inventory = InventoryManager.get_inventory()

        print("\n" + "=" * 60)
        print("              ALL INVENTORY")
        print("=" * 60)
        print(f"{'No':<4} {'Item':<30} {'Category':<15} {'Stock':<8} {'Status'}")
        print("-" * 60)

        for i, item in enumerate(inventory):
            qty    = item.get("available_half_qty", item.get("available_qty", 0))
            status = "LOW" if qty < 100 else "OK"
            print(
                f"{i+1:<4} "
                f"{item.get('name', 'N/A')[:29]:<30} "
                f"{item.get('category', 'N/A'):<15} "
                f"{qty:<8} "
                f"{status}"
            )
        print("-" * 60)

    @staticmethod
    def add_stock():
        inventory = InventoryManager.get_inventory()
        if not inventory:
            print("No inventory items found.")
            return

        print("\n" + "-" * 50)
        print(f"{'No':<4} {'Item':<32} {'Stock'}")
        print("-" * 50)
        for i, item in enumerate(inventory):
            qty = item.get("available_half_qty", item.get("available_qty", 0))
            print(f"{i+1:<4} {item.get('name', 'N/A')[:31]:<32} {qty}")
        print("-" * 50)

        try:
            choice = int(input("Enter item number to restock: ").strip())
            if not (1 <= choice <= len(inventory)):
                print("Invalid selection.")
                return

            item          = inventory[choice - 1]
            item_name     = item.get("name", "Unknown")
            current_stock = item.get("available_half_qty", item.get("available_qty", 0))

            print(f"\nItem: {item_name}")
            print(f"Current stock: {current_stock}")

            add_qty = int(input("Quantity to add: ").strip())
            if add_qty <= 0:
                print("Quantity must be greater than 0.")
                return

            new_stock = current_stock + add_qty

            if "available_half_qty" in item:
                item["available_half_qty"] = new_stock
            else:
                item["available_qty"] = new_stock

            InventoryManager.save_inventory(inventory)
            status = "OK" if new_stock >= 100 else "LOW STOCK"
            print(f"Updated: {current_stock} -> {new_stock}  [{status}]")

        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def manage_inventory():
        while True:
            print("\n" + "=" * 35)
            print("       MANAGE INVENTORY")
            print("=" * 35)
            print("1. View Low Stock  (below 100)")
            print("2. View All Inventory")
            print("3. Add Stock")
            print("0. Back")
            print("=" * 35)

            choice = Validation.menu_choice()

            if choice == 0:
                break
            elif choice == 1:
                InventoryManager.view_low_stock()
            elif choice == 2:
                InventoryManager.view_all()
            elif choice == 3:
                InventoryManager.add_stock()
            else:
                print("Invalid option.")

            input("\nPress Enter to continue...")