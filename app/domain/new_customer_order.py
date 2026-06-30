import re
import uuid
from datetime import datetime, timedelta
from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.model.time_slots import TimeSlots


class NewCustomerOrder:
 
    @staticmethod
    def make_reservation_id(reservations_list):
        """Generates a unique 6-character hex booking ID."""
        while True:
            rid    = uuid.uuid4().hex.upper()[:6]
            exists = any(r.get("reservation_id") == rid for r in reservations_list)
            if not exists:
                return rid

    @staticmethod
    def input_customer_name():
        while True:
            name = input("Customer name: ").strip()
            if len(name) < 2:
                print("Name must be at least 2 characters.")
                continue
            if re.fullmatch(r"[A-Za-z ]+", name) is None:
                print("Name must contain letters and spaces only.")
                continue
            return name.title()

    @staticmethod
    def input_booking_date():
        while True:
            date_str = input("Booking date (YYYY-MM-DD): ").strip()
            try:
                booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid format. Example: 2026-06-30")
                continue
            today    = datetime.now().date()
            max_date = today + timedelta(days=30)
            if booking_date < today:
                print("Past dates are not allowed.")
                continue
            if booking_date > max_date:
                print("Bookings only allowed up to 30 days ahead.")
                continue
            return date_str

    @staticmethod
    def input_seats(max_capacity):
        while True:
            try:
                seats = int(input(f"Number of seats (max {max_capacity}): ").strip())
                if seats <= 0:
                    print("Seats must be greater than 0.")
                    continue
                if seats > max_capacity:
                    print(f"Cannot exceed {max_capacity} seats.")
                    continue
                return seats
            except ValueError:
                print("Please enter a number.")

    @staticmethod
    def pick_from_list(prompt, count):
        while True:
            try:
                n = int(input(prompt).strip())
                if 1 <= n <= count:
                    return n
                print(f"Enter a number between 1 and {count}.")
            except ValueError:
                print("Please enter a number.")

    @staticmethod
    def get_available_slots(date_str):
        try:
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return []
        all_slots = TimeSlots.SLOTS
        today     = datetime.now().date()
        if booking_date != today:
            return all_slots
        now_time = datetime.now().time()
        result   = []
        for slot in all_slots:
            start_str  = slot.split("-")[0].strip()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            if start_time > now_time:
                result.append(slot)
        return result

    # ------------------------------------------------------------------
    # STEP 1 — SHOW MENU AND BUILD CART
    # ------------------------------------------------------------------

    @staticmethod
    def browse_menu(menu_data):
        """
        Shows the full menu category by category.
        Customer picks items and quantities.
        Returns a list of cart items.
        """
        menu = menu_data.get("menu", {})
        cart = []

        print("\n" + "=" * 50)
        print(f"{'FOOD MENU':^50}")
        print("=" * 50)

        # Build a flat numbered list of all items
        all_items = []

        for category, items in menu.items():
            print(f"\n  --- {category.replace('_',' ').upper()} ---")

            for item in items:
                all_items.append({
                    "name"    : item["name"],
                    "category": category,
                    "price"   : item["price"]
                })
                idx   = len(all_items)
                price = item["price"]

                if isinstance(price, dict):
                    print(f"  {idx:>3}. {item['name']:<30} Half: Rs{price['half']}  Full: Rs{price['full']}")
                else:
                    print(f"  {idx:>3}. {item['name']:<30} Rs{price}")

        print("\n" + "=" * 50)

        # Let customer pick items
        print("Enter item numbers to add to cart. Type 0 when done.\n")

        while True:
            try:
                choice = int(input("Item number (0 to finish): ").strip())
            except ValueError:
                print("Please enter a number.")
                continue

            if choice == 0:
                if not cart:
                    print("Cart is empty. Please add at least one item.")
                    continue
                break

            if not (1 <= choice <= len(all_items)):
                print(f"Please enter a number between 1 and {len(all_items)}.")
                continue

            selected = all_items[choice - 1]
            price    = selected["price"]

            # Ask size if item has half/full
            size = "none"
            if isinstance(price, dict) and selected["category"] != "breads":
                while True:
                    size = input(f"  Size for {selected['name']} (half / full): ").strip().lower()
                    if size in ("half", "full"):
                        break
                    print("  Please enter half or full.")

            # Ask quantity
            while True:
                try:
                    qty = int(input(f"  Quantity: ").strip())
                    if qty > 0:
                        break
                    print("  Quantity must be greater than 0.")
                except ValueError:
                    print("  Please enter a number.")

            # Check if same item+size already in cart — add to it
            existing = next(
                (c for c in cart
                 if c["item_name"] == selected["name"] and c["size"] == size),
                None
            )
            if existing:
                existing["quantity"] += qty
            else:
                cart.append({
                    "item_name": selected["name"],
                    "category" : selected["category"],
                    "size"     : size,
                    "quantity" : qty
                })

            # Show unit price confirmation
            if isinstance(price, dict):
                unit = price.get(size, price.get("full", 0))
            else:
                unit = price

            print(f"  Added: {selected['name']} x{qty}  @ Rs{unit} each")

            # Show current cart summary
            print(f"\n  Cart so far: {len(cart)} item(s)")
            for c in cart:
                print(f"    - {c['item_name']} ({c['size']}) x{c['quantity']}")
            print()

        return cart

    # ------------------------------------------------------------------
    # STEP 2 — SHOW CART SUMMARY WITH PRICES
    # ------------------------------------------------------------------

    @staticmethod
    def show_cart_summary(cart, menu_data):
        """
        Prints a full cart summary with subtotal and estimated total.
        Returns the estimated grand total.
        """
        print("\n" + "=" * 50)
        print(f"{'YOUR ORDER SUMMARY':^50}")
        print("=" * 50)
        print(f"  {'Item':<25} {'Size':<6} {'Qty':>4} {'Amount':>10}")
        print("  " + "-" * 48)

        subtotal = 0
        menu     = menu_data.get("menu", {})

        for cart_item in cart:
            name     = cart_item["item_name"]
            size     = cart_item["size"]
            qty      = cart_item["quantity"]
            price    = 0

            # Look up price from menu
            for category_items in menu.values():
                for menu_item in category_items:
                    if menu_item.get("name", "").lower() == name.lower():
                        p = menu_item.get("price", {})
                        if isinstance(p, dict):
                            price = p.get(size, p.get("full", 0))
                        else:
                            price = p
                        break

            amount    = price * qty
            subtotal += amount
            size_lbl  = size if size != "none" else "-"
            print(f"  {name[:24]:<25} {size_lbl:<6} {qty:>4} Rs{amount:>8.0f}")

        gst         = subtotal * 0.05
        grand_total = subtotal + gst

        print("  " + "-" * 48)
        print(f"  {'Subtotal':<38} Rs{subtotal:>8.0f}")
        print(f"  {'GST @ 5%':<38} Rs{gst:>8.0f}")
        print(f"  {'ESTIMATED TOTAL':<38} Rs{grand_total:>8.0f}")
        print("=" * 50)
        print("  (Final total confirmed at payment)")

        return grand_total

    # ------------------------------------------------------------------
    # STEP 3 — BOOK TABLE
    # ------------------------------------------------------------------

    @staticmethod
    def book_table_for_customer(reservations_list, tables_list):
        """
        Collects booking details and finds a suitable table.
        Returns (customer_name, booking_date, selected_slot,
                 chosen_table, seats) or None if failed.
        """
        print("\n" + "=" * 50)
        print(f"{'TABLE BOOKING':^50}")
        print("=" * 50)

        customer_name = NewCustomerOrder.input_customer_name()
        booking_date  = NewCustomerOrder.input_booking_date()

        max_capacity = max(
            (t.get("capacity", 0) for t in tables_list), default=0
        )
        if max_capacity <= 0:
            print("No valid tables available.")
            return None

        seats = NewCustomerOrder.input_seats(max_capacity)

        # Show available time slots
        slots = NewCustomerOrder.get_available_slots(booking_date)
        if not slots:
            print("No time slots available for this date.")
            return None

        print("\nAvailable time slots:")
        for i, slot in enumerate(slots, 1):
            print(f"  {i}. {slot}")

        slot_number   = NewCustomerOrder.pick_from_list("Select slot number: ", len(slots))
        selected_slot = slots[slot_number - 1]

        # Find tables that fit and are not already booked
        available_tables = []
        for t in tables_list:
            if t.get("capacity", 0) < seats:
                continue
            already_booked = any(
                r.get("status")    == "booked"
                and r.get("table_id")  == t.get("table_id")
                and str(r.get("date")) == booking_date
                and r.get("time_slot") == selected_slot
                for r in reservations_list
            )
            if not already_booked:
                available_tables.append(t)

        if not available_tables:
            print(f"No tables available for {selected_slot} on {booking_date}.")
            return None

        available_tables.sort(key=lambda x: x.get("capacity", 0))

        print(f"\nAvailable tables for {selected_slot}:")
        for j, t in enumerate(available_tables, 1):
            print(f"  {j}. {t.get('table_name')}  (capacity {t.get('capacity')})")

        table_number = NewCustomerOrder.pick_from_list(
            "Select table number: ", len(available_tables)
        )
        chosen_table = available_tables[table_number - 1]

        return customer_name, booking_date, selected_slot, chosen_table, seats

    # ------------------------------------------------------------------
    # STEP 4 — DEDUCT INVENTORY
    # ------------------------------------------------------------------

    @staticmethod
    def deduct_inventory(cart, inventory_list):
        """
        Deducts stock for every cart item.
        Returns True if all items had enough stock, False otherwise.
        """
        # First pass — check all stock before deducting anything
        for cart_item in cart:
            name     = cart_item["item_name"]
            size     = cart_item["size"]
            qty      = cart_item["quantity"]
            category = cart_item["category"]

            inv_item = next(
                (i for i in inventory_list if i.get("name", "").lower() == name.lower()),
                None
            )

            if inv_item is None:
                print(f"Warning: {name} not found in inventory.")
                continue

            if category == "breads":
                available = inv_item.get("available_qty",
                            inv_item.get("available_half_qty", 0))
                if available < qty:
                    print(f"Not enough stock for {name}. Available: {available}")
                    return False

            elif "available_half_qty" in inv_item:
                required  = qty if size == "half" else qty * 2
                available = inv_item.get("available_half_qty", 0)
                if available < required:
                    print(f"Not enough stock for {name}. Available (half units): {available}")
                    return False

        # Second pass — deduct
        for cart_item in cart:
            name     = cart_item["item_name"]
            size     = cart_item["size"]
            qty      = cart_item["quantity"]
            category = cart_item["category"]

            inv_item = next(
                (i for i in inventory_list if i.get("name", "").lower() == name.lower()),
                None
            )
            if inv_item is None:
                continue

            if category == "breads":
                key = "available_qty" if "available_qty" in inv_item else "available_half_qty"
                inv_item[key] -= qty

            elif "available_half_qty" in inv_item:
                required = qty if size == "half" else qty * 2
                inv_item["available_half_qty"] -= required

        return True

    # ------------------------------------------------------------------
    # MAIN FLOW — ties all steps together
    # ------------------------------------------------------------------

    @staticmethod
    def start():
        print("\n" + "=" * 50)
        print(f"{'NEW CUSTOMER ORDER':^50}")
        print("=" * 50)
        print("Step 1 of 3 : Browse menu and select items")
        print("Step 2 of 3 : Book a table")
        print("Step 3 of 3 : Confirm and get Booking ID")
        print("=" * 50)

        # Load all data
        menu_data         = ReadWrite.read(Path.food_item_path)
        tables_data       = ReadWrite.read(Path.tables_data_path)
        reservations_data = ReadWrite.read(Path.reservations_data_path)
        inventory_data    = ReadWrite.read(Path.inventory_data_path)
        orders_data       = ReadWrite.read(Path.orders_data_path)

        if not reservations_data or "reservations" not in reservations_data:
            reservations_data = {"reservations": []}
        if not orders_data or "orders" not in orders_data:
            orders_data = {"orders": []}

        tables_list       = (
            tables_data if isinstance(tables_data, list)
            else tables_data.get("tables", [])
        )
        reservations_list = reservations_data["reservations"]
        inventory_list    = inventory_data["inventory"]

        # ---- STEP 1 : Browse menu and build cart ----
        print("\n[ STEP 1 OF 3 ] — Browse menu and add items to cart")
        cart = NewCustomerOrder.browse_menu(menu_data)

        # ---- Show cart summary ----
        NewCustomerOrder.show_cart_summary(cart, menu_data)

        confirm = input("\nProceed to table booking? (y / n): ").strip().lower()
        if confirm != "y":
            print("Order cancelled.")
            return

        # ---- STEP 2 : Book table ----
        print("\n[ STEP 2 OF 3 ] — Book a table")
        result = NewCustomerOrder.book_table_for_customer(
            reservations_list, tables_list
        )
        if result is None:
            print("Table booking failed. Order cancelled.")
            return

        customer_name, booking_date, selected_slot, chosen_table, seats = result

        # ---- Check inventory ----
        stock_ok = NewCustomerOrder.deduct_inventory(cart, inventory_list)
        if not stock_ok:
            print("\nSome items are out of stock. Order cancelled.")
            return

        # ---- STEP 3 : Save everything ----
        reservation_id = NewCustomerOrder.make_reservation_id(reservations_list)
        created_at     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_datetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        # Save reservation
        new_reservation = {
            "reservation_id": reservation_id,
            "customer_name" : customer_name,
            "table_id"      : chosen_table.get("table_id"),
            "table_name"    : chosen_table.get("table_name"),
            "date"          : booking_date,
            "time_slot"     : selected_slot,
            "seats"         : seats,
            "status"        : "booked",
            "created_at"    : created_at
        }
        reservations_list.append(new_reservation)

        # Save order
        new_order = {
            "order_id"      : len(orders_data["orders"]) + 1,
            "reservation_id": reservation_id,
            "customer_name" : customer_name,
            "table_id"      : chosen_table.get("table_id"),
            "table_name"    : chosen_table.get("table_name"),
            "order_datetime": order_datetime,
            "order_status"  : "pending",
            "items"         : cart
        }
        orders_data["orders"].append(new_order)

        # Write all changes to disk
        ReadWrite.write_json(reservations_data, Path.reservations_data_path)
        ReadWrite.write_json(orders_data,        Path.orders_data_path)
        ReadWrite.write_json(inventory_data,     Path.inventory_data_path)

        # ---- STEP 3 : Confirmation ----
        print("\n" + "=" * 50)
        print(f"{'ORDER CONFIRMED':^50}")
        print("=" * 50)
        print(f"  Booking ID   : {reservation_id}")
        print(f"  Customer     : {customer_name}")
        print(f"  Table        : {chosen_table.get('table_name')}  "
              f"(capacity {chosen_table.get('capacity')})")
        print(f"  Date         : {booking_date}")
        print(f"  Time Slot    : {selected_slot}")
        print(f"  Seats        : {seats}")
        print(f"  Order ID     : {new_order['order_id']}")
        print(f"  Items        : {len(cart)}")
        print("=" * 50)
        print(f"\n  *** Give this Booking ID to the customer ***")
        print(f"\n         >>  {reservation_id}  <<")
        print(f"\n  Customer uses this ID for payment and bill.")
        print("=" * 50)

        input("\nPress Enter to continue...")