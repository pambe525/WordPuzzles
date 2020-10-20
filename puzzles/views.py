from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from puzzles.models import Crossword
import logging


class HomeView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "home.html", {})


class NewCrosswordView(LoginRequiredMixin, View):

    model = Crossword

    def __init__(self):
        super().__init__()
        self.context = {'puzzle_id': 0, 'has_error': False, 'message': ''}

    def get(self, request):
        return render(request, "edit_xword.html", { 'pk':0 })

    def post(self, request):
        if self.request.is_ajax():
            request.POST.get('data')
            return JsonResponse({"success": "succeeded"})

        if self._validate_data(request.POST):
            grid_size = request.POST.get('grid_size')
            grid_content = request.POST.get('grid_content')
            xword = self.model.objects.create(grid_size=grid_size, grid_content=grid_content, editor=request.user)
            self.context['puzzle_id'] = xword.id
        return render(request, "edit_xword.html", self.context)

    def _validate_data(self, data_dict):
        grid_size = int(data_dict.get('grid_size'))
        if grid_size == 0:
            self.context['has_error'] = True
            self.context['message'] = "Grid size cannot be zero"
            return False
        elif len(data_dict.get('grid_content')) != grid_size * grid_size:
            self.context['has_error'] = True
            self.context['message'] = "Grid content length must match no. of grid squares"
            return False
        return True