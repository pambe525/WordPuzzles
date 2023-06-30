from django.contrib import admin

from .models import Puzzle, WordPuzzle, Clue, SolveSession

# Register your models here.
admin.site.register(Puzzle)
admin.site.register(WordPuzzle)
admin.site.register(Clue)
admin.site.register(SolveSession)
