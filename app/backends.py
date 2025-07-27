from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class CaseInsensitiveEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows case-insensitive email login
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username first (case-sensitive as per Django default)
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # If not found by username, try case-insensitive email lookup
            try:
                user = User.objects.get(email__iexact=username)
            except User.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a non-existing user
                User().set_password(password)
                return None
        
        # Check if the password is correct
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
