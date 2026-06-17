from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user_repository.repository import UserRepository
from session_manager.services import SessionService
from .services import TokenService

class JWTAuthentication(BaseAuthentication):
    # Custom JWT authentication class for DRF.
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = TokenService.verify_token(token)
            
            if payload.get('token_type') != 'access':
                raise AuthenticationFailed('Invalid token type')
            
            user = UserRepository.get_by_id(payload.get('user_id'))
            
            if not user:
                raise AuthenticationFailed('User not found')
                
            if not user.is_active:
                raise AuthenticationFailed('User account is suspended')
                
            if not SessionService.is_session_valid(payload.get('jti')):
                raise AuthenticationFailed('Session is inactive or expired')
            
            return (user, token)
            
        except Exception as e:
            raise AuthenticationFailed(str(e))
