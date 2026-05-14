from django.contrib.auth.hashers import check_password
from user_repository.repository import UserRepository

class PasswordAuthService:
    # Service for username/password authentication.
    # Validates credentials and returns user if valid.
    
    @staticmethod
    def authenticate(username: str, password: str):
    # Authenticate user with username and password.
    # Returns user if valid, None otherwise.
        user = UserRepository.get_by_username(username)
        
        if not user:
            return None
        
        if not check_password(password, user.password):
            return None
        
        return user
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple:
    # Validate password strength.
    # Returns (is_valid, error_message)
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(char.isdigit() for char in password):
            return False, "Password must contain at least one digit"
        
        if not any(char.isupper() for char in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(char.islower() for char in password):
            return False, "Password must contain at least one lowercase letter"
        
        return True, ""
