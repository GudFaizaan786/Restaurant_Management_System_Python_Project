from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.validation.all_validation import Validation
from datetime import datetime, timedelta
from collections import Counter


class Reports:

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _load_orders():
        """Reads orders.json and returns the list of orders."""
        orders_data = ReadWrite.read(Path.orders_data_path)
        return orders_data.get("orders", []) if orders_data else []

    @staticmethod
    def _parse_date(order):
        """
        Extracts a date object from order_datetime field.
        Format stored: '2026-01-11 12:16 PM'
        Returns None if parsing fails.
        """
        raw = order.get("order_datetime", "")
        for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:len(fmt) + 2].strip(), fmt).date()
            except ValueError:
                continue
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def _status_counts(orders):
        """Returns a Counter of order statuses."""
        return Counter(o.get("order_status", "unknown") for o in orders)

    @staticmethod
    def _revenue(orders):
        """Total revenue from paid orders only."""
        return sum(
            o.get("total_amount", 0)
            for o in orders
            if o.get("order_status") == "paid"
        )

    @staticmethod
    def _print_summary_block(title, orders):
        """
        Shared printer used by daily, weekly, yearly summaries.
        Prints order counts by status and revenue.
        """
        statuses  = Reports._status_counts(orders)
        revenue   = Reports._revenue(orders)
        total     = len(orders)
        paid      = statuses.get("paid", 0)
        pending   = statuses.get("pending", 0)
        cancelled = statuses.get("cancelled", 0)
        other     = total - paid - pending - cancelled
        avg       = revenue / paid if paid > 0 else 0

        print("\n" + "=" * 50)
        print(f"{title:^50}")
        print("=" * 50)
        print(f"  Total Orders          : {total}")
        print("-" * 50)
        print("  ORDER STATUS BREAKDOWN")
        print(f"    Paid                : {paid}")
        print(f"    Pending             : {pending}")
        print(f"    Cancelled           : {cancelled}")
        if other > 0:
            print(f"    Other               : {other}")
        print("-" * 50)
        print("  REVENUE")
        print(f"    Total Revenue       : Rs {revenue:>10,.0f}")
        print(f"    Average Order Value : Rs {avg:>10,.0f}")
        print("=" * 50)

    # ------------------------------------------------------------------
    # DAILY SUMMARY
    # ------------------------------------------------------------------

    @staticmethod
    def daily_summary(orders):
        print("\n" + "=" * 40)
        print(f"{'DAILY SUMMARY':^40}")
        print("=" * 40)
        print("1. Today")
        print("2. Pick a specific date")
        print("3. All dates overview")
        print("=" * 40)

        choice = Validation.menu_choice()

        if choice == 1:
            target     = datetime.now().date()
            day_orders = [o for o in orders if Reports._parse_date(o) == target]
            Reports._print_summary_block(
                f"DAILY  |  {target.strftime('%d %b %Y')}",
                day_orders
            )

        elif choice == 2:
            while True:
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                try:
                    target = datetime.strptime(date_str, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Invalid format. Example: 2026-01-11")
            day_orders = [o for o in orders if Reports._parse_date(o) == target]
            if not day_orders:
                print(f"No orders found for {target}.")
                return
            Reports._print_summary_block(
                f"DAILY  |  {target.strftime('%d %b %Y')}",
                day_orders
            )

        elif choice == 3:
            # Group by date and print one row per day
            by_date = {}
            for o in orders:
                d = Reports._parse_date(o)
                if d:
                    by_date.setdefault(d, []).append(o)

            if not by_date:
                print("No dated orders found.")
                return

            print("\n" + "=" * 70)
            print(f"{'Date':<14} {'Total':>6} {'Paid':>6} {'Pending':>8} {'Cancelled':>10} {'Revenue':>12}")
            print("-" * 70)
            for d in sorted(by_date.keys()):
                day_list = by_date[d]
                statuses = Reports._status_counts(day_list)
                rev      = Reports._revenue(day_list)
                print(
                    f"{d.strftime('%d %b %Y'):<14} "
                    f"{len(day_list):>6} "
                    f"{statuses.get('paid', 0):>6} "
                    f"{statuses.get('pending', 0):>8} "
                    f"{statuses.get('cancelled', 0):>10} "
                    f"Rs {rev:>8,.0f}"
                )
            print("=" * 70)

        else:
            print("Invalid option.")

    # ------------------------------------------------------------------
    # WEEKLY SUMMARY
    # ------------------------------------------------------------------

    @staticmethod
    def weekly_summary(orders):
        print("\n" + "=" * 40)
        print(f"{'WEEKLY SUMMARY':^40}")
        print("=" * 40)
        print("1. This week  (Mon to today)")
        print("2. Last week")
        print("3. Pick a specific week number")
        print("4. All weeks overview")
        print("=" * 40)

        choice = Validation.menu_choice()
        today  = datetime.now().date()

        if choice == 1:
            week_start  = today - timedelta(days=today.weekday())
            week_end    = today
            label       = f"This Week  ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')})"
            week_orders = [
                o for o in orders
                if Reports._parse_date(o) is not None
                and week_start <= Reports._parse_date(o) <= week_end
            ]
            Reports._print_summary_block(label, week_orders)

        elif choice == 2:
            week_start  = today - timedelta(days=today.weekday() + 7)
            week_end    = week_start + timedelta(days=6)
            label       = f"Last Week  ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')})"
            week_orders = [
                o for o in orders
                if Reports._parse_date(o) is not None
                and week_start <= Reports._parse_date(o) <= week_end
            ]
            Reports._print_summary_block(label, week_orders)

        elif choice == 3:
            year = today.year
            try:
                week_num = int(input(f"Enter ISO week number (1-52) for {year}: ").strip())
                if not (1 <= week_num <= 53):
                    print("Invalid week number.")
                    return
            except ValueError:
                print("Please enter a number.")
                return
            week_start  = datetime.strptime(f"{year}-W{week_num:02d}-1", "%Y-W%W-%w").date()
            week_end    = week_start + timedelta(days=6)
            label       = f"Week {week_num}  ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')})"
            week_orders = [
                o for o in orders
                if Reports._parse_date(o) is not None
                and week_start <= Reports._parse_date(o) <= week_end
            ]
            if not week_orders:
                print(f"No orders found for week {week_num} of {year}.")
                return
            Reports._print_summary_block(label, week_orders)

        elif choice == 4:
            by_week = {}
            for o in orders:
                d = Reports._parse_date(o)
                if d:
                    key = (d.isocalendar()[0], d.isocalendar()[1])
                    by_week.setdefault(key, []).append(o)

            if not by_week:
                print("No orders found.")
                return

            print("\n" + "=" * 72)
            print(f"{'Year':<6} {'Week':>5} {'Date Range':<22} {'Total':>6} {'Paid':>6} {'Pending':>8} {'Revenue':>12}")
            print("-" * 72)
            for (yr, wk) in sorted(by_week.keys()):
                week_list  = by_week[(yr, wk)]
                statuses   = Reports._status_counts(week_list)
                rev        = Reports._revenue(week_list)
                ws         = datetime.strptime(f"{yr}-W{wk:02d}-1", "%Y-W%W-%w").date()
                we         = ws + timedelta(days=6)
                date_range = f"{ws.strftime('%d %b')} - {we.strftime('%d %b')}"
                print(
                    f"{yr:<6} {wk:>5} {date_range:<22} "
                    f"{len(week_list):>6} "
                    f"{statuses.get('paid', 0):>6} "
                    f"{statuses.get('pending', 0):>8} "
                    f"Rs {rev:>8,.0f}"
                )
            print("=" * 72)

        else:
            print("Invalid option.")

    # ------------------------------------------------------------------
    # YEARLY SUMMARY
    # ------------------------------------------------------------------

    @staticmethod
    def yearly_summary(orders):
        print("\n" + "=" * 40)
        print(f"{'YEARLY SUMMARY':^40}")
        print("=" * 40)
        print("1. This year")
        print("2. Pick a specific year")
        print("3. All years overview")
        print("=" * 40)

        choice = Validation.menu_choice()
        today  = datetime.now().date()

        if choice == 1:
            target      = today.year
            year_orders = [
                o for o in orders
                if Reports._parse_date(o) is not None
                and Reports._parse_date(o).year == target
            ]
            Reports._print_summary_block(f"YEARLY  |  {target}", year_orders)
            Reports._monthly_breakdown(year_orders, target)

        elif choice == 2:
            try:
                target = int(input("Enter year (e.g. 2026): ").strip())
            except ValueError:
                print("Invalid year.")
                return
            year_orders = [
                o for o in orders
                if Reports._parse_date(o) is not None
                and Reports._parse_date(o).year == target
            ]
            if not year_orders:
                print(f"No orders found for {target}.")
                return
            Reports._print_summary_block(f"YEARLY  |  {target}", year_orders)
            Reports._monthly_breakdown(year_orders, target)

        elif choice == 3:
            by_year = {}
            for o in orders:
                d = Reports._parse_date(o)
                if d:
                    by_year.setdefault(d.year, []).append(o)

            if not by_year:
                print("No orders found.")
                return

            print("\n" + "=" * 62)
            print(f"{'Year':<8} {'Total':>6} {'Paid':>6} {'Pending':>8} {'Cancelled':>10} {'Revenue':>12}")
            print("-" * 62)
            for yr in sorted(by_year.keys()):
                yr_list  = by_year[yr]
                statuses = Reports._status_counts(yr_list)
                rev      = Reports._revenue(yr_list)
                print(
                    f"{yr:<8} "
                    f"{len(yr_list):>6} "
                    f"{statuses.get('paid', 0):>6} "
                    f"{statuses.get('pending', 0):>8} "
                    f"{statuses.get('cancelled', 0):>10} "
                    f"Rs {rev:>8,.0f}"
                )
            print("=" * 62)

        else:
            print("Invalid option.")

    @staticmethod
    def _monthly_breakdown(year_orders, year):
        """Month-by-month table shown inside yearly summary."""
        MONTHS = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        by_month = {}
        for o in year_orders:
            d = Reports._parse_date(o)
            if d:
                by_month.setdefault(d.month, []).append(o)

        if not by_month:
            return

        print(f"\n  MONTH-BY-MONTH BREAKDOWN  ({year})")
        print("  " + "-" * 58)
        print(f"  {'Month':<10} {'Orders':>7} {'Paid':>6} {'Pending':>8} {'Revenue':>12}")
        print("  " + "-" * 58)
        for m in range(1, 13):
            if m not in by_month:
                continue
            m_list   = by_month[m]
            statuses = Reports._status_counts(m_list)
            rev      = Reports._revenue(m_list)
            print(
                f"  {MONTHS[m-1]:<10} "
                f"{len(m_list):>7} "
                f"{statuses.get('paid', 0):>6} "
                f"{statuses.get('pending', 0):>8} "
                f"Rs {rev:>8,.0f}"
            )
        print("  " + "-" * 58)

    # ------------------------------------------------------------------
    # TODAY SUMMARY
    # ------------------------------------------------------------------

    @staticmethod
    def today_summary(orders):
        today      = datetime.now().date()
        day_orders = [o for o in orders if Reports._parse_date(o) == today]
        Reports._print_summary_block(
            f"TODAY  |  {today.strftime('%d %b %Y')}",
            day_orders
        )

    # ------------------------------------------------------------------
    # TOTAL SALES
    # ------------------------------------------------------------------

    @staticmethod
    def total_sales(orders):
        statuses      = Reports._status_counts(orders)
        total_revenue = Reports._revenue(orders)
        paid          = statuses.get("paid", 0)
        avg_value     = total_revenue / paid if paid > 0 else 0

        print("\n" + "=" * 50)
        print(f"{'TOTAL SALES REPORT  (All Time)':^50}")
        print("=" * 50)
        print(f"  Total Orders          : {len(orders)}")
        print("-" * 50)
        print("  ORDER STATUS BREAKDOWN")
        print(f"    Paid                : {statuses.get('paid', 0)}")
        print(f"    Pending             : {statuses.get('pending', 0)}")
        print(f"    Cancelled           : {statuses.get('cancelled', 0)}")
        print("-" * 50)
        print("  REVENUE")
        print(f"    Total Revenue       : Rs {total_revenue:>10,.0f}")
        print(f"    Average Order Value : Rs {avg_value:>10,.0f}")
        print("=" * 50)

    # ------------------------------------------------------------------
    # TOP ITEMS
    # ------------------------------------------------------------------

    @staticmethod
    def top_items(orders):
        item_quantity = Counter()
        for order in orders:
            for item in order.get("items", []):
                item_quantity[item.get("item_name", "Unknown")] += item.get("quantity", 1)

        print("\n" + "=" * 48)
        print(f"{'TOP SELLING ITEMS  (by Quantity)':^48}")
        print("=" * 48)
        print(f"  {'Rank':<6} {'Item Name':<28} {'Qty':>6}")
        print("-" * 48)
        if item_quantity:
            for i, (item, qty) in enumerate(item_quantity.most_common(10), 1):
                print(f"  {i:<6} {item[:27]:<28} {qty:>6}")
        else:
            print("  No item data available.")
        print("=" * 48)

    # ------------------------------------------------------------------
    # PENDING ORDERS
    # ------------------------------------------------------------------

    @staticmethod
    def pending_orders(orders):
        pending = [o for o in orders if o.get("order_status") == "pending"]

        print("\n" + "=" * 62)
        print(f"{'PENDING ORDERS':^62}")
        print("=" * 62)
        print(f"  Total Pending : {len(pending)}")

        if pending:
            print(f"\n  {'Order ID':<10} {'Table':<7} {'Customer':<20} {'Booking ID':<12} {'Date'}")
            print("  " + "-" * 58)
            for o in pending:
                d = Reports._parse_date(o)
                print(
                    f"  {str(o.get('order_id','N/A')):<10} "
                    f"{str(o.get('table_name','N/A')):<7} "
                    f"{str(o.get('customer_name','N/A'))[:19]:<20} "
                    f"{o.get('reservation_id','N/A'):<12} "
                    f"{d.strftime('%d %b %Y') if d else 'N/A'}"
                )
        print("=" * 62)

    # ------------------------------------------------------------------
    # ORDER STATUS REPORT
    # ------------------------------------------------------------------

    @staticmethod
    def order_status_report(orders):
        print("\n" + "=" * 62)
        print(f"{'ORDER STATUS REPORT':^62}")
        print("=" * 62)

        for status in ["paid", "pending", "cancelled"]:
            group = [o for o in orders if o.get("order_status", "").lower() == status]
            rev   = Reports._revenue(group)

            print(f"\n  {status.upper()}  ({len(group)} orders)")
            print("  " + "-" * 58)

            if not group:
                print("    No orders with this status.")
                continue

            if status == "paid":
                print(f"  {'Order ID':<10} {'Table':<7} {'Customer':<20} {'Date':<14} {'Amount':>10}")
            else:
                print(f"  {'Order ID':<10} {'Table':<7} {'Customer':<20} {'Date':<14}")
            print("  " + "-" * 58)

            for o in group:
                d    = Reports._parse_date(o)
                line = (
                    f"  {str(o.get('order_id','N/A')):<10} "
                    f"{str(o.get('table_name','N/A')):<7} "
                    f"{str(o.get('customer_name','N/A'))[:19]:<20} "
                    f"{d.strftime('%d %b %Y') if d else 'N/A':<14}"
                )
                if status == "paid":
                    line += f" Rs {o.get('total_amount', 0):>6,.0f}"
                print(line)

            if status == "paid":
                print("  " + "-" * 58)
                print(f"  {'Total Revenue':<51} Rs {rev:>6,.0f}")

        print("\n" + "=" * 62)

    # ------------------------------------------------------------------
    # MAIN MENU
    # ------------------------------------------------------------------

    @staticmethod
    def view_reports():
        while True:
            print("\n" + "=" * 40)
            print(f"{'VIEW REPORTS':^40}")
            print("=" * 40)
            print("1. Today Summary")
            print("2. Daily Summary")
            print("3. Weekly Summary")
            print("4. Yearly Summary")
            print("5. Total Sales  (All Time)")
            print("6. Top Selling Items")
            print("7. Pending Orders")
            print("8. Order Status Report")
            print("0. Back")
            print("=" * 40)

            try:
                choice = Validation.menu_choice()

                if choice == 0:
                    break

                orders = Reports._load_orders()

                if not orders:
                    print("No orders data available yet.")
                    input("\nPress Enter to continue...")
                    continue

                if   choice == 1:
                    Reports.today_summary(orders)
                elif choice == 2:
                    Reports.daily_summary(orders)
                elif choice == 3:
                    Reports.weekly_summary(orders)
                elif choice == 4:
                    Reports.yearly_summary(orders)
                elif choice == 5:
                    Reports.total_sales(orders)
                elif choice == 6:
                    Reports.top_items(orders)
                elif choice == 7:
                    Reports.pending_orders(orders)
                elif choice == 8:
                    Reports.order_status_report(orders)
                else:
                    print("Invalid option. Enter 0 to 8.")

                input("\nPress Enter to continue...")

            except Exception as e:
                print(f"\nError: {e}")
                input("\nPress Enter to continue...")