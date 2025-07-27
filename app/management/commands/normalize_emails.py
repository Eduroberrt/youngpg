from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class Command(BaseCommand):
    help = 'Test case-insensitive email authentication and normalize user emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--normalize',
            action='store_true',
            help='Normalize all user emails to lowercase',
        )
        parser.add_argument(
            '--test-auth',
            type=str,
            help='Test authentication with the given email/username',
        )

    def handle(self, *args, **options):
        if options['normalize']:
            self.normalize_emails()
        
        if options['test_auth']:
            self.test_authentication(options['test_auth'])

    def normalize_emails(self):
        """Normalize all user emails to lowercase"""
        updated_count = 0
        for user in User.objects.all():
            if user.email:
                original_email = user.email
                normalized_email = user.email.lower()
                if original_email != normalized_email:
                    user.email = normalized_email
                    user.save(update_fields=['email'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {user.username}: {original_email} -> {normalized_email}'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully normalized {updated_count} email addresses')
        )

    def test_authentication(self, email_or_username):
        """Test authentication with different case variations"""
        test_cases = [
            email_or_username,
            email_or_username.lower(),
            email_or_username.upper(),
        ]
        
        for test_case in test_cases:
            self.stdout.write(f'\nTesting authentication with: "{test_case}"')
            
            # Note: We can't test password without knowing it, so this just checks
            # if a user exists with that email/username
            try:
                # Try by username
                user = User.objects.get(username=test_case)
                self.stdout.write(
                    self.style.SUCCESS(f'  Found user by username: {user.username} ({user.email})')
                )
            except User.DoesNotExist:
                try:
                    # Try by case-insensitive email
                    user = User.objects.get(email__iexact=test_case)
                    self.stdout.write(
                        self.style.SUCCESS(f'  Found user by email: {user.username} ({user.email})')
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  No user found with: {test_case}')
                    )
