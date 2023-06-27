from django.contrib.auth.models import User
from django.utils.timezone import now

from puzzles.models import WordPuzzle, PuzzleSession, Clue


def create_user(username='test_user', password='secret_key', email='user@test.com'):
    return User.objects.create_user(username=username, email=email, password=password)


def create_draft_puzzle(editor=None, desc=None, type=0, clues_pts=None, has_parsing=False):
    if clues_pts is None: clues_pts = [1]
    n_clues = len(clues_pts)
    SUFFIX = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
    puzzle = WordPuzzle.objects.create(editor=editor, type=type, desc=desc)
    for n in range(1, n_clues + 1):
        parsing = None if not has_parsing else "Parsing for word" + SUFFIX[n]
        add_clue(puzzle,
            {'answer': 'WORD-' + SUFFIX[n], 'clue_text': 'Clue for Word' + SUFFIX[n],
             'parsing': parsing, 'points': clues_pts[n - 1]})
    return puzzle


def create_published_puzzle(editor=None, desc=None, type=0, posted_on=now(), clues_pts=None, has_parsing=False):
    puzzle = create_draft_puzzle(editor=editor, desc=desc, type=type, clues_pts=clues_pts, has_parsing=has_parsing)
    puzzle.publish(time_stamp=posted_on)
    return puzzle


def get_full_clue_desc(clue):
    return str(clue.clue_num) + ". " + clue.get_decorated_clue_text()  # + " [" + str(clue.points) + " pts]"


def create_session(solver=None, puzzle=None, solved_clues=None, revealed_clues=None, elapsed_secs=0):
    return PuzzleSession.objects.create(solver=solver, puzzle=puzzle, solved_clue_nums=solved_clues,
                                        revealed_clue_nums=revealed_clues, elapsed_seconds=elapsed_secs)


def add_clue(puzzle, clue_data):
    puzzle.size += 1
    puzzle.total_points += clue_data['points']
    new_clue = Clue.objects.create(puzzle=puzzle, clue_num=puzzle.size, **clue_data)
    puzzle.save(update_fields=['size', 'total_points'])
    return new_clue
