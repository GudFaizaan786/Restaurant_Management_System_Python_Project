import re
from datetime import datetime
from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class DoPayment:

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
    def input_payment_method():
        while True:
            method = input("Payment method (cash / upi / card): ").strip().lower()
            if method in ("cash", "upi", "card"):
                return method
            print("Please enter cash, upi or card.")

    @staticmethod
    def get_item_price(menu_data, item_name, size):
        """Looks up price from food_items.json by item name and size."""
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

    @staticmethod
    def print_bill(bill_rows, subtotal, gst, grand_total):
        print("\n" + "=" * 58)
        print(f"{'No':<4} {'Item':<22} {'Size':<6} {'Qty':>4} {'Price':>7} {'Amount':>8}")
        print("-" * 58)
        for i, row in enumerate(bill_rows, 1):
            size_label = row["size"] if row["size"] != "none" else "-"
            print(
                f"{i:<4} {row['name'][:21]:<22} {size_label:<6} "
                f"{row['qty']:>4} {row['price']:>7} {row['amount']:>8}"
            )
        print("-" * 58)
        print(f"{'Subtotal':<45} Rs {subtotal:>6.0f}")
        print(f"{'GST @ 5%':<45} Rs {gst:>6.0f}")
        print(f"{'GRAND TOTAL':<45} Rs {grand_total:>6.0f}")
        print("=" * 58)

    @staticmethod
    def do_payment():
        print("\n" + "=" * 40)
        print("           DO PAYMENT")
        print("=" * 40)

        booking_id = DoPayment.input_booking_id()

        orders_data       = ReadWrite.read(Path.orders_data_path)
        food_data         = ReadWrite.read(Path.food_item_path)
        reservations_data = ReadWrite.read(Path.reservation_data_path)

        if not orders_data or "orders" not in orders_data:
            print("Orders data not found.")
            return
        if not food_data or "menu" not in food_data:
            print("Food items data not found.")
            return
        if not reservations_data or "reservations" not in reservations_data:
            print("Reservations data not found.")
            return

        # Find active reservation
        reservation = next(
            (r for r in reservations_data["reservations"]
             if r.get("reservation_id") == booking_id
             and r.get("status") == "booked"),
            None
        )
        if reservation is None:
            print("No active booking found with this ID.")
            return

        # Find order
        order = next(
            (o for o in orders_data["orders"]
             if o.get("reservation_id") == booking_id),
            None
        )
        if order is None:
            print("No food order found for this booking.")
            return

        if order.get("order_status") == "paid":
            print("This order has already been paid.")
            return

        items = order.get("items", [])
        if not items:
            print("Order has no items.")
            return

        # Build bill
        bill_rows = []
        subtotal  = 0

        for it in items:
            name  = it.get("item_name")
            size  = it.get("size", "none")
            qty   = it.get("quantity", 0)
            if not name or qty <= 0:
                continue
            price  = DoPayment.get_item_price(food_data, name, size)
            amount = price * qty
            subtotal += amount
            bill_rows.append({
                "name"  : name,
                "size"  : size,
                "qty"   : qty,
                "price" : price,
                "amount": amount
            })

        if not bill_rows:
            print("No valid items found in order.")
            return

        gst         = subtotal * 0.05
        grand_total = subtotal + gst

        print(f"\nTable    : {reservation.get('table_name')}")
        print(f"Customer : {order.get('customer_name')}")
        print(f"Date     : {reservation.get('date')}  |  Slot: {reservation.get('time_slot')}")

        DoPayment.print_bill(bill_rows, subtotal, gst, grand_total)

        confirm = input("Confirm payment? (y / n): ").strip().lower()
        if confirm != "y":
            print("Payment cancelled.")
            return

        method = DoPayment.input_payment_method()

        # Mark order paid
        order["order_status"]   = "paid"
        order["payment_method"] = method
        order["paid_at"]        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order["total_amount"]   = grand_total

        # Mark reservation completed
        reservation["status"]       = "completed"
        reservation["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ReadWrite.write_json(orders_data,       Path.orders_data_path)
        ReadWrite.write_json(reservations_data, Path.reservation_data_path)

        print(f"\nPayment successful!")
        print(f"  Booking ID   : {booking_id}")
        print(f"  Grand Total  : Rs {grand_total:.0f}")
        print(f"  Method       : {method.upper()}")