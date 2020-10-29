from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from puzzles.models import Crossword
from datetime import timezone
import json


class HomeView(LoginRequiredMixin, View):
    model = Crossword

    def get(self, request):
        puzzles = self.model.objects.order_by('-modified_at')
        puzzles_list = []
        for i in range(len(puzzles)):
            timestamp = puzzles[i].modified_at.replace(tzinfo=timezone.utc).timestamp()
            dict_obj = {'id': puzzles[i].id, 'date': timestamp, 'is_ready': puzzles[i].is_ready,
                        'name': str(puzzles[i]), 'editor': str(puzzles[i].editor)}
            puzzles_list.append(dict_obj)
        return render(request, "home.html", context={'data': json.dumps(puzzles_list)})


class EditCrosswordView(LoginRequiredMixin, View):
    model = Crossword

    def __init__(self):
        super().__init__()
        self.grid_size = self.puzzle_id = self.is_ready = self.grid_blocks = None
        self.across_words = self.down_words = self.editor = None

    def get(self, request, puzzle_id=0):
        if puzzle_id == 0:
            data_dict = {'puzzle_id': 0}
            return self._render_get_response(request, data_dict)
        else:
            error_msg = None
            if self.model.objects.filter(id=puzzle_id).exists():
                record = self.model.objects.get(id=puzzle_id)
                if request.user == record.editor:
                    data_dict = self._build_puzzle_data_dict_from_dbrecord(record)
                else:
                    data_dict = {'puzzle_id': puzzle_id}
                    error_msg = "You are not authorized to edit this puzzle"
            else:
                data_dict = {'puzzle_id': puzzle_id}
                error_msg = "Puzzle ID " + str(puzzle_id) + " does not exist"
            return self._render_get_response(request, data_dict, error_msg)

    def post(self, request, puzzle_id=0):
        try:
            if request.POST.get('action') == 'delete':
                return self._delete_puzzle_data(request)
            else:
                return self._save_puzzle_data(request)
        except Exception as err:
            return JsonResponse({'error_message': str(err)})

    def _save_puzzle_data(self, request):
        self._extract_puzzle_data_from_request(request)
        self._clean_data()
        if self._validate_data():
            record = None
            if self.puzzle_id == 0:
                record = self._save_as_new()
            else:
                record = self._save_as_update()
            return JsonResponse({'puzzle_id': record.id})

    def _delete_puzzle_data(self, request):
        puzzle_id = request.POST.get('puzzle_id')
        if not self.model.objects.filter(id=puzzle_id).exists():
            raise Exception("Puzzle id does not exist")
        else:
            self.model.objects.filter(id=puzzle_id).delete()
            return JsonResponse({'puzzle_id': puzzle_id})

    def _extract_puzzle_data_from_request(self, request):
        dict_obj = json.loads(request.POST.get('data'))
        self.grid_size = dict_obj.get('grid_size')
        self.puzzle_id = dict_obj.get('puzzle_id')
        self.is_ready = dict_obj.get('is_ready')
        self.grid_blocks = dict_obj.get('blocks')
        self.across_words = dict_obj.get('across')
        self.down_words = dict_obj.get('down')
        self.editor = request.user

    def _clean_data(self):
        self.across_words = json.dumps(self.across_words) if self.across_words is not None else ""
        self.down_words = json.dumps(self.down_words) if self.down_words is not None else ""

    def _validate_data(self):
        if self.grid_size == 0:
            raise Exception("Grid size cannot be zero")
        if self.is_ready is None or self.grid_blocks is None:
            raise Exception("Missing keys in grid data")
        return True

    def _save_as_new(self):
        xword = self.model.objects.create(
            grid_size=self.grid_size, is_ready=self.is_ready,
            grid_blocks=self.grid_blocks, across_words=self.across_words, down_words=self.down_words,
            editor=self.editor
        )
        return xword

    def _save_as_update(self):
        record = self.model.objects.get(id=self.puzzle_id)
        record.grid_size = self.grid_size
        record.is_ready = self.is_ready
        record.grid_blocks = self.grid_blocks
        record.across_words = self.across_words
        record.down_words = self.down_words
        record.save()
        return record

    def _build_puzzle_data_dict_from_dbrecord(self, record):
        data_dict = {'puzzle_id': record.id, 'grid_size': record.grid_size,
                     'grid_blocks': record.grid_blocks, 'is_ready': record.is_ready,
                     'across_words': json.loads(record.across_words),
                     'down_words': json.loads(record.down_words)
                     }
        return data_dict

    def _render_get_response(self, request, data_dict, error_msg=None):
        page_title = "New Crossword Puzzle" if data_dict['puzzle_id'] == 0 else "Edit Crossword Puzzle"
        context = {'data': json.dumps(data_dict), 'title': page_title}
        if error_msg:
            context['error_message'] = error_msg
        return render(request, "edit_xword.html", context=context)
