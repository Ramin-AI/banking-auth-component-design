import random
import secrets
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import OTP

class OTPService:
    # Service for OTP generation and verification.
    # Handles all OTP-related business logic.
    
    @staticmethod
    def generate_otp(user) -> str:
    # Generate a 6-digit OTP for the user.
    # Invalidates any previous unused OTPs.
        # Invalidate previous OTPs
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate random 6-digit code using CSPRNG
        code = ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])
        
        # Calculate expiry time
        expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        
        # Create OTP record
        otp = OTP.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        
        # In a real system, send OTP via SMS/Email
        print(f"[OTP Service] Generated OTP for {user.username}: {code}")
        
        return code
    
    @staticmethod
    def verify_otp(user, code: str) -> bool:
    # Verify OTP code for the user.
    # Returns True if valid, False otherwise.
        try:
            otp = OTP.objects.get(
                user=user,
                code=code,
                is_used=False
            )
            
            # Check if expired
            if timezone.now() > otp.expires_at:
                return False
            
            # Mark as used
            otp.is_used = True
            otp.save()
            
            return True
            
        except OTP.DoesNotExist:
            return False
    
    @staticmethod
    def get_latest_otp(user):
        # Get the latest OTP for a user (for testing/demo purposes)
        try:
            return OTP.objects.filter(user=user, is_used=False).latest('created_at')
        except OTP.DoesNotExist:
            return None
