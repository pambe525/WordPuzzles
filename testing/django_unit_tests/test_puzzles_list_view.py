from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from puzzles.models import SolverSession
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle, create_session


class PuzzlesListViewTest(TestCase):
    target_page = "/puzzles_list"

    def setUp(self):
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username='user2', email="abc@de.com")
        self.client.force_login(self.user1)

    def test_Redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(self.target_page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzles_list")

    def test_list_when_no_puzzles_exist(self):
        response = self.client.get(self.target_page)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertContains(response, "No puzzles meet show filter criteria.")
        form = response.context['form']
        self.assertEqual(form['show'].value(), 'all')

    def test_List_is_sorted_in_descending_order_of_published_date_by_default(self):
        create_draft_puzzle(editor=self.user1)
        puzzle1 = create_published_puzzle(self.user1, posted_on=now() - timedelta(days=1))
        puzzle2 = create_published_puzzle(self.user1, posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user1, posted_on=now() - timedelta(days=3))
        response = self.client.get(self.target_page)
        objects = response.context['object_list']
        self.assertNotContains(response, "No published puzzles.")
        self.assertEqual(len(objects), 3)
        self.assertEqual(objects[0].id, puzzle1.id)
        self.assertEqual(objects[1].id, puzzle3.id)
        self.assertEqual(objects[2].id, puzzle2.id)

    def test_list_has_status_for_each_puzzle(self):
        puzzle1 = create_published_puzzle(editor=self.user1, clues_pts=[1, 2], posted_on=now() - timedelta(days=1))
        puzzle2 = create_published_puzzle(editor=self.user2, clues_pts=[3, 2], posted_on=now() - timedelta(days=2))
        puzzle3 = create_published_puzzle(editor=self.user2, clues_pts=[1, 1], posted_on=now() - timedelta(days=3))
        p2_session = SolverSession.new(puzzle2, self.user1)  # Incomplete session
        p3_session = SolverSession.new(puzzle3, self.user1)
        p3_clues = puzzle3.get_clues()
        p3_session.set_solved_clue(p3_clues[0])
        p3_session.set_solved_clue(p3_clues[1])
        response = self.client.get(self.target_page)
        objects = response.context['object_list']
        self.assertEqual(objects[0].status, 0)  # Puzzle 1 - created last - no session
        self.assertEqual(objects[1].status, 1)  # Puzzle 2 - incomplete session
        self.assertEqual(objects[2].status, 2)  # Puzzle 3 - completed session

    def test_list_has_count_of_other_sessions_for_each_puzzle(self):
        user3 = User.objects.create(username="user3", email="xyz@abc.com")
        puzzle1 = create_published_puzzle(editor=self.user1, clues_pts=[1, 2], posted_on=now() - timedelta(days=2))
        puzzle2 = create_published_puzzle(editor=self.user2, clues_pts=[3, 2], posted_on=now() - timedelta(days=3))
        puzzle3 = create_published_puzzle(editor=self.user2, clues_pts=[1, 1], posted_on=now() - timedelta(days=4))
        p2_session = SolverSession.new(puzzle2, self.user1)  # Current user session for puzzle 2
        p3_session = SolverSession.new(puzzle3, user3)  # User3 session for puzzle 3
        response = self.client.get(self.target_page)
        objects = response.context['object_list']
        self.assertEqual(objects[0].other_sessions, 0)  # Puzzle 1 - created last - no session
        self.assertEqual(objects[1].other_sessions, 0)  # Puzzle 2 - current user session only
        self.assertEqual(objects[2].other_sessions, 1)  # Puzzle 3 - user3 session

    def test_has_show_filter_form_with_selection_matching_url_parameter(self):
        response = self.client.get(self.target_page)
        self.assertEqual(response.context['form']['show'].value(), "all")
        response = self.client.get(self.target_page + "?show=all")
        self.assertEqual(response.context['form']['show'].value(), "all")
        response = self.client.get(self.target_page + "?show=me_editor")
        self.assertEqual(response.context['form']['show'].value(), "me_editor")
        response = self.client.get(self.target_page + "?show=unsolved")
        self.assertEqual(response.context['form']['show'].value(), "unsolved")
        response = self.client.get(self.target_page + "?show=unfinished")
        self.assertEqual(response.context['form']['show'].value(), "unfinished")

    def test_list_when_show_filter_is_me_editor(self):
        puzzle1 = create_published_puzzle(self.user1, posted_on=now() - timedelta(days=2))
        puzzle2 = create_published_puzzle(self.user2, posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user1, posted_on=now() - timedelta(days=1))  # user1 latest
        response = self.client.get(self.target_page + "?show=me_editor")
        objects = response.context['object_list']
        self.assertEqual(len(objects), 2)
        self.assertEqual(objects[0].id, puzzle3.id)
        self.assertEqual(objects[1].id, puzzle1.id)

    def test_list_when_show_filter_is_unsolved(self):
        user3 = User.objects.create(username="user3", email="xyx@uvz.com")
        puzzle0 = create_draft_puzzle(editor=self.user2)
        puzzle1 = create_published_puzzle(self.user1, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=2))
        puzzle2 = create_published_puzzle(self.user2, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user2, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=3))
        puzzle4 = create_published_puzzle(self.user2, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=1))
        create_session(puzzle2, self.user1, 3, 2, 12)
        create_session(puzzle3, self.user1, 3, 1, 10)
        create_session(puzzle4, user3, 2, 1, 8)
        response = self.client.get(self.target_page + "?show=unsolved")
        objects = response.context['object_list']
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].id, puzzle4.id)

    def test_list_when_show_filter_is_unfinished(self):
        user3 = User.objects.create(username="user3", email="xy@uvz.com")
        puzzle0 = create_draft_puzzle(editor=self.user2)
        puzzle1 = create_published_puzzle(self.user1, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=2))
        puzzle2 = create_published_puzzle(self.user2, clues_pts=[1, 1, 3, 1, 1], posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(self.user2, clues_pts=[1, 2, 1, 1, 1], posted_on=now() - timedelta(days=3))
        puzzle4 = create_published_puzzle(self.user2, clues_pts=[1, 1, 1, 1, 1], posted_on=now() - timedelta(days=1))
        create_session(puzzle2, self.user1, 3, 2, 12)
        create_session(puzzle3, self.user1, 2, 1, 10)
        create_session(puzzle4, user3, 2, 0, 8)
        response = self.client.get(self.target_page + "?show=unfinished")
        objects = response.context['object_list']
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].id, puzzle3.id)
