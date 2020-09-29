from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.models import Crossword


# ==============================================================================================
class CrosswordModelTest(TestCase):
    def test_string_representation(self):
        user = User.objects.create_user(username='testuser', password='12345')
        puzzle = Crossword.objects.create(editor=user)
        self.assertEquals(user, puzzle.editor)
        self.assertEqual(13, puzzle.size)
        self.assertEqual("", puzzle.blocks)
        self.assertEqual("Crossword Puzzle #1", str(puzzle))
