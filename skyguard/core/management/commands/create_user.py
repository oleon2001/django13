from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates a regular user with default credentials'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='user', help='Username for the new user')
        parser.add_argument('--email', type=str, default='user@skyguard.com', help='Email for the new user')
        parser.add_argument('--password', type=str, default='user123', help='Password for the new user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Regular',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS(f'User created successfully with username: {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User with username {username} already exists')
            ) 