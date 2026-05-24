from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    EVENT_TYPES = [
        ('LOGIN_SUCCESS', 'Login Success'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('OTP_GENERATED', 'OTP Generated'),
        ('OTP_VERIFIED', 'OTP Verified'),
        ('OTP_FAILED', 'OTP Failed'),
        ('SSO_INITIATED', 'SSO Initiated'),
        ('SSO_SUCCESS', 'SSO Success'),
        ('SSO_FAILED', 'SSO Failed'),
        ('LOGOUT', 'Logout'),
        ('TOKEN_REFRESH', 'Token Refresh'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f"{self.event_type} - {username} - {self.timestamp}"
