from typing import Optional
from .models import User

class UserRepository:
    # Repository pattern for User data access.
    # Abstracts database operations from business logic.
    
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        # Get user by username
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        # Get user by email
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        # Get user by ID
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def create_user(username: str, email: str, password: str, **extra_fields) -> User:
        # Create a new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        return user
    
    @staticmethod
    def update_user(user: User, **fields) -> User:
        # Update user fields
        for field, value in fields.items():
            setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def delete_user(user: User) -> None:
        # Delete a user
        user.delete()
    
    @staticmethod
    def user_exists(username: str) -> bool:
        # Check if user exists
        return User.objects.filter(username=username).exists()

    @staticmethod
    def get_all():
        # Get all users
        return User.objects.all()
