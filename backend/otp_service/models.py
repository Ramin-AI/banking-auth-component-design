from django.db import models
from django.conf import settings

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'

    def __str__(self):
        return f"OTP for {self.user.username} - {self.code}"
