from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.timezone import now, localtime
from django.db.utils import IntegrityError


def get_name(self):
    if self.first_name:
        return (self.first_name + ' ' + self.last_name).strip()
    else:
        return self.username

def utc_date_to_local_format(utc_date):
    dt_format = '%b %d, %Y at %H:%M:%S %p'
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
        return "Puzzle #" + str(self.id) + ": " + str(self.size) + " " + puzzle_type + " " + points

    def add_clue(self, form_data_dict):
        self.size += 1
        self.total_points += form_data_dict['points']
        new_clue = Clue.objects.create(puzzle=self, clue_num=self.size, **form_data_dict)
        self.save(update_fields=['size', 'total_points'])
        return new_clue

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
        self._adjust_clue_nums(clue_num)

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

    def get_local_time_info_text(self, current_user=None):
        username = str(self.editor)
        if current_user is not None and current_user == self.editor:
            username = "me"
        text = "Created by " + username + " on " + utc_date_to_local_format(self.created_at) + \
               " and last modified on " + utc_date_to_local_format(self.modified_at)
        return text

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
        return self.clue_text + " (" + self.get_answer_footprint_as_string() + ")"

    def get_answer_footprint_as_string(self):
        footprint = ''
        words = self.answer.split()
        for idx, word in enumerate(words):
            footprint += self.get_word_length_as_string(word)
            if idx < len(words) - 1: footprint += ','
        return footprint

    def get_word_length_as_string(self, word):
        len_text = str(len(word))
        hyphenated_parts = word.split('-')
        if len(hyphenated_parts) > 1:
            len_text = ''
            for idx, part in enumerate(hyphenated_parts):
                len_text += str(len(part))
                if idx < (len(hyphenated_parts) - 1):
                    len_text += '-'
        return len_text


class PuzzleSession(models.Model):
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    solver = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_clue_nums = models.CharField(null=True, validators=[validate_comma_separated_integer_list], max_length=100)
    revealed_clue_nums = models.CharField(null=True, validators=[validate_comma_separated_integer_list], max_length=100)
    score = models.IntegerField(default=0)
    elapsed_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def get_solved_clue_nums(self):
        return [] if self.solved_clue_nums is None else [int(e) for e in self.solved_clue_nums.split(',')]

    def get_revealed_clue_nums(self):
        return [] if self.revealed_clue_nums is None else [int(e) for e in self.revealed_clue_nums.split(',')]

    def get_total_clues(self):
        return WordPuzzle.objects.get(id=self.puzzle.id).size

    def get_clue_points(self):
        clues = WordPuzzle.objects.get(id=self.puzzle.id).get_clues()
        points = []
        for clue in clues: points.append(clue.points)
        return points

    def is_complete(self):
        complete = False
        solved = self.get_solved_clue_nums()
        revealed = self.get_revealed_clue_nums()
        if any(item in solved for item in revealed):
            raise IntegrityError("Solved and revealed clue numbers are not mutually exclusive.")
        if len(solved) + len(revealed) == self.get_total_clues(): complete = True
        return complete

    def get_solved_points(self):
        solved = self.get_solved_clue_nums()
        points = self.get_clue_points()
        sum = 0
        for clue_num in solved:
            sum += points[clue_num - 1]
        return sum

    def get_revealed_points(self):
        revealed = self.get_revealed_clue_nums()
        points = self.get_clue_points()
        sum = 0
        for clue_num in revealed:
            sum += points[clue_num - 1]
        return sum

    def add_solved_clue_num(self, clue_num):
        if clue_num not in self.get_solved_clue_nums() and clue_num not in self.get_revealed_clue_nums():
            if self.solved_clue_nums is None:
                self.solved_clue_nums = str(clue_num)
            else:
                self.solved_clue_nums += ',' + str(clue_num)
            self.save(update_fields=['solved_clue_nums', 'score'])

    def add_revealed_clue_num(self, clue_num):
        if clue_num not in self.get_revealed_clue_nums() and clue_num not in self.get_solved_clue_nums():
            if self.revealed_clue_nums is None:
                self.revealed_clue_nums = str(clue_num)
            else:
                self.revealed_clue_nums += ',' + str(clue_num)
            self.save(update_fields=['revealed_clue_nums'])

    def save(self, *args, **kwargs):
        self.score = self.get_solved_points()
        super(PuzzleSession, self).save(*args, **kwargs)
