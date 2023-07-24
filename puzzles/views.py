import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import UpdateView, DeleteView, TemplateView, ListView

from puzzles.forms import WordPuzzleForm, ClueForm, AddCluesForm, SortPuzzlesForm
from puzzles.models import WordPuzzle, Clue, SolverSession, GroupSession


def add_session_data(puzzles, user):
    for puzzle in puzzles:
        puzzle.session_count = len(SolverSession.objects.filter(puzzle=puzzle))
        current_user_session = SolverSession.objects.filter(puzzle=puzzle, solver=user)
        puzzle.user_session = None if len(current_user_session) == 0 else current_user_session[0]


class ReleaseNotesView(TemplateView):
    template_name = "release_notes.html"


class HomeView(LoginRequiredMixin, View):

    def get(self, request):
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
            msg = "Set your first & last name in <a href='/account'>Account Settings</a>."
            notifications.append(msg)
        other_published_puzzles = WordPuzzle.objects.exclude(shared_at=None).exclude(editor=request.user)
        users_unattempted_puzzles = other_published_puzzles.exclude(solversession__solver=request.user)
        users_unfinished_puzzles = \
            other_published_puzzles.filter(solversession__finished_at=None, solversession__solver=request.user)
        if len(users_unattempted_puzzles) > 0:
            msg = "Pick a puzzle to solve in <a href='/puzzles_list?show=unsolved'>Published Puzzles</a>."
            notifications.append(msg)
        if len(users_unfinished_puzzles) > 0:
            msg = "You have " + str(len(users_unfinished_puzzles)) + \
                  " <a href='/puzzles_list?show=unfinished'>unfinished puzzle(s)</a> to solve."
            notifications.append(msg)
        return notifications


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
        if puzzle.has_sessions():
            err_msg = "Puzzle cannot be unpublished due to existing sessions."
            ctx = {'err_msg': err_msg, 'id': kwargs['pk']}
            return render(request, "puzzle_error.html", context=ctx)
        puzzle.unpublish()
        return redirect('home')


class ScheduleGroupSessionView(EditorRequiredMixin, View):
    model = WordPuzzle

    def post(self, request, pk=None):
        puzzle = self.model.objects.get(id=pk)
        err_msg = None
        if puzzle.size == 0:
            err_msg = "No clues found.  Add clues before scheduling."
        elif puzzle.is_published():
            err_msg = "This puzzle is published and cannot be scheduled."
        elif len(GroupSession.objects.filter(puzzle=puzzle)) > 0:
            err_msg = "Puzzle has a previous group session."
        if err_msg is not None:
            ctx = {'err_msg': err_msg, 'id': pk}
            return render(request, "puzzle_error.html", context=ctx)
        GroupSession.objects.create(puzzle=puzzle, host=request.user, start_at=request.POST['scheduled_at'])
        return redirect('home')


class UnscheduleGroupSessionView(EditorRequiredMixin, View):
    model = WordPuzzle

    def post(self, request, pk=None):
        puzzle = self.model.objects.get(id=pk)
        err_msg = None
        group_session = GroupSession.objects.filter(puzzle=puzzle)
        if not group_session.exists():
            err_msg = 'No group session found for given puzzle.'
        elif SolverSession.objects.filter(puzzle=puzzle, group_session=group_session[0]).exists():
            err_msg = 'Puzzle group session has participants and cannot be deleted.'
        if err_msg is not None:
            ctx = {'err_msg': err_msg, 'id': pk}
            return render(request, "puzzle_error.html", context=ctx)
        group_session[0].delete()
        return redirect('home')


class PuzzlesListView(LoginRequiredMixin, ListView):
    template_name = "puzzles_list.html"
    paginate_by = 10
    show_filter = None

    def get_context_data(self, **kwargs):
        context = super(PuzzlesListView, self).get_context_data(**kwargs)
        for puzzle in context['object_list']:
            solver_session = SolverSession.objects.filter(solver=self.request.user, puzzle=puzzle, group_session=None)
            other_sessions = SolverSession.objects.filter(puzzle=puzzle, group_session=None).exclude(
                solver=self.request.user)
            if len(solver_session) == 0:
                puzzle.status = 0  # No session exists
            elif solver_session[0].finished_at is None:
                puzzle.status = 1  # Session in progress
            else:
                puzzle.status = 2  # Session completed
            puzzle.other_sessions = len(other_sessions)
        context['form'] = SortPuzzlesForm(initial={'show': self.show_filter})
        return context

    def get_queryset(self):
        self.show_filter = self.request.GET.get('show', 'all')
        query_set = WordPuzzle.objects.exclude(shared_at=None)
        if self.show_filter == 'me_editor':
            query_set = query_set.filter(editor=self.request.user)
        elif self.show_filter == 'unsolved':
            query_set = query_set.exclude(editor=self.request.user).exclude(solversession__solver=self.request.user)
        elif self.show_filter == 'unfinished':
            query_set = query_set.filter(solversession__solver=self.request.user, solversession__finished_at=None)
        return query_set.order_by("-shared_at")


class PuzzleSessionView(IsSolvableMixin, View):
    session = None
    clues = None

    def get(self, request, *args, **kwargs):
        if SolverSession.objects.filter(solver=request.user, puzzle=self.puzzle, group_session=None).exists():
            self.session = SolverSession.objects.get(puzzle=self.puzzle, solver=request.user)
        if request.user == self.puzzle.editor: return redirect("edit_puzzle", self.pk)
        return render(request, "puzzle_session.html", context=self.get_context_data(request.user))

    def post(self, request, *args, **kwargs):
        SolverSession.new(self.puzzle, request.user)
        return redirect("puzzle_session", self.puzzle.id)

    def get_context_data(self, solver):
        if self.session is not None:
            self.clues = self.puzzle.get_clues()
            solved_clues_ids = self.session.get_all_solved_clue_ids()
            revealed_clues_ids = self.session.get_all_revealed_clue_ids()
            for clue in self.clues:
                clue.state = 0
                clue.clue_text = clue.get_decorated_clue_text()
                if clue.id in solved_clues_ids:
                    clue.state = 1
                elif clue.id in revealed_clues_ids:
                    clue.state = 2
        return {'puzzle': self.puzzle, 'session': self.session, 'clues': self.clues}


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
                session.set_solved_clue(target_clue)
        else:
            session.set_revealed_clue(target_clue)
        return JsonResponse({'err_msg': ''})


class PuzzleScoreView(IsSolvableMixin, View):

    def get(self, request, *args, **kwargs):
        self.puzzle = WordPuzzle.objects.get(id=kwargs['pk'])
        sessions = SolverSession.objects.filter(puzzle=self.puzzle, group_session=None).order_by("-score")
        if len(sessions) == 0: sessions = None
        return render(request, "puzzle_score.html", context={'object': self.puzzle, 'sessions': sessions})
