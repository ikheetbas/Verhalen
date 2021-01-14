from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Get a list of all permissions available in the system.'

    def handle(self, *args, **options):

        # We create (but not persist) a temporary superuser and use it to game the
        # system and pull all permissions easily.
        tmp_superuser = get_user_model()(
            is_active=True,
            is_superuser=True
        )

        all_permission_ids = {
            f'{app_label}.{codename}'
            for (app_label, codename)
            in Permission.objects.values_list('content_type__app_label', 'codename')
        }
        print(f'all_permission_ids: {all_permission_ids}')
        print("\r")

        permissions = set()

        print(f"All permissions: {tmp_superuser.get_all_permissions()}")

        # We go over each AUTHENTICATION_BACKEND and try to fetch
        # a list of permissions
        for backend in auth.get_backends():
            print(f"Backend: {backend}")
            if hasattr(backend, "get_all_permissions"):
                print(f"Backend: {backend} has attr get_all_permissions")
                permissions.update(backend.get_all_permissions(tmp_superuser))
            else:
                print(f"Backend: {backend} has NO attr get_all_permissions")

        # Make an unique list of permissions sorted by permission name.
        sorted_list_of_permissions = sorted(list(permissions))

        # Send a joined list of permissions to a command-line output.
        self.stdout.write('\n'.join(sorted_list_of_permissions))
