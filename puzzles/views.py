import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, ListView

from puzzles.forms import WordPuzzleForm, ClueForm, SortPuzzlesForm
from puzzles.models import WordPuzzle, Clue, PuzzleSession


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
        recent_puzzles = self.model.objects.exclude(shared_at=None).filter(shared_at__gte=seven_days_ago).order_by(
            '-shared_at')
        ctx = {'draft_puzzles': draft_puzzles, 'recent_puzzles': recent_puzzles}
        return render(request, "home.html", context=ctx)


class NewPuzzleView(LoginRequiredMixin, View):
    model = WordPuzzle

    def get(self, request):
        puzzle = self.model.objects.create(editor=self.request.user)
        return redirect('edit_puzzle', puzzle.id)


class EditorRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        err_msg = None
        pk = kwargs['pk']
        clue_num = kwargs['clue_num'] if 'clue_num' in kwargs else None

        if request.user.is_authenticated:
            try:
                puzzle = WordPuzzle.objects.get(id=pk)
                if clue_num: Clue.objects.get(puzzle=kwargs['pk'], clue_num=clue_num)
            except WordPuzzle.DoesNotExist:
                err_msg = "This puzzle does not exist."
            except Clue.DoesNotExist:
                err_msg = "This clue does not exist."
            else:
                url_name = request.resolver_match.url_name
                if puzzle.is_published():
                    if "publish" not in url_name and "preview" not in url_name and "solve" not in url_name:
                        err_msg = "Published puzzle cannot be edited. Unpublish to edit."
                    elif "solve" in url_name and request.user == puzzle.editor:
                        return redirect("preview_puzzle", puzzle.id)
                elif request.user != puzzle.editor:
                    err_msg = "This operation is not permitted since you are not the editor."
                elif "solve" in url_name:
                    err_msg = "This puzzle is not published."
        if err_msg is not None:
            ctx = {'err_msg': err_msg, 'id': pk, 'clue_num': clue_num}
            return render(request, "puzzle_error.html", context=ctx)
        return super(EditorRequiredMixin, self).dispatch(request, *args, **kwargs)


class EditPuzzleView(EditorRequiredMixin, UpdateView):
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


class DeletePuzzleView(EditorRequiredMixin, DeleteView):
    model = WordPuzzle
    template_name = 'delete_confirm.html'
    success_url = '/'


class EditClueView(EditorRequiredMixin, View):
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


class DeleteClueView(EditorRequiredMixin, View):
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


class PublishPuzzleView(EditorRequiredMixin, View):
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


class UnpublishPuzzleView(EditorRequiredMixin, View):
    model = WordPuzzle

    def get(self, request, **kwargs):
        puzzle = self.model.objects.get(id=kwargs['pk'])
        puzzle.unpublish()
        return redirect('home')


class PuzzlesListView(LoginRequiredMixin, ListView):
    template_name = "puzzles_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        sort_by = self.request.GET.get('sort_by', 'shared_at')
        order = self.request.GET.get('order', '-')
        context = super(PuzzlesListView, self).get_context_data(**kwargs)
        context['form'] = SortPuzzlesForm(initial={'sort_by': sort_by, 'order': order})
        return context

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'shared_at')
        order = self.request.GET.get('order', '-')
        query_set = WordPuzzle.objects.exclude(shared_at=None).order_by(order + sort_by)
        return query_set


class PreviewPuzzleView(EditorRequiredMixin, View):
    show_answers = True
    heading = "Preview Puzzle"
    puzzle = None
    active_session = False

    def get(self, request, *args, **kwargs):
        self.puzzle = WordPuzzle.objects.get(id=kwargs['pk'])
        if self.puzzle.editor == request.user:
            self.heading += " & Unpublish" if self.puzzle.is_published() else " & Publish"
        else:
            self.heading += " & Solve"
            self.show_answers = False
        return render(request, "word_puzzle.html", context=self.get_context_data())

    def get_context_data(self):
        return {'heading': self.heading, 'show_answers': self.show_answers, 'object': self.puzzle,
               'clues': json.dumps(self.get_clues_list()), 'active_session': self.active_session}

    def get_clues_list(self):
        clues = self.puzzle.get_clues()
        clues_list = []
        for index in range(0, len(clues)):
            data = {'clue_num': clues[index].clue_num, 'clue_text': clues[index].get_decorated_clue_text(),
                    'points': clues[index].points}
            if self.show_answers:
                data.update({'answer': clues[index].answer, 'parsing': clues[index].parsing})
            clues_list.append(data)
        return clues_list

class SolvePuzzleView(PreviewPuzzleView):

    solve_session = None
    active_session = True

    def get(self, request, *args, **kwargs):
        self.puzzle = WordPuzzle.objects.get(id=kwargs['pk'])
        self.heading = "Solve Puzzle"
        self.show_answers = False
        self.solve_session, created = PuzzleSession.objects.get_or_create(solver=request.user, puzzle=self.puzzle)
        return render(request, "word_puzzle.html", context=self.get_context_data())

    def get_context_data(self):
        ctx = super(SolvePuzzleView, self).get_context_data()
        session_dict = {'solver_id':self.solve_session.solver.id, 'puzzle_id': self.puzzle.id,
                        'elapsed_secs': self.solve_session.elapsed_seconds, 'score': self.solve_session.get_score(),
                        'solved_clues': self.solve_session.get_solved_clue_nums(),
                        'revealed_clues': self.solve_session.get_revealed_clue_nums()
                        }
        ctx['session'] = json.dumps(session_dict)
        return ctx
