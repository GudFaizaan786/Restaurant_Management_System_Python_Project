from app.validation.all_validation import Validation


class Menu:

    @staticmethod
    def main_menu():
        """Displays the landing menu shown before login."""
        print("\n" + "=" * 30)
        print("         MAIN MENU")
        print("=" * 30)
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("=" * 30)

    @staticmethod
    def admin_menu():
        """Displays the admin dashboard and returns the chosen option."""
        print("\n" + "=" * 30)
        print("       ADMIN DASHBOARD")
        print("=" * 30)
        print("1. View Menu")
        print("2. Manage Menu")
        print("3. Remove Staff")
        print("4. Manage Tables")
        print("5. View Reports")
        print("6. Manage Inventory")
        print("7. Logout")
        print("=" * 30)
        return Validation.menu_choice()

    @staticmethod
    def staff_menu():
        """Displays the staff dashboard and returns the chosen option."""
        print("\n" + "=" * 30)
        print("       STAFF DASHBOARD")
        print("=" * 30)
        print("1. View Menu")
        print("2. Take Order")
        print("3. View Orders")
        print("4. Do Payment")
        print("5. Generate Bill")
        print("6. Table Booking")
        print("7. Logout")
        print("=" * 30)
        return Validation.menu_choice()

    @staticmethod
    def manage_food_menu():
        """Displays the manage menu screen and returns the chosen option."""
        print("\n" + "=" * 30)
        print("        MANAGE MENU")
        print("=" * 30)
        print("1. Add Menu Item")
        print("2. Delete Menu Item")
        print("3. Update Menu Item")
        print("4. Back")
        print("=" * 30)
        return Validation.menu_choice()