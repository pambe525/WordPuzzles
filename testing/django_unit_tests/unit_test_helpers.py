from django.utils.timezone import now

from puzzles.models import WordPuzzle


def create_published_puzzle(user=None, desc=None, type=0, posted_on=now(), clues_pts=None):
    if clues_pts is None: clues_pts = [1]
    n_clues = len(clues_pts)
    SUFFIX = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
    puzzle = WordPuzzle.objects.create(editor=user, type=type, desc=desc, shared_at=posted_on)
    for n in range(1, n_clues + 1):
        puzzle.add_clue(
            {'answer': 'WORD-' + SUFFIX[n], 'clue_text': 'Clue for Word' + SUFFIX[n], 'points': clues_pts[n - 1]})
    return puzzle
