from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.test import TestCase
from django.urls import reverse

from .models import Crossword

# ==============================================================================================
class CrosswordModelTest(TestCase):
    def test_string_representation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        puzzle = Crossword.objects.create(editor=user)
        self.assertEquals(user, puzzle.editor)
        self.assertEqual(13, puzzle.size)
        self.assertEqual("", puzzle.blocks)
        self.assertEqual("Crossword Puzzle #1", str(puzzle))

# ==============================================================================================
class HomeViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "home.html")
        self.assertContains(response, "Home Page")

    def test_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/")

# ==============================================================================================
class NewCrosswordViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("new_xword"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "new_xword.html")
        self.assertContains(response, "New Crossword Puzzle")

    def test_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/new_xword/")