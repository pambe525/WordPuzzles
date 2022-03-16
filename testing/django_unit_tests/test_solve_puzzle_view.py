from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase

from testing.django_unit_tests.unit_test_helpers import create_published_puzzle


class SolvePuzzleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.other_user = User.objects.create(username="other_user")
        self.client.force_login(self.user)

    def test_Redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/solve_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/solve_puzzle/1/")

    def test_Redirects_to_PREVIEW_PAGE_if_user_is_editor(self):
        puzzle = create_published_puzzle(user=self.user)
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("preview_puzzle.html")

    def test_Response_context_contains_puzzle_object(self):
        puzzle = create_published_puzzle(user=self.other_user)
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['object'], puzzle)