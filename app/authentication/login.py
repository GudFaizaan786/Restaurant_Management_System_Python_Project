import getpass
from app.validation.all_validation import Validation
from app.domain.read_write import ReadWrite
from app.module.error_module import Module
from app.module.json_file import Paths
from app.module.role_model import Role


class Login:

    @staticmethod
    def login_user():
        """
        Asks for email and password.
        If email matches and password is correct, routes to
        Admin or Staff dashboard depending on the user's role.
        Password input is hidden using getpass.
        """
        # Import here to avoid circular imports at module level
        from app.domain.admin_function import Admin_handle
        from app.domain.staff_access import Staff_handle

        all_data = ReadWrite.read(Paths.staff_data_path)

        print("\n" + "=" * 30)
        print("          LOGIN MENU")
        print("=" * 30)

        email = Validation.email(Module.login)

        found = False
        for item in all_data:
            if item["email"] == email:
                found = True
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
            print("No account found with that email.")