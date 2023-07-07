from django.contrib import admin

from .models import Puzzle, WordPuzzle, Clue, SolverSession, SolvedClue, GroupSession

# Register your models here.
admin.site.register(Puzzle)
admin.site.register(WordPuzzle)
admin.site.register(Clue)
admin.site.register(SolverSession)
admin.site.register(SolvedClue)
admin.site.register(GroupSession)
