from django.contrib.auth import logout, login
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.views import LoginView, PasswordResetView

from .forms import NewUserForm


class SignUpView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "signup.html", {'form': NewUserForm()})
        else:
            return redirect("home")

    def post(self, request):
        form = NewUserForm(request.POST)
        if not form.is_valid():
            return render(request, "signup.html", {'form': form})
        else:
            user = form.save()
            login(request, user)
            return redirect("home")

