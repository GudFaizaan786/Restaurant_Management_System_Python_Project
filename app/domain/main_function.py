from app.menu.all_menu import Menu
from app.authentication.staff_registeration import Staff
from app.domain.read_write import ReadWrite
from app.model.json_file import Path
from app.authentication.login import Login
from app.validation.all_validation import Validation


class Main:
     
    @staticmethod
    def dashboard_menu():
        while True:
            Menu.main_menu()
            choice = Validation.menu_choice()

            if choice == 1:
                Login.login_user()

            elif choice == 2:
                data     = Staff.register()
                all_data = ReadWrite.read(Path.staff_data_path)
                all_data.append(data)
                ReadWrite.write_json(all_data, Path.staff_data_path)

            elif choice == 3:
                print("Goodbye!")
                break

            else:
                print("Please enter a number between 1 and 3.")