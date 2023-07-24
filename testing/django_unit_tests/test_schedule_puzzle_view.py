from datetime import timedelta

from django.contrib.auth.models import User
from django.utils.timezone import now

from puzzles.models import WordPuzzle, SolverSession, GroupSession
from testing.data_setup_utils import add_clue, create_published_puzzle, create_draft_puzzle
from testing.django_unit_tests.test_puzzle_crud_views import BaseEditPuzzleTest


class ScheduleGroupSessionViewTest(BaseEditPuzzleTest):
    target_page = "/schedule_group_session/"

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_POST_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.post(self.target_page + "1/", data={})
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 1")
        self.assertContains(response, 'This puzzle does not exist.')

    def test_POST_shows_error_if_host_is_not_editor(self):
        user2 = User.objects.create(username="user2", email="xyz@cde.com")
        puzzle = create_draft_puzzle(editor=user2)
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data={})
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, 'This operation is not permitted since you are not the editor.')

    def test_POST_shows_error_if_puzzle_has_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        data = {'scheduled_at': now()}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data=data)  # Schedule puzzle
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, "No clues found.  Add clues before scheduling.")

    def test_POST_shows_error_if_puzzle_is_published(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data={})
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, "This puzzle is published and cannot be scheduled.")

    def test_POST_creates_new_group_session_and_redirects_to_home(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        scheduled_at = now()
        data = {'scheduled_at': scheduled_at}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data)
        session = GroupSession.objects.get(puzzle=puzzle, host=self.user)
        self.assertIsNotNone(session)
        self.assertEqual(session.start_at, scheduled_at)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)  # puzzle is still unpublished

    def test_POST_shows_error_if_puzzle_already_has_group_session(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 2, 1, 1])
        scheduled_at = now() + timedelta(days=3)
        data = {'scheduled_at': scheduled_at}
        self.client.post(self.target_page + str(puzzle.id) + "/", data)
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data)  # do it again
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, "Puzzle has a previous group session.")
        self.assertEqual(len(GroupSession.objects.filter(puzzle=puzzle, host=self.user)), 1)


class UnscheduleGroupSessionViewTest(BaseEditPuzzleTest):
    target_page = "/unschedule_group_session/"

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_POST_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.post(self.target_page + "1/", data={})
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 1")
        self.assertContains(response, 'This puzzle does not exist.')

    def test_POST_shows_error_if_group_session_does_not_exist(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        response = self.client.post(self.target_page + str(puzzle.id) + "/", data={})
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, 'No group session found for given puzzle.')

    def test_POST_shows_error_if_host_is_not_editor(self):
        user2 = User.objects.create(username="user2", email="xyz@cde.com")
        puzzle = create_draft_puzzle(editor=user2)
        session = GroupSession.objects.create(puzzle=puzzle, host=user2, start_at=now() + timedelta(days=2))
        response = self.client.post(self.target_page + str(puzzle.id) + "/")
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, 'This operation is not permitted since you are not the editor.')

    def test_POST_shows_error_if_group_session_has_participant_sessions(self):
        user2 = User.objects.create(username="user2", email="xyz@cde.com")
        puzzle = create_draft_puzzle(editor=self.user)
        group_session = GroupSession.objects.create(puzzle=puzzle, host=self.user, start_at=now() + timedelta(days=1))
        SolverSession.objects.create(puzzle=puzzle, solver=user2, group_session=group_session)
        response = self.client.post(self.target_page + str(puzzle.id) + "/")
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, 'Puzzle group session has participants and cannot be deleted.')

    def test_POST_deletes_group_session_if_no_errors_and_redirects_to_homepage(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        group_session = GroupSession.objects.create(puzzle=puzzle, host=self.user, start_at=now())
        response = self.client.post(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.url, "/")
        self.assertFalse(GroupSession.objects.filter(puzzle=puzzle).exists())
