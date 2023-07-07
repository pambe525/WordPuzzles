from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.utils import IntegrityError
from django.utils.timezone import now

from puzzles.text_parsers import ClueChecker


def get_name(self):
    if self.first_name:
        return (self.first_name + ' ' + self.last_name).strip()
    else:
        return self.username


def utc_date_to_local_format(utc_date):
    dt_format = '%b %d, %Y at %H:%M:%S'
    return utc_date.astimezone().strftime(dt_format)


User.add_to_class("__str__", get_name)


class Puzzle(models.Model):
    is_xword = models.BooleanField(default=True)
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    size = models.IntegerField(default=0)
    desc = models.TextField(default="")
    data = models.TextField(default="")
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        if self.is_xword:
            puzzle_size = "(" + str(self.size) + "x" + str(self.size) + ")"
            return "Puzzle #" + str(self.id) + ": Crossword Puzzle " + puzzle_size
        else:
            puzzle_size = "(" + str(self.size) + " clues)"
            return "Puzzle #" + str(self.id) + ": Word Puzzle " + puzzle_size


class WordPuzzle(models.Model):
    TYPE_CHOICES = [(0, "Non-cryptic Clues"), (1, "Cryptic Clues")]
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    desc = models.TextField(null=True, blank=True)
    size = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        puzzle_type = str(self.TYPE_CHOICES[self.type][1])
        points = "[" + str(self.total_points) + " pts]"
        return "Puzzle " + str(self.id) + ": " + str(self.size) + " " + puzzle_type + " " + points

    @staticmethod
    def get_draft_puzzles_count(current_user_id):
        return WordPuzzle.objects.filter(editor=current_user_id, shared_at=None).count()

    @staticmethod
    def get_draft_puzzles_as_list(current_user_id):
        query_set = WordPuzzle.objects.filter(editor=current_user_id, shared_at=None).order_by('-modified_at')
        draft_puzzle_list = []
        for puzzle in query_set:
            puzzle_dict = {}.fromkeys(['id', 'title', 'type', 'type_text', 'desc', 'utc_modified_at'])
            puzzle_dict['id'] = puzzle.id
            puzzle_dict['title'] = str(puzzle)
            puzzle_dict['type'] = puzzle.type
            puzzle_dict['type_text'] = WordPuzzle.TYPE_CHOICES[puzzle.type][1]
            puzzle_dict['desc'] = puzzle.desc
            puzzle_dict['utc_modified_at'] = puzzle.modified_at.strftime("%Y-%m-%d %H:%M:%SZ")
            draft_puzzle_list.append(puzzle_dict)
        return draft_puzzle_list

    @staticmethod
    def create_new_puzzle(editor, data):
        return WordPuzzle.objects.create(editor=editor, type=data['type'], desc=data['desc'])

    def add_clues(self, cleaned_clues_data):
        for clue_data in cleaned_clues_data:
            clue, created = Clue.objects.get_or_create(puzzle=self, clue_num=clue_data['clue_num'])
            clue.clue_text = clue_data['clue_text']
            clue.answer = clue_data['answer']
            clue.save()
            if created:
                self.size += 1
                self.total_points += 1
                self.save()

    # Checks if given unsaved clue has the same answer in existing saved clues
    # returns clue number that has same answer as given clue
    def has_duplicate_answer(self, clue_data):
        for saved_clue in self.get_clues():
            if saved_clue.clue_num == clue_data['clue_num']: break
            if saved_clue.answer.upper() == clue_data['answer'].upper():
                return saved_clue.clue_num
        return None

    def update_clue(self, clue_num, form_data_dict):
        clue = Clue.objects.filter(puzzle=self, clue_num=clue_num)
        self.total_points += (form_data_dict['points'] - clue[0].points)
        clue.update(**form_data_dict)
        self.save(update_fields=['total_points'])
        return clue

    def delete_clue(self, clue_num):
        clue = Clue.objects.get(puzzle=self, clue_num=clue_num)
        self.total_points -= clue.points
        self.size -= 1
        clue.delete()
        self.save(update_fields=['size', 'total_points'])
        # self._adjust_clue_nums(clue_num)

    def _adjust_clue_nums(self, start_clue_num):
        clues = Clue.objects.filter(puzzle=self)
        new_clue_num = start_clue_num
        for index in range(start_clue_num - 1, len(clues)):
            clues[index].clue_num = new_clue_num
            new_clue_num += 1
            clues[index].save(update_fields=['clue_num'])

    def get_clues(self):
        return Clue.objects.filter(puzzle=self).order_by('clue_num')

    def publish(self, time_stamp=now()):
        self.shared_at = time_stamp
        self.save(update_fields=['shared_at'])
        return self

    def unpublish(self):
        self.shared_at = None
        self.save(update_fields=['shared_at'])
        return self

    def is_published(self):
        return self.shared_at is not None

    def get_all_solved_clue_ids(self, solver):
        solved_clues = SolvedClue.objects.filter(clue__puzzle=self, solver=solver, revealed=False).order_by('clue')
        return list(solved_clues.values_list('clue', flat=True))

    def get_all_revealed_clue_ids(self, solver):
        solved_clues = SolvedClue.objects.filter(clue__puzzle=self, solver=solver, revealed=True).order_by('clue')
        return list(solved_clues.values_list('clue', flat=True))


class Clue(models.Model):
    INTEGER_CHOICES = [tuple([x, x]) for x in range(1, 6)]
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    clue_num = models.IntegerField(null=True)
    answer = models.CharField(null=True, max_length=24)
    clue_text = models.TextField(null=True)
    parsing = models.TextField(null=True, blank=True)
    points = models.IntegerField(default=1, choices=INTEGER_CHOICES)

    def __str__(self):
        text = ''
        text += ("<#>" if self.clue_num is None else str(self.clue_num)) + ". "
        text += ("<clue>" if self.clue_text is None else self.clue_text) + " ["
        text += ("<answer>" if self.answer is None else self.answer) + "]"
        return text

    def get_decorated_clue_text(self):
        return ClueChecker().get_decorated_clue_text(self.clue_text, self.answer)


class GroupSession(models.Model):
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    start_at = models.DateTimeField(null=False)
    finish_at = models.DateTimeField(null=True)


class SolverSession(models.Model):
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    solver = models.ForeignKey(User, on_delete=models.CASCADE)
    group_session = models.ForeignKey(GroupSession, on_delete=models.CASCADE, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    def check_if_ended(self):
        puzzle = WordPuzzle.objects.get(id=self.puzzle.id)
        resolved_count = len(SolvedClue.objects.filter(clue__puzzle=self.puzzle, solver=self.solver))
        if puzzle.size == resolved_count:
            self.finished_at = now()
            self.save()
        return puzzle.size == resolved_count


class SolvedClue(models.Model):
    clue = models.ForeignKey(Clue, on_delete=models.CASCADE)
    solver = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(SolverSession, on_delete=models.CASCADE)
    revealed = models.BooleanField(default=False)  # If True, revealed; else Solved
