from django.views import View
from django.shortcuts import render
from .forms import NewUserForm


class NewUserView(View):
    def get(self, request):
        form = NewUserForm()
        context = {'form': form}
        return render(request, "new_user.html", context)
