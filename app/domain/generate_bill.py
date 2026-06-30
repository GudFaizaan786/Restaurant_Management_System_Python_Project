import re
from datetime import datetime
from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class GenerateBill:

    @staticmethod
    def input_identifier():
        """Accepts either a 6-char booking ID or a numeric order ID."""
        while True:
            val = input("Enter Booking ID (e.g. A1B2C3) or Order ID (number): ").strip().upper()
            if not val:
                print("Cannot be empty.")
                continue
            if re.fullmatch(r"[A-F0-9]{6}", val):
                return {"type": "booking_id", "value": val}
            try:
                order_id = int(val)
                if order_id <= 0:
                    print("Order ID must be greater than 0.")
                    continue
                return {"type": "order_id", "value": order_id}
            except ValueError:
                print("Invalid. Use Booking ID (A1B2C3) or Order ID (1, 2, 3...).")

    @staticmethod
    def find_order(orders_data, identifier):
        orders = orders_data.get("orders", [])
        # Always try booking ID first
        for order in orders:
            if order.get("reservation_id") == identifier["value"]:
                return order
        # Fall back to order ID
        if identifier["type"] == "order_id":
            for order in orders:
                if order.get("order_id") == identifier["value"]:
                    return order
        return None

    @staticmethod
    def get_item_price(item_name, size, menu_data):
        for category in menu_data.get("menu", {}).values():
            for item in category:
                if item.get("name", "").lower() == item_name.lower():
                    price_data = item.get("price", {})
                    if isinstance(price_data, dict):
                        if size == "half":
                            return price_data.get("half", 0)
                        if size == "full":
                            return price_data.get("full", 0)
                        return price_data.get("full", price_data.get("half", 0))
                    return price_data
        return 0

    @staticmethod
    def generate_bill():
        print("\n" + "=" * 40)
        print("         GENERATE BILL")
        print("=" * 40)

        orders_data = ReadWrite.read(Path.orders_data_path)
        menu_data   = ReadWrite.read(Path.food_item_path)

        if not orders_data or "orders" not in orders_data:
            print("No orders found.")
            return

        identifier = GenerateBill.input_identifier()
        order      = GenerateBill.find_order(orders_data, identifier)

        if not order:
            print("Order not found.")
            return

        items = order.get("items", [])
        if not items:
            print("This order has no items.")
            return

        bill_items = []
        subtotal   = 0.0

        for item in items:
            item_name = item.get("item_name", "")
            size      = item.get("size", "none")
            qty       = item.get("quantity", 0)
            if not item_name or qty <= 0:
                continue
            price  = GenerateBill.get_item_price(item_name, size, menu_data)
            amount = price * qty
            bill_items.append({
                "name"  : item_name,
                "size"  : size,
                "qty"   : qty,
                "price" : price,
                "amount": amount
            })
            subtotal += amount

        tax         = subtotal * 0.05
        grand_total = subtotal + tax

        restaurant = menu_data.get("restaurant_name", "Gud-Life Restaurant")
        location   = menu_data.get("location", "")

        print("\n" + "=" * 60)
        print(f"{restaurant:^60}")
        print(f"{location:^60}")
        print("=" * 60)
        print(f"Order ID    : {order.get('order_id', 'N/A')}")
        print(f"Booking ID  : {order.get('reservation_id', 'N/A')}")
        print(f"Customer    : {order.get('customer_name', 'N/A')}")
        print(f"Table       : {order.get('table_name', 'N/A')}")
        print(f"Date & Time : {order.get('order_datetime', 'N/A')}")
        print(f"Status      : {order.get('order_status', 'N/A').upper()}")
        print("-" * 60)
        print(f"{'Item':<25} {'Size':<6} {'Qty':>4} {'Price':>7} {'Amount':>9}")
        print("-" * 60)

        for item in bill_items:
            size_label = item["size"] if item["size"] != "none" else "-"
            print(
                f"{item['name'][:24]:<25} {size_label:<6} "
                f"{item['qty']:>4} {item['price']:>7.0f} {item['amount']:>9.0f}"
            )

        print("-" * 60)
        print(f"{'Subtotal':<46} Rs {subtotal:>7.0f}")
        print(f"{'GST @ 5%':<46} Rs {tax:>7.0f}")
        print(f"{'GRAND TOTAL':<46} Rs {grand_total:>7.0f}")
        print("=" * 60)
        print(f"{'[ Thank you for dining with us! ]':^60}")
        print("=" * 60)