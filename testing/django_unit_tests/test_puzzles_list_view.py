from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from testing.data_setup_utils import create_published_puzzle


class PuzzlesListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_Redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/puzzles_list")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzles_list")

    def test_Default_form_and_list_when_no_puzzles_exist(self):
        response = self.client.get("/puzzles_list")
        form = response.context['form']
        self.assertEqual(form.initial['sort_by'], 'shared_at')
        self.assertEqual(form.initial['order'], '-')
        self.assertEqual(len(response.context['object_list']), 0)

    def test_Form_reflects_passed_parameters_on_url(self):
        create_published_puzzle(self.user)
        response = self.client.get("/puzzles_list?sort_by=desc&order=")
        form = response.context['form']
        self.assertEqual(form.initial['sort_by'], 'desc')
        self.assertEqual(form.initial['order'], '')
        self.assertEqual(len(response.context['object_list']), 1)

    def test_List_is_sorted_in_descending_order_of_published_date_by_default(self):
        puzzle1 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=1))
        puzzle2 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=3))
        response = self.client.get("/puzzles_list")
        objects = response.context['object_list']
        self.assertEqual(len(objects), 3)
        self.assertEqual(objects[0].id, puzzle1.id)
        self.assertEqual(objects[1].id, puzzle3.id)
        self.assertEqual(objects[2].id, puzzle2.id)

    def test_List_with_parameters_sort_by_shared_at_and_order_ascending(self):
        puzzle1 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=1))
        puzzle2 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=3))
        response = self.client.get("/puzzles_list?sort_by=shared_at&order=")
        objects = response.context['object_list']
        self.assertEqual(objects[0].id, puzzle2.id)
        self.assertEqual(objects[1].id, puzzle3.id)
        self.assertEqual(objects[2].id, puzzle1.id)

    def test_List_with_parameters_sort_by_editor_and_order_ascending(self):
        user2 = User.objects.create_user(username="joe_smith", password="secretkey2")
        user3 = User.objects.create_user(username="another_user", password="secretkey3")
        puzzle1 = create_published_puzzle(user2, posted_on=now() - timedelta(days=1))
        puzzle2 = create_published_puzzle(user3, posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=3))
        response = self.client.get("/puzzles_list?sort_by=editor__username&order=")
        objects = response.context['object_list']
        self.assertEqual(objects[0].id, puzzle2.id)
        self.assertEqual(objects[1].id, puzzle1.id)
        self.assertEqual(objects[2].id, puzzle3.id)

    def test_List_with_parameters_sort_by_size_and_order_descending(self):
        puzzle1 = create_published_puzzle(self.user, clues_pts=[3, 5])
        puzzle2 = create_published_puzzle(self.user, clues_pts=[3, 4, 5, 1])
        puzzle3 = create_published_puzzle(self.user, clues_pts=[3, 2, 1])
        response = self.client.get("/puzzles_list?sort_by=size&order=-")
        objects = response.context['object_list']
        self.assertEqual(objects[0].id, puzzle2.id)
        self.assertEqual(objects[1].id, puzzle3.id)
        self.assertEqual(objects[2].id, puzzle1.id)
        response = self.client.get("/puzzles_list?sort_by=total_points&order=")
        objects = response.context['object_list']
        self.assertEqual(objects[0].id, puzzle3.id)
        self.assertEqual(objects[1].id, puzzle1.id)
        self.assertEqual(objects[2].id, puzzle2.id)
