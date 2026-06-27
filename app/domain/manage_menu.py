from app.domain.manage_menu_item import Manage_item
from app.menu.all_menu import Menu


class Manage_menu:

    @staticmethod
    def menu_manage(email):
        while True:
            choice = Menu.manage_food_menu()

            if choice == 1:
                Manage_item.add_item()
            elif choice == 2:
                Manage_item.delete_item()
            elif choice == 3:
                Manage_item.update_item(email)
            elif choice == 4:
                break
            else:
                print("Invalid choice. Enter 1 to 4.")