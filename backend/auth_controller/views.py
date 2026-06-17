from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import redirect

from password_auth.services import PasswordAuthService
from otp_service.services import OTPService
from sso_provider.services import SSOService
from token_service.services import TokenService
from session_manager.services import SessionService
from audit_logger.services import AuditService
from user_repository.repository import UserRepository


class PasswordLoginView(APIView):
    # handle login, also check if they need otp
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'success': False,
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # try to login
        user = PasswordAuthService.authenticate(username, password)
        
        if not user:
            # Log failed attempt
            AuditService.log_event('LOGIN_FAILED', None, request, {
                'username': username,
                'reason': 'Invalid credentials'
            })
            
            return Response({
                'success': False,
                'message': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        if not user.is_active:
            return Response({'success': False, 'message': 'Account suspended'}, status=403)
        
        # Check if OTP is enabled
        if user.otp_enabled:
            # Generate OTP
            otp_code = OTPService.generate_otp(user)
            
            # Log OTP generation
            AuditService.log_event('OTP_GENERATED', user, request)
            
            return Response({
                'success': False,
                'requires_otp': True,
                'user_id': user.id,
                'message': f'OTP sent to your registered device. Code: {otp_code} (Demo)'
            }, status=status.HTTP_200_OK)
        
        # Generate tokens
        tokens = TokenService.generate_tokens(user)
        
        # save session
        SessionService.create_session(
            user,
            tokens['access_jti'],
            tokens['refresh_expires_at'],
            request
        )
        
        # Log successful login
        AuditService.log_event('LOGIN_SUCCESS', user, request, {
            'method': 'password'
        })
        
        return Response({
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'otp_enabled': user.otp_enabled,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    # checks the otp code
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')
        
        if not user_id or not otp_code:
            return Response({
                'success': False,
                'message': 'User ID and OTP code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        user = UserRepository.get_by_id(user_id)
        if not user:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify OTP
        is_valid = OTPService.verify_otp(user, otp_code)
        
        if not is_valid:
            # Log failed OTP
            AuditService.log_event('OTP_FAILED', user, request, {
                'reason': 'Invalid or expired OTP'
            })
            
            return Response({
                'success': False,
                'message': 'Invalid or expired OTP'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        tokens = TokenService.generate_tokens(user)
        
        # Create session
        SessionService.create_session(
            user,
            tokens['access_jti'],
            tokens['refresh_expires_at'],
            request
        )
        
        # Log successful OTP verification
        AuditService.log_event('OTP_VERIFIED', user, request)
        AuditService.log_event('LOGIN_SUCCESS', user, request, {
            'method': 'otp'
        })
        
        return Response({
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'otp_enabled': user.otp_enabled,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)


class SSOLoginView(APIView):
    # redirect to sso
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Generate SSO authorization URL
        sso_data = SSOService.generate_authorization_url()
        
        # Log SSO initiation
        AuditService.log_event('SSO_INITIATED', None, request, {
            'state': sso_data['state']
        })
        
        return Response({
            'success': True,
            'authorization_url': sso_data['authorization_url'],
            'state': sso_data['state']
        }, status=status.HTTP_200_OK)


class SSOSimulateView(APIView):
    # fake sso login for demo purposes
    permission_classes = [AllowAny]
    
    def get(self, request):
        state = request.GET.get('state')
        
        if not state:
            return Response({
                'success': False,
                'message': 'State parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate SSO login
        code = SSOService.simulate_sso_login(state)
        
        # Redirect back to callback
        callback_url = f"http://localhost:3000/auth/sso-callback?code={code}&state={state}"
        return redirect(callback_url)


class SSOCallbackView(APIView):
    # handle the callback from sso
    permission_classes = [AllowAny]
    
    def post(self, request):
        code = request.data.get('code')
        state = request.data.get('state')
        
        if not code or not state:
            return Response({
                'success': False,
                'message': 'Code and state are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Validate callback and get user info
            user_info = SSOService.validate_callback(code, state)
            
            # Get or create user
            user = SSOService.get_or_create_sso_user(user_info)
            
            if not user.is_active:
                return Response({'success': False, 'message': 'Account suspended'}, status=403)
            
            # Generate tokens
            tokens = TokenService.generate_tokens(user)
            
            # Create session
            SessionService.create_session(
                user,
                tokens['access_jti'],
                tokens['refresh_expires_at'],
                request
            )
            
            # Log successful SSO login
            AuditService.log_event('SSO_SUCCESS', user, request)
            AuditService.log_event('LOGIN_SUCCESS', user, request, {
                'method': 'sso'
            })
            
            return Response({
                'success': True,
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'sso_provider': user.sso_provider,
                    'is_staff': user.is_staff,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log failed SSO
            AuditService.log_event('SSO_FAILED', None, request, {
                'error': str(e)
            })
            
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    # Logout user and invalidate session.
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        token = request.auth
        
        try:
            # Decode token to get JTI
            payload = TokenService.verify_token(token)
            jti = payload.get('jti')
            
            # Invalidate session
            SessionService.invalidate_session(jti)
            
            # Log logout
            AuditService.log_event('LOGOUT', user, request)
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    # Test protected route that requires authentication.
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        return Response({
            'success': True,
            'message': 'You have access to this protected resource',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)


class AuditLogsView(APIView):
    # Get audit logs (admin or user's own logs).
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        user_id = request.GET.get('user_id')
        
        if user.is_staff:
            if user_id:
                target_user = UserRepository.get_by_id(user_id)
                if not target_user:
                    return Response({
                        'success': False,
                        'message': 'User not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                logs = AuditService.get_user_logs(target_user)
            else:
                logs = AuditService.get_all_logs()
        else:
            logs = AuditService.get_user_logs(user)
        
        logs_data = [{
            'id': log.id,
            'event_type': log.event_type,
            'username': log.user.username if log.user else 'System',
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
            'metadata': log.metadata,
            'timestamp': log.timestamp.isoformat()
        } for log in logs]
        
        return Response({
            'success': True,
            'logs': logs_data
        }, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    # Refresh access token using refresh token.
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify refresh token
            payload = TokenService.verify_token(refresh_token)
            
            # Check session validity in database
            session_jti = payload.get('jti')
            if not SessionService.is_session_valid(session_jti):
                return Response({
                    'success': False,
                    'message': 'Session is inactive or expired'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            user_id = payload.get('user_id')
            
            # Get user
            user = UserRepository.get_by_id(user_id)
            if not user:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
            if not user.is_active:
                return Response({
                    'success': False,
                    'message': 'User account is suspended'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate new access token
            new_tokens = TokenService.refresh_access_token(refresh_token, user)
            
            # Log token refresh
            AuditService.log_event('TOKEN_REFRESH', user, request)
            
            return Response({
                'success': True,
                'access_token': new_tokens['access_token']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class SSODirectLoginView(APIView):
    # direct sso login without redirects (just for testing)
    permission_classes = [AllowAny]
    
    def post(self, request):
        # doing it this way because I couldn't get the oauth redirect to work locally
        import secrets
        
        # Simulate SSO authentication
        
        # Generate a simulated SSO user (fixed to single identity)
        user_info = {
            'sso_id': 'simulated_sso_user_999',
            'email': 'jane.sso@bankdemo.com',
            'username': 'jane_sso',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }
        
        # Get or create user
        user = SSOService.get_or_create_sso_user(user_info)
        
        if not user.is_active:
            return Response({'success': False, 'message': 'Account suspended'}, status=403)
        
        # Generate tokens
        tokens = TokenService.generate_tokens(user)
        
        # Create session
        SessionService.create_session(
            user,
            tokens['access_jti'],
            tokens['refresh_expires_at'],
            request
        )
        
        # Log successful SSO login
        AuditService.log_event('SSO_LOGIN_SUCCESS', user, request, {
            'method': 'sso',
            'provider': 'simulated_sso'
        })
        
        return Response({
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'otp_enabled': user.otp_enabled,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        }, status=status.HTTP_200_OK)


class AdminUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        users = UserRepository.get_all()
        users_data = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_staff': u.is_staff,
            'is_active': u.is_active,
            'otp_enabled': u.otp_enabled,
            'created_at': u.created_at.isoformat() if u.created_at else None
        } for u in users]
        
        return Response(users_data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        is_staff = request.data.get('is_staff', False)
        otp_enabled = request.data.get('otp_enabled', False)
        
        if not username or not email or not password:
            return Response({'success': False, 'message': 'Username, email, and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if UserRepository.user_exists(username):
            return Response({'success': False, 'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = UserRepository.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=is_staff,
                otp_enabled=otp_enabled
            )
            AuditService.log_event('USER_CREATED_BY_ADMIN', request.user, request, {'new_user': username})
            return Response({
                'success': True, 
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                    'otp_enabled': user.otp_enabled
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminToggleOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.otp_enabled = not user.otp_enabled
        user.save()
        AuditService.log_event('OTP_TOGGLED_BY_ADMIN', user, request, {'new_status': user.otp_enabled})
        return Response({'success': True, 'otp_enabled': user.otp_enabled}, status=status.HTTP_200_OK)


class AdminDeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.id == request.user.id:
            return Response({'success': False, 'message': 'Cannot delete yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
        username = user.username
        user.delete()
        AuditService.log_event('USER_DELETED_BY_ADMIN', request.user, request, {'deleted_user': username})
        return Response({'success': True, 'message': 'User deleted'}, status=status.HTTP_200_OK)


class AdminToggleActiveView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = not user.is_active
        user.save()
        AuditService.log_event('ACTIVE_TOGGLED_BY_ADMIN', user, request, {'new_status': user.is_active})
        return Response({'success': True, 'is_active': user.is_active}, status=status.HTTP_200_OK)


class AdminResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        if not request.user.is_staff:
            return Response({'success': False, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.set_password('Password123!')
        user.save()
        AuditService.log_event('PASSWORD_RESET_BY_ADMIN', user, request, {})
        return Response({'success': True, 'message': 'Password reset successfully'}, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'success': False, 'message': 'Old and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({'success': False, 'message': 'Invalid old password. If your password was reset by an admin, your current old password is "Password123!".'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        AuditService.log_event('PASSWORD_CHANGED', user, request, {})
        return Response({'success': True, 'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class UserToggleOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        user.otp_enabled = not user.otp_enabled
        user.save()
        AuditService.log_event('OTP_TOGGLED', user, request, {'new_status': user.otp_enabled})
        return Response({'success': True, 'otp_enabled': user.otp_enabled}, status=status.HTTP_200_OK)

