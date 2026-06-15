#!/usr/bin/env python3
    # Database management script for creating demo users.
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_platform.settings')
django.setup()

from user_repository.repository import UserRepository

def create_demo_users():
    # Create demo users for testing
    
    users = [
        {
            'username': 'ramin_joon',
            'email': 'ramin@example.com',
            'password': 'Password123!',
            'first_name': 'Ramin',
            'last_name': 'Joon',
            'otp_enabled': False
        },
        {
            'username': 'parsa_joon',
            'email': 'parsa@example.com',
            'password': 'Password123!',
            'first_name': 'Parsa',
            'last_name': 'Joon',
            'otp_enabled': True
        },
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'Admin123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'otp_enabled': False,
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    for user_data in users:
        username = user_data['username']
        if not UserRepository.user_exists(username):
            user = UserRepository.create_user(**user_data)
            print(f"✓ Created user: {username} (OTP: {user.otp_enabled})")
        else:
            print(f"- User already exists: {username}")

if __name__ == '__main__':
    print("Creating demo users...")
    create_demo_users()
    print("\nDemo users created successfully!")
    print("\nLogin credentials:")
    print("1. Username: ramin_joon, Password: Password123! (No OTP)")
    print("2. Username: parsa_joon, Password: Password123! (With OTP)")
    print("3. Username: admin_user, Password: Admin123! (Admin, No OTP)")
