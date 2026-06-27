import re
import getpass
from app.domain.read_write import ReadWrite
from app.model.logs_path import Logs
from app.model.pattern import Pattern


class Validation:

    @staticmethod
    def menu_choice():
        """Accepts only a positive integer. Used for all menu selections."""
        while True:
            choice = input("Please enter your choice: ").strip()
            if choice.isdigit():
                return int(choice)
            else:
                print("Invalid input. Please enter a number only.")

    @staticmethod
    def opening_qty():
        """Accepts only a positive integer. Used when adding a new menu item to set its opening stock."""
        while True:
            qty = input("Opening stock quantity: ").strip()
            if qty.isdigit():
                return int(qty)
            else:
                print("Invalid input. Please enter a number only.")

    @staticmethod
    def name():
        """Accepts a full name — letters, spaces, hyphens, apostrophes only. Length 2 to 50."""
        while True:
            name = input("Please enter your full name: ").strip()
            if re.fullmatch(Pattern.name_pattern, name) and 2 <= len(name) <= 50:
                return name
            else:
                print("Invalid name. Only letters, spaces, hyphens and apostrophes allowed.")

    @staticmethod
    def contact(email, model):
        """Accepts a 10-digit phone number. Logs any unexpected errors."""
        while True:
            try:
                contact = int(input("Please enter your contact number: ").strip())
                if len(str(contact)) == 10:
                    return contact
                else:
                    print("Invalid contact. Please enter a 10-digit number.")
            except Exception as e:
                print("Invalid input. Numbers only.")
                ReadWrite.log_error(Logs.contact, str(e), email, model)

    @staticmethod
    def email(model):
        """Accepts a valid email address format. Logs any unexpected errors."""
        while True:
            try:
                email = input("Please enter your email: ").strip().lower()
                if re.fullmatch(Pattern.email_pattern, email):
                    return email
                else:
                    print("Invalid email. Please try again.")
            except Exception as e:
                print("Something went wrong.")
                ReadWrite.log_error(Logs.email, str(e), "unknown", model)

    @staticmethod
    def experience(email, model):
        """Accepts years of experience as an integer between 0 and 50. Logs ValueError."""
        while True:
            try:
                years = int(input("Please enter your experience (in years): ").strip())
                if years < 0:
                    print("Experience cannot be negative.")
                elif years > 50:
                    print("Experience value is too high.")
                else:
                    return years
            except ValueError as e:
                print("Please enter numbers only.")
                ReadWrite.log_error(Logs.experience, str(e), email, model)

    @staticmethod
    def password(email, model):
        """
        Accepts a password between 8 and 20 characters.
        No spaces allowed. Must be confirmed by typing twice.
        Uses getpass so the password is hidden while typing.
        Logs any unexpected errors.
        """
        while True:
            try:
                password         = getpass.getpass("Enter password: ")
                confirm_password = getpass.getpass("Confirm password: ")

                if len(password) < 8:
                    print("Minimum 8 characters required.")
                elif " " in password:
                    print("Password must not contain spaces.")
                elif len(password) > 20:
                    print("Password must be between 8 and 20 characters.")
                elif password != confirm_password:
                    print("Passwords do not match. Try again.")
                else:
                    return password

            except Exception as e:
                print("Something went wrong.")
                ReadWrite.log_error(Logs.password, str(e), email, model)