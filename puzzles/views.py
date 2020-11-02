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


class EditPuzzleView(LoginRequiredMixin, View):
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

    def post(self, request):
        try:
            id = None
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
            context['data'] = data_dict
        return render(request, "edit_puzzle.html", context=context)
