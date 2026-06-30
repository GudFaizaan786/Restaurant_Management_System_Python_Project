import getpass
from app.validation.all_validation import Validation
from app.domain.read_write import ReadWrite
from app.model.error_model import model
from app.model.json_file import Path
from app.model.role_model import Role


class Login:

    @staticmethod
    def login_user():
        """
        Shows a login type selector — Staff/Admin or Customer.
        Routes to the correct dashboard based on role after
        verifying email and password.
        """
        from app.domain.admin_function import Admin_handle
        from app.domain.staff_access import Staff_handle
        from app.domain.customer_access import Customer_handle

        print("\n" + "=" * 30)
        print("            LOGIN")
        print("=" * 30)
        print("1. Staff / Admin Login")
        print("2. Customer Login")
        print("=" * 30)

        login_type = Validation.menu_choice()

        if login_type == 1:
            Login._staff_admin_login(Admin_handle, Staff_handle)
        elif login_type == 2:
            Login._customer_login(Customer_handle)
        else:
            print("Invalid choice. Enter 1 or 2.")

    @staticmethod
    def _staff_admin_login(Admin_handle, Staff_handle):
        """Handles login for Staff and Admin accounts."""
        all_data = ReadWrite.read(Path.staff_data_path)
        email    = Validation.email(model.login)

        found = False
        for item in all_data:
            if item["email"] == email:
                found    = True
                password = getpass.getpass("Enter your password: ")

                if item["password"] == password:
                    print(f"\nWelcome, {item['name']}! Login successful.")

                    if item["role"] == Role.staff:
                        Staff_handle.menu_show_staff(email)
                        
                    elif item["role"] == Role.admin:
                        Admin_handle.menu_show(email)
                else:
                    print("Incorrect password. Please try again.")
                break

        if not found:
            print("No staff or admin account found with that email.")

    @staticmethod
    def _customer_login(Customer_handle):
        """Handles login for Customer accounts."""
        all_customers = ReadWrite.read(Path.customer_data_path)
        email          = Validation.email(model.login)

        found = False
        for customer in all_customers:
            if customer["email"] == email:
                found    = True
                password = getpass.getpass("Enter your password: ")

                if customer["password"] == password:
                    print(f"\nWelcome, {customer['name']}! Login successful.")
                    Customer_handle.menu_show_customer(email, customer["name"])
                else:
                    print("Incorrect password. Please try again.")
                break

        if not found:
            print("No customer account found with that email.")