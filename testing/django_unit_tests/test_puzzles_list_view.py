from datetime import timedelta

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from puzzles.models import SolverSession
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle


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
        self.assertContains(response, "No published puzzles.")
        # form = response.context['form']
        # self.assertEqual(form.initial['sort_by'], 'shared_at')
        # self.assertEqual(form.initial['order'], '-')

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
        puzzle1 = create_published_puzzle(editor=self.user1, clues_pts=[1, 2], posted_on=now()-timedelta(days=1))
        puzzle2 = create_published_puzzle(editor=self.user2, clues_pts=[3, 2], posted_on=now()-timedelta(days=2))
        puzzle3 = create_published_puzzle(editor=self.user2, clues_pts=[1, 1], posted_on=now()-timedelta(days=3))
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
        puzzle1 = create_published_puzzle(editor=self.user1, clues_pts=[1, 2], posted_on=now()-timedelta(days=2))
        puzzle2 = create_published_puzzle(editor=self.user2, clues_pts=[3, 2], posted_on=now()-timedelta(days=3))
        puzzle3 = create_published_puzzle(editor=self.user2, clues_pts=[1, 1], posted_on=now()-timedelta(days=4))
        p2_session = SolverSession.new(puzzle2, self.user1)  # Current user session for puzzle 2
        p3_session = SolverSession.new(puzzle3, user3)       # User3 session for puzzle 3
        response = self.client.get(self.target_page)
        objects = response.context['object_list']
        self.assertEqual(objects[0].other_sessions, 0)  # Puzzle 1 - created last - no session
        self.assertEqual(objects[1].other_sessions, 0)  # Puzzle 2 - current user session only
        self.assertEqual(objects[2].other_sessions, 1)  # Puzzle 3 - user3 session


    # def test_Form_reflects_passed_parameters_on_url(self):
    #     create_published_puzzle(self.user)
    #     response = self.client.get("/puzzles_list?sort_by=desc&order=")
    #     form = response.context['form']
    #     self.assertEqual(form.initial['sort_by'], 'desc')
    #     self.assertEqual(form.initial['order'], '')
    #     self.assertEqual(len(response.context['object_list']), 1)
    #
    # def test_List_with_parameters_sort_by_shared_at_and_order_ascending(self):
    #     puzzle1 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=1))
    #     puzzle2 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=5))
    #     puzzle3 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=3))
    #     response = self.client.get("/puzzles_list?sort_by=shared_at&order=")
    #     objects = response.context['object_list']
    #     self.assertEqual(objects[0].id, puzzle2.id)
    #     self.assertEqual(objects[1].id, puzzle3.id)
    #     self.assertEqual(objects[2].id, puzzle1.id)
    #
    # def test_List_with_parameters_sort_by_editor_and_order_ascending(self):
    #     user2 = User.objects.create_user(username="joe_smith", password="secretkey2")
    #     user3 = User.objects.create_user(username="another_user", password="secretkey3")
    #     puzzle1 = create_published_puzzle(user2, posted_on=now() - timedelta(days=1))
    #     puzzle2 = create_published_puzzle(user3, posted_on=now() - timedelta(days=5))
    #     puzzle3 = create_published_puzzle(self.user, posted_on=now() - timedelta(days=3))
    #     response = self.client.get("/puzzles_list?sort_by=editor__username&order=")
    #     objects = response.context['object_list']
    #     self.assertEqual(objects[0].id, puzzle2.id)
    #     self.assertEqual(objects[1].id, puzzle1.id)
    #     self.assertEqual(objects[2].id, puzzle3.id)
    #
    # def test_List_with_parameters_sort_by_size_and_order_descending(self):
    #     puzzle1 = create_published_puzzle(self.user, clues_pts=[3, 5])
    #     puzzle2 = create_published_puzzle(self.user, clues_pts=[3, 4, 5, 1])
    #     puzzle3 = create_published_puzzle(self.user, clues_pts=[3, 2, 1])
    #     response = self.client.get("/puzzles_list?sort_by=size&order=-")
    #     objects = response.context['object_list']
    #     self.assertEqual(objects[0].id, puzzle2.id)
    #     self.assertEqual(objects[1].id, puzzle3.id)
    #     self.assertEqual(objects[2].id, puzzle1.id)
    #     response = self.client.get("/puzzles_list?sort_by=total_points&order=")
    #     objects = response.context['object_list']
    #     self.assertEqual(objects[0].id, puzzle3.id)
    #     self.assertEqual(objects[1].id, puzzle1.id)
    #     self.assertEqual(objects[2].id, puzzle2.id)
    #
    # def test_posted_puzzles_include_session_data(self):
    #     user1 = create_user(username="user1")
    #     user2 = create_user(username="user2")
    #     create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1, 2, 1])
    #     puzzle2 = create_published_puzzle(editor=user2, desc="Daily Puzzle 2", clues_pts=[1, 1])
    #     session1 = create_session(solver=self.user, puzzle=puzzle2)
    #     create_session(solver=user2, puzzle=puzzle2)
    #     response = self.client.get('/puzzles_list')
    #     self.assertEqual(response.context['object_list'][0].session_count, 0)
    #     self.assertEqual(response.context['object_list'][1].session_count, 2)
    #     self.assertIsNone(response.context['object_list'][0].user_session)
    #     self.assertEqual(response.context['object_list'][1].user_session, session1)
