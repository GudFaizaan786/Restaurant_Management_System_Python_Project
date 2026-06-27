class Pattern:
    
    # Regular expression patterns for validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    name_pattern  = r"^[A-Za-z]+([ '\-][A-Za-z]+)*$" 
    