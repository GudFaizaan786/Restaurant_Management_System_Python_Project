import uuid
from app.validation.all_validation import Validation
from app.model.user import Customer_model
from app.model.error_model import model
from app.model.role_model import Role


class CustomerAuth:

    @staticmethod
    def register():
        """
        Registers a new customer.
        Customers only need name, email, contact and password.
        No experience field — that is staff only.
        """
        print("\n" + "=" * 35)
        print("      CUSTOMER REGISTRATION")
        print("=" * 35)

        c          = Customer_model()
        c.id       = uuid.uuid4().hex[:7]
        c.name     = Validation.name()
        c.email    = Validation.email(model.register)
        c.contact  = Validation.contact(c.email, model.register)
        c.password = Validation.password(c.email, model.register)
        c.role     = Role.customer

        print("Registration successful.You can now login.")
        return c.__dict__

    @staticmethod
    def check_duplicate_email(email, customer_list):
        """Returns True if email already exists in customer database."""
        return any(c.get("email") == email for c in customer_list)