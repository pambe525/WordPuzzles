from django.utils.timezone import now

from puzzles.models import WordPuzzle


def create_draft_puzzle(user=None, desc=None, type=0, clues_pts=None, has_parsing=False):
    if clues_pts is None: clues_pts = [1]
    n_clues = len(clues_pts)
    SUFFIX = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
    puzzle = WordPuzzle.objects.create(editor=user, type=type, desc=desc)
    for n in range(1, n_clues + 1):
        parsing = None if not has_parsing else "Parsing for word" + SUFFIX[n]
        puzzle.add_clue(
            {'answer': 'WORD-' + SUFFIX[n], 'clue_text': 'Clue for Word' + SUFFIX[n],
             'parsing': parsing, 'points': clues_pts[n - 1]})
    return puzzle


def create_published_puzzle(user=None, desc=None, type=0, posted_on=now(), clues_pts=None, has_parsing=False):
    puzzle = create_draft_puzzle(user=user, desc=desc, type=type, clues_pts=clues_pts, has_parsing=has_parsing)
    puzzle.publish(time_stamp=posted_on)
    return puzzle


def get_full_clue_desc(clue):
    return str(clue.clue_num) + ". " + clue.get_decorated_clue_text() + " [" + str(clue.points) + " pts]"
