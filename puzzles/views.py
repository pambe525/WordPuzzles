import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, ListView

from puzzles.forms import WordPuzzleForm, ClueForm, SortPuzzlesForm
from puzzles.models import WordPuzzle, Clue


def utc_date_to_local_format(utc_date):
    dt_format = '%b %d, %Y at %H:%M:%S'
    return utc_date.astimezone().strftime(dt_format)

class ReleaseNotesView(TemplateView):
    template_name = "release_notes.html"


class HomeView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        seven_days_ago = now() - timedelta(days=7)
        draft_puzzles = self.model.objects.filter(editor=request.user.id, shared_at=None).order_by('-modified_at')
        recent_puzzles = self.model.objects.exclude(shared_at=None).filter(shared_at__gte=seven_days_ago).order_by('-shared_at')
        ctx = {'draft_puzzles': draft_puzzles, 'recent_puzzles': recent_puzzles}
        return render(request, "home.html", context=ctx)


class NewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        puzzle = self.model.objects.create(editor=self.request.user)
        return redirect('edit_puzzle', puzzle.id)


class PuzzleEditorMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, pk=None, clue_num=None):
        err_msg = None
        if request.user.is_authenticated:
            try:
                puzzle = WordPuzzle.objects.get(id=pk)
                if clue_num: Clue.objects.get(puzzle=pk, clue_num=clue_num)
            except WordPuzzle.DoesNotExist:
                err_msg = "This puzzle does not exist."
            except Clue.DoesNotExist:
                err_msg = "This clue does not exist."
            else:
                if request.user != puzzle.editor:
                    err_msg = "This operation is not permitted since you are not the editor."
                elif puzzle.shared_at is not None and "publish" not in request.resolver_match.url_name \
                        and "preview" not in request.resolver_match.url_name:
                    err_msg = "Published puzzle cannot be edited. Unpublish to edit."
        if err_msg is not None:
            ctx = {'err_msg': err_msg, 'id': pk, 'clue_num': clue_num}
            return render(request, "puzzle_error.html", context=ctx)
        return super(PuzzleEditorMixin, self).dispatch(request, *args, pk=pk, clue_num=clue_num)


class EditPuzzleView(PuzzleEditorMixin, UpdateView):
    model = WordPuzzle
    template_name = 'edit_puzzle.html'
    form_class = WordPuzzleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clues'] = self.object.get_clues()
        context['id'] = self.object.id
        context['saved'] = False
        return context

    def form_valid(self, form):
        form.save()
        ctx = {'form': form, 'saved': True, 'id': self.object.id, 'clues': self.object.get_clues(),
               'object': self.object}
        return render(self.request, self.template_name, context=ctx)


class DeletePuzzleView(PuzzleEditorMixin, DeleteView):
    model = WordPuzzle
    template_name = 'delete_confirm.html'
    success_url = '/'


class EditClueView(PuzzleEditorMixin, View):
    template_name = "edit_clue.html"

    def get(self, request, pk=None, clue_num=None):
        ctx = {'form': ClueForm(), 'clue_num': clue_num, 'id': pk}
        puzzle = WordPuzzle.objects.get(id=pk)
        if clue_num is None:
            ctx['clue_num'] = puzzle.size + 1
        else:
            clue = Clue.objects.get(puzzle=pk, clue_num=clue_num)
            ctx['form'] = ClueForm(instance=clue)
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None, clue_num=None):
        form = ClueForm(request.POST)
        puzzle = WordPuzzle.objects.get(id=pk)
        if form.is_valid():
            if clue_num is None:  # New clue
                puzzle.add_clue(form.cleaned_data)
            else:
                puzzle.update_clue(clue_num, form.cleaned_data)
            return redirect("edit_puzzle", puzzle.id)
        else:
            if clue_num is None: clue_num = puzzle.size + 1
            ctx = {'id': pk, 'clue_num': clue_num, 'form': form}
            return render(request, self.template_name, ctx)


class DeleteClueView(PuzzleEditorMixin, View):
    model = Clue
    template_name = "delete_confirm.html"
    success_url = 'edit_puzzle'

    def get(self, request, pk=None, clue_num=None):
        puzzle = WordPuzzle.objects.get(id=pk)
        ctx = {'object': puzzle, 'clue_num': clue_num}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None, clue_num=None):
        puzzle = WordPuzzle.objects.get(id=pk)
        puzzle.delete_clue(clue_num)
        return redirect('edit_puzzle', pk)


class PreviewPuzzleView(PuzzleEditorMixin, View):
    model = WordPuzzle

    def get(self, request, **kwargs):
        puzzle = self.model.objects.get(id=kwargs['pk'])
        ctx = {'object': puzzle}
        return render(request, 'preview_puzzle.html', context=ctx)


class PublishPuzzleView(PuzzleEditorMixin, View):
    model = WordPuzzle

    def get(self, request, **kwargs):
        puzzle = self.model.objects.get(id=kwargs['pk'])
        if puzzle.size == 0:
            err_msg = "No clues to publish.  Add clues before publishing."
            ctx = {'err_msg': err_msg, 'id': kwargs['pk']}
            return render(request, "puzzle_error.html", context=ctx)
        if not puzzle.is_published():
            puzzle.publish()
        return redirect('home')


class UnpublishPuzzleView(PuzzleEditorMixin, View):
    model = WordPuzzle

    def get(self, request, **kwargs):
        puzzle = self.model.objects.get(id=kwargs['pk'])
        puzzle.unpublish()
        return redirect('home')

class PuzzlesListView(LoginRequiredMixin, ListView):
    template_name = "all_puzzles.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        sort_by = self.request.GET.get('sort_by', 'shared_at')
        order = self.request.GET.get('order', '-')
        context = super(PuzzlesListView, self).get_context_data(**kwargs)
        context['form'] = SortPuzzlesForm(initial={'sort_by':sort_by, 'order':order})
        return context

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'shared_at')
        order = self.request.GET.get('order', '-')
        query_set = WordPuzzle.objects.exclude(shared_at=None).order_by(order + sort_by)
        return query_set

class SolvePuzzleView(LoginRequiredMixin, View):
    def get(self, request, pk=None):
        try:
            puzzle = WordPuzzle.objects.get(id=pk)
        except WordPuzzle.DoesNotExist:
            err_msg = "This puzzle does not exist."
            ctx = {'err_msg': err_msg, 'id': pk}
            return render(request, "puzzle_error.html", context=ctx)
        else:
            if puzzle.editor == request.user:
                return redirect('preview_puzzle', pk)
            else:
                clues_list = self.get_clues_list(puzzle)
                return render(request, "solve_puzzle.html", context={'object':puzzle, 'clues': json.dumps(clues_list)})

    def get_clues_list(self, puzzle):
        clues = puzzle.get_clues()
        clues_list = []
        for index in range(0, len(clues)):
            data = {'clue_num': clues[index].clue_num, 'clue_text': clues[index].get_decorated_clue_text(),
                    'points': clues[index].points}
            clues_list.append(data)
        return clues_list