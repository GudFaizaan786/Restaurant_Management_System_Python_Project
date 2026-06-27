from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class View_Orders:

    @staticmethod
    def view_orders():
        orders_data = ReadWrite.read(Path.orders_data_path)

        if not orders_data or "orders" not in orders_data:
            print("No orders found.")
            return

        orders = orders_data.get("orders", [])
        if not orders:
            print("No orders found.")
            return

        print("\n" + "=" * 60)
        print(f"{'VIEW ALL ORDERS':^60}")
        print("=" * 60)

        for order in orders:
            status = str(order.get("order_status", "unknown")).lower()

            print(f"\nOrder ID    : {order.get('order_id', 'N/A')}")
            print(f"Booking ID  : {order.get('reservation_id', 'N/A')}")
            print(f"Customer    : {order.get('customer_name', 'N/A')}")
            print(f"Table       : {order.get('table_name', 'N/A')}")
            print(f"Date & Time : {order.get('order_datetime', 'N/A')}")
            print(f"Status      : {status.upper()}")

            print("-" * 60)
            print(f"{'No':<4} {'Item Name':<25} {'Qty':>4} {'Size':<8} {'Category'}")
            print("-" * 60)

            items = order.get("items", [])
            if not items:
                print("  No items in this order.")
            else:
                for idx, item in enumerate(items, 1):
                    size = item.get("size", "none")
                    if size == "none":
                        size = "-"
                    print(
                        f"{idx:<4} {str(item.get('item_name','N/A'))[:24]:<25} "
                        f"{item.get('quantity', 0):>4} {size:<8} "
                        f"{item.get('category','N/A')}"
                    )

            if order.get("total_amount"):
                print(f"\n  Total Paid : Rs {order.get('total_amount'):,.0f}  "
                      f"({order.get('payment_method','').upper()})")
            print("=" * 60)

        input("\nPress Enter to continue...")