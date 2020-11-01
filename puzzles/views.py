from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from puzzles.models import Puzzle
import json
from django.forms.models import model_to_dict


class HomeView(LoginRequiredMixin, View):
    model = Puzzle

    def get(self, request):
        puzzles = self.model.objects.order_by('-modified_at')
        puzzles_list = []
        for i in range(len(puzzles)):
            last_edited = puzzles[i].modified_at.isoformat()
            share_date = None if puzzles[i].shared_at is None else puzzles[i].shared_at.isoformat()
            dict_obj = {'puzzle_id': puzzles[i].id, 'is_xword': puzzles[i].is_xword, 'modified_at': last_edited,
                        'is_ready': puzzles[i].is_ready, 'desc': puzzles[i].desc, 'shared_at': share_date,
                        'name': str(puzzles[i]), 'editor': str(puzzles[i].editor)}
            puzzles_list.append(dict_obj)
        return render(request, "home.html", context={'data': json.dumps(puzzles_list)})


class NewPuzzleView(LoginRequiredMixin, View):
    model = Puzzle

    def get(self, request):
        page_title = "New Crossword Puzzle" if "xword" in request.path else "New Word Puzzle"
        context = {'puzzle_id':0, 'title': page_title}
        return render(request, "edit_puzzle.html", context)

    def post(self, request):
        try:
            if request.POST.get('action') == 'save':
                data_dict = json.loads(request.POST.get('data'))
                data_dict['data'] = json.dumps(data_dict['data'])
                puzzle_id = data_dict['id']
                del data_dict['id']
                if puzzle_id == 0:
                    record = self.model(**data_dict)
                    record.save()
                else:
                    puzzle_id = self.model.objects.filter(id=puzzle_id).update(**data_dict)
                    #record(**data_dict).save()
                return JsonResponse({'id': puzzle_id})
        except Exception as err:
            print(str(err))
            return JsonResponse({'error_message': str(err)})

class EditPuzzleView(LoginRequiredMixin, View):
    model = Puzzle

    def __init__(self):
        super().__init__()
        self.size = self.puzzle_id = self.is_ready = self.is_xword = None
        self.desc = self.editor = self.data = None

    def get(self, request, puzzle_id=0):
        if puzzle_id == 0:
            data_dict = {'puzzle_id': 0, 'is_xword': True}
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
        # self._form_data_string()
        record = None
        if self._validate_data():
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
        self.dict_obj = json.loads(request.POST.get('data'))
        self.dict_obj['editor'] = request.user
        # self.puzzle_id = dict_obj.get('puzzle_id')
        # self.size = dict_obj.get('size')
        # self.desc = dict_obj.get('desc')
        # self.is_xword = dict_obj.get('is_xword')
        # self.is_ready = dict_obj.get('is_ready')
        # self.shared_at = dict_obj.get('shared_at')
        # self.data = dict_obj.get('data')
        # self.editor = request.user

    # def _form_data_string(self):
    #     self.across_words = self.across_words if self.across_words is not None else {}
    #     self.down_words = self.down_words if self.down_words is not None else {}
    #     self.data = {'blocks': self.grid_blocks, 'across': self.across_words, 'down': self.down_words}

    def _validate_data(self):
        if self.size == 0:
            raise Exception("Size cannot be zero")
        if self.is_ready is None or self.is_xword is None or self.data is None:
            raise Exception("Missing keys in data")
        return True

    def _save_as_new(self):
        xword = self.model.objects.create(
            size=self.size, is_ready=self.is_ready, is_xword=self.is_xword, desc=self.desc,
            data=json.dumps(self.data), editor=self.editor
        )
        return xword

    def _save_as_update(self):
        record = self.model.objects.get(id=self.puzzle_id)
        record.size = self.size
        record.is_ready = self.is_ready
        record.is_xword = self.is_xword
        record.desc = self.desc
        record.data = json.dumps(self.data)
        record.save()
        return record

    def _build_puzzle_data_dict_from_dbrecord(self, record):
        data = json.loads(record.data)
        data_dict = {'puzzle_id': record.id, 'size': record.size, 'is_ready': record.is_ready,
                     'is_xword': record.is_xword, 'desc': record.desc, 'data': record.data
                    }
        return data_dict

    def _render_get_response(self, request, data_dict, error_msg=None):
        template = "edit_puzzle.html" if data_dict['is_xword'] else "edit_wpuzzle.html"
        prefix = "New " if data_dict['puzzle_id'] == 0 else "Edit "
        puzzle_type = "Crossword Puzzle" if data_dict['is_xword'] else "Word Puzzle"
        page_title = prefix + puzzle_type
        context = {'data': json.dumps(data_dict), 'title': page_title}
        if error_msg:
            context['error_message'] = error_msg
        return render(request, template, context=context)
