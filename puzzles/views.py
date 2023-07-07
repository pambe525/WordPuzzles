import json
import logging
import pdb
import re
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.defaultfilters import register
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, ListView

from puzzles.forms import WordPuzzleForm, ClueForm, AddCluesForm
from puzzles.models import WordPuzzle, Clue, SolverSession, SolvedClue


def add_session_data(puzzles, user):
    for puzzle in puzzles:
        puzzle.session_count = len(SolverSession.objects.filter(puzzle=puzzle))
        current_user_session = SolverSession.objects.filter(puzzle=puzzle, solver=user)
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
        notifications = self.__build_notifications(request)
        new_puzzle_form = WordPuzzleForm()
        ctx = {'notifications': notifications, 'draft_puzzles': draft_puzzles, 'form': new_puzzle_form}
        return render(request, "home.html", context=ctx)

    @staticmethod
    def __build_notifications(request):
        notifications = ["See <b>What's New</b> in the <a href='/release_notes'>Release Notes</a>.",
                         "<a id='btnCreatePuzzle'>Create a New Puzzle.</a>"]
        if request.user.first_name == "" and request.user.last_name == "":
            notifications.append("Set your first & last name in <a href='/account'>Account Settings</a>.")
        if len(WordPuzzle.objects.exclude(shared_at=None)) > 0:
            notifications.append("Pick a puzzle to solve in <a href='/puzzles_list'>Published Puzzles</a>.")
        return notifications

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


class ItemRequiredMixin(LoginRequiredMixin):
    puzzle = None
    err_msg = None
    pk = None
    clue_num = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            response = self.do_checks(request, *args, **kwargs)
            if response: return response
        if self.err_msg is not None:
            ctx = {'err_msg': self.err_msg, 'id': self.pk, 'clue_num': self.clue_num}
            return render(request, "puzzle_error.html", context=ctx)
        return super(ItemRequiredMixin, self).dispatch(request, *args, **kwargs)

    def do_checks(self, request, *args, **kwargs):
        self.pk = kwargs['pk']
        self.clue_num = kwargs['clue_num'] if 'clue_num' in kwargs else None
        try:
            self.puzzle = WordPuzzle.objects.get(id=self.pk)
            if self.clue_num: Clue.objects.get(puzzle=kwargs['pk'], clue_num=self.clue_num)
        except WordPuzzle.DoesNotExist:
            self.err_msg = "This puzzle does not exist."
        except Clue.DoesNotExist:
            self.err_msg = "This clue does not exist."


class IsSolvableMixin(ItemRequiredMixin):

    def do_checks(self, request, *args, **kwargs):
        super(IsSolvableMixin, self).do_checks(request, *args, **kwargs)
        if self.err_msg is not None: return
        if not self.puzzle.is_published():
            self.err_msg = "This puzzle is not published."
        elif request.user == self.puzzle.editor:
            return redirect("edit_puzzle", self.pk)


class EditorRequiredMixin(ItemRequiredMixin):

    def do_checks(self, request, *args, **kwargs):
        super(EditorRequiredMixin, self).do_checks(request, *args, **kwargs)
        if self.err_msg is not None: return
        if request.user != self.puzzle.editor:
            self.err_msg = "This operation is not permitted since you are not the editor."


class DraftRequiredMixin(EditorRequiredMixin):

    def do_checks(self, request, *args, **kwargs):
        super(DraftRequiredMixin, self).do_checks(request, *args, **kwargs)
        if self.err_msg is not None: return
        if self.puzzle.is_published():
            self.err_msg = "Cannot add clues to published puzzle."


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


class AddCluesView(DraftRequiredMixin, View):
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

    def post(self, request, **kwargs):
        puzzle = self.model.objects.get(id=kwargs['pk'])
        puzzle.unpublish()
        return redirect('home')


class PuzzlesListView(LoginRequiredMixin, ListView):
    template_name = "puzzles_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PuzzlesListView, self).get_context_data(**kwargs)
        # sort_by = self.request.GET.get('sort_by', 'shared_at')
        # order = self.request.GET.get('order', '-')
        # context['form'] = SortPuzzlesForm(initial={'sort_by': sort_by, 'order': order})
        return context

    def get_queryset(self):
        query_set = WordPuzzle.objects.exclude(shared_at=None).order_by("-shared_at")
        #     sort_by = self.request.GET.get('sort_by', 'shared_at')
        #     order = self.request.GET.get('order', '-')
        #     query_set = WordPuzzle.objects.exclude(shared_at=None).order_by(order + sort_by)
        #     add_session_data(query_set, self.request.user)
        return query_set


class PuzzleSessionView(IsSolvableMixin, View):
    session = None

    def get(self, request, *args, **kwargs):
        if SolverSession.objects.filter(solver=request.user, puzzle=self.puzzle, group_session=None).exists():
            self.session = SolverSession.objects.get(solver=request.user, puzzle=self.puzzle, group_session=None)
        return render(request, "puzzle_session.html", context=self.get_context_data(request.user))

    def post(self, request, *args, **kwargs):
        SolverSession.objects.create(solver=request.user, puzzle=self.puzzle)
        return redirect("puzzle_session", self.puzzle.id)

    def get_context_data(self, solver):
        clues = self.puzzle.get_clues()
        solved_clues_ids = self.puzzle.get_all_solved_clue_ids(solver)
        revealed_clues_ids = self.puzzle.get_all_revealed_clue_ids(solver)
        score = 0
        for clue in clues:
            clue.state = 0
            clue.clue_text = clue.get_decorated_clue_text()
            if clue.id in solved_clues_ids:
                clue.state = 1
                score += clue.points
            elif clue.id in revealed_clues_ids:
                clue.state = 2
        if self.session is not None:
            self.session.score = score
            self.session.solved = len(solved_clues_ids)
            self.session.revealed = len(revealed_clues_ids)
        return {'puzzle': self.puzzle, 'session': self.session, 'clues': clues}


class AjaxAnswerRequest(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)['data']
        action = json.loads(request.body)['action']
        session = SolverSession.objects.get(id=data['session_id'])
        puzzle_id = data['puzzle_id']
        clue_num = data['clue_num']
        target_clue = Clue.objects.get(puzzle=puzzle_id, clue_num=clue_num)
        if action == 'check':
            input_answer = data['input_answer']
            if target_clue.answer.upper() != input_answer.upper():
                return JsonResponse({'err_msg': "Answer is incorrect."})
            else:
                SolvedClue.objects.create(clue=target_clue, session=session, solver=request.user)
        else:
            SolvedClue.objects.create(clue=target_clue, session=session, solver=request.user, revealed=True)
        session.check_if_ended()
        return JsonResponse({'err_msg': ''})


class PuzzleScoreView(LoginRequiredMixin, View):
    err_msg = None
    score_data = None
    puzzle = None
    sessions = None

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            self.puzzle = WordPuzzle.objects.get(id=pk)
            self.sessions = SolverSession.objects.filter(puzzle=self.puzzle).order_by("-score")
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
