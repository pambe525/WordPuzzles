from datetime import datetime

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.utils.timezone import now

from puzzles.models import Puzzle, WordPuzzle, Clue, SolverSession, GroupSession, SolvedClue
from testing.data_setup_utils import create_published_puzzle


class UserNameTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joesmith')

    def test_name_without_first_or_last_name(self):
        self.assertEqual(str(self.user), "joesmith")

    def test_name_with_last_name_only(self):
        self.user.last_name = "Smith"
        self.assertEqual(str(self.user), "joesmith")

    def test_name_with_first_name_only(self):
        self.user.first_name = "Joe"
        self.assertEqual(str(self.user), "Joe")

    def test_name_with_first_and_last_name(self):
        self.user.first_name = "Joe"
        self.user.last_name = "Smith"
        self.assertEqual(str(self.user), "Joe Smith")


class PuzzleModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_editor_field(self):
        puzzle = Puzzle.objects.create(editor=self.user)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual("testuser", puzzle.editor.username)

    def test_shared_at_field(self):
        current_time_stamp = datetime.now(tz=timezone.utc).isoformat()  # timestamp as ISO string (UTC)
        puzzle = Puzzle.objects.create(shared_at=current_time_stamp)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual(current_time_stamp, puzzle.shared_at.isoformat())  # Convert date object to string

    def test_field_defaults(self):
        puzzle = Puzzle.objects.create()
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertTrue(puzzle.is_xword)
        self.assertIsNone(puzzle.editor)
        self.assertEqual(0, puzzle.size)
        self.assertEqual("", puzzle.desc)
        self.assertEqual("", puzzle.data)
        self.assertIsNone(puzzle.shared_at)

    def test_string_representation(self):
        puzzle = Puzzle.objects.create(size=10)
        self.assertEqual("Puzzle #1: Crossword Puzzle (10x10)", str(puzzle))
        puzzle = Puzzle.objects.create(size=20, is_xword=False)
        self.assertEqual("Puzzle #2: Word Puzzle (20 clues)", str(puzzle))


class WordPuzzleModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')

    def test_default_instance_with_editor_field(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.assertEqual("testuser", puzzle.editor.username)
        self.assertEqual(puzzle.type, 1)
        self.assertEqual(puzzle.size, 0)
        self.assertIsNone(puzzle.desc)
        self.assertIsNone(puzzle.shared_at)

    def test_string_representation(self):
        puzzle = WordPuzzle.objects.create(size=10, type=0, editor=self.user)
        self.assertEqual("Puzzle 1: 10 Non-cryptic Clues [0 pts]", str(puzzle))
        puzzle = WordPuzzle.objects.create(size=20, type=1, editor=self.user)
        self.assertEqual("Puzzle 2: 20 Cryptic Clues [0 pts]", str(puzzle))

    def test_add_clues_creates_new_clues_and_updates_counts(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        cleaned_input = [{'clue_num': 1, 'clue_text': 'some clue text (2-4)', 'answer': 'my-word'},
                         {'clue_num': 2, 'clue_text': 'another clue', 'answer': 'ANOTHER WORD'}]
        puzzle.add_clues(cleaned_input)
        created_clues = Clue.objects.all()
        self.assertEqual(2, len(created_clues))
        clue1 = created_clues[0]
        clue2 = created_clues[1]
        # first clue
        self.assertEqual(clue1.puzzle, puzzle)
        self.assertEqual(clue1.clue_num, 1)
        self.assertEqual(clue1.answer, 'my-word')  # NOT capitalized
        self.assertEqual(clue1.clue_text, 'some clue text (2-4)')
        self.assertIsNone(clue1.parsing)
        self.assertEqual(clue1.points, 1)
        # second clue
        self.assertEqual(clue2.puzzle, puzzle)
        self.assertEqual(clue2.clue_num, 2)
        self.assertEqual(clue2.answer, 'ANOTHER WORD')  # capitalization preserved
        self.assertEqual(clue2.clue_text, 'another clue')
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 2)
        self.assertEqual(puzzle.size, 2)

    def test_get_clues_returns_all_clues_as_a_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        cleaned_input = [{'clue_num': 1, 'clue_text': 'some clue text (2-4)', 'answer': 'my-word'},
                         {'clue_num': 3, 'clue_text': 'another clue', 'answer': 'ANOTHER WORD'}]
        puzzle.add_clues(cleaned_input)
        clues_list = puzzle.get_clues()
        self.assertEqual(len(clues_list), 2)
        self.assertEqual(1, clues_list[0].clue_num)
        self.assertEqual(3, clues_list[1].clue_num)

    def test_get_all_solved_clue_nums(self):
        creator = User.objects.create(username="creator", password="secretkey", email="abc@cde.com")
        puzzle = create_published_puzzle(editor=creator, clues_pts=[4, 2, 1, 2, 1, 3])
        clues = puzzle.get_clues()
        session1 = SolverSession.objects.create(solver=self.user, puzzle=puzzle)
        session2 = SolverSession.objects.create(solver=self.user, puzzle=puzzle)
        SolvedClue.objects.create(clue=clues[1], session=session1, solver=self.user)
        SolvedClue.objects.create(clue=clues[4], session=session1, solver=self.user)
        SolvedClue.objects.create(clue=clues[2], session=session2, solver=self.user)
        SolvedClue.objects.create(clue=clues[0], session=session2, solver=self.user, revealed=True)
        clue_ids = puzzle.get_all_solved_clue_ids(self.user)
        self.assertListEqual(clue_ids, [2, 3, 5])

    def test_get_all_revealed_clue_nums(self):
        creator = User.objects.create(username="creator", password="secretkey", email="abc@de.com")
        puzzle = create_published_puzzle(editor=creator, clues_pts=[4, 2, 1, 2, 1, 3])
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(solver=self.user, puzzle=puzzle)
        SolvedClue.objects.create(clue=clues[1], session=session, solver=self.user, revealed=True)
        SolvedClue.objects.create(clue=clues[4], session=session, solver=self.user)
        SolvedClue.objects.create(clue=clues[2], session=session, solver=self.user, revealed=True)
        clue_ids = puzzle.get_all_revealed_clue_ids(self.user)
        self.assertListEqual(clue_ids, [2, 3])


class ClueModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)

    def test_default_instance(self):
        clue = Clue.objects.create(puzzle=self.puzzle)
        self.assertIsNone(clue.clue_num)
        self.assertIsNone(clue.clue_text)
        self.assertIsNone(clue.answer)
        self.assertIsNone(clue.parsing)
        self.assertEqual(str(clue), "<#>. <clue> [<answer>]")

    def test_string_representation(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, answer="SOME WORD", clue_text="Cryptic clue (4,4)")
        self.assertEqual(str(clue), "1. Cryptic clue (4,4) [SOME WORD]")

    def test_clues_are_deleted_if_related_puzzle_is_deleted(self):
        clue1 = Clue.objects.create(puzzle=self.puzzle, clue_num=1)
        clue2 = Clue.objects.create(puzzle=self.puzzle, clue_num=2)
        clue3 = Clue.objects.create(puzzle=self.puzzle, clue_num=3)
        self.assertEqual(Clue.objects.all().count(), 3)
        self.puzzle.delete()
        self.assertEqual(Clue.objects.all().count(), 0)

    def test_get_decorated_clue_with_length_not_specified_in_clue(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, clue_text='This is a clue')
        clue.answer = "ONEWORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (7)')
        clue.answer = "TWO WORDS"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,5)')
        clue.answer = "MULTIPLE  SINGLE   WORDS IN A SENTENCE"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (8,6,5,2,1,8)')
        clue.answer = "HYPHENATED-WORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (10-4)')
        clue.answer = "THE EDITOR-IN-CHIEF FOR ALL-IN"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,6-2-5,3,3-2)')

    def test_get_decorated_clue_with_length_specified_in_clue(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, clue_text='This is a clue (3,4)')
        clue.answer = "ONE WORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,4)')


class GroupSessionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)

    def test_puzzle_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, host=self.user)

    def test_host_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, puzzle=self.puzzle)

    def test_start_at_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, puzzle=self.puzzle, host=self.user)

    def test_default_instance(self):
        scheduled_date = now()
        session = GroupSession.objects.create(puzzle=self.puzzle, host=self.user, start_at=scheduled_date)
        self.assertEqual(session.puzzle, self.puzzle)
        self.assertEqual(session.host, self.user)
        self.assertEqual(session.start_at, scheduled_date)
        self.assertIsNone(session.finish_at)


class SolvedClueModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)
        self.clue = Clue.objects.create(puzzle=self.puzzle)
        self.session = SolverSession.objects.create(puzzle=self.puzzle, solver=self.user)

    def test_clue_is_required(self):
        self.assertRaises(Exception, SolvedClue.objects.create, solver=self.user)

    def test_solver_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, clue=self.clue)

    def test_session_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, clue=self.clue, solver=self.user)

    def test_default_instance(self):
        solved_clue = SolvedClue.objects.create(clue=self.clue, solver=self.user, session=self.session)
        self.assertEqual(solved_clue.clue, self.clue)
        self.assertEqual(solved_clue.solver, self.user)
        self.assertEqual(solved_clue.session, self.session)
        self.assertFalse(solved_clue.revealed)


class SolveSessionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.puzzle = create_published_puzzle(editor=self.user, clues_pts=[4, 2, 1, 2, 1, 3])

    def test_puzzle_is_required_field(self):
        self.assertRaises(Exception, SolverSession.objects.create, solver=self.user)

    def test_solver_is_required_field(self):
        self.assertRaises(IntegrityError, SolverSession.objects.create, puzzle=self.puzzle)

    def test_default_instance(self):
        session = SolverSession.objects.create(solver=self.user, puzzle=self.puzzle)
        self.assertEqual(session.puzzle, self.puzzle)
        self.assertEqual(session.solver, self.user)
        self.assertIsNone(session.group_session)
        self.assertLessEqual(session.started_at, now())
        self.assertIsNone(session.finished_at)
#
#     def test_get_solved_clue_nums(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         self.assertEqual(session.get_solved_clue_nums(), [])
#         session.solved_clue_nums = '1,2,3,4,5,6,7,8,9,10,11,12,13,14'
#         self.assertEqual(session.get_solved_clue_nums(), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

#
#     def test_get_revealed_clue_nums(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         self.assertEqual(session.get_revealed_clue_nums(), [])
#         session.revealed_clue_nums = '1,2,3,4,5,6,7,8,9'
#         self.assertEqual(session.get_revealed_clue_nums(), [1, 2, 3, 4, 5, 6, 7, 8, 9])
#
#     def test_is_complete_returns_false_with_default_data(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         self.assertFalse(session.is_complete())
#
#     def test_is_complete_raises_error_if_solved_and_revealed_clues_are_not_mutually_exclusive(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         session.solved_clue_nums = '2,3,5'
#         session.revealed_clue_nums = '1,2,3'
#         self.assertRaises(IntegrityError, session.is_complete)
#
#     def test_is_complete_returns_false_with_unsolved_clues(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         session.solved_clue_nums = '2,3,5'
#         session.revealed_clue_nums = '1,4'
#         self.assertFalse(session.is_complete())
#
#     def test_is_complete_returns_true_with_no_unsolved_clues(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         session.solved_clue_nums = '2,3,5'
#         session.revealed_clue_nums = '1,4,6'
#         self.assertTrue(session.is_complete())
#
#     def test_get_score_returns_correct_score(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         self.assertEqual(session.get_solved_points(), 0)
#         session.revealed_clue_nums = '1,4,6'
#         self.assertEqual(session.get_solved_points(), 0)
#         session.solved_clue_nums = '2,3'
#         self.assertEqual(session.get_solved_points(), 3)
#
#     def test_checking_contained_clue_nums(self):
#         SolveSession.objects.create(solver=self.user, puzzle=self.puzzle, solved_clue_nums="1,3")
#         self.assertFalse(SolveSession.objects.filter(solved_clue_nums__contains="2"))
#         self.assertTrue(SolveSession.objects.filter(solved_clue_nums__contains="3"))
#
#     def test_adding_solved_clue_num(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         session.add_solved_clue_num(2)
#         self.assertEqual(session.solved_clue_nums, "2")
#         session.add_solved_clue_num(4)
#         self.assertEqual(session.solved_clue_nums, "2,4")
#         session.add_solved_clue_num(2)  # Adding existing clue num ignored
#         self.assertEqual(session.solved_clue_nums, "2,4")
#         session = SolveSession.objects.get(solver=self.user, puzzle=self.puzzle)  # Retreived saved record
#         self.assertEqual(session.solved_clue_nums, "2,4")  # Verify updated data is saved
#
#     def test_adding_revealed_clue_num(self):
#         session = SolveSession.objects.create(solver=self.user, puzzle=self.puzzle)
#         session.add_revealed_clue_num(1)
#         self.assertEqual(session.revealed_clue_nums, "1")
#         session.add_revealed_clue_num(3)
#         self.assertEqual(session.revealed_clue_nums, "1,3")
#         session.add_revealed_clue_num(3)  # Adding existing clue num ignored
#         self.assertEqual(session.revealed_clue_nums, "1,3")
#         session = SolveSession.objects.get(solver=self.user, puzzle=self.puzzle)  # Retreived saved record
#         self.assertEqual(session.revealed_clue_nums, "1,3")  # Verify updated data is saved
