from .models import AuditLog

class AuditService:
    # Service for logging authentication events.
    # Provides audit trail for security and compliance.
    
    @staticmethod
    def log_event(event_type: str, user, request, metadata: dict = None):
    # Log an authentication event.
        ip_address = AuditService._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        audit_log = AuditLog.objects.create(
            user=user,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        return audit_log
    
    @staticmethod
    def get_user_logs(user, limit: int = 50):
    # Get audit logs for a specific user.
        return AuditLog.objects.filter(user=user)[:limit]
    
    @staticmethod
    def get_all_logs(limit: int = 100):
    # Get all audit logs (for admin).
        return AuditLog.objects.all()[:limit]
    
    @staticmethod
    def get_logs_by_event_type(event_type: str, limit: int = 50):
    # Get logs by event type.
        return AuditLog.objects.filter(event_type=event_type)[:limit]
    
    @staticmethod
    def _get_client_ip(request):
        # Extract client IP from request
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip
