from django.utils import timezone
from .models import Session

class SessionService:
    # Service for managing user sessions.
    # Tracks active sessions and handles session lifecycle.
    
    @staticmethod
    def create_session(user, token_jti: str, expires_at, request) -> Session:
    # Create a new session for the user.
        ip_address = SessionService._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        session = Session.objects.create(
            user=user,
            token_jti=token_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True
        )
        
        return session
    
    @staticmethod
    def invalidate_session(token_jti: str) -> bool:
    # Invalidate a session by token JTI.
        try:
            session = Session.objects.get(token_jti=token_jti)
            session.is_active = False
            session.save()
            return True
        except Session.DoesNotExist:
            return False
    
    @staticmethod
    def is_session_valid(token_jti: str) -> bool:
    # Check if a session is valid.
        try:
            session = Session.objects.get(token_jti=token_jti, is_active=True)
            return timezone.now() < session.expires_at
        except Session.DoesNotExist:
            return False
    
    @staticmethod
    def get_active_sessions(user):
    # Get all active sessions for a user.
        return Session.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        )
    
    @staticmethod
    def invalidate_all_sessions(user) -> int:
    # Invalidate all sessions for a user.
    # Returns the number of sessions invalidated.
        count = Session.objects.filter(user=user, is_active=True).update(is_active=False)
        return count
    
    @staticmethod
    def _get_client_ip(request):
        # Extract client IP from request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
