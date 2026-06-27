import re
from datetime import datetime
from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class Order_Take:

    @staticmethod
    def input_booking_id():
        while True:
            booking_id = input("Enter booking ID (6 chars): ").strip().upper()
            if not booking_id:
                print("Booking ID cannot be empty.")
                continue
            if re.fullmatch(r"[A-F0-9]{6}", booking_id) is None:
                print("Invalid booking ID. Example: A1B2C3")
                continue
            return booking_id

    @staticmethod
    def input_item_name(inventory_list):
        while True:
            item_name = input("Item name: ").strip()
            if not item_name:
                print("Item name cannot be empty.")
                continue
            if not re.fullmatch(r"[A-Za-z &]+", item_name):
                print("Item name must contain letters only.")
                continue
            item_name  = item_name.title()
            found_item = next(
                (item for item in inventory_list if item.get("name") == item_name),
                None
            )
            if not found_item:
                print(f"'{item_name}' not found in inventory. Check spelling.")
                continue
            return found_item

    @staticmethod
    def input_size(found_item):
        """
        Only asks for size if the item has a half/full option.
        Breads are always 'none'.
        """
        if found_item.get("category") == "breads":
            return "none"
        if "available_half_qty" in found_item:
            while True:
                size = input("Size (half / full): ").strip().lower()
                if size in ("half", "full"):
                    return size
                print("Please enter 'half' or 'full'.")
        return "none"

    @staticmethod
    def input_quantity():
        while True:
            try:
                qty = int(input("Quantity: ").strip())
                if qty <= 0:
                    print("Quantity must be greater than 0.")
                    continue
                return qty
            except ValueError:
                print("Please enter a number.")

    @staticmethod
    def check_and_deduct_stock(found_item, size, qty):
        """
        Checks if enough stock exists then deducts it.
        Returns True on success, False if stock is insufficient.

        Stock logic:
          - Breads        -> available_qty,      deduct qty directly
          - half order    -> available_half_qty,  deduct qty
          - full order    -> available_half_qty,  deduct qty * 2
          - other items   -> available_qty,       deduct qty directly
        """
        category = found_item.get("category")

        if category == "breads":
            available = found_item.get("available_qty",
                        found_item.get("available_half_qty", 0))
            if available < qty:
                print(f"Not enough stock. Available: {available}")
                return False
            key = "available_qty" if "available_qty" in found_item else "available_half_qty"
            found_item[key] = available - qty
            print(f"Stock remaining: {found_item[key]}")

        elif "available_half_qty" in found_item:
            required  = qty if size == "half" else qty * 2
            available = found_item.get("available_half_qty", 0)
            if available < required:
                print(f"Not enough stock. Available (half units): {available}")
                return False
            found_item["available_half_qty"] = available - required
            print(f"Stock remaining (half units): {found_item['available_half_qty']}")

        else:
            available = found_item.get("available_qty", 0)
            if available < qty:
                print(f"Not enough stock. Available: {available}")
                return False
            found_item["available_qty"] = available - qty
            print(f"Stock remaining: {found_item['available_qty']}")

        return True

    @staticmethod
    def take_order():
        print("\n" + "=" * 45)
        print("             TAKE NEW ORDER")
        print("=" * 45)

        booking_id = Order_Take.input_booking_id()

        # Validate booking exists and is active
        reservations_data = ReadWrite.read(Path.reservations_data_path)
        if not reservations_data or "reservations" not in reservations_data:
            print("Reservations data not found.")
            return

        reservation = next(
            (r for r in reservations_data["reservations"]
             if r.get("reservation_id") == booking_id
             and r.get("status") == "booked"),
            None
        )

        if reservation is None:
            print("No active booking found with this ID.")
            return

        customer_name = reservation.get("customer_name", "N/A")
        table_name    = reservation.get("table_name",    "N/A")
        booking_date  = reservation.get("date",          "N/A")
        booking_slot  = reservation.get("time_slot",     "N/A")

        print(f"\nBooking : {table_name}  |  {booking_date}  |  {booking_slot}")
        print(f"Customer: {customer_name}")

        # Check no order already exists for this booking
        orders_data = ReadWrite.read(Path.orders_data_path)
        if not orders_data:
            orders_data = {"orders": []}
        if "orders" not in orders_data:
            orders_data["orders"] = []

        existing = next(
            (o for o in orders_data["orders"]
             if o.get("reservation_id") == booking_id),
            None
        )
        if existing:
            print(f"An order already exists for this booking (Order ID: {existing.get('order_id')}).")
            return

        # Load inventory
        inventory_data = ReadWrite.read(Path.inventory_data_path)
        if not inventory_data or "inventory" not in inventory_data:
            print("Inventory data not found.")
            return

        inventory_list = inventory_data["inventory"]
        order_items    = []

        while True:
            # Show available items
            print("\n" + "-" * 60)
            print(f"{'No':<4} {'Item':<30} {'Stock':<8} {'Category'}")
            print("-" * 60)
            for i, item in enumerate(inventory_list):
                qty    = item.get("available_half_qty", item.get("available_qty", 0))
                status = "LOW" if qty < 20 else ""
                print(
                    f"{i+1:<4} {item.get('name','')[:29]:<30} "
                    f"{qty:<8} {item.get('category',''):<15} {status}"
                )
            print("-" * 60)

            found_item = Order_Take.input_item_name(inventory_list)
            size       = Order_Take.input_size(found_item)
            qty        = Order_Take.input_quantity()

            success = Order_Take.check_and_deduct_stock(found_item, size, qty)
            if not success:
                continue

            # If item+size already in order, add to existing line
            existing_line = next(
                (line for line in order_items
                 if line["item_name"] == found_item.get("name")
                 and line["size"] == size),
                None
            )
            if existing_line:
                existing_line["quantity"] += qty
            else:
                order_items.append({
                    "item_name": found_item.get("name"),
                    "category" : found_item.get("category"),
                    "size"     : size,
                    "quantity" : qty
                })

            # Save inventory after every item
            ReadWrite.write_json(inventory_data, Path.inventory_data_path)
            print("Item added to order.")

            while True:
                more = input("Add more items? (y / n): ").strip().lower()
                if more in ("y", "n"):
                    break
                print("Please enter y or n.")

            if more == "n":
                break

        if not order_items:
            print("No items added. Order cancelled.")
            return

        new_order = {
            "order_id"      : len(orders_data["orders"]) + 1,
            "reservation_id": booking_id,
            "customer_name" : customer_name,
            "table_id"      : reservation.get("table_id"),
            "table_name"    : table_name,
            "order_datetime": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "order_status"  : "pending",
            "items"         : order_items
        }

        orders_data["orders"].append(new_order)
        ReadWrite.write_json(orders_data, Path.orders_data_path)

        print("\n" + "-" * 40)
        print(f"Order placed successfully!")
        print(f"  Order ID   : {new_order['order_id']}")
        print(f"  Booking ID : {booking_id}")
        print(f"  Items      : {len(order_items)}")
        print("-" * 40)