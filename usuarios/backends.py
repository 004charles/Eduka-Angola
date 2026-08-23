from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    Handles both regular user authentication and Django admin authentication.
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Prioritize email if provided, otherwise use username
        email_or_username = email or username
        
        if not email_or_username:
            return None
        
        try:
            # Try to fetch the user by email
            user = User.objects.get(email=email_or_username)
            
            if not user.check_password(password):
                return None
            
            # Check if this is a Django admin login attempt
            # Django admin authentication is handled by checking is_staff/is_superuser
            # We detect admin login by checking the request path
            if request and hasattr(request, 'path'):
                is_admin_login = request.path.startswith('/admin-interno/')
                
                if is_admin_login:
                    # For Django admin, only allow staff or superuser
                    if not (user.is_staff or user.is_superuser):
                        return None
            
            return user
            
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
