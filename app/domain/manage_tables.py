from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.validation.all_validation import Validation


class TableManager:

    @staticmethod
    def get_tables():
        """Reads tables from JSON. Handles both list and dict formats."""
        tables_data = ReadWrite.read(Path.tables_data_path)
        if isinstance(tables_data, list):
            return tables_data
        return tables_data.get("tables", [])

    @staticmethod
    def save_tables(tables):
        ReadWrite.write_json(tables, Path.tables_data_path)

    @staticmethod
    def get_int(prompt):
        """Keeps asking until a valid integer is entered."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a valid number.")

    @staticmethod
    def view_tables():
        tables = TableManager.get_tables()
        if not tables:
            print("No tables found.")
            return

        print("\n" + "-" * 45)
        print(f"{'ID':<6} {'Name':<8} {'Capacity':<12} {'Status'}")
        print("-" * 45)
        for table in tables:
            tid      = table.get("table_id", "N/A")
            tname    = table.get("table_name", "N/A")
            capacity = table.get("capacity", "N/A")
            status   = table.get("status", "N/A")
            print(f"{tid:<6} {tname:<8} {capacity:<12} {status}")
        print("-" * 45)

    @staticmethod
    def add_table():
        tables  = TableManager.get_tables()
        next_id = max([t.get("table_id", 0) for t in tables], default=0) + 1
        name    = f"T{next_id}"

        print(f"\nNew table will be: ID={next_id}, Name={name}")

        while True:
            capacity_input = input("Enter capacity (2 / 4 / 6 / 8): ").strip()
            if capacity_input in ["2", "4", "6", "8"]:
                capacity = int(capacity_input)
                break
            print("Only 2, 4, 6 or 8 allowed.")

        new_table = {
            "table_id"  : next_id,
            "table_name": name,
            "capacity"  : capacity,
            "status"    : "free"
        }
        tables.append(new_table)
        TableManager.save_tables(tables)
        print(f"Table {name} (capacity {capacity}) added successfully.")

    @staticmethod
    def remove_table():
        tables = TableManager.get_tables()
        if not tables:
            print("No tables to remove.")
            return

        TableManager.view_tables()
        tid = TableManager.get_int("Enter Table ID to remove (0 to cancel): ")

        if tid == 0:
            print("Cancelled.")
            return

        table_to_remove = next((t for t in tables if t.get("table_id") == tid), None)
        if not table_to_remove:
            print("Table ID not found.")
            return

        name = table_to_remove.get("table_name")
        while True:
            confirm = input(f"Remove {name}? (y/n): ").strip().lower()
            if confirm == "y":
                tables = [t for t in tables if t.get("table_id") != tid]
                TableManager.save_tables(tables)
                print(f"Table {name} removed successfully.")
                break
            elif confirm == "n":
                print("Cancelled.")
                break
            else:
                print("Please enter y or n.")

    @staticmethod
    def manage_tables():
        while True:
            print("\n" + "=" * 35)
            print("         MANAGE TABLES")
            print("=" * 35)
            print("1. View All Tables")
            print("2. Add New Table")
            print("3. Remove Table")
            print("0. Back")
            print("=" * 35)

            choice = Validation.menu_choice()

            if choice == 0:
                break
            elif choice == 1:
                TableManager.view_tables()
            elif choice == 2:
                TableManager.add_table()
            elif choice == 3:
                TableManager.remove_table()
            else:
                print("Invalid option. Enter 0, 1, 2 or 3.")

            input("\nPress Enter to continue...")