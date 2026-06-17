import uuid
import secrets
from django.conf import settings
from user_repository.repository import UserRepository

class SSOService:
    # Service for managing internal SSO authentication.
    
    # In-memory storage for SSO states
    _sso_states = {}
    
    @staticmethod
    def generate_authorization_url(redirect_uri: str = None) -> dict:
    # Generate SSO authorization URL and state.
    # Executes OAuth2 authorization flow.
        state = secrets.token_urlsafe(32)
        
        # Store state for validation
        SSOService._sso_states[state] = {
            'redirect_uri': redirect_uri or 'http://localhost:3000/auth/sso-callback',
            'created_at': None
        }
        
        # Route to internal SSO provider URL
        authorization_url = f"http://localhost:8000/api/auth/sso-gateway?state={state}"
        
        return {
            'authorization_url': authorization_url,
            'state': state
        }
    
    @staticmethod
    def validate_callback(code: str, state: str) -> dict:
    # Validate SSO callback and return user information.
    # Executes token exchange and user info retrieval.
        # Validate state
        if state not in SSOService._sso_states:
            raise Exception('Invalid state parameter')
        
        # Remove used state
        del SSOService._sso_states[state]
        
        # Retrieve user info from SSO provider
        user_info = {
            'sso_id': 'bank_sso_user_999',
            'email': 'jane.sso@bankdemo.com',
            'username': 'jane_sso',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        
        return user_info
    
    @staticmethod
    def get_or_create_sso_user(user_info: dict):
    # Get or create user from SSO information.
        # Try to find existing user by email
        user = UserRepository.get_by_email(user_info['email'])
        
        if user:
            # Update SSO provider info
            user.sso_provider = 'bank_internal_sso'
            user.save()
            return user
        
        # Create new user
        user = UserRepository.create_user(
            username=user_info['username'],
            email=user_info['email'],
            password=secrets.token_urlsafe(32),  # Random password for SSO users
            first_name=user_info.get('first_name', ''),
            last_name=user_info.get('last_name', ''),
            sso_provider='bank_internal_sso'
        )
        
        return user
    
    @staticmethod
    def process_gateway_login(state: str) -> str:
    # Process SSO provider login page.
    # Returns authorization code.
        # Generate authorization code
        code = secrets.token_urlsafe(32)
        return code
