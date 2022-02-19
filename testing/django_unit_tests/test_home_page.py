from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey")
        self.client.force_login(self.user)

    def test_Renders_home_page_if_user_is_authenticated(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "home.html")
        self.assertContains(response, "Dashboard")

    def test_Redirects_to_login_page_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/")

