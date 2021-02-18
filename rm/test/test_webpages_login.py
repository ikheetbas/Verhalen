from django.test import TestCase
from django.urls import reverse

from rm.test import test_util


class HomepageTest(TestCase):

    def setUp(self):
        test_util.set_up_user_login_with_interface_call_and_contract(self)

    def test_homepage(self):
        c = self.client
        response = c.get("/")
        self.assertEqual(response.status_code, 200)


class LoginRequiredTests(TestCase):
    """
    All pages require login, except the login page
    """

    def test_login_required_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse('account_login') + "?next=/")

    def test_login_required_upload_page(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertRedirects(response, reverse('account_login') + "?next=/contracten_upload/")

    def test_inloggen_text(self):
        response = self.client.get(reverse("account_login"))
        self.assertContains(response, 'Inloggen')
