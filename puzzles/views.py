import json
import re
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, ListView

from puzzles.forms import WordPuzzleForm, ClueForm, SortPuzzlesForm, AddCluesForm
from puzzles.models import WordPuzzle, Clue, PuzzleSession


def add_session_data(puzzles, user):
    for puzzle in puzzles:
        puzzle.session_count = len(PuzzleSession.objects.filter(puzzle=puzzle))
        current_user_session = PuzzleSession.objects.filter(puzzle=puzzle, solver=user)
        puzzle.user_session = None if len(current_user_session) == 0 else current_user_session[0]


class ReleaseNotesView(TemplateView):
    template_name = "release_notes.html"


class HomeView(LoginRequiredMixin, View):

    def get(self, request):
        # seven_days_ago = now() - timedelta(days=7)
        # draft_puzzles = self.model.objects.filter(editor=request.user.id, shared_at=None).order_by('-modified_at')
        # recently_published = self.model.objects.exclude(shared_at=None).filter(shared_at__gte=seven_days_ago) \
        #     .order_by('-shared_at')
        # in_recent_sessions = self.get_puzzles_in_recent_sessions()
        # recent_puzzles = (in_recent_sessions | recently_published).distinct()  # Union of 2 sets
        # add_session_data(recent_puzzles, request.user)
        # drafts_count = WordPuzzle.get_draft_puzzles_count(request.user.id)
        draft_puzzles = WordPuzzle.get_draft_puzzles_as_list(request.user.id)
        new_puzzle_form = WordPuzzleForm()
        ctx = {'draft_puzzles': draft_puzzles, 'form': new_puzzle_form}
        return render(request, "home.html", context=ctx)

    # def get_puzzles_in_recent_sessions(self):
    #     seven_days_ago = now() - timedelta(days=7)
    #     puzzles_in_recent_sessions = WordPuzzle.objects.filter(puzzlesession__solver=self.request.user,
    #                                                            puzzlesession__modified_at__gte=seven_days_ago).order_by(
    #         '-puzzlesession__modified_at')
    #     return puzzles_in_recent_sessions


class NewPuzzleView(View):
    def post(self, request):
        form = WordPuzzleForm(request.POST)
        if form.is_valid():
            puzzle = WordPuzzle.create_new_puzzle(request.user, form.cleaned_data)
            return redirect("edit_puzzle", puzzle.id)


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


class DeletePuzzleView(EditorRequiredMixin, DeleteView):
    model = WordPuzzle
    success_url = '/'


class EditPuzzleView(EditorRequiredMixin, UpdateView):
    model = WordPuzzle
    template_name = 'edit_puzzle.html'
    fields = ['desc']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clues = self.object.get_clues()
        context['clues'] = clues
        context['id'] = self.object.id
        context['has_gaps'] = self.__clue_nums_have_gaps(clues)
        return context

    def form_valid(self, form):
        form.save(True)
        ctx = {'form': form, 'clues': self.object.get_clues(), 'object': self.object}
        return render(self.request, self.template_name, context=ctx)

    @staticmethod
    def __clue_nums_have_gaps(clues_list):
        if len(clues_list) == 0: return False
        clue_nums = [clue.clue_num for clue in clues_list]
        clue_nums.sort()
        if clue_nums[0] != 1: return True
        for i in range(1, len(clue_nums)):
            if clue_nums[i] - clue_nums[i - 1] > 1: return True
        return False


