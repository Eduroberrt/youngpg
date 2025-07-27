from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User


class CaseInsensitivePasswordResetForm(PasswordResetForm):
    """
    Custom password reset form that handles case-insensitive email lookup
    """
    
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        
        # Check if user exists with case-insensitive email lookup
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No user with that email address exists.")
        
        return email
    
    def get_users(self, email):
        """
        Given an email, return matching user(s) who should receive a reset.
        This uses case-insensitive lookup.
        """
        email_field_name = User.get_email_field_name()
        active_users = User._default_manager.filter(**{
            '%s__iexact' % email_field_name: email,
            'is_active': True,
        })
        return (
            u for u in active_users
            if u.has_usable_password() and
               self._get_user_email(u).lower() == email.lower()
        )
    
    def _get_user_email(self, user):
        """
        Get the email address for the user.
        """
        email_field_name = User.get_email_field_name()
        return getattr(user, email_field_name, '')
