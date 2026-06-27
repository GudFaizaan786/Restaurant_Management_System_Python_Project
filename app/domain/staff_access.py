from app.menu.food_menu import Food_menu
from app.menu.all_menu import Menu
from app.domain.take_order import Order_Take
from app.reports.view_orders import View_Orders
from app.domain.generate_bill import GenerateBill
from app.domain.table_booking import TableBooking
from app.domain.do_payment import DoPayment


class Staff_handle:

    @staticmethod
    def menu_show_staff(email):
        while True:
            choice = Menu.staff_menu()

            if choice == 1:
                Food_menu.food_items()
            elif choice == 2:
                Order_Take.take_order()
            elif choice == 3:
                View_Orders.view_orders()
            elif choice == 4:
                DoPayment.do_payment()
            elif choice == 5:
                GenerateBill.generate_bill()
            elif choice == 6:
                TableBooking.book_table()
            elif choice == 7:
                print("Logged out successfully.")
                break
            else:
                print("Invalid choice. Enter 1 to 7.")