class AddCluesView(EditorRequiredMixin, View):
    template_name = "add_clues.html"

    def get(self, request, pk=None):
        puzzle = WordPuzzle.objects.get(id=pk)
        form = AddCluesForm
        ctx = {'id': pk, 'title': str(puzzle), 'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        puzzle = WordPuzzle.objects.get(id=pk)
        form = AddCluesForm(request.POST)
        self.__check_duplicate_answers(form, puzzle)
        if form.is_valid():
            puzzle.add_clues(form.cleaned_data_list)
            return redirect('edit_puzzle', pk)
        else:
            ctx = {'id': pk, 'title': str(puzzle), 'form': form}
            return render(request, self.template_name, ctx)

    @staticmethod
    def __check_duplicate_answers(form, puzzle):
        if form.has_error('answers'): return
        msg = "#{} answer is same as answer in clue #{}."
        for input_clue in form.cleaned_data_list:
            clue_num = puzzle.has_duplicate_answer(input_clue)
            if clue_num is not None:
                form.add_error('answers', msg.format(input_clue['clue_num'], clue_num))
                return


class EditClueView(EditorRequiredMixin, View):
    template_name = "edit_clue.html"

    def get(self, request, pk=None, clue_num=None):
        clue = Clue.objects.get(puzzle=pk, clue_num=clue_num)
        ctx = {'form': ClueForm(instance=clue), 'clue_num': clue_num, 'id': pk}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None, clue_num=None):
        form = ClueForm(request.POST)
        puzzle = WordPuzzle.objects.get(id=pk)
        self.__check_duplicate_answers(clue_num, form, puzzle)
        if form.is_valid():
            puzzle.update_clue(clue_num, form.cleaned_data)
            return redirect("edit_puzzle", puzzle.id)
        else:
            if clue_num is None: clue_num = puzzle.size + 1
            ctx = {'id': pk, 'clue_num': clue_num, 'form': form}
            return render(request, self.template_name, ctx)

    @staticmethod
    def __check_duplicate_answers(clue_num, form, puzzle):
        if form.has_error('answers'): return
        msg = "Answer is same as in clue #{}."
        clue_data = {'clue_num': clue_num, 'answer': form.data['answer']}
        repeated_clue_num = puzzle.has_duplicate_answer(clue_data)
        if repeated_clue_num is not None:
            form.add_error('answer', msg.format(repeated_clue_num))
            return


class DeleteClueView(EditorRequiredMixin, View):
    model = Clue
    success_url = 'edit_puzzle'

    def post(self, request, pk=None, clue_num=None):
        puzzle = WordPuzzle.objects.get(id=pk)
        puzzle.delete_clue(clue_num)
        return redirect('edit_puzzle', pk)


class PublishPuzzleView(EditorRequiredMixin, View):
    model = WordPuzzle

    def post(self, request, pk=None):
        puzzle = self.model.objects.get(id=pk)
        if puzzle.size == 0:
            err_msg = "No clues to publish.  Add clues before publishing."
            ctx = {'err_msg': err_msg, 'id': pk}
            return render(request, "puzzle_error.html", context=ctx)
        if not puzzle.is_published(): puzzle.publish()
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
        add_session_data(query_set, self.request.user)
        return query_set


class PreviewPuzzleView(EditorRequiredMixin, View):
    heading = "Preview Puzzle"
    puzzle = None
    active_session = None
    clues = None

    def get(self, request, *args, **kwargs):
        self.puzzle = WordPuzzle.objects.get(id=kwargs['pk'])
        if self.puzzle.editor == request.user:
            self.heading += " & Unpublish" if self.puzzle.is_published() else " & Publish"
            self.clues = self.get_clues_list(mode='PREVIEW')
        else:
            if PuzzleSession.objects.filter(solver=request.user, puzzle=self.puzzle).exists():
                return redirect("solve_puzzle", self.puzzle.id)
            self.heading += " & Solve"
            self.clues = self.get_clues_list(mode='PRESOLVE')
        return render(request, "word_puzzle.html", context=self.get_context_data())

    def get_context_data(self):
        if self.active_session is not None:
            self.active_session = json.dumps(self.active_session)
        return {'heading': self.heading, 'object': self.puzzle, 'active_session': self.active_session,
                'clues': json.dumps(self.clues)}

    def get_clues_list(self, mode='PREVIEW'):
        clues = self.puzzle.get_clues()
        clues_list = []
        for clue in clues:
            clue_dict = self.get_clue_as_dict(clue, mode=mode)
            clues_list.append(clue_dict)
        return clues_list

    def get_clue_as_dict(self, clue, mode='PREVIEW'):
        clue_dict = {'clue_num': clue.clue_num, 'clue_text': clue.get_decorated_clue_text(),
                     'points': clue.points}
        if mode == 'PREVIEW' or mode == 'SOLVED' or mode == 'REVEALED':
            clue_dict.update({'answer': clue.answer, 'parsing': clue.parsing, 'mode': mode})
        else:
            masked_answer = re.sub("[a-zA-Z]", "*", clue.answer)
            clue_dict.update({'answer': masked_answer, 'parsing': '', 'mode': mode})
        return clue_dict


