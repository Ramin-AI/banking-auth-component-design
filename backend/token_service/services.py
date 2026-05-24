import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

class TokenService:
    # Service for JWT token generation and verification.
    # Handles access and refresh tokens.
    
    @staticmethod
    def generate_tokens(user) -> dict:
    # Generate access and refresh tokens for a user.
    # Returns dict with access_token, refresh_token, and token metadata.
        # Generate unique JTI (JWT ID) for token tracking
        access_jti = str(uuid.uuid4())
        refresh_jti = str(uuid.uuid4())
        
        # Calculate expiration times
        access_exp = timezone.now() + settings.JWT_ACCESS_TOKEN_LIFETIME
        refresh_exp = timezone.now() + settings.JWT_REFRESH_TOKEN_LIFETIME
        
        # Access token payload
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'jti': access_jti,
            'token_type': 'access',
            'exp': access_exp,
            'iat': timezone.now()
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user.id,
            'jti': refresh_jti,
            'token_type': 'refresh',
            'exp': refresh_exp,
            'iat': timezone.now()
        }
        
        # Generate tokens
        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_jti': access_jti,
            'refresh_jti': refresh_jti,
            'access_expires_at': access_exp,
            'refresh_expires_at': refresh_exp
        }
    
    @staticmethod
    def verify_token(token: str) -> dict:
    # Verify and decode a JWT token.
    # Returns payload if valid, raises exception if invalid.
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')
    
    @staticmethod
    def refresh_access_token(refresh_token: str, user) -> dict:
    # Generate a new access token using a refresh token.
        # Verify refresh token
        payload = TokenService.verify_token(refresh_token)
        
        if payload.get('token_type') != 'refresh':
            raise Exception('Invalid token type')
        
        if payload.get('user_id') != user.id:
            raise Exception('Token user mismatch')
        
        # Generate new access token
        access_jti = str(uuid.uuid4())
        access_exp = timezone.now() + settings.JWT_ACCESS_TOKEN_LIFETIME
        
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'jti': access_jti,
            'token_type': 'access',
            'exp': access_exp,
            'iat': timezone.now()
        }
        
        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        return {
            'access_token': access_token,
            'access_jti': access_jti,
            'access_expires_at': access_exp
        }
