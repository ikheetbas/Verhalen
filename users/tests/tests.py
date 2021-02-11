from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from rm.models import InterfaceCall
from users.models import CustomUser


class CustomUserTests(TestCase):

    def test_create_user(self):
        User = get_user_model()  # through this method we get the object defined
        # in the settings.py
        user = User.objects.create_user(
            username='will',
            email='will@email.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'will')
        self.assertEqual(user.email, 'will@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.username, 'superadmin')
        self.assertEqual(admin_user.email, 'superadmin@email.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

class CustomUserGetUrlNameForRmFunctionIfHasPermission(TestCase):

    def setUp(self):
        self.user: CustomUser = get_user_model().objects.create(
                                               username="TestUser",
                                               is_superuser=False,
                                               is_active=True)
        content_type_interfaceCall = ContentType.objects.get_for_model(InterfaceCall)
        self.perm, created = Permission.objects.get_or_create(codename='contracten_upload',
                                                         defaults=dict(name="Contracten upload",
                                                                       content_type=content_type_interfaceCall))
        self.user.save()

    def test_get_url_name_for_rm_function_if_has_permission_none(self):

        self.assertEqual(self.user.get_url_name_for_rm_function_if_has_permission("Contracten upload"), None)

    def test_get_url_name_for_rm_function_if_has_permission(self):
        self.user.user_permissions.add(self.perm)

        self.assertEqual(self.user.get_url_name_for_rm_function_if_has_permission("Contracten upload"),
                         "contracten_upload")