from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.model.logs_path import Logs
from app.model.error_model import model
from app.validation.all_validation import Validation


class Manage_item:

    @staticmethod
    def add_item():
        data           = ReadWrite.read(Path.food_item_path)
        inventory_data = ReadWrite.read(Path.inventory_data_path)

        print("\nCategories: starters / main_course / breads / drinks / desserts")
        category = input("Enter category: ").strip().lower()

        if category not in data["menu"]:
            print("Invalid category.")
            return

        name = input("Enter item name: ").strip().title()

        if not name:
            print("Item name cannot be empty.")
            return

        if not name.replace(" ", "").isalpha():
            print("Item name must contain letters only.")
            return

        # Check for duplicate
        for item in data["menu"][category]:
            if item["name"].lower() == name.lower():
                print("This item already exists in the menu.")
                return

        try:
            if category in ["starters", "main_course"]:
                food_type = input("Type (veg / non-veg): ").strip().lower()
                if food_type not in ["veg", "non-veg"]:
                    print("Invalid type. Enter veg or non-veg.")
                    return

                half = int(input("Half price: Rs ").strip())
                full = int(input("Full price: Rs ").strip())

                if half <= 0 or full <= 0:
                    print("Price must be greater than 0.")
                    return

                new_item = {
                    "name" : name,
                    "type" : food_type,
                    "price": {"half": half, "full": full}
                }

            elif category == "breads":
                price = int(input("Price: Rs ").strip())
                if price <= 0:
                    print("Price must be greater than 0.")
                    return
                new_item = {"name": name, "price": price}

            else:  # drinks, desserts
                half = int(input("Half price: Rs ").strip())
                full = int(input("Full price: Rs ").strip())
                if half <= 0 or full <= 0:
                    print("Price must be greater than 0.")
                    return
                new_item = {"name": name, "price": {"half": half, "full": full}}

            quantity = Validation.opening_qty()

            # Add to inventory — breads use available_qty, everything else uses available_half_qty
            if category == "breads":
                inventory_data["inventory"].append({
                    "name"         : name,
                    "category"     : category,
                    "available_qty": quantity
                })
            else:
                inventory_data["inventory"].append({
                    "name"              : name,
                    "category"          : category,
                    "available_half_qty": quantity
                })

            data["menu"][category].append(new_item)
            ReadWrite.write_json(data, Path.food_item_path)
            ReadWrite.write_json(inventory_data, Path.inventory_data_path)
            print(f"{name} added successfully.")

        except ValueError:
            print("Price must be a number.")

    @staticmethod
    def delete_item():
        data           = ReadWrite.read(Path.food_item_path)
        inventory_data = ReadWrite.read(Path.inventory_data_path)

        print("\nCategories: starters / main_course / breads / drinks / desserts")
        category = input("Enter category: ").strip().lower()

        if category not in data["menu"]:
            print("Invalid category.")
            return

        items = data["menu"][category]

        if not items:
            print("No items in this category.")
            return

        print("\nAvailable items:")
        for item in items:
            print(f"  - {item['name']}")

        name_to_delete = input("Enter item name to delete: ").strip().lower()

        for item in items[:]:
            if item["name"].strip().lower() == name_to_delete:
                items.remove(item)

                # Remove from inventory too
                inv_items = inventory_data["inventory"]
                for inv in inv_items[:]:
                    if (inv["name"].strip().lower() == name_to_delete
                            and inv["category"] == category):
                        inv_items.remove(inv)

                ReadWrite.write_json(data, Path.food_item_path)
                ReadWrite.write_json(inventory_data, Path.inventory_data_path)
                print(f"Item deleted from menu and inventory successfully.")
                return

        print("Item not found.")

    @staticmethod
    def update_item(email):
        data           = ReadWrite.read(Path.food_item_path)
        inventory_data = ReadWrite.read(Path.inventory_data_path)

        print("\nCategories: starters / main_course / breads / drinks / desserts")
        category = input("Enter category: ").strip().lower()

        if category not in data["menu"]:
            print("Invalid category.")
            return

        items           = data["menu"][category]
        inventory_items = inventory_data["inventory"]

        if not items:
            print("No items in this category.")
            return

        print("\nAvailable items:")
        for item in items:
            print(f"  - {item['name']}")

        search_name = input("Enter item name to update: ").strip().lower()

        for item in items:
            if item["name"].strip().lower() == search_name:
                old_name = item["name"]

                print("\n1. Update Name")
                print("2. Update Price")
                if category in ["starters", "main_course"]:
                    print("3. Update Type  (veg / non-veg)")

                choice = Validation.menu_choice()

                if choice == 1:
                    new_name = input("New name: ").strip().title()
                    if not new_name:
                        print("Name cannot be empty.")
                        return
                    item["name"] = new_name
                    # Keep inventory name in sync
                    for inv in inventory_items:
                        if (inv["name"].strip().lower() == old_name.strip().lower()
                                and inv["category"] == category):
                            inv["name"] = new_name
                            break

                elif choice == 2:
                    try:
                        if isinstance(item["price"], dict):
                            print("1. Update Half Price")
                            print("2. Update Full Price")
                            print("3. Update Both")
                            price_choice = Validation.menu_choice()

                            if price_choice == 1:
                                item["price"]["half"] = int(input("New half price: Rs ").strip())
                            elif price_choice == 2:
                                item["price"]["full"] = int(input("New full price: Rs ").strip())
                            elif price_choice == 3:
                                item["price"]["half"] = int(input("New half price: Rs ").strip())
                                item["price"]["full"] = int(input("New full price: Rs ").strip())
                            else:
                                print("Invalid choice.")
                                return
                        else:
                            item["price"] = int(input("New price: Rs ").strip())

                    except ValueError as e:
                        print("Invalid price. Enter a number.")
                        ReadWrite.log_error(Logs.update_item, str(e), email, model.update)
                        return

                elif choice == 3 and category in ["starters", "main_course"]:
                    while True:
                        new_type = input("New type (veg / non-veg): ").strip().lower()
                        if new_type in ["veg", "v"]:
                            item["type"] = "veg"
                            break
                        elif new_type in ["non-veg", "nonveg", "n"]:
                            item["type"] = "non-veg"
                            break
                        else:
                            print("Invalid. Enter veg or non-veg.")
                else:
                    print("Invalid option.")
                    return

                ReadWrite.write_json(data, Path.food_item_path)
                ReadWrite.write_json(inventory_data, Path.inventory_data_path)
                print("Item updated successfully.")
                return

        print("Item not found.")