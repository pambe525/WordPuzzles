from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.forms.models import model_to_dict
from puzzles.models import Puzzle
import json


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
        context = {'id': None}
        return render(request, "edit_puzzle.html", context)

    def post(self, request, id=None):
        try:
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
                return JsonResponse({'id': record.id})
        except Exception as err:
            return JsonResponse({'error_message': str(err)})

class EditPuzzleView(LoginRequiredMixin, View):
    model = Puzzle

    def get(self, request, id=None):
        # New Puzzle GET (URL is new_xword_puzzle or new_word_puzzle)
        if "word" in request.path:
            is_word = True if "new_xword_puzzle" in request.path else False
            context = {'id': None, 'is_xword': is_word}
            return self.render_get_response(request, context)
        # Edit Puzzle GET (URL is edit_puzzle/id/)
        elif "edit_puzzle" in request.path:
            error_msg = None
            if id is None or id == 0:
                error_msg = "Invalid puzzle id"
                return self.render_get_response(request, {'id': id, 'is_xword': True}, error_msg)
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
                error_msg = "Puzzle ID " + str(id) + " does not exist"
            return self.render_get_response(request, data_dict, error_msg)

    def post(self, request, id=0):
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
            return JsonResponse({'id': record.id})

        # try:
        #     if request.POST.get('action') == 'delete':
        #         return self._delete_puzzle_data(request)
        #     else:
        #         return self._save_puzzle_data(request)
        # except Exception as err:
        #     return JsonResponse({'error_message': str(err)})

    # def _save_puzzle_data(self, request):
    #     self._extract_puzzle_data_from_request(request)
    #     record = None
    #     if self._validate_data():
    #         if self.id == 0:
    #             record = self._save_as_new()
    #         else:
    #             record = self._save_as_update()
    #     return JsonResponse({'id': record.id})

    def _delete_puzzle_data(self, request):
        id = request.POST.get('id')
        if not self.model.objects.filter(id=id).exists():
            raise Exception("Puzzle id does not exist")
        else:
            self.model.objects.filter(id=id).delete()
            return JsonResponse({'id': id})

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
        record = self.model.objects.get(id=self.id)
        record.size = self.size
        record.is_ready = self.is_ready
        record.is_xword = self.is_xword
        record.desc = self.desc
        record.data = json.dumps(self.data)
        record.save()
        return record

    def _build_puzzle_data_dict_from_dbrecord(self, record):
        data = json.loads(record.data)
        data_dict = {'id': record.id, 'size': record.size, 'is_ready': record.is_ready,
                     'is_xword': record.is_xword, 'desc': record.desc, 'data': record.data}
        return data_dict

    def render_get_response(self, request, data_dict, error_msg=None):
        context = {}
        if error_msg:
            context['error_message'] = error_msg
        if data_dict is not None:
            context['data'] = data_dict
        return render(request, "edit_puzzle.html", context=context)
