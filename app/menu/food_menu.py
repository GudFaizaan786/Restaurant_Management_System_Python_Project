from app.domain.read_write import ReadWrite
from app.model.json_file import Paths


class Food_menu:

    @staticmethod
    def food_items():
        data = ReadWrite.read(Paths.food_items_path)
        menu = data["menu"]

        print("\n" + "=" * 70)
        print(f"{data['restaurant_name']:^70}")
        print(f"{data['location']:^70}")
        print("=" * 70)

        # --- Starters and Main Course (have veg/non-veg and half/full price) ---
        for category in ["starters", "main_course"]:
            items = menu[category]
            category_title = category.replace("_", " ").upper()

            for food_type in ["veg", "non-veg"]:
                title = f"{category_title} - {food_type.upper()}"
                print(f"\n{title:^70}")
                print("-" * 70)
                print(f"{'ITEM NAME':<35} {'HALF':>10} {'FULL':>10}")
                print("-" * 70)
                for item in items:
                    if item["type"] == food_type:
                        half = item["price"]["half"]
                        full = item["price"]["full"]
                        print(f"{item['name']:<35} Rs{half:>8} Rs{full:>8}")

        # --- Breads (single price, no half/full) ---
        print(f"\n{'BREADS':^70}")
        print("-" * 70)
        print(f"{'ITEM NAME':<50} {'PRICE':>10}")
        print("-" * 70)
        for item in menu["breads"]:
            print(f"{item['name']:<50} Rs{item['price']:>8}")

        # --- Drinks (half/full price) ---
        print(f"\n{'DRINKS':^70}")
        print("-" * 70)
        print(f"{'ITEM NAME':<35} {'HALF':>10} {'FULL':>10}")
        print("-" * 70)
        for item in menu["drinks"]:
            half = item["price"]["half"]
            full = item["price"]["full"]
            print(f"{item['name']:<35} Rs{half:>8} Rs{full:>8}")

        # --- Desserts (half/full price) ---
        print(f"\n{'DESSERTS':^70}")
        print("-" * 70)
        print(f"{'ITEM NAME':<35} {'HALF':>10} {'FULL':>10}")
        print("-" * 70)
        for item in menu["desserts"]:
            half = item["price"]["half"]
            full = item["price"]["full"]
            print(f"{item['name']:<35} Rs{half:>8} Rs{full:>8}")

        print("\n" + "=" * 70)
        print(f"{'[ THANK YOU FOR VISITING ]':^70}")
        print("=" * 70)

        input("\nPress Enter to continue...")