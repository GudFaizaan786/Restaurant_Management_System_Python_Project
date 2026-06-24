import uuid
from app.validation.all_validation import Validation
from app.module.user import User_model
from app.module.error_module import Module
from app.module.role_model import Role


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
        stud.email      = Validation.email(Module.register)
        stud.contact    = Validation.contact(stud.email, Module.register)
        stud.experience = Validation.experience(stud.email, Module.register)
        stud.password   = Validation.password(stud.email, Module.register)
        stud.role       = Role.staff

        print("Registration successful.")
        return stud.__dict__