class SolvePuzzleView(PreviewPuzzleView):
    solve_session = None

    def get(self, request, *args, **kwargs):
        self.puzzle = WordPuzzle.objects.get(id=kwargs['pk'])
        self.heading = "Solve Puzzle"
        self.solve_session, created = PuzzleSession.objects.get_or_create(solver=request.user, puzzle=self.puzzle)
        self.active_session = self.get_session_as_dict()
        self.clues = self.get_clues_list()
        return render(request, "word_puzzle.html", context=self.get_context_data())

    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.POST['data'])
        self.solve_session = PuzzleSession.objects.get(id=request_data['session_id'])
        self.puzzle = WordPuzzle.objects.get(id=self.solve_session.puzzle.id)
        if request.POST['action'] == 'timer':
            self.solve_session.elapsed_seconds = request_data['elapsed_secs']
            self.solve_session.save()
            return HttpResponse(status=204)
        else:
            clue = Clue.objects.get(puzzle_id=self.puzzle.id, clue_num=request_data['clue_num'])
            if request.POST['action'] == 'solve':
                answer_input = request_data['answer_input']
                if clue.answer.upper() == answer_input.upper():
                    self.solve_session.add_solved_clue_num(clue.clue_num)
                else:
                    raise AssertionError("Incorrect answer")
            elif request.POST['action'] == 'reveal':
                self.solve_session.add_revealed_clue_num(clue.clue_num)
        return self.get_json_response()

    def get_json_response(self):
        self.active_session = self.get_session_as_dict()
        self.clues = self.get_clues_list()
        return JsonResponse({'clues': json.dumps(self.clues), 'active_session': self.active_session})

    def get_session_as_dict(self):
        return {'session_id': self.solve_session.id,
                'elapsed_secs': self.solve_session.elapsed_seconds,
                'score': self.solve_session.score,
                'num_clues': self.solve_session.puzzle.size,
                'num_solved': len(self.solve_session.get_solved_clue_nums()),
                'num_revealed': len(self.solve_session.get_revealed_clue_nums())
                }

    def get_clues_list(self, **kwargs):
        clues = self.puzzle.get_clues()
        solved_clue_nums = self.solve_session.get_solved_clue_nums()
        revealed_clue_nums = self.solve_session.get_revealed_clue_nums()
        clues_list = []
        for clue in clues:
            if clue.clue_num in solved_clue_nums:
                mode = 'SOLVED'
            elif clue.clue_num in revealed_clue_nums:
                mode = 'REVEALED'
            else:
                mode = 'UNSOLVED'
            clue_dict = self.get_clue_as_dict(clue, mode=mode)
            clues_list.append(clue_dict)
        return clues_list


class PuzzleScoreView(LoginRequiredMixin, View):
    err_msg = None
    score_data = None
    puzzle = None
    sessions = None

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            self.puzzle = WordPuzzle.objects.get(id=pk)
            self.sessions = PuzzleSession.objects.filter(puzzle=self.puzzle).order_by("-score")
        except WordPuzzle.DoesNotExist:
            self.err_msg = "This puzzle does not exist."
        else:
            if not self.puzzle.is_published():
                self.err_msg = "This puzzle is not published."
            else:
                self.score_data = self.get_session_score_data(self.sessions)
        if self.err_msg is not None:
            return render(request, "puzzle_error.html", context={'err_msg': self.err_msg, 'id': pk})
        else:
            context = {'object': self.puzzle, 'id': pk, 'scores': self.score_data}
            return render(request, "puzzle_score.html", context=context)

    def get_session_score_data(self, sessions):
        scores = []
        for session in sessions:
            num_clues = session.puzzle.size
            num_solved = len(session.get_solved_clue_nums())
            num_revealed = len(session.get_revealed_clue_nums())
            perc_solved = str(round(100 * num_solved / num_clues)) + "%"
            perc_revealed = str(round(100 * num_revealed / num_clues)) + "%"
            is_complete = (num_solved + num_revealed == num_clues)
            elapsed_time = self.get_elapsed_time(session.elapsed_seconds)
            scores.append({'user': str(session.solver), 'elapsed_time': elapsed_time, 'score': session.score,
                           'perc_solved': perc_solved, 'perc_revealed': perc_revealed, 'is_complete': is_complete,
                           'num_solved': num_solved, 'num_revealed': num_revealed, 'modified_at': session.modified_at})
        return scores if len(scores) > 0 else None

    def get_elapsed_time(self, seconds):
        return str(timedelta(seconds=seconds)) + "s"
