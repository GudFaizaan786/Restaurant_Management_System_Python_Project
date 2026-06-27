from app.domain.read_write import ReadWrite
from app.model.json_file import Path


class StaffManager:

    @staticmethod
    def remove_staff():
        print("\n" + "=" * 40)
        print("           REMOVE STAFF")
        print("=" * 40)

        staff_data = ReadWrite.read(Path.staff_data_path)
        staff_list = staff_data if isinstance(staff_data, list) else staff_data.get("staff", [])

        # Admins cannot be removed through the app
        non_admin = [s for s in staff_list if s.get("role") != "Admin"]

        if not non_admin:
            print("No staff members available to remove.")
            input("\nPress Enter to continue...")
            return

        print(f"\n{'No':<4} {'ID':<10} {'Name':<18} {'Role':<10} {'Contact'}")
        print("-" * 55)
        for i, staff in enumerate(non_admin):
            print(
                f"{i+1:<4} "
                f"{staff.get('id', 'N/A'):<10} "
                f"{str(staff.get('name', 'N/A')):<18} "
                f"{staff.get('role', 'N/A'):<10} "
                f"{staff.get('contact', 'N/A')}"
            )
        print("-" * 55)

        try:
            choice = int(input("Enter staff number to remove (0 to cancel): ").strip())

            if choice == 0:
                print("Cancelled.")
                input("\nPress Enter to continue...")
                return

            if not (1 <= choice <= len(non_admin)):
                print("Invalid selection.")
                input("\nPress Enter to continue...")
                return

            staff_to_remove = non_admin[choice - 1]
            name            = staff_to_remove.get("name", "Unknown")
            role            = staff_to_remove.get("role", "Unknown")

            confirm = input(f"Remove {name} ({role})? (y/n): ").strip().lower()

            if confirm in ["y", "yes"]:
                original_index = staff_list.index(staff_to_remove)
                staff_list.pop(original_index)
                ReadWrite.write_json(staff_list, Path.staff_data_path)
                print(f"{name} removed successfully.")
            else:
                print("Cancelled.")

        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"Error: {e}")

        input("\nPress Enter to continue...")