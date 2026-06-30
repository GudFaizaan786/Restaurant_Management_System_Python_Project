import re
from datetime import datetime, timedelta
from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.model.time_slots import TimeSlots
from app.domain.new_customer_order import NewCustomerOrder
from app.domain.receipt_printer import ReceiptPrinter
import uuid


class Customer_handle:

    

    @staticmethod
    def menu_show_customer(email, name):
        while True:
            print("\n" + "=" * 35)
            print(f"  Welcome, {name.split()[0]}!")
            print("=" * 35)
            print("1. View Menu")
            print("2. New Order")
            print("3. My Orders")
            print("4. Pay Bill")
            print("5. View Receipt")
            print("6. Logout")
            print("=" * 35)

            try:
                choice = int(input("Please enter your choice: ").strip())
            except ValueError:
                print("Please enter a number.")
                continue

            if choice == 1:
                Customer_handle.view_menu()
            elif choice == 2:
                Customer_handle.new_order(email, name)
            elif choice == 3:
                Customer_handle.my_orders(email)
            elif choice == 4:
                Customer_handle.pay_bill(email)
            elif choice == 5:
                Customer_handle.view_receipt(email)
            elif choice == 6:
                print("Logged out successfully.")
                break
            else:
                print("Invalid choice. Enter 1 to 6.")

    # ------------------------------------------------------------------
    # OPTION 1 — VIEW MENU
    # ------------------------------------------------------------------

    @staticmethod
    def view_menu():
        menu_data = ReadWrite.read(Path.food_item_path)
        menu      = menu_data.get("menu", {})

        print("\n" + "=" * 70)
        print(f"{menu_data.get('restaurant_name','FlavorPoint'):^70}")
        print(f"{menu_data.get('location',''):^70}")
        print("=" * 70)

        for category, items in menu.items():
            print(f"\n  --- {category.replace('_',' ').upper()} ---")
            print(f"  {'Item':<35} {'Price'}")
            print("  " + "-" * 55)

            for item in items:
                price = item.get("price", {})
                name  = item.get("name", "")

                if isinstance(price, dict):
                    print(f"  {name:<35} Half: Rs{price.get('half',0)}  Full: Rs{price.get('full',0)}")
                else:
                    print(f"  {name:<35} Rs{price}")

        print("\n" + "=" * 70)
        input("\nPress Enter to continue...")

    # ------------------------------------------------------------------
    # OPTION 2 — NEW ORDER
    # ------------------------------------------------------------------

    @staticmethod
    def new_order(email, name):
        """
        Full guided flow:
        Browse menu → build cart → book table → save order → show Booking ID
        Uses NewCustomerOrder internally but passes customer details automatically.
        """
        print("\n" + "=" * 50)
        print(f"{'NEW ORDER':^50}")
        print("=" * 50)
        print("Step 1 of 3 : Browse menu and select items")
        print("Step 2 of 3 : Book a table")
        print("Step 3 of 3 : Confirm and get Booking ID")
        print("=" * 50)

        # Load all data
        menu_data         = ReadWrite.read(Path.food_item_path)
        tables_data       = ReadWrite.read(Path.tables_data_path)
        reservations_data = ReadWrite.read(Path.reservation_data_path)
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

        # Step 1 — Browse menu
        print("\n[ STEP 1 OF 3 ] — Select your items")
        cart = NewCustomerOrder.browse_menu(menu_data)

        # Show cart summary
        NewCustomerOrder.show_cart_summary(cart, menu_data)

        confirm = input("\nProceed to table booking? (y / n): ").strip().lower()
        if confirm != "y":
            print("Order cancelled.")
            return

        # Step 2 — Book table
        # Customer name comes from their login — no need to ask again
        print("\n[ STEP 2 OF 3 ] — Book a table")

        booking_date = NewCustomerOrder.input_booking_date()

        max_capacity = max(
            (t.get("capacity", 0) for t in tables_list), default=0
        )
        if max_capacity <= 0:
            print("No tables available.")
            return

        seats = NewCustomerOrder.input_seats(max_capacity)

        # Show available slots
        slots = NewCustomerOrder.get_available_slots(booking_date)
        if not slots:
            print("No time slots available for this date.")
            return

        print("\nAvailable time slots:")
        for i, slot in enumerate(slots, 1):
            print(f"  {i}. {slot}")

        slot_number   = NewCustomerOrder.pick_from_list("Select slot number: ", len(slots))
        selected_slot = slots[slot_number - 1]

        # Find available tables
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
            return

        available_tables.sort(key=lambda x: x.get("capacity", 0))

        print(f"\nAvailable tables for {selected_slot}:")
        for j, t in enumerate(available_tables, 1):
            print(f"  {j}. {t.get('table_name')}  (capacity {t.get('capacity')})")

        table_number = NewCustomerOrder.pick_from_list(
            "Select table number: ", len(available_tables)
        )
        chosen_table = available_tables[table_number - 1]

        # Check and deduct inventory
        stock_ok = NewCustomerOrder.deduct_inventory(cart, inventory_list)
        if not stock_ok:
            print("Some items are out of stock. Order cancelled.")
            return

        # Step 3 — Save everything
        reservation_id = NewCustomerOrder.make_reservation_id(reservations_list)
        created_at     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_datetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        new_reservation = {
            "reservation_id": reservation_id,
            "customer_name" : name,
            "customer_email": email,
            "table_id"      : chosen_table.get("table_id"),
            "table_name"    : chosen_table.get("table_name"),
            "date"          : booking_date,
            "time_slot"     : selected_slot,
            "seats"         : seats,
            "status"        : "booked",
            "created_at"    : created_at
        }
        reservations_list.append(new_reservation)

        new_order = {
            "order_id"      : len(orders_data["orders"]) + 1,
            "reservation_id": reservation_id,
            "customer_name" : name,
            "customer_email": email,
            "table_id"      : chosen_table.get("table_id"),
            "table_name"    : chosen_table.get("table_name"),
            "order_datetime": order_datetime,
            "order_status"  : "pending",
            "items"         : cart
        }
        orders_data["orders"].append(new_order)

        ReadWrite.write_json(reservations_data, Path.reservation_data_path)
        ReadWrite.write_json(orders_data,       Path.orders_data_path)
        ReadWrite.write_json(inventory_data,    Path.inventory_data_path)

        # Confirmation
        print("\n" + "=" * 50)
        print(f"{'ORDER CONFIRMED':^50}")
        print("=" * 50)
        print(f"  Booking ID   : {reservation_id}")
        print(f"  Customer     : {name}")
        print(f"  Table        : {chosen_table.get('table_name')}  "
              f"(capacity {chosen_table.get('capacity')})")
        print(f"  Date         : {booking_date}")
        print(f"  Time Slot    : {selected_slot}")
        print(f"  Seats        : {seats}")
        print(f"  Order ID     : {new_order['order_id']}")
        print(f"  Total Items  : {len(cart)}")
        print("=" * 50)
        print(f"\n  *** Save your Booking ID ***")
        print(f"\n         >>  {reservation_id}  <<")
        print(f"\n  Use this ID to pay and get your bill.")
        print("=" * 50)

        input("\nPress Enter to continue...")

    # ------------------------------------------------------------------
    # OPTION 3 — MY ORDERS
    # ------------------------------------------------------------------

    @staticmethod
    def my_orders(email):
        """Shows only orders that belong to this customer."""
        orders_data = ReadWrite.read(Path.orders_data_path)
        if not orders_data or "orders" not in orders_data:
            print("\nNo orders found.")
            input("\nPress Enter to continue...")
            return

        all_orders = orders_data["orders"]

        # Filter by customer email
        my = [
            o for o in all_orders
            if o.get("customer_email", "").lower() == email.lower()
        ]

        if not my:
            print("\nYou have no orders yet.")
            input("\nPress Enter to continue...")
            return

        print("\n" + "=" * 60)
        print(f"{'MY ORDERS':^60}")
        print("=" * 60)

        for order in my:
            status     = order.get("order_status", "unknown").upper()
            order_time = order.get("order_datetime", "N/A")

            print(f"\n  Order ID    : {order.get('order_id')}")
            print(f"  Booking ID  : {order.get('reservation_id')}")
            print(f"  Table       : {order.get('table_name')}")
            print(f"  Date & Time : {order_time}")
            print(f"  Status      : {status}")

            items = order.get("items", [])
            if items:
                print(f"  Items:")
                for item in items:
                    size = item.get("size", "none")
                    size_lbl = f"({size})" if size != "none" else ""
                    print(f"    - {item.get('item_name')} {size_lbl} x{item.get('quantity')}")

            if order.get("total_amount"):
                print(f"  Total Paid  : Rs {order.get('total_amount'):,.0f} "
                      f"({order.get('payment_method','').upper()})")

            print("  " + "-" * 55)

        input("\nPress Enter to continue...")

    # ------------------------------------------------------------------
    # OPTION 4 — PAY BILL
    # ------------------------------------------------------------------

    @staticmethod
    def pay_bill(email):
        """
        Customer pays their own order using their Booking ID.
        Validates that the order belongs to them before processing.
        """
        print("\n" + "=" * 40)
        print(f"{'PAY BILL':^40}")
        print("=" * 40)

        # Ask for booking ID
        while True:
            booking_id = input("Enter your Booking ID: ").strip().upper()
            if not booking_id:
                print("Cannot be empty.")
                continue
            if re.fullmatch(r"[A-F0-9]{6}", booking_id) is None:
                print("Invalid Booking ID. Example: A1B2C3")
                continue
            break

        orders_data       = ReadWrite.read(Path.orders_data_path)
        food_data         = ReadWrite.read(Path.food_item_path)
        reservations_data = ReadWrite.read(Path.reservations_data_path)

        if not orders_data or not food_data or not reservations_data:
            print("Data not found.")
            return

        orders_list       = orders_data["orders"]
        reservations_list = reservations_data["reservations"]

        # Find reservation
        reservation = next(
            (r for r in reservations_list
             if r.get("reservation_id") == booking_id
             and r.get("status") == "booked"),
            None
        )
        if reservation is None:
            print("No active booking found with this ID.")
            return

        # Find order
        order = next(
            (o for o in orders_list
             if o.get("reservation_id") == booking_id),
            None
        )
        if order is None:
            print("No order found for this Booking ID.")
            return

        # Security check — order must belong to this customer
        if order.get("customer_email", "").lower() != email.lower():
            print("This booking does not belong to your account.")
            return

        if order.get("order_status") == "paid":
            print("This order has already been paid.")
            return

        # Build bill
        menu     = food_data.get("menu", {})
        items    = order.get("items", [])
        rows     = []
        subtotal = 0

        for it in items:
            name   = it.get("item_name")
            size   = it.get("size", "none")
            qty    = it.get("quantity", 0)
            price  = 0

            for cat_items in menu.values():
                for mi in cat_items:
                    if mi.get("name", "").lower() == name.lower():
                        p = mi.get("price", {})
                        if isinstance(p, dict):
                            price = p.get(size, p.get("full", 0))
                        else:
                            price = p
                        break

            amount    = price * qty
            subtotal += amount
            rows.append({
                "name": name, "size": size,
                "qty": qty, "price": price, "amount": amount
            })

        gst         = subtotal * 0.05
        grand_total = subtotal + gst

        # Show bill
        print(f"\n  Table    : {reservation.get('table_name')}")
        print(f"  Date     : {reservation.get('date')}  |  {reservation.get('time_slot')}")
        print("\n" + "  " + "-" * 52)
        print(f"  {'Item':<22} {'Size':<6} {'Qty':>4} {'Price':>7} {'Amt':>8}")
        print("  " + "-" * 52)

        for r in rows:
            size_lbl = r["size"] if r["size"] != "none" else "-"
            print(
                f"  {r['name'][:21]:<22} {size_lbl:<6} "
                f"{r['qty']:>4} {r['price']:>7.0f} {r['amount']:>8.0f}"
            )

        print("  " + "-" * 52)
        print(f"  {'Subtotal':<42} Rs{subtotal:>7.0f}")
        print(f"  {'GST @ 5%':<42} Rs{gst:>7.0f}")
        print(f"  {'GRAND TOTAL':<42} Rs{grand_total:>7.0f}")
        print("  " + "-" * 52)

        confirm = input("\nConfirm payment? (y / n): ").strip().lower()
        if confirm != "y":
            print("Payment cancelled.")
            return

        # Payment method
        while True:
            method = input("Payment method (cash / upi / card): ").strip().lower()
            if method in ("cash", "upi", "card"):
                break
            print("Please enter cash, upi or card.")

        # Save changes
        order["order_status"]   = "paid"
        order["payment_method"] = method
        order["paid_at"]        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order["total_amount"]   = grand_total

        reservation["status"]       = "completed"
        reservation["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ReadWrite.write_json(orders_data,       Path.orders_data_path)
        ReadWrite.write_json(reservations_data, Path.reservations_data_path)

        print(f"\n  Payment successful!")
        print(f"  Booking ID  : {booking_id}")
        print(f"  Grand Total : Rs {grand_total:.0f}")
        print(f"  Method      : {method.upper()}")

        # Auto print receipt
        ReceiptPrinter.print_after_payment(booking_id)

    # ------------------------------------------------------------------
    # OPTION 5 — VIEW RECEIPT
    # ------------------------------------------------------------------

    @staticmethod
    def view_receipt(email):
        """
        Customer can reprint receipt for any of their paid orders.
        Validates ownership before printing.
        """
        print("\n" + "=" * 40)
        print(f"{'VIEW RECEIPT':^40}")
        print("=" * 40)

        # First show their paid orders
        orders_data = ReadWrite.read(Path.orders_data_path)
        if not orders_data or "orders" not in orders_data:
            print("No orders found.")
            input("\nPress Enter to continue...")
            return

        paid_orders = [
            o for o in orders_data["orders"]
            if o.get("customer_email", "").lower() == email.lower()
            and o.get("order_status") == "paid"
        ]

        if not paid_orders:
            print("\nYou have no paid orders yet.")
            input("\nPress Enter to continue...")
            return

        print("\nYour paid orders:")
        print(f"  {'No':<4} {'Order ID':<10} {'Booking ID':<12} {'Date':<14} {'Total':>10}")
        print("  " + "-" * 55)

        for i, o in enumerate(paid_orders, 1):
            print(
                f"  {i:<4} "
                f"{str(o.get('order_id')):<10} "
                f"{o.get('reservation_id'):<12} "
                f"{o.get('order_datetime','N/A')[:10]:<14} "
                f"Rs {o.get('total_amount',0):>7,.0f}"
            )

        print("  " + "-" * 55)

        try:
            choice = int(input("\nEnter order number to view receipt (0 to cancel): ").strip())
            if choice == 0:
                return
            if not (1 <= choice <= len(paid_orders)):
                print("Invalid selection.")
                return
        except ValueError:
            print("Please enter a number.")
            return

        selected_order = paid_orders[choice - 1]
        booking_id     = selected_order.get("reservation_id")

        # Load reservation
        reservations_data = ReadWrite.read(Path.reservations_data_path)
        reservation = next(
            (r for r in reservations_data.get("reservations", [])
             if r.get("reservation_id") == booking_id),
            None
        )

        menu_data = ReadWrite.read(Path.food_item_path)
        ReceiptPrinter.print_receipt(selected_order, reservation, menu_data)