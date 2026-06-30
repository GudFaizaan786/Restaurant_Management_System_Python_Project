from app.menu.all_menu import Menu
from app.authentication.staff_registeration import Staff
from app.authentication.customer_registration import CustomerAuth
from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.authentication.login import Login
from app.validation.all_validation import Validation
 

class Main:
    

    @staticmethod
    def dashboard_menu():
        while True:
            print("\n" + "=" * 30)
            print("         MAIN MENU")
            print("=" * 30)
            print("1. Login")
            print("2. Register as Staff")
            print("3. Register as Customer")
            print("4. Exit")
            print("=" * 30)

            choice = Validation.menu_choice()

            if choice == 1:
                Login.login_user()

            elif choice == 2:
                Main.register_staff()

            elif choice == 3:
                Main.register_customer()

            elif choice == 4:
                print("Goodbye!")
                break

            else:
                print("Please enter a number between 1 and 4.")

    @staticmethod
    def register_staff():
         
        all_data = ReadWrite.read(Path.staff_data_path)
        data     = Staff.register()

        if any(s.get("email") == data["email"] for s in all_data):
            print("An account with this email already exists.")
            return

        all_data.append(data)
        ReadWrite.write_json(all_data, Path.staff_data_path)
        print("Staff account created. You can now login.")

    @staticmethod
    def register_customer():
         
        all_customers = ReadWrite.read(Path.customer_data_path)
        data           = CustomerAuth.register()

        if CustomerAuth.check_duplicate_email(data["email"], all_customers):
            print("An account with this email already exists.")
            return

        all_customers.append(data)
        ReadWrite.write_json(all_customers, Path.customer_data_path)
        print("Customer account created. You can now login.")