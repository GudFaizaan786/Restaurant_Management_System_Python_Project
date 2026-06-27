from datetime import datetime, timedelta
import re
import uuid
from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.model.time_slots import TimeSlots


class TableBooking:

    @staticmethod
    def make_reservation_id(reservations_list):
        """Generates a unique 6-character hex ID that doesn't already exist."""
        while True:
            reservation_id = uuid.uuid4().hex.upper()[:6]
            exists = any(r.get("reservation_id") == reservation_id for r in reservations_list)
            if not exists:
                return reservation_id

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
                print("Invalid format. Example: 2026-01-15")
                continue
            today    = datetime.now().date()
            max_date = today + timedelta(days=30)
            if booking_date < today:
                print("Past dates are not allowed.")
                continue
            if booking_date > max_date:
                print("Bookings are only allowed up to 30 days ahead.")
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
                    print(f"Cannot exceed maximum capacity of {max_capacity}.")
                    continue
                return seats
            except ValueError:
                print("Please enter a number.")

    @staticmethod
    def pick_from_list(prompt, count):
        """Keeps asking until the user picks a valid number from 1 to count."""
        while True:
            try:
                n = int(input(prompt).strip())
                if 1 <= n <= count:
                    return n
                print(f"Please enter a number between 1 and {count}.")
            except ValueError:
                print("Please enter a number.")

    @staticmethod
    def get_available_slots(date_str):
        """
        Returns all slots for a future date.
        For today, filters out slots whose start time has already passed.
        """
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

    @staticmethod
    def book_table():
        print("\n" + "=" * 40)
        print("          TABLE BOOKING")
        print("=" * 40)

        customer_name = TableBooking.input_customer_name()
        booking_date  = TableBooking.input_booking_date()

        # Load tables
        tables_data = ReadWrite.read(Path.tables_data_path)
        if isinstance(tables_data, list):
            tables_list = tables_data
        elif isinstance(tables_data, dict) and tables_data.get("tables"):
            tables_list = tables_data["tables"]
        else:
            print("No tables data found.")
            return

        # Load reservations
        reservations_data = ReadWrite.read(Path.reservations_data_path)
        if not reservations_data or "reservations" not in reservations_data:
            reservations_data = {"reservations": []}
        reservations_list = reservations_data["reservations"]

        max_capacity = max((t.get("capacity", 0) for t in tables_list), default=0)
        if max_capacity <= 0:
            print("No valid tables found.")
            return

        seats = TableBooking.input_seats(max_capacity)

        # Show available time slots
        slots = TableBooking.get_available_slots(booking_date)
        if not slots:
            print("No time slots available for this date.")
            return

        print("\nAvailable time slots:")
        for i, slot in enumerate(slots, 1):
            print(f"  {i}. {slot}")

        slot_number   = TableBooking.pick_from_list("Select slot number: ", len(slots))
        selected_slot = slots[slot_number - 1]

        # Find tables that fit seats and are not already booked for this slot
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

        # Show smallest suitable tables first
        available_tables.sort(key=lambda x: x.get("capacity", 0))

        print(f"\nAvailable tables for {selected_slot}:")
        for j, t in enumerate(available_tables, 1):
            print(f"  {j}. {t.get('table_name')}  (capacity {t.get('capacity')})")

        table_number  = TableBooking.pick_from_list("Select table number: ", len(available_tables))
        chosen_table  = available_tables[table_number - 1]
        reservation_id = TableBooking.make_reservation_id(reservations_list)
        created_at    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_reservation = {
            "reservation_id"  : reservation_id,
            "customer_name"   : customer_name,
            "table_id"        : chosen_table.get("table_id"),
            "table_name"      : chosen_table.get("table_name"),
            "date"            : booking_date,
            "time_slot"       : selected_slot,
            "seats"           : seats,
            "status"          : "booked",
            "created_at"      : created_at
        }

        reservations_list.append(new_reservation)
        ReadWrite.write_json(reservations_data, Path.reservations_data_path)

        print("\n" + "-" * 40)
        print("Booking confirmed!")
        print(f"  Booking ID : {reservation_id}")
        print(f"  Customer   : {customer_name}")
        print(f"  Table      : {chosen_table.get('table_name')}  (capacity {chosen_table.get('capacity')})")
        print(f"  Date       : {booking_date}")
        print(f"  Slot       : {selected_slot}")
        print(f"  Seats      : {seats}")
        print("-" * 40)
        input("\nPress Enter to continue...")