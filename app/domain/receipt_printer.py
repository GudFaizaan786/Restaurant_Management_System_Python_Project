import re
from datetime import datetime
from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class ReceiptPrinter:

    RECEIPT_WIDTH = 44

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _line(char="-"):
        """Prints a full-width divider line."""
        print(char * ReceiptPrinter.RECEIPT_WIDTH)

    @staticmethod
    def _center(text):
        """Prints text centered to receipt width."""
        print(text.center(ReceiptPrinter.RECEIPT_WIDTH))

    @staticmethod
    def _row(left, right):
        """Prints a left-aligned label and right-aligned value on one line."""
        space = ReceiptPrinter.RECEIPT_WIDTH - len(left) - len(right)
        print(left + " " * max(space, 1) + right)

    @staticmethod
    def get_item_price(menu_data, item_name, size):
        """Looks up unit price by item name and size from food_items.json."""
        for category_items in menu_data.get("menu", {}).values():
            for menu_item in category_items:
                if menu_item.get("name", "").lower() == item_name.lower():
                    price_data = menu_item.get("price", {})
                    if isinstance(price_data, dict):
                        if size in price_data:
                            return price_data[size]
                        return price_data.get("full", price_data.get("half", 0))
                    return price_data
        return 0

    # ------------------------------------------------------------------
    # CORE PRINTER
    # ------------------------------------------------------------------

    @staticmethod
    def print_receipt(order, reservation, menu_data):
        """
        Prints a fully formatted receipt for a given order.
        Called after payment or when reprinting.
        """
        line      = ReceiptPrinter._line
        center    = ReceiptPrinter._center
        row       = ReceiptPrinter._row
        get_price = ReceiptPrinter.get_item_price

        restaurant = menu_data.get("restaurant_name", "FlavorPoint")
        location   = menu_data.get("location", "")

        now = datetime.now().strftime("%d %b %Y  %I:%M %p")

        # ------ HEADER ------
        print()
        line("=")
        center(restaurant)
        center(location)
        line("=")
        center("PAYMENT RECEIPT")
        line("-")

        # ------ ORDER INFO ------
        row("Receipt Date :", now)
        row("Order ID     :", str(order.get("order_id",       "N/A")))
        row("Booking ID   :", str(order.get("reservation_id", "N/A")))
        row("Customer     :", str(order.get("customer_name",  "N/A")))
        row("Table        :", str(order.get("table_name",     "N/A")))

        if reservation:
            row("Date         :", str(reservation.get("date",      "N/A")))
            row("Time Slot    :", str(reservation.get("time_slot", "N/A")))
            row("Seats        :", str(reservation.get("seats",     "N/A")))

        order_time = order.get("order_datetime", "N/A")
        row("Order Time   :", str(order_time))

        paid_at = order.get("paid_at", "N/A")
        row("Paid At      :", str(paid_at))

        method = order.get("payment_method", "N/A").upper()
        row("Payment      :", method)

        line("-")

        # ------ ITEMS ------
        center("ITEMS ORDERED")
        line("-")

        header_left  = f"{'Item':<20} {'Sz':<5} {'Qty':>3}"
        header_right = f"{'Amt':>8}"
        row(header_left, header_right)
        line("-")

        items    = order.get("items", [])
        subtotal = 0.0

        for item in items:
            name   = item.get("item_name", "")
            size   = item.get("size", "none")
            qty    = item.get("quantity", 0)
            price  = get_price(menu_data, name, size)
            amount = price * qty
            subtotal += amount

            size_label = size[:2].upper() if size != "none" else "  "

            name_short = name[:20]
            left_part  = f"{name_short:<20} {size_label:<5} {qty:>3}"
            right_part = f"Rs{amount:>6.0f}"
            row(left_part, right_part)

            unit_line = f"  @ Rs{price:.0f} x {qty}"
            print(unit_line)

        line("-")

        # ------ TOTALS ------
        gst         = subtotal * 0.05
        grand_total = subtotal + gst

        row("Subtotal", f"Rs{subtotal:>8.0f}")
        row("GST @ 5%", f"Rs{gst:>8.0f}")
        line("-")
        row("GRAND TOTAL", f"Rs{grand_total:>8.0f}")
        line("=")

        # ------ STATUS ------
        status = order.get("order_status", "").upper()
        center(f"STATUS : {status}")
        center(f"PAID VIA {method}")
        line("=")

        # ------ FOOTER ------
        center("Thank you for dining with us!")
        center("Visit us again!")
        line("=")
        print()

    # ------------------------------------------------------------------
    # FIND ORDER
    # ------------------------------------------------------------------

    @staticmethod
    def find_order_and_reservation(identifier):
        """
        Looks up order and its matching reservation.
        identifier is either a booking ID string or an order ID integer.
        Returns (order, reservation) — reservation may be None.
        """
        orders_data       = ReadWrite.read(Path.orders_data_path)
        reservations_data = ReadWrite.read(Path.reservations_data_path)

        if not orders_data or "orders" not in orders_data:
            return None, None

        orders       = orders_data["orders"]
        reservations = reservations_data.get("reservations", []) if reservations_data else []

        order = None

        # Try as booking ID first
        if isinstance(identifier, str):
            order = next(
                (o for o in orders if o.get("reservation_id") == identifier),
                None
            )

        # Try as order ID
        if order is None and isinstance(identifier, int):
            order = next(
                (o for o in orders if o.get("order_id") == identifier),
                None
            )

        if order is None:
            return None, None

        reservation = next(
            (r for r in reservations
             if r.get("reservation_id") == order.get("reservation_id")),
            None
        )

        return order, reservation
 
    @staticmethod
    def input_identifier():
        """Accepts a booking ID (A1B2C3) or numeric order ID."""
        while True:
            val = input("Enter Booking ID (e.g. A1B2C3) or Order ID (number): ").strip().upper()
            if not val:
                print("Cannot be empty.")
                continue
            if re.fullmatch(r"[A-F0-9]{6}", val):
                return val                  # booking ID as string
            try:
                oid = int(val)
                if oid <= 0:
                    print("Order ID must be greater than 0.")
                    continue
                return oid                  # order ID as integer
            except ValueError:
                print("Invalid. Use Booking ID (A1B2C3) or Order ID (1, 2, 3...).")

     
    @staticmethod
    def reprint_receipt():
         
        print("\n" + "=" * 40)
        print(f"{'REPRINT RECEIPT':^40}")
        print("=" * 40)

        identifier = ReceiptPrinter.input_identifier()
        order, reservation = ReceiptPrinter.find_order_and_reservation(identifier)

        if order is None:
            print("Order not found.")
            return

        if order.get("order_status") != "paid":
            status = order.get("order_status", "unknown").upper()
            print(f"This order is not yet paid. Current status: {status}")
            print("Receipt can only be printed for paid orders.")
            return

        menu_data = ReadWrite.read(Path.food_item_path)
        ReceiptPrinter.print_receipt(order, reservation, menu_data)

    @staticmethod
    def print_after_payment(booking_id):
         
        order, reservation = ReceiptPrinter.find_order_and_reservation(booking_id)
        if order is None:
            print("Could not load receipt.")
            return
        menu_data = ReadWrite.read(Path.food_item_path)
        ReceiptPrinter.print_receipt(order, reservation, menu_data)