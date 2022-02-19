import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from puzzles.models import Puzzle, WordPuzzle


class HomeView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        puzzles = self.model.objects.filter(editor=request.user.id).order_by('-modified_at')
        puzzles_list = []
        for i in range(len(puzzles)):
            last_edited = puzzles[i].modified_at.strftime('%b %d, %Y')
            dict_obj = {'id': puzzles[i].id, 'modified_at': last_edited, 'name': str(puzzles[i])}
            puzzles_list.append(dict_obj)
        return render(request, "home.html", context={'puzzles': puzzles_list})

class NewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        new_puzzle = self.model.objects.create(editor=request.user)
        return redirect('edit_puzzle', puzzle_id=new_puzzle.id)

class DeletePuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):

        if "delete_puzzle_confirm" in request.path:
            return render(request, 'delete_puzzle.html', context={'puzzle_id': puzzle_id})
        else:
            if not self.model.objects.filter(id=puzzle_id).exists():
                msg = 'Puzzle #' + str(puzzle_id) + " does not exist."
                return render(request, 'delete_puzzle.html', context={'error_message': msg})
            puzzle = self.model.objects.get(id=puzzle_id)
            if request.user != puzzle.editor:
                msg ='You cannot delete this puzzle since you are not the editor.'
                return render(request, 'delete_puzzle.html', context={'error_message': msg})
            else:
                puzzle.delete()
                return redirect("home")


#================================================================================
class EditPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):
        data_dict = {'id': puzzle_id}
        return render(request, 'edit_puzzle.html', context=data_dict)

class PreviewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):
        data_dict = {'id': puzzle_id}
        return render(request, 'preview_puzzle.html', context=data_dict)

class OldEditPuzzleView(LoginRequiredMixin, View):
    model = Puzzle

    def get(self, request, id=None):
        data_dict = error_msg = None
        # New Puzzle GET (URL is new_xword_puzzle or new_word_puzzle)
        if "word" in request.path:
            is_word = True if "new_xword_puzzle" in request.path else False
            data_dict = {'id': None, 'is_xword': is_word}

        # Edit Puzzle GET (URL is edit_puzzle/id/)
        elif "edit_puzzle" in request.path:
            if self.model.objects.filter(id=id).exists():
                record = self.model.objects.get(id=id)
                if request.user == record.editor:
                    data_dict = model_to_dict(record)
                    data_dict['data'] = json.loads(data_dict['data'])
                    if data_dict['shared_at']:
                        data_dict['shared_at'] = data_dict['shared_at'].isoformat()
                else:
                    data_dict = {'id': id}
                    error_msg = "You are not authorized to edit this puzzle"
            else:
                data_dict = {'id': id}
                error_msg = "Puzzle id " + str(id) + " does not exist"
        return self.render_get_response(request, data_dict, error_msg)

    def post(self, request, id=None):
        try:
            # id = None
            if request.POST.get('action') == 'save':
                data_dict = json.loads(request.POST.get('data'))
                data_dict['data'] = json.dumps(data_dict['data'])
                data_dict['editor'] = request.user
                if data_dict['id'] is None:
                    record = self.model(**data_dict)
                    record.save()
                else:
                    record = self.model.objects.get(id=data_dict['id'])
                    for attr, value in data_dict.items():
                        setattr(record, attr, value)
                    record.save()
                id = record.id
            elif request.POST.get('action') == 'delete':
                id = request.POST.get('id')
                self.model.objects.get(id=id).delete()
            return JsonResponse({'id': id})
        except Exception as err:
            return JsonResponse({'error_message': str(err)})

    def render_get_response(self, request, data_dict, error_msg=None):
        context = {}
        if error_msg:
            context['error_message'] = error_msg
        if data_dict is not None:
            context['data'] = json.dumps(data_dict)
        return render(request, "edit_puzzle.html", context=context)
