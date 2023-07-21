import sys
import django
import os
import const

sys.path[0] = '/app/'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User


def create_admin():
    username = os.getenv("ADMIN_USERNAME")
    if not User.objects.filter(username=username).first():
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        User.objects.create_superuser(username, email, password)
        print(f'Superuser "{username}" was created')
    else:
        print(f'Superuser "{username}" already exists')


if __name__ == '__main__':
    create_admin()
