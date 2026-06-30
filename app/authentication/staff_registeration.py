import uuid
from app.validation.all_validation import Validation
from app.model.user import User_model
from app.model.error_model import model
from app.model.role_model import Role


class Staff:

    @staticmethod
    def register():
        """
        Collects details for a new staff member.
        Returns a dict ready to be appended to staff_data.json.
        Role is always set to Staff — only existing admins
        can promote someone manually in the JSON file.
        """
        print("\n" + "=" * 30)
        print("      REGISTRATION MENU")
        print("=" * 30)

        stud = User_model()

        stud.id         = uuid.uuid4().hex[:7]
        stud.name       = Validation.name()
        stud.email      = Validation.email(model.register)
        stud.contact    = Validation.contact(stud.email, model.register)
        stud.experience = Validation.experience(stud.email, model.register)
        stud.password   = Validation.password(stud.email, model.register)
        stud.role       = Role.staff

        print("Registration successful.")
        return stud.__dict__