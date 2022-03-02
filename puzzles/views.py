from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View

from puzzles.forms import WordPuzzleForm, ClueForm
from puzzles.models import WordPuzzle, Clue


class HomeView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        puzzles = self.model.objects.filter(editor=request.user.id).order_by('-modified_at')
        draft_puzzles = []
        for i in range(len(puzzles)):
            last_edited = puzzles[i].modified_at.strftime('%b %d, %Y')
            dict_obj = {'id': puzzles[i].id, 'desc': puzzles[i].desc, 'size': puzzles[i].size,
                        'modified_at': last_edited, 'name': str(puzzles[i])}
            draft_puzzles.append(dict_obj)
        return render(request, "home.html", context={'draft_puzzles': draft_puzzles})


class NewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        new_puzzle = self.model.objects.create(editor=request.user)
        return redirect('edit_puzzle', puzzle_id=new_puzzle.id)


class DeletePuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):
        msg = None
        try:
            puzzle = self.model.objects.get(id=puzzle_id)
        except ObjectDoesNotExist:
            msg = 'Puzzle #' + str(puzzle_id) + " does not exist."
        else:
            if request.user != puzzle.editor:
                msg = 'You cannot delete this puzzle since you are not the editor.'
            elif "delete_puzzle_confirm" not in request.path:
                puzzle.delete()
                return redirect('home')
        return render(request, 'delete_puzzle.html', context={'puzzle_id': puzzle_id, 'err_msg': msg})


class EditPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):
        msg = None
        data_dict = {'id': puzzle_id, 'saved': False}
        try:
            puzzle = WordPuzzle.objects.get(id=puzzle_id)
            data_dict['total_points'] = puzzle.total_points
        except ObjectDoesNotExist:
            msg = 'Puzzle #' + str(puzzle_id) + " does not exist."
        else:
            if request.user != puzzle.editor:
                msg = 'You cannot edit this puzzle since you are not the creator.'
            else:
                form = WordPuzzleForm(instance=puzzle)
                data_dict['form'] = form
                data_dict['clues'] = puzzle.get_clues()
        finally:
            data_dict['err_msg'] = msg
            return render(request, 'edit_puzzle.html', context=data_dict)

    def post(self, request, puzzle_id=None):
        puzzle = WordPuzzle.objects.get(id=puzzle_id)
        form = WordPuzzleForm(request.POST, instance=puzzle)
        data_dict = {'id': puzzle_id, 'form': form, 'saved': False}
        if form.is_valid():
            form.save()
            data_dict['saved'] = True
            data_dict['total_points'] = puzzle.total_points
            data_dict['clues'] = puzzle.get_clues()
        return render(request, 'edit_puzzle.html', context=data_dict)


class EditClueView(LoginRequiredMixin, View):
    model = Clue

    def get(self, request, puzzle_id=None, clue_num=None):
        msg = None
        data_dict = {'id': puzzle_id, 'clue_num': 1, 'form': ClueForm()}
        try:
            puzzle = WordPuzzle.objects.get(id=puzzle_id)
        except ObjectDoesNotExist:
            msg = 'Puzzle #' + str(puzzle_id) + " does not exist."
        else:
            if request.user != puzzle.editor:
                msg = 'You cannot edit this puzzle since you are not the creator.'
            else:
                if clue_num is None:
                    data_dict['clue_num'] = puzzle.size + 1
                else:
                    data_dict['clue_num'] = clue_num
                    clue = Clue.objects.get(puzzle=puzzle, clue_num=clue_num)
                    data_dict['form'] = ClueForm(instance=clue)
        finally:
            data_dict['err_msg'] = msg
            return render(request, 'edit_clue.html', context=data_dict)

    def post(self, request, puzzle_id=None, clue_num=None):
        puzzle = WordPuzzle.objects.get(id=puzzle_id)
        form = ClueForm(request.POST)
        if form.is_valid():
            if clue_num == (puzzle.size + 1):  # New clue
                puzzle.add_clue(form.cleaned_data)
            else:
                puzzle.update_clue(clue_num, form.cleaned_data)
            return redirect("edit_puzzle", puzzle.id)
        else:
            data_dict = {'id': puzzle_id, 'clue_num': clue_num, 'form': form}
            return render(request, "edit_clue.html", context=data_dict)


class DeleteClueView(LoginRequiredMixin, View):
    model = Clue

    def get(self, request, puzzle_id=None, clue_num=None):
        msg = None
        try:
            puzzle = WordPuzzle.objects.get(id=puzzle_id)
            self.model.objects.get(puzzle=puzzle, clue_num=clue_num)
        except ObjectDoesNotExist:
            msg = 'This clue does not exist.'
        else:
            if request.user != puzzle.editor:
                msg = 'You cannot delete this clue since you are not the editor.'
            elif "delete_clue_confirm" not in request.path:
                puzzle.delete_clue(clue_num)
                return redirect('edit_puzzle', puzzle.id)
        return render(request, 'delete_clue.html',
                      context={'puzzle_id': puzzle_id, 'clue_num': clue_num, 'err_msg': msg})


class PreviewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, puzzle_id=None):
        msg = None
        data_dict = {'id': puzzle_id}
        try:
            puzzle = WordPuzzle.objects.get(id=puzzle_id)
        except ObjectDoesNotExist:
            msg = "This puzzle does not exist."
        else:
            if request.user != puzzle.editor:
                msg = 'You cannot preview this puzzle since you are not the creator.'
            else:
                data_dict['title'] = str(puzzle)
                data_dict['puzzle'] = puzzle
                data_dict['clues'] = puzzle.get_clues()
        data_dict['err_msg'] = msg
        return render(request, 'preview_puzzle.html', context=data_dict)


# ================================================================================
'''
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
'